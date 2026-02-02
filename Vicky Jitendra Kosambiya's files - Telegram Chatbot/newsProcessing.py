import os
from dotenv import load_dotenv
from pymongo import MongoClient
from newsFetch import fetch_news
from translation import *
import datetime
from datetime import datetime
from preprocessing_and_sentiment_analysis import *

# Load env vars
load_dotenv()

# Connect to MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["News"]
processed_news_col = db["processed_news"]

def process_and_store_articles():
    news = fetch_news()
    if not news or "results" not in news:
        print("No news fetched.")
        return

    for article in news["results"]:
        title = article.get("title") or ''
        description = article.get("description") or ''

        translated_title = translate_text(title)
        translated_desc = translate_text(description)
        translated_combined = translate_text(f"{title} {description}")

        # Run RAG processing
        rag_output = process_rag(translated_combined, article.get("link", ""), translated_title)

        # Build the processed article object
        processed_article = {
            **article,
            "Translated Title": translated_title,
            "Translated Description": translated_desc,
            "Translated_Text_Code": translated_combined,
            "RAG_Output": rag_output,  # ✅ <--- Added here
            "message_sent_status": False,
            "processed_at": datetime.utcnow()
        }

        # Avoid duplicates (check by link)
        if not processed_news_col.find_one({"link": article["link"]}):
            processed_news_col.insert_one(processed_article)
            print(f"✅ Stored with RAG output: {translated_title}")


if __name__ == "__main__":
    process_and_store_articles()
