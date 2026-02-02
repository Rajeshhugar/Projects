import time
import schedule
from telegram_alert import send_news_alerts

# Run every 10 minutes
schedule.every(10).minutes.do(send_news_alerts)

print("Telegram News Alert System Started...")

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
