
import sys
import re
import json
from playwright.sync_api import sync_playwright

def discover_wechat_info(url):
    """使用 Playwright 浏览器精确提取公众号信息"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            html = page.content()
            
            # 1. 提取 __biz
            biz_match = re.search(r'__biz\s*=\s*"([^"]+)"', html)
            biz = biz_match.group(1) if biz_match else None
            
            # 2. 提取 nickname (公众号名)
            nickname_match = re.search(r'nickname\s*:\s*"([^"]+)"', html)
            nickname = nickname_match.group(1) if nickname_match else None
            
            # 3. 如果通过正则没抓到，尝试通过选择器抓取页面上的 nickname
            if not nickname:
                try:
                    nickname = page.inner_text("#profileBt .profile_nickname")
                except: pass
            
            browser.close()
            return biz, nickname
        except Exception as e:
            browser.close()
            return None, str(e)

def generate_rsshub_url(biz):
    """基于 biz 生成准确的订阅源"""
    if biz:
        return f"https://rsshub.app/wechat/msghistory/{biz}"
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "Missing URL"}))
        sys.exit(1)
    
    target_url = sys.argv[1]
    biz, nickname = discover_wechat_info(target_url)
    rss_url = generate_rsshub_url(biz)
    
    if biz and nickname:
        print(json.dumps({
            "status": "success",
            "biz": biz,
            "nickname": nickname,
            "rss_url": rss_url,
            "message": f"成功识别: {nickname} (ID: {biz})"
        }, ensure_ascii=False))
    else:
        print(json.dumps({"status": "error", "message": f"核准失败: {nickname or '无法识别该公众号'}"}))
