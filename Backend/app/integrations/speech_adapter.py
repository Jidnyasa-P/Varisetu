import logging
from typing import Any, Dict
from app.core.config import settings

logger = logging.getLogger("varisetu.speech")


class SpeechAdapter:
    """
    Speech-to-Text (ASR) interface for helpline audio call recordings (Deccan Marathi / Hindi / English).
    """
    def __init__(self):
        self.provider = settings.SPEECH_PROVIDER

    async def transcribe(self, audio_bytes: bytes, language: str = "mr") -> Dict[str, Any]:
        """
        Transcribe helpline call recording audio.
        In mock mode, returns realistic Devanagari Marathi transcripts with confidence.
        """
        if self.provider == "mock":
            return {
                "transcript": (
                    "हॅलो कंट्रोल रूम, आमचे आजोबा मारुती शिंदे (वय ६८) वारीत वाखरी फाट्याजवळ "
                    "गर्दीत सुटले आहेत. त्यांनी पांढरा सुती कुर्ता, धोती आणि पांढरी टोपी घातली आहे. "
                    "गळ्यात तुळशीची माळ आहे आणि हातात टाळ आहेत. कृपया शोध घेण्यास मदत करा."
                ),
                "language": "mr",
                "asr_confidence": 0.94,
                "extracted_attributes": {
                    "gender": "M",
                    "estimated_age": 68,
                    "clothing": "पांढरा कुर्ता, धोती, पांढरी टोपी",
                    "accessories": "तुळशीची माळ, टाळ",
                    "last_seen": "वाखरी फाटा"
                },
                "source": "DEMO"
            }

        # Real Whisper / IndicWhisper adapter integration point
        return {
            "transcript": "",
            "language": language,
            "asr_confidence": 0.0,
            "extracted_attributes": {},
            "source": "WHISPER_ASR"
        }


speech_adapter = SpeechAdapter()
