import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# def send_telegram_message(message):
#     url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
#     payload = {
#         "chat_id": TELEGRAM_CHAT_ID,
#         "text": message,
#         "parse_mode": "Markdown"
#     }
#     response = requests.post(url, json=payload)
#     print(response.text)
#     return response.json()


def send_telegram_message(text, chat_id=TELEGRAM_CHAT_ID, max_retries=3, delay=2):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}

    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                return response.json()  # Success
            elif response.status_code == 503:
                print(f"503 Error: Service Unavailable. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"Request failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            time.sleep(delay)

    print("Failed to send message after multiple attempts.")
    return None  # Return None if all retries fail




# def send_news_alerts(articles):
#     """Fetch news and send each article as a Telegram message."""
    
#     # print(articles)

#     if not articles:
#         send_telegram_message("No new articles found for Aramco.")
#         return
    
#     for i in articles:  
        
        
#         message = i
#         send_telegram_message(message)
