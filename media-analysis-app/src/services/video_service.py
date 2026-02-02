import streamlit as st
import os
import json
import tempfile
import pandas as pd
from dotenv import load_dotenv
from utils.audio_converter import AudioConverter
from utils.transcriber import Transcriber
import logging
import traceback
from io import StringIO
import urllib.parse
import requests
import concurrent.futures
import math
from pydub import AudioSegment
from deep_translator import GoogleTranslator
from langdetect import detect
from utils.video_downloader import VideoDownloader
from utils.aramco_alert import AramcoMediaAlertRAG,MediaAlertAnalysis,clasification_level


class Translator:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s: %(message)s',
            filename='translation.log'
        )
        self.logger = logging.getLogger(__name__)

    def split_text_into_chunks(self, text, max_length=500):
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 > max_length:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0
            current_chunk.append(word)
            current_length += len(word) + 1

        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks

    def translate_text(self, text, target_lang='en'):
        try:
            if not text:
                self.logger.warning("Empty text provided for translation")
                return "No text to translate"

            chunks = self.split_text_into_chunks(text)
            translator = GoogleTranslator(target=target_lang)
            translated_chunks = [translator.translate(chunk) for chunk in chunks]
            translated_text = " ".join(translated_chunks)

            self.logger.info(f"Successfully translated to {target_lang}")
            return translated_text
        except Exception as e:
            error_msg = f"Translation error: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            return f"Translation failed: {error_msg}"


