"""
feishu.py — 飞书 API 封装模块
职责：
  1. 上传图片到飞书图床（解决公众号防盗链）
  2. 在指定位置（个人空间文件夹 or 知识库）创建文档
  3. 查询可用的文件夹和知识库列表（供 OpenClaw 展示给用户选择）
"""

import json
import os
import re
import time
import requests
import tempfile
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

FEISHU_BASE = "https://open.feishu.cn/open-apis"


@dataclass
class SaveTarget:
    """存储目标描述"""
    type: str           # "folder"（个人空间文件夹）或 "wiki"（知识库节点）
    token: str          # folder_token 或 wiki space_id
    node_token: str     # wiki 节点 token（仅 wiki 类型使用）
    display_name: str   # 显示名称


@dataclass
class SaveResult:
    """保存结果"""
    document_url: str
    document_id: str
    title: str


# ─── 主要公开接口 ──────────────────────────────────────────────────────────────

def upload_image(image_url: str, user_token: str, doc_id: str = "", image_b64: str = "") -> str | None:
    """
    上传图片至飞书图床。
    优先使用 image_b64（base64编码的图片数据，由Playwright在浏览器上下文中下载）。
    若 image_b64 为空则尝试直接下载（可能因微信防盗链失败）。
    doc_id: 文档ID，用于关联图片到具体文档（parent_node）
    返回飞书图片 token（用于插入文档），失败返回 None
    """
    import base64 as _base64
    try:
        if image_b64:
            # 从base64数据恢复图片字节
            img_bytes = _base64.b64decode(image_b64)
            content_type = "image/jpeg"
            ext = ".jpg"
            # 根据文件头判断实际格式
            if img_bytes[:4] == b'\x89PNG':
                content_type, ext = "image/png", ".png"
            elif img_bytes[:6] in (b'GIF87a', b'GIF89a'):
                content_type, ext = "image/gif", ".gif"
            elif img_bytes[:4] == b'RIFF' and img_bytes[8:12] == b'WEBP':
                content_type, ext = "image/webp", ".webp"
        else:
            # 回退：直接下载（微信CDN可能拦截）
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148"
                ),
                "Referer": "https://mp.weixin.qq.com/",
            }
            resp = requests.get(image_url, headers=headers, timeout=15)
            if resp.status_code != 200 or len(resp.content) == 0:
                print(f"  ⚠️  图片下载失败 HTTP {resp.status_code} ({image_url[:60]}…)")
                return None
            img_bytes = resp.content
            content_type = resp.headers.get("content-type", "image/jpeg")
            ext = _content_type_to_ext(content_type)

        # 上传到飞书图床
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
            f.write(img_bytes)
            tmp_path = f.name

        try:
            upload_resp = requests.post(
                f"{FEISHU_BASE}/drive/v1/medias/upload_all",
                headers={"Authorization": f"Bearer {user_token}"},
                data={
                    "file_name": f"img_{int(time.time())}{ext}",
                    "parent_type": "docx_image",
                    "parent_node": doc_id,
                    "size": str(len(img_bytes)),
                },
                files={"file": (f"image{ext}", open(tmp_path, "rb"), content_type)},
                timeout=30,
            )
            result = upload_resp.json()
            if result.get("code") == 0:
                return result["data"]["file_token"]
            print(f"  ⚠️  图片上传API返回错误 (code={result.get('code')}): {result.get('msg')}")
            return None
        finally:
            os.unlink(tmp_path)

    except Exception as e:
        print(f"  ⚠️  图片上传失败 ({image_url[:60]}…): {e}")
        return None


