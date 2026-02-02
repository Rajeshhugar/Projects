# from newsFetch import fetch_news
# from telegram_alert import *
# # from translation import *
# # from preprocessing_and_sentiment_analysis import *
# from newsProcessing import *
# import os
# from dotenv import load_dotenv
# from pymongo import MongoClient


# def text_formatting(alert_data):
#     level_colors = {
#         "High": "🔴",
#         "Medium": "🟠",
#         "Low": "🟢"
#     }    
#     alert = alert_data.get("Alert Analysis", {})
#     level = alert.get("Alert Level", "Low")  # Default to Low if not provided
#     color = level_colors.get(level, "🟢")  # Default to green
    
#     formatted_text = f"""
#                 Aramco Alert 

# URL: {alert.get("URL", "N/A")}
# Level: {level} {color}
# Title: {alert.get("Title", "No title available.")}
# Summary: {alert.get("Summary", "No summary available.")}
# Action: {alert.get("Classification Details", {}).get("Required Action", "No action specified.")}"""
    
#     return formatted_text.strip()


# process_and_store_articles()

# mongo_uri = os.getenv("MONGO_URI")
# client = MongoClient(mongo_uri)
# db = client["News"]
# processed_news = db["processed_news"]

# not_sent_news = processed_news.find({"message_sent_status": False})

# for article in not_sent_news:
#     alert_data = article.get("RAG_Output", {})
#     if not alert_data:
#         print("No alert data found.")
#         continue
    
#     formatted_text = text_formatting(alert_data)
#     send_telegram_message(formatted_text)
    
#     # Update the message sent status
#     processed_news.update_one({"_id": article["_id"]}, {"$set": {"message_sent_status": True}})
# #     print(f"Message sent for article: {article['Translated Title']}")



import time
from newsFetch import fetch_news
from telegram_alert import send_telegram_message
from newsProcessing import process_and_store_articles
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

def text_formatting(alert_data):
    print(alert_data)
    level_colors = {
        "High": "🔴",
        "Medium": "🟠",
        "Low": "🟢"
    }
    alert = alert_data.get("Alert Analysis", {})
    level = alert.get("Alert Level", "Low")
    color = level_colors.get(level, "🟢")
    
    formatted_text = f"""
                Aramco Alert 

URL: {alert.get("URL", "N/A")}
Level: {level} {color}
Title: {alert.get("Title", "No title available.")}
Summary: {alert.get("Summary", "No summary available.")}
Action: {alert.get("Classification Details", {}).get("Required Action", "No action specified.")}"""
    
    return formatted_text.strip()

# MongoDB setup
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["News"]
processed_news = db["processed_news"]

# 🔁 Continuous execution every 60 seconds
# while True:
print("🔄 Running scheduled process...")

    # Step 1: Fetch & process new articles
process_and_store_articles()

    # Step 2: Send unsent Telegram alerts
not_sent_news = processed_news.find({"message_sent_status": False})

for article in not_sent_news:
        alert_data = article.get("RAG_Output", {})
        if not alert_data:
            print("⚠️ No alert data found.")
            continue
        
        formatted_text = text_formatting(alert_data)
        send_telegram_message(formatted_text)

        # Mark as sent
        processed_news.update_one(
            {"_id": article["_id"]},
            {"$set": {"message_sent_status": True}}
        )
        print(f"✅ Message sent for article: {article.get('Translated Title', 'N/A')}")
 
    # print("⏳ Sleeping for 600 seconds...\n")
    # time.sleep(600)
