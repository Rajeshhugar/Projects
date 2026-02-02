import streamlit as st
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.video_downloader import VideoDownloader
from utils.audio_converter import Audio_Prcessor
from services.news_service import NewsService


def main():
    # Streamlit configuration
    st.set_page_config(page_title="Media Analysis App", page_icon="📊", layout="wide")
    st.title("Media Analysis App")

    # Sidebar input options
    st.sidebar.header("Input Options")
    input_source = st.sidebar.radio("Choose Input Source", ["Video File", "Video URL", "News Article URL"])

    audio_path = None  # Initialize audio_path variable for later use

    # Handle Video File Input
    if input_source == "Video File":
        uploaded_file = st.file_uploader("Upload Video", type=["mp4", "avi", "mov"])
        if uploaded_file is not None:
            video_service = VideoDownloader()
            video_path = video_service.download(uploaded_file)
            audio_service = Audio_Prcessor()
            audio_output = audio_service.audio_processor(video_path)
            st.json(audio_output)
            # st.success("Video uploaded and converted to audio!")

    # Handle Video URL Input
    elif input_source == "Video URL":
        video_url = st.text_input("Enter Video URL")
        if st.button("Download Video"):
            if video_url:
                video_url_str = str(video_url)
                video_service = VideoDownloader()
                video_path = video_service.download(video_url_str)
                audio_service = Audio_Prcessor()
                audio_output = audio_service.audio_processor(video_path=video_path)
                st.json(audio_output)
                # st.success("Video uploaded and converted to audio!")
                st.success("Video downloaded and converted to audio!")
            else:
                st.error("Please enter a valid Video URL.")

    # Handle News Article URL Input
    elif input_source == "News Article URL":
        news_url = st.text_input("Enter News Article URL")
        if st.button("Fetch News"):
            if news_url:
                news_service = NewsService()
                article_data = news_service.fetch_article(news_url)
                # st.write(article_data)
                st.json(article_data)
            else:
                st.error("Please enter a valid News Article URL.")

    # Transcription and Translation Section
    # st.markdown("---")
    # st.subheader("Transcription and Translation")
    # if audio_path:
    #     transcription_service = TranscriptionService()
    #     transcribed_text = transcription_service.transcribe_audio(audio_path)
    #     st.text_area("Transcribed Text", transcribed_text, height=300)

    #     # translation_service = TranslationService()
    #     translated_text = translate_article_data(transcribed_text)
    #     st.text_area("Translated Text", translated_text, height=300)
    # else:
    #     st.info("Upload or process a video to enable transcription and translation.")
        

if __name__ == "__main__":
    main()