def create_document(
    title: str,
    markdown_text: str,
    image_url_map: dict[str, str],   # {原始URL: 飞书token}（已废弃，保留兼容）
    target: SaveTarget,
    user_token: str,
    image_urls: list[str] | None = None,   # 原始图片URL列表
    image_data: dict[str, str] | None = None,  # {url: base64} Playwright已下载的图片数据
) -> SaveResult:
    """
    在飞书指定位置创建文档，写入内容。
    执行顺序：1) 创建空文档拿到 doc_id → 2) 上传图片（传入 doc_id 作为 parent_node）→ 3) 写入内容块
    image_data: {url: base64字符串}，由Playwright在浏览器上下文中下载，可绕过微信防盗链
    """
    if target.type == "folder":
        doc_id, doc_url = _create_in_folder(title, target.token, user_token)
    elif target.type == "wiki":
        if target.token.isdigit():
            space_id = target.token
            node_token = target.node_token
        else:
            space_id = ""
            node_token = target.token
        doc_id, doc_url = _create_in_wiki(title, space_id, node_token, user_token)
    else:
        raise ValueError(f"不支持的存储类型：{target.type}")

    # 文档已创建，现在用 doc_id 作为 parent_node 上传图片
    if image_urls:
        total = len(image_urls)
        print(json.dumps({
            "status": "uploading_images",
            "message": f"正在上传 {total} 张图片到飞书图床…"
        }), flush=True)
        for idx, img_url in enumerate(image_urls, 1):
            b64 = (image_data or {}).get(img_url, "")
            token = upload_image(img_url, user_token, doc_id=doc_id, image_b64=b64)
            if token:
                image_url_map[img_url] = token
            print(json.dumps({
                "status": "image_progress",
                "current": idx,
                "total": total,
            }), flush=True)

    # 将 Markdown 转换为飞书文档块并写入
    blocks = _markdown_to_feishu_blocks(markdown_text, image_url_map)
    _write_blocks(doc_id, blocks, user_token)

    return SaveResult(document_url=doc_url, document_id=doc_id, title=title)


def list_folders(user_token: str, parent_token: str = "") -> list[dict]:
    """
    列出个人云空间中的文件夹
    返回格式：[{"name": "...", "token": "...", "type": "folder"}]
    """
    params = {"page_size": 50}
    if parent_token:
        params["folder_token"] = parent_token

    resp = _api_get("/drive/v1/files", params, user_token)
    items = resp.get("data", {}).get("files", [])
    return [
        {"name": item["name"], "token": item["token"], "type": item["type"]}
        for item in items
        if item["type"] == "folder"
    ]


def list_wikis(user_token: str) -> list[dict]:
    """
    列出用户有权限的知识库空间
    返回格式：[{"name": "...", "space_id": "..."}]
    """
    resp = _api_get("/wiki/v2/spaces", {"page_size": 50}, user_token)
    items = resp.get("data", {}).get("items", [])
    return [
        {"name": item["name"], "space_id": item["space_id"]}
        for item in items
    ]


def list_wiki_nodes(space_id: str, parent_node_token: str, user_token: str) -> list[dict]:
    """列出知识库中某节点下的子节点（文件夹类型）"""
    params = {
        "page_size": 50,
        "parent_node_token": parent_node_token,
    }
    resp = _api_get(f"/wiki/v2/spaces/{space_id}/nodes", params, user_token)
    items = resp.get("data", {}).get("items", [])
    return [
        {
            "title": item.get("title", ""),
            "node_token": item["node_token"],
            "has_child": item.get("has_child", False),
        }
        for item in items
        if item.get("obj_type") in ("doc", "docx", "folder", "wiki")
    ]


# ─── 文档创建内部函数 ─────────────────────────────────────────────────────────

def _create_in_folder(title: str, folder_token: str, user_token: str):
    """在个人云空间文件夹中创建文档"""
    resp = requests.post(
        f"{FEISHU_BASE}/docx/v1/documents",
        headers=_headers(user_token),
        json={
            "title": title,
            "folder_token": folder_token,
        },
        timeout=15,
    ).json()

    _check_response(resp, "创建文档")
    doc_id  = resp["data"]["document"]["document_id"]
    doc_url = f"https://feishu.cn/docx/{doc_id}"
    return doc_id, doc_url


