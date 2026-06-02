import whisper
import os
from typing import Optional

class WhisperService:
    def __init__(self, model_size: str = "base"):
        self.model = whisper.load_model(model_size)

    def transcribe_audio(self, audio_path: str, language: str = "zh") -> str:
        try:
            result = self.model.transcribe(audio_path, language=language)
            return result["text"]
        except Exception as e:
            return f"Transcription error: {str(e)}"

    def transcribe_with_timestamps(self, audio_path: str, language: str = "zh") -> dict:
        try:
            result = self.model.transcribe(audio_path, language=language, word_timestamps=True)
            segments = []
            for seg in result["segments"]:
                segments.append({
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"]
                })
            return {
                "full_text": result["text"],
                "segments": segments
            }
        except Exception as e:
            return {"error": str(e)}
