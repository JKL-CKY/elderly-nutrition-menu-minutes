from pyannote.audio import Pipeline
import os
from dotenv import load_dotenv

load_dotenv()

class PyannoteService:
    def __init__(self):
        auth_token = os.getenv("PYANNOTE_AUTH_TOKEN")
        self.diarization_pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=auth_token
        )

    def diarize_audio(self, audio_path: str) -> dict:
        try:
            diarization = self.diarization_pipeline(audio_path)
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker
                })
            return {
                "speakers": list(set([s["speaker"] for s in segments])),
                "segments": segments
            }
        except Exception as e:
            return {"error": str(e)}

    def map_speakers_to_roles(self, diarization_result: dict, transcription_segments: list) -> list:
        if "error" in diarization_result:
            return []
        
        speaker_mapping = {}
        speaker_text_count = {}
        
        for seg in transcription_segments:
            mid_time = (seg["start"] + seg["end"]) / 2
            for dia_seg in diarization_result["segments"]:
                if dia_seg["start"] <= mid_time <= dia_seg["end"]:
                    speaker = dia_seg["speaker"]
                    if speaker not in speaker_text_count:
                        speaker_text_count[speaker] = ""
                    speaker_text_count[speaker] += seg["text"] + " "
                    break
        
        for speaker, text in speaker_text_count.items():
            text_lower = text.lower()
            if any(kw in text_lower for kw in ["营养", "营养师", "dietitian", "nutrition", "维生素", "蛋白质"]):
                speaker_mapping[speaker] = "营养师"
            elif any(kw in text_lower for kw in ["厨师", "厨房", "烹饪", "chef", "cook", "菜单", "菜"]):
                speaker_mapping[speaker] = "厨师长"
            else:
                speaker_mapping[speaker] = f"参会者{speaker}"
        
        annotated_segments = []
        for seg in transcription_segments:
            mid_time = (seg["start"] + seg["end"]) / 2
            role = "未知"
            for dia_seg in diarization_result["segments"]:
                if dia_seg["start"] <= mid_time <= dia_seg["end"]:
                    speaker = dia_seg["speaker"]
                    role = speaker_mapping.get(speaker, f"参会者{speaker}")
                    break
            annotated_segments.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"],
                "role": role
            })
        
        return annotated_segments