def _get_space_id_from_node(node_token: str, user_token: str) -> str:
    """通过节点 token 查询所属知识库的 space_id"""
    resp = _api_get(f"/wiki/v2/spaces/get_node", {"token": node_token, "obj_type": "wiki"}, user_token)
    node = resp.get("data", {}).get("node", {})
    space_id = node.get("space_id", "")
    if not space_id:
        raise RuntimeError(f"无法从节点 {node_token} 获取 space_id，API 返回：{resp}")
    return space_id


def _create_in_wiki(title: str, space_id: str, parent_node_token: str, user_token: str):
    """在知识库中创建文档节点

    如果 space_id 为空但 parent_node_token 有值，则自动从节点查询 space_id。
    """
    # 自动解析 space_id
    if not space_id and parent_node_token:
        space_id = _get_space_id_from_node(parent_node_token, user_token)
    elif not space_id:
        raise RuntimeError("知识库保存需要提供 space_id 或 node_token")

    resp = requests.post(
        f"{FEISHU_BASE}/wiki/v2/spaces/{space_id}/nodes",
        headers=_headers(user_token),
        json={
            "obj_type": "docx",
            "node_type": "origin",
            "parent_node_token": parent_node_token,
            "title": title,
        },
        timeout=15,
    ).json()

    _check_response(resp, "在知识库创建文档")
    node      = resp["data"]["node"]
    doc_url   = node.get("obj_edit_url") or f"https://feishu.cn/wiki/{node['node_token']}"
    # 知识库文档的 document_id 需要再查一次
    doc_token = node.get("obj_token", "")
    return doc_token, doc_url


def _write_blocks(doc_id: str, blocks: list[dict], user_token: str):
    """批量写入文档块（每批最多50块，index始终为0追加到末尾）"""
    BATCH = 50
    for i in range(0, len(blocks), BATCH):
        chunk = blocks[i: i + BATCH]
        resp = requests.post(
            f"{FEISHU_BASE}/docx/v1/documents/{doc_id}/blocks/{doc_id}/children",
            headers=_headers(user_token),
            json={"children": chunk, "index": 0},
            timeout=30,
        ).json()
        _check_response(resp, f"写入文档块 batch {i//BATCH + 1}")


# ─── Markdown → 飞书块转换 ────────────────────────────────────────────────────