class VideoTranslationApp:
    def __init__(self):
        load_dotenv()
        self.GROQ_API_KEY = os.getenv('GROQ_API_KEY')
        self.video_downloader = VideoDownloader()
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s',
            filename='video_translation.log'
        )
        self.logger = logging.getLogger(__name__)
        # Initialize classification first
        self.classification = clasification_level()
        # Get the classification data
        self.data = self.classification.classification_data
        # Initialize RAG system with the data
        self.rag_system = AramcoMediaAlertRAG(self.data)

        st.set_page_config(
            page_title="Video Translation AI",
            layout="wide",
            page_icon="🎬"
        )


        
    def get_download_button(self, text, filename, button_text):
        """Create a download button for text content"""
        text_bytes = text.encode()
        return st.download_button(
            label=button_text,
            data=text_bytes,
            file_name=filename,
            mime='text/plain'
        )

    def video_to_audio(self, video_path):
        """Convert a video file to an audio file."""
        try:
            audio = AudioSegment.from_file(video_path)
            audio_path = video_path.replace(".mp4", ".mp3")
            audio.export(audio_path, format="mp3")
            return audio_path
        except Exception as e:
            st.error(f"Failed to convert video to audio: {str(e)}")
            self.logger.error(f"Video to audio conversion error: {str(e)}")
            raise e

    def transcribe_audio(self, audio_path):
        """Transcribe the audio file to text by chunking into 5MB segments."""
        try:
            st.info("Chunking audio into 5MB segments and transcribing...")
            audio = AudioSegment.from_file(audio_path)
            total_length = len(audio)
            
            # Calculate chunk size based on 5MB limit
            # We'll estimate chunk duration based on typical audio file sizes
            # Assuming ~1 MB per minute of audio at standard quality
            chunk_duration = 10 * 60 * 1000  # 10 minutes in milliseconds
            
            chunk_count = math.ceil(total_length / chunk_duration)
            progress_bar = st.progress(0)
            transcribed_text = ""

            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Prepare chunk futures
                chunk_futures = []
                for i in range(chunk_count):
                    start = i * chunk_duration
                    end = min((i + 1) * chunk_duration, total_length)
                    chunk = audio[start:end]
                    
                    # Create a temporary file for the chunk
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_chunk_file:
                        chunk.export(temp_chunk_file.name, format="mp3")
                        chunk_futures.append(
                            executor.submit(self.transcribe_chunk, temp_chunk_file.name)
                        )
                
                # Collect results
                for i, future in enumerate(concurrent.futures.as_completed(chunk_futures)):
                    try:
                        chunk_text = future.result()
                        transcribed_text += chunk_text + " "
                        progress_bar.progress((i + 1) / chunk_count)
                    except Exception as chunk_error:
                        st.warning(f"Failed to transcribe chunk {i}: {str(chunk_error)}")
            
            return transcribed_text.strip()
        
        except Exception as e:
            st.error(f"Failed to transcribe audio: {str(e)}")
            self.logger.error(f"Audio transcription error: {str(e)}")
            raise e

    def transcribe_chunk(self, chunk_path):
        """Transcribe a single audio chunk."""
        try:
            # Check chunk file size
            chunk_size = os.path.getsize(chunk_path) / (1024 * 1024)  # Size in MB
            st.info(f"Transcribing chunk of {chunk_size:.2f} MB")

            with open(chunk_path, "rb") as audio_file:
                transcriber = Transcriber("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")
                chunk_text = transcriber.transcribe_audio(chunk_path)
                
            # Clean up temporary chunk file
            os.remove(chunk_path)
            
            return chunk_text
        except Exception as e:
            self.logger.error(f"Error transcribing chunk {chunk_path}: {str(e)}")
            # Remove the temporary file if an error occurs
            if os.path.exists(chunk_path):
                os.remove(chunk_path)
            raise e



    def process_rag(self, translated_text):
        try:
            # Use the already initialized RAG system
            result = self.rag_system.process_media_alert(translated_text)
            
            # Create a formatted output with alert classification details
            classification_details = self.data["Classification Levels"].get(result["flag"], {})
            
            formatted_result = {
                "Alert Analysis": {
                    "Summary": result["summarization"],
                    "Overall Sentiment": result["sentiment"],
                    "Alert Level": result["flag"],
                    "Classification Details": {
                        "Criteria": classification_details.get("Criteria for Flagging", []),
                        "Required Action": classification_details.get("Action Required", [{"Action": "No specific action defined"}])[0]["Action"]
                    }
                }
            }
            
            return json.dumps(formatted_result, indent=2)
        except Exception as e:
            self.logger.error(f"RAG processing error: {str(e)}")
            return str(e)



    def run(self):
        st.title("🎬 AI Video Translation & Transcription")

        input_source = st.radio(
            "Choose Video Source",
            ["Upload File", "Video URL"],
            help="Select how you want to provide the video for translation"
        )
        video_path = None

        if input_source == "Video URL":
            video_url = st.text_input("Enter Video URL", help="Paste a direct link to the video file")
            if video_url:
                with st.spinner("Downloading video..."):
                    video_path = self.video_downloader.download(video_url)
        else:
            uploaded_file = st.file_uploader("Upload Video", type=['mp4', 'avi', 'mov'])
            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
                    temp_file.write(uploaded_file.getbuffer())
                    video_path = temp_file.name

        if video_path:
            try:
                with st.spinner("Converting video to audio..."):
                    try:
                        audio_path = self.video_to_audio(video_path)
                        st.success("Audio extraction complete!")
                    except RuntimeError as e:
                        if "FFmpeg is not installed" in str(e):
                            st.error("FFmpeg is required but not installed. Please contact the administrator.")
                            st.info("Technical details: " + str(e))
                            return
                        raise

                # Flash message for transcription
                st.info("Starting transcription...")

                with st.spinner("Transcribing audio..."):
                    transcribed_text = self.transcribe_audio(audio_path)

                detected_lang = detect(transcribed_text)
                st.subheader(f"Transcribed Text (Detected Language: {detected_lang.upper()})")
                st.text_area("Transcription", transcribed_text, height=100)
                
                # Add download button for transcribed text
                self.get_download_button(
                    transcribed_text,
                    f"transcription_{detected_lang}.txt",
                    f"📥 Download Transcription ({detected_lang.upper()})"
                )

                # Process original language transcription first
                with st.spinner(f"Analyzing original {detected_lang.upper()} content..."):
                    original_analysis = self.process_rag(transcribed_text)
                    st.subheader(f"Alert Analysis Results ({detected_lang.upper()})")
                    st.json(original_analysis)

                    # Add download button for original analysis
                    self.get_download_button(
                        original_analysis,
                        f"analysis_{detected_lang}.txt",
                        f"📥 Download {detected_lang.upper()} Analysis Report"
                    )

                if detected_lang != 'en':
                    translator = Translator()
                    with st.spinner("Translating to English..."):
                        translated_text = translator.translate_text(transcribed_text)

                    st.subheader("English Translation")
                    st.text_area("Translation", translated_text, height=300)
                    
                    # Add download button for translated text
                    self.get_download_button(
                        translated_text,
                        "translation_en.txt",
                        "📥 Download English Translation"
                    )

                    # Process English translation
                    with st.spinner("Analyzing English translation..."):
                        english_analysis = self.process_rag(translated_text)
                        st.subheader("Alert Analysis Results (English)")
                        st.json(english_analysis)

                        # Add download button for English analysis
                        self.get_download_button(
                            english_analysis,
                            "analysis_en.txt",
                            "📥 Download English Analysis Report"
                        )

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                self.logger.error(f"Exception during processing: {str(e)}")
            finally:
                # Cleanup temporary files
                if video_path and os.path.exists(video_path):
                    os.remove(video_path)
                if 'audio_path' in locals() and os.path.exists(audio_path):
                    os.remove(audio_path)
            
            # Add some spacing before the footer
        st.markdown("<br>" * 2, unsafe_allow_html=True)
        
        APP_VERSION = "0.3(Analysis_Url_Added)"
        DEVELOPER_NAME = "Rajesh Hugar"

            # Add some spacing before the footer
        st.markdown("<br>" * 2, unsafe_allow_html=True)
        
        # Footer with version and developer info using format method
        footer_html = """
        <div style="position: fixed; bottom: 0; left: 0; width: 100%; 
                    background-color: #f0f2f6; padding: 8px; 
                    font-size: 12px; text-align: center;
                    border-top: 1px solid #ddd;">
            <span style="margin-right: 20px;">Version: {}</span>
            <span>Developer: {}</span>
        </div>
        """.format(APP_VERSION, DEVELOPER_NAME)
        
        st.markdown(footer_html, unsafe_allow_html=True)
    


if __name__ == "__main__":
    app = VideoTranslationApp()
    app.run()