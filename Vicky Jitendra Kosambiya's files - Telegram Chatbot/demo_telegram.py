import os
import requests
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set Telegram credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "your_bot_token_here"
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or "-1001234567890"  # Must start with -100 for channels

def escape_markdown(text):
    """Escape special characters for Telegram MarkdownV2."""
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

def send_telegram_message(message):
    """Send a properly formatted message to Telegram channel."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    escaped_message = escape_markdown(message)  # Escape MarkdownV2 special characters

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": escaped_message,
        "parse_mode": "MarkdownV2"
    }

    response = requests.post(url, json=payload)
    print(response.status_code, response.json())  # Debugging output
    return response.json()

# Test message
send_telegram_message("🚀 *Hello, Telegram!* This is a test message with MarkdownV2 formatting!")
