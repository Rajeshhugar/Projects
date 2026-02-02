import asyncio
from crawl4ai import *

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.channelnewsasia.com/business/ai-chip-startup-groq-secures-15-billion-commitment-saudi-arabia-4928996",
        )
        print(result)
        with open("news_output_3.txt", "w", encoding="utf-8") as file:
            file.write(result.markdown)

    print("✅ Extracted news saved to 'news_output_3.txt'")


if __name__ == "__main__":
    asyncio.run(main())