# Transcription Service Implementation

class TranscriptionService:
    def __init__(self, transcriber):
        self.transcriber = transcriber

    def transcribe_audio(self, audio_path):
        """Transcribe the audio file to text."""
        try:
            return self.transcriber.transcribe_audio(audio_path)
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {str(e)}")