class AudioService:
    def __init__(self):
        pass

    def convert_video_to_audio(self, video_path, audio_format='mp3'):
        from pydub import AudioSegment

        audio_path = video_path.rsplit('.', 1)[0] + f'.{audio_format}'
        audio = AudioSegment.from_file(video_path)
        audio.export(audio_path, format=audio_format)
        return audio_path

    def extract_audio_from_video(self, video_path):
        return self.convert_video_to_audio(video_path)