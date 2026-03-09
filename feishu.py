
import json
import os
import re
import time
import requests
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

FEISHU_BASE = "https://open.feishu.cn/open-apis"

@dataclass
class SaveTarget:
    type: str           # "folder" or "wiki"
    token: str          # folder_token or space_id
    node_token: str     # wiki node token
    display_name: str

@dataclass
class SaveResult:
    document_url: str
    document_id: str
    title: str

def _headers(user_token: str) -> dict:
    return {"Authorization": f"Bearer {user_token}", "Content-Type": "application/json; charset=utf-8"}

def _api_get(path: str, params: dict, user_token: str) -> dict:
    resp = requests.get(f"{FEISHU_BASE}{path}", headers=_headers(user_token), params=params, timeout=15)
    return resp.json()

def _check_response(resp: dict, action: str):
    if resp.get("code", -1) != 0:
        raise RuntimeError(f"{action} 失败：{resp.get('msg')} (code={resp.get('code')})")

def _get_root_folder(user_token: str) -> str:
    resp = _api_get("/drive/explorer/v2/root_folder/meta", {}, user_token)
    _check_response(resp, "获取云空间根目录")
    return resp["data"]["token"]

def create_document(
    title: str,
    markdown_text: str,
    image_url_map: dict[str, str],
    target: SaveTarget,
    user_token: str,
    image_urls: list[str] | None = None,
    image_data: dict[str, str] | None = None,
) -> SaveResult:
    """
    1. 统一导入到用户根目录 (mount_type=1)
    2. 如果是 Wiki，导入后将文档挂载/移动到 Wiki
    3. PATCH blocks 注入高保真图片
    """
    root_token = _get_root_folder(user_token)

    # 1. 第一阶段：上传占位图片获取临时 Token
    if image_urls:
        import base64 as _base64
        for idx, img_url in enumerate(image_urls, 1):
            base_img_url = img_url.split("?")[0]
            placeholder_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
            placeholder_bytes = _base64.b64decode(placeholder_b64)
            files = {"file": (f"tmp_{idx}.png", placeholder_bytes, "image/png")}
            data = {"file_name": f"tmp_{idx}.png", "parent_type": "explorer", "parent_node": root_token, "size": str(len(placeholder_bytes))}
            up_resp = requests.post(f"{FEISHU_BASE}/drive/v1/files/upload_all", headers={"Authorization": f"Bearer {user_token}"}, data=data, files=files, timeout=30).json()
            if up_resp.get("code") == 0:
                file_token = up_resp["data"]["file_token"]
                image_url_map[img_url] = file_token
                markdown_text = re.sub(re.escape(base_img_url) + r"[^\s\)]*", file_token, markdown_text)

    # 2. 上传 MD 文件
    md_bytes = markdown_text.encode('utf-8')
    safe_name = re.sub(r'[\\/:*?"<>|]', '_', title)
    files_md = {"file": (f"{safe_name}.md", md_bytes, "text/markdown")}
    data_md = {"file_name": f"{safe_name}.md", "parent_type": "explorer", "parent_node": root_token, "size": str(len(md_bytes))}
    md_resp = requests.post(f"{FEISHU_BASE}/drive/v1/files/upload_all", headers={"Authorization": f"Bearer {user_token}"}, data=data_md, files=files_md, timeout=30).json()
    _check_response(md_resp, "上传临时文本")
    md_token = md_resp["data"]["file_token"]

    # 3. 创建导入任务 (始终使用 mount_type=1)
    mount_key = target.token if target.type == "folder" else root_token
    import_payload = {
        "file_extension": "md",
        "file_token": md_token,
        "type": "docx",
        "title": title,
        "point": {
            "mount_type": 1,
            "mount_key": mount_key
        }
    }
    task_resp = requests.post(f"{FEISHU_BASE}/drive/v1/import_tasks", headers=_headers(user_token), json=import_payload).json()
    _check_response(task_resp, "创建转换任务")
    ticket = task_resp["data"]["ticket"]

    # 4. 轮询结果
    doc_token = ""
    doc_url = ""
    for _ in range(30):
        time.sleep(2)
        res = requests.get(f"{FEISHU_BASE}/drive/v1/import_tasks/{ticket}", headers=_headers(user_token)).json()
        status = res.get("data", {}).get("result", {}).get("job_status")
        if status == 0:
            doc_token = res["data"]["result"]["token"]
            doc_url = res["data"]["result"]["url"]
            break
        elif status in (3, 4, 10, 11):
            raise RuntimeError(f"导入失败: {res.get('data', {}).get('result', {}).get('job_error_msg')}")

    if not doc_token: raise RuntimeError("导入超时")

    # 5. 如果是 Wiki，将生成的文档挂载/移动至知识库
    if target.type == "wiki":
        time.sleep(2)
        space_id = target.token if target.token.isdigit() else ""
        parent_node_token = target.node_token or target.token
        if not space_id:
            node_resp = _api_get(f"/wiki/v2/spaces/get_node", {"token": parent_node_token, "obj_type": "wiki"}, user_token)
            space_id = node_resp.get("data", {}).get("node", {}).get("space_id", "")
            
        wiki_payload = {
            "obj_type": "docx",
            "obj_token": doc_token,
            "parent_node_token": parent_node_token
        }
        wiki_resp = requests.post(
            f"{FEISHU_BASE}/wiki/v2/spaces/{space_id}/nodes/move_docs_to_wiki", 
            headers=_headers(user_token), 
            json=wiki_payload, 
            timeout=15
        ).json()
        _check_response(wiki_resp, "移动文档至知识库")
        wiki_token = wiki_resp.get("data", {}).get("wiki_token") or ""
        doc_url = f"https://feishu.cn/wiki/{wiki_token}"

    # 6. 修补图片
    if image_urls:
        print(json.dumps({"status": "uploading_images", "message": "正在注入高保真图片..."}), flush=True)
        blocks_resp = requests.get(f"{FEISHU_BASE}/docx/v1/documents/{doc_token}/blocks?page_size=500", headers=_headers(user_token)).json()
        blocks = blocks_resp.get("data", {}).get("items", [])
        image_blocks = [b for b in blocks if b["block_type"] == 27]
        
        patched_count = 0
        for i in range(min(len(image_blocks), len(image_urls))):
            block, img_url = image_blocks[i], image_urls[i]
            block_id = block["block_id"]
            try:
                base_img_url = img_url.split("?")[0]
                b64 = ""
                for loaded_url, data in (image_data or {}).items():
                    if loaded_url.split("?")[0] == base_img_url: b64 = data; break
                
                import base64 as _base64
                if b64:
                    img_bytes = _base64.b64decode(b64)
                    if img_bytes[:4] == b'\x89PNG': ext, mime = ".png", "image/png"
                    elif img_bytes[:6] in (b'GIF87a', b'GIF89a'): ext, mime = ".gif", "image/gif"
                    elif b'WEBP' in img_bytes[:16]: ext, mime = ".webp", "image/webp"
                    else: ext, mime = ".jpg", "image/jpeg"
                else:
                    resp = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
                    if resp.status_code != 200: continue
                    img_bytes = resp.content
                    mime = resp.headers.get("content-type", "image/jpeg")
                    ext = ".jpg" if "jpeg" in mime else ".png"

                if len(img_bytes) < 100: continue
                img_w, img_h = 800, 600
                try:
                    from PIL import Image
                    import io
                    with Image.open(io.BytesIO(img_bytes)) as im: img_w, img_h = im.size
                except: pass

                up_data = {"file_name": f"img_{block_id}{ext}", "parent_type": "docx_image", "parent_node": block_id, "size": str(len(img_bytes)), "extra": json.dumps({"drive_route_token": doc_token})}
                up_res = requests.post(f"{FEISHU_BASE}/drive/v1/medias/upload_all", headers={"Authorization": f"Bearer {user_token}"}, data=up_data, files={"file": (f"img_{block_id}{ext}", img_bytes, mime)}, timeout=30).json()

                if up_res.get("code") == 0:
                    new_token = up_res["data"]["file_token"]
                    requests.patch(f"{FEISHU_BASE}/docx/v1/documents/{doc_token}/blocks/{block_id}", headers=_headers(user_token), 
                                   json={"replace_image": {"token": new_token, "width": img_w, "height": img_h}}, timeout=15)
                    patched_count += 1
                    print(json.dumps({"status": "image_progress", "current": patched_count, "total": len(image_urls)}), flush=True)
            except Exception: pass

    return SaveResult(document_url=doc_url, document_id=doc_token, title=title)

def list_folders(user_token: str, parent_token: str = "") -> list[dict]:
    params = {"page_size": 50}
    if parent_token: params["folder_token"] = parent_token
    resp = _api_get("/drive/v1/files", params, user_token)
    files = resp.get("data", {}).get("files", [])
    return [{"name": i["name"], "token": i["token"], "type": i["type"]} for i in files if i["type"] == "folder"]

def list_wikis(user_token: str) -> list[dict]:
    resp = _api_get("/wiki/v2/spaces", {"page_size": 50}, user_token)
    return [{"name": i["name"], "space_id": i["space_id"]} for i in resp.get("data", {}).get("items", [])]

def list_wiki_nodes(space_id: str, parent_node_token: str, user_token: str) -> list[dict]:
    params = {"page_size": 50, "parent_node_token": parent_node_token}
    resp = _api_get(f"/wiki/v2/spaces/{space_id}/nodes", params, user_token)
    items = resp.get("data", {}).get("items", [])
    return [{"title": i.get("title", ""), "node_token": i["node_token"], "has_child": i.get("has_child", False)} for i in items if i.get("obj_type") in ("doc", "docx", "folder", "wiki")]