def _markdown_to_feishu_blocks(markdown: str, image_map: dict[str, str]) -> list[dict]:
    """
    将 Markdown 文本转换为飞书文档块列表
    支持：段落、标题(H1-H4)、图片、粗体、斜体、行内代码、代码块、分割线
    """
    blocks = []
    lines  = markdown.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i]

        # 代码块
        if line.startswith("```"):
            lang  = line[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            code_content = "\n".join(code_lines)
            # 代码块内容不能为空
            if code_content.strip():
                blocks.append(_code_block(code_content, lang))
            else:
                blocks.append(_paragraph_block(" "))
            i += 1
            continue

        # 分割线
        if re.match(r"^[-*_]{3,}$", line.strip()):
            blocks.append(_divider_block())
            i += 1
            continue

        # 标题
        heading_match = re.match(r"^(#{1,4})\s+(.+)", line)
        if heading_match:
            level = len(heading_match.group(1))
            text  = heading_match.group(2)
            # 标题内容不能含换行符，替换为空格
            text = text.replace("\n", " ").replace("\r", " ").strip()
            if text:
                blocks.append(_heading_block(text, level))
            i += 1
            continue

        # 图片
        img_match = re.match(r"^!\[.*?\]\((https?://[^\)]+)\)", line.strip())
        if img_match:
            url   = img_match.group(1)
            token = image_map.get(url)
            if token:
                blocks.append(_image_block(token))
            i += 1
            continue

        # 普通段落（含行内样式）
        if line.strip():
            blocks.append(_paragraph_block(line))
        else:
            # 空行 → 空段落（保留段落间距）
            blocks.append(_paragraph_block(""))

        i += 1

    return blocks


def _paragraph_block(text: str) -> dict:
    # 飞书 API 不接受空内容，用空格占位
    if not text.strip():
        text = " "
    return {
        "block_type": 2,
        "text": {"elements": _parse_inline(text)},
    }


def _heading_block(text: str, level: int) -> dict:
    block_type = {1: 3, 2: 4, 3: 5, 4: 6}.get(level, 4)
    key = f"heading{level}"
    return {
        "block_type": block_type,
        key: {"elements": _parse_inline(text)},
    }


def _image_block(file_token: str) -> dict:
    return {
        "block_type": 27,
        "image": {"file_token": file_token},
    }


def _code_block(code: str, language: str = "") -> dict:
    """将代码内容渲染为段落（飞书文档API代码块格式受限，改用行内代码段落代替）"""
    # 代码块改为带行内代码样式的段落，避免API格式问题
    return {
        "block_type": 2,
        "text": {
            "elements": [{"text_run": {"content": code, "text_element_style": {"inline_code": True}}}],
        },
    }


def _divider_block() -> dict:
    return {"block_type": 11, "divider": {}}


def _parse_inline(text: str) -> list[dict]:
    """解析行内样式：粗体、斜体、行内代码、链接、普通文本"""
    # 先将 Markdown 链接 [text](url) 替换为纯文本（保留显示文字）
    text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', text)
    # 去除图片标记 ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\([^\)]*\)', '', text)
    # 去除换行
    text = text.replace('\n', ' ').replace('\r', ' ').strip()

    if not text:
        return [_text_run(' ')]

    elements = []
    pos = 0
    for m in re.finditer(
        r'\*\*(.+?)\*\*|__(.+?)__|`(.+?)`|_(.+?)_', text
    ):
        # 普通文本（匹配前）
        if m.start() > pos:
            elements.append(_text_run(text[pos: m.start()]))

        raw = m.group(0)
        if raw.startswith("**") or raw.startswith("__"):
            inner = m.group(1) or m.group(2) or ""
            elements.append(_text_run(inner, bold=True))
        elif raw.startswith("`"):
            elements.append(_text_run(m.group(3) or "", inline_code=True))
        elif raw.startswith("_"):
            elements.append(_text_run(m.group(4) or "", italic=True))

        pos = m.end()

    # 剩余文本
    if pos < len(text):
        elements.append(_text_run(text[pos:]))

    return elements if elements else [_text_run(text)]


def _text_run(content: str, bold=False, italic=False, inline_code=False) -> dict:
    style = {}
    if bold:        style["bold"]        = True
    if italic:      style["italic"]      = True
    if inline_code: style["inline_code"] = True
    run = {"content": content}
    if style:
        run["text_element_style"] = style
    return {"text_run": run}


# ─── 工具函数 ────────────────────────────────────────────────────────────────

def _headers(user_token: str) -> dict:
    return {
        "Authorization": f"Bearer {user_token}",
        "Content-Type":  "application/json; charset=utf-8",
    }


def _api_get(path: str, params: dict, user_token: str) -> dict:
    resp = requests.get(
        f"{FEISHU_BASE}{path}",
        headers=_headers(user_token),
        params=params,
        timeout=15,
    )
    return resp.json()


def _check_response(resp: dict, action: str):
    if resp.get("code", -1) != 0:
        raise RuntimeError(f"{action} 失败：{resp.get('msg')} (code={resp.get('code')})")


def _content_type_to_ext(content_type: str) -> str:
    mapping = {
        "image/jpeg": ".jpg",
        "image/png":  ".png",
        "image/gif":  ".gif",
        "image/webp": ".webp",
    }
    for k, v in mapping.items():
        if k in content_type:
            return v
    return ".jpg"
