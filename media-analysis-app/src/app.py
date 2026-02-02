import streamlit as st
import sys
from pathlib import Path
from services.video_service import VideoService
from services.audio_service import AudioService
from services.news_service import NewsService
from services.transcription_service import TranscriptionService
from services.translation_service import TranslationService


# Add src to Python path

# sys.path.append('../src')

def main():
    st.set_page_config(page_title="Media Analysis App", page_icon="📊", layout="wide")
    st.title("Media Analysis App")

    st.sidebar.header("Input Options")
    input_source = st.sidebar.radio("Choose Input Source", ["Video File", "Video URL", "News Article URL"])

    if input_source == "Video File":
        uploaded_file = st.file_uploader("Upload Video", type=["mp4", "avi", "mov"])
        if uploaded_file:
            video_service = VideoService()
            video_path = video_service.save_video(uploaded_file)
            audio_service = AudioService()
          # not needed 2 seperate services for video and audio translation of video to audio is already done in video servicea function in video service
            audio_path = audio_service.convert_video_to_audio(uploaded_file)
            st.success("Video uploaded and converted to audio!")

    elif input_source == "Video URL":
        video_url = st.text_input("Enter Video URL")
        if st.button("Download Video"):
            video_service = VideoService()
            video_path = video_service.download_video(video_url)
            audio_path = video_service.convert_video_to_audio(video_path)
            audio_service = AudioService()
            audio_path = audio_service.convert_video_to_audio(video_path)
            st.success("Video downloaded and converted to audio!")

    elif input_source == "News Article URL":
        news_url = st.text_input("Enter News Article URL")
        if st.button("Fetch News"):
            news_service = NewsService()
            article_data = news_service.fetch_article(news_url)
            st.write(article_data)

    st.markdown("---")
    st.subheader("Transcription and Translation")
    if 'audio_path' in locals():
        transcription_service = TranscriptionService()
        transcribed_text = transcription_service.transcribe_audio(audio_path)
        st.text_area("Transcribed Text", transcribed_text, height=300)

        translation_service = TranslationService()
        translated_text = translation_service.translate_text(transcribed_text)
        st.text_area("Translated Text", translated_text, height=300)

if __name__ == "__main__":
    main()