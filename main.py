"""
main.py — 主入口
两种调用模式：

  模式1 - 只抓取处理（不写飞书，供 OpenClaw 先展示预览）：
    python main.py scrape <url>
    输出 JSON，OpenClaw 展示给用户，用户确认存储目标后再调用 save

  模式2 - 保存到飞书（用户确认目标后调用）：
    python main.py save --dest-type folder --dest-token <folder_token>
    python main.py save --dest-type wiki --dest-token <space_id> --node-token <node_token>

  模式3 - 列出可用的存储目标（供 OpenClaw 展示给用户选择）：
    python main.py list-folders
    python main.py list-wikis
    python main.py list-wiki-nodes --space-id <id> --parent-token <token>

  模式4 - 飞书授权：
    python main.py auth

所有输出均为 JSON，便于 OpenClaw 解析。
"""

import sys
import json
import argparse
import tempfile
import os
from pathlib import Path

# 临时文件路径（scrape 和 save 之间共享处理结果）
TEMP_DIR      = Path(tempfile.gettempdir()) / "wechat2feishu"
TEMP_ARTICLE  = TEMP_DIR / "last_article.json"


def cmd_scrape(url: str):
    """
    阶段1：抓取 + 处理，结果存本地临时文件
    输出供 OpenClaw 展示的预览 JSON
    """
    from scraper import scrape
    from processor import process

    print(json.dumps({"status": "processing", "message": "正在抓取文章，请稍候…"}),
          flush=True)

    try:
        raw     = scrape(url)
        article = process(raw)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)

    # 持久化处理结果（供 save 阶段使用）
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    cache = {
        "url":         article.url,
        "title":       article.title,
        "author":      article.author,
        "publish_time": article.publish_time,
        "markdown":    article.markdown,
        "image_urls":  article.image_urls,
        "image_data":  raw.image_data,   # {url: base64} 在浏览器上下文中已下载
        "word_count":  article.word_count,
        "summary":     article.summary,
    }
    TEMP_ARTICLE.write_text(json.dumps(cache, ensure_ascii=False, indent=2))

    # 返回供 OpenClaw 展示的预览
    print(json.dumps({
        "status":       "ready",
        "title":        article.title,
        "author":       article.author,
        "publish_time": article.publish_time,
        "word_count":   article.word_count,
        "image_count":  len(article.image_urls),
        "summary":      article.summary,
        "message":      "文章处理完毕，请告知存储目标。",
    }, ensure_ascii=False))


def cmd_save(dest_type: str, dest_token: str, node_token: str = ""):
    """
    阶段2：上传图片 + 创建飞书文档
    读取 scrape 阶段缓存的文章数据
    """
    from auth import get_valid_token
    from feishu import (
        create_document, SaveTarget
    )

    # 读取缓存
    if not TEMP_ARTICLE.exists():
        print(json.dumps({
            "status": "error",
            "message": "未找到待保存的文章，请先运行 scrape 命令。"
        }))
        sys.exit(1)

    cache = json.loads(TEMP_ARTICLE.read_text())

    try:
        user_token = get_valid_token()
    except RuntimeError as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)

    # 1. 创建飞书文档（图片上传在 create_document 内部完成，需要 doc_id 作为 parent_node）
    target = SaveTarget(
        type=dest_type,
        token=dest_token,
        node_token=node_token,
        display_name="",
    )

    print(json.dumps({"status": "creating_doc", "message": "正在创建飞书文档…"}),
          flush=True)

    try:
        result = create_document(
            title=cache["title"],
            markdown_text=cache["markdown"],
            image_url_map={},
            image_urls=cache.get("image_urls", []),
            image_data=cache.get("image_data", {}),
            target=target,
            user_token=user_token,
        )
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)

    # 清理临时文件
    TEMP_ARTICLE.unlink(missing_ok=True)

    print(json.dumps({
        "status":       "success",
        "title":        result.title,
        "document_url": result.document_url,
        "document_id":  result.document_id,
        "message":      f"✅ 转存成功！",
    }, ensure_ascii=False))


def cmd_list_folders():
    """列出个人云空间文件夹，供用户选择存储目标"""
    from auth import get_valid_token
    from feishu import list_folders

    try:
        user_token = get_valid_token()
        folders    = list_folders(user_token)
        print(json.dumps({
            "status": "success",
            "type":   "folders",
            "items":  folders,
        }, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


def cmd_list_wikis():
    """列出知识库空间，供用户选择存储目标"""
    from auth import get_valid_token
    from feishu import list_wikis

    try:
        user_token = get_valid_token()
        wikis      = list_wikis(user_token)
        print(json.dumps({
            "status": "success",
            "type":   "wikis",
            "items":  wikis,
        }, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


def cmd_list_wiki_nodes(space_id: str, parent_token: str):
    """列出知识库节点（二级目录），供用户选择"""
    from auth import get_valid_token
    from feishu import list_wiki_nodes

    try:
        user_token = get_valid_token()
        nodes      = list_wiki_nodes(space_id, parent_token, user_token)
        print(json.dumps({
            "status": "success",
            "type":   "wiki_nodes",
            "items":  nodes,
        }, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


def cmd_auth():
    """发起飞书 OAuth 授权"""
    from auth import login
    login()


# ─── CLI 解析 ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="微信公众号 → 飞书文档转存工具"
    )
    sub = parser.add_subparsers(dest="command")

    # scrape
    p_scrape = sub.add_parser("scrape", help="抓取并处理文章")
    p_scrape.add_argument("url", help="公众号文章链接")

    # save
    p_save = sub.add_parser("save", help="保存文章到飞书")
    p_save.add_argument("--dest-type",  required=True, choices=["folder", "wiki"],
                        help="存储类型：folder（个人空间）或 wiki（知识库）")
    p_save.add_argument("--dest-token", required=True,
                        help="folder_token 或知识库 space_id")
    p_save.add_argument("--node-token", default="",
                        help="知识库父节点 token（仅 wiki 类型需要）")

    # list-folders
    sub.add_parser("list-folders", help="列出个人云空间文件夹")

    # list-wikis
    sub.add_parser("list-wikis", help="列出知识库")

    # list-wiki-nodes
    p_nodes = sub.add_parser("list-wiki-nodes", help="列出知识库节点")
    p_nodes.add_argument("--space-id",     required=True)
    p_nodes.add_argument("--parent-token", required=True)

    # auth
    sub.add_parser("auth", help="飞书 OAuth 授权")

    args = parser.parse_args()

    if args.command == "scrape":
        cmd_scrape(args.url)
    elif args.command == "save":
        cmd_save(args.dest_type, args.dest_token, args.node_token)
    elif args.command == "list-folders":
        cmd_list_folders()
    elif args.command == "list-wikis":
        cmd_list_wikis()
    elif args.command == "list-wiki-nodes":
        cmd_list_wiki_nodes(args.space_id, args.parent_token)
    elif args.command == "auth":
        cmd_auth()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
