from groq import Groq
from typing import Optional

class Transcriber:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
    
    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """Transcribe audio file using Groq API"""
        try:
            with open(audio_path, "rb") as file:
                translation = self.client.audio.translations.create(
                    file=(audio_path, file.read()),
                    model="whisper-large-v3",
                    response_format="json",
                    temperature=0.0
                )
                return translation.text
        except Exception as e:
            raise Exception(f"Error transcribing audio: {str(e)}")
