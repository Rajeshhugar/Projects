# import os
# from datetime import datetime
# from newsdataapi import NewsDataApiClient
# from dotenv import load_dotenv
# from pymongo import MongoClient

# # Load environment variables
# load_dotenv()

# # Connect to MongoDB
# mongo_uri = os.getenv("MONGO_URI")
# client = MongoClient(mongo_uri)
# db = client["News"]
# raw_news_col = db["raw_news"]

# # Fetch news and store in MongoDB
# def fetch_news(query="aramco"):
#     api_key = os.getenv("NEWSIO_API")
#     if not api_key:
#         raise ValueError("API key not found. Check your .env file.")

#     api = NewsDataApiClient(apikey=api_key)
#     response = api.news_api(q=query)

#     if "results" not in response or not response["results"]:
#         print("No news articles found.")
#         return

#     for article in response["results"]:
#         # Optional: add fetched_at timestamp
#         article["fetched_at"] = datetime.utcnow()

#         # Optional: prevent duplicates (e.g., by URL)
#         if not raw_news_col.find_one({"link": article["link"]}):
#             raw_news_col.insert_one(article)

#     print(f"✅ Inserted {len(response['results'])} articles into raw_news.")
#     return response  # Return the response for reference

# if __name__ == "__main__":
#     fetch_news()



import os
from datetime import datetime
from newsdataapi import NewsDataApiClient
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# Connect to MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["News"]
raw_news_col = db["raw_news"]

def fetch_news(query="aramco"):
    api_key = os.getenv("NEWSIO_API")
    if not api_key:
        raise ValueError("API key not found. Check your .env file.")

    api = NewsDataApiClient(apikey=api_key)

    # Find the most recent article in the DB
    last_article = raw_news_col.find_one(
        {"pubDate": {"$exists": True}}, 
        sort=[("pubDate", -1)]
    )
    last_pub_date = last_article["pubDate"] if last_article else None

    # Fetch new articles
    response = api.news_api(q=query)

    if "results" not in response or not response["results"]:
        print("No news articles found.")
        return

    new_articles = 0
    for article in response["results"]:
        # Parse article pubDate to datetime
        try:
            article_time = datetime.strptime(article["pubDate"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue  # Skip if date format is wrong

        # Skip if it's older or same as last pubDate
        if last_pub_date and article_time <= datetime.strptime(last_pub_date, "%Y-%m-%d %H:%M:%S"):
            continue

        # Add fetched_at timestamp
        article["fetched_at"] = datetime.utcnow()

        # Avoid duplicates by URL
        if not raw_news_col.find_one({"link": article["link"]}):
            raw_news_col.insert_one(article)
            new_articles += 1

    print(f"✅ Inserted {new_articles} new articles into raw_news.")
    return response

if __name__ == "__main__":
    fetch_news()

