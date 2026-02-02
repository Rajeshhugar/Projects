# File: /media-analysis-app/media-analysis-app/src/core/config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration settings
class Config:
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    STREAMLIT_PAGE_TITLE = "Media Analysis App"
    STREAMLIT_PAGE_ICON = "📊"
    STREAMLIT_LAYOUT = "centered"
    DEFAULT_LANGUAGE = "en"
    AUDIO_FORMAT = "mp3"
    VIDEO_FORMAT = "mp4"
    MAX_TEXT_LENGTH = 5000
    ERROR_MESSAGES = {
        "video_download": "Error downloading the video. Please check the URL.",
        "audio_conversion": "Error converting video to audio.",
        "transcription": "Error transcribing audio.",
        "translation": "Error translating text.",
        "news_fetch": "Error fetching news article."
    }