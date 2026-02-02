import os
from pydub import AudioSegment
import streamlit as st
import concurrent.futures
import math
import tempfile
from utils.transcriber import Transcriber
from services.translation_service import translate_article_data
from utils.aramco_alert import process_rag

# AudioSegment.converter = "C:\FFmpeg-Builds-latest\FFmpeg-Builds-latest\build.exe"

class Audio_Prcessor:
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
        
    def audio_processor(self, video_path):
        try:
            # Convert video to audio
            print(video_path)
            audio_processor = Audio_Prcessor()
            audio_path = audio_processor.video_to_audio(video_path)
            audio_trancript = audio_processor.transcribe_audio(audio_path)
            audio_dict = {"audio_path":audio_path, "content":audio_trancript}
            audio_translated = translate_article_data(audio_dict)
            if "aramco" not in audio_trancript.lower():
                return {"Mention":"No Aramco Mention"}
            else:
                rag_result = process_rag(translated_text=audio_translated['content'])
            return rag_result
        except Exception as e:
            st.error(f"Error processing audio: {str(e)}")