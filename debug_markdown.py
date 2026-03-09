
import asyncio
from scraper import fetch_article
from processor import process

async def main():
    raw = await fetch_article("https://mp.weixin.qq.com/s/qNJRqekm6I6Y5KrawcmsmQ")
    processed = process(raw)
    with open("output.md", "w", encoding="utf-8") as f:
        f.write(processed.markdown)

if __name__ == "__main__":
    asyncio.run(main())
