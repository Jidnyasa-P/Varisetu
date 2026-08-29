"""
Speech-to-Text (ASR) & AI Translation Adapter for Helpline Audio Calls.
Routes calls to configured BaseSpeechProvider (Sarvam, Groq, Mock) with structured entity extraction.
"""

import logging
import re
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.integrations.speech_provider import get_speech_provider, BaseSpeechProvider

logger = logging.getLogger("varisetu.speech")


class SpeechAdapter:
    def __init__(self):
        self.provider_type = settings.SPEECH_PROVIDER

    @property
    def provider(self) -> BaseSpeechProvider:
        return get_speech_provider()

    # Pre-calibrated pilgrimage helpline scenarios (Exclusively for DEMO Simulation Mode)
    SCENARIOS: Dict[str, Dict[str, Any]] = {
        "marathi_senior_wakhri": {
            "id": "marathi_senior_wakhri",
            "title": "Elderly Pilgrim Separated at Wakhri Phata (मराठी)",
            "caller_phone": "+91 98234 11204",
            "caller_name": "Dnyaneshwar Shinde",
            "dialed_line": "112 / Wari SOS 1077",
            "language": "mr",
            "language_name": "मराठी (Marathi)",
            "native_transcript": (
                "हॅलो कंट्रोल रूम, आमचे आजोबा मारुती शिंदे (वय ६८) वारीत वाखरी फाट्याजवळ "
                "गर्दीत सुटले आहेत. त्यांनी पांढरा सुती कुर्ता, धोती आणि पांढरी टोपी घातली आहे. "
                "गळ्यात तुळशीची माळ आहे आणि हातात टाळ आहेत. कृपया शोध घेण्यास मदत करा."
            ),
            "english_translation": (
                "Hello Control Room, our grandfather Maruti Shinde (age 68) got separated "
                "in the crowd near Wakhri Phata. He is wearing a white cotton kurta, dhoti, "
                "and a white Gandhi cap. He has a Tulsi mala around his neck and cymbals in hand. "
                "Please help us locate him."
            ),
            "confidence": 0.96,
            "extracted_attributes": {
                "name": "Maruti Shinde (मारुती शिंदे)",
                "age": 68,
                "gender": "M",
                "clothing_description": "White cotton kurta, White dhoti, White Gandhi cap",
                "physical_description": None,
                "accessories": "Tulsi mala, Taal cymbals",
                "last_seen_location": "Wakhri Phata Dindi Confluence",
                "urgency": "HIGH"
            },
            "source": "DEMO"
        },
        "marathi_child_pundalik": {
            "id": "marathi_child_pundalik",
            "title": "Lost Child near Pundalik Temple (मराठी)",
            "caller_phone": "+91 94220 88912",
            "caller_name": "Sunita Jadhav",
            "dialed_line": "112 / Emergency Helpline",
            "language": "mr",
            "language_name": "मराठी (Marathi)",
            "native_transcript": (
                "माझी लहान मुलगी गोदावरी जाधव (वय ८ वर्षे) पुंडलिक मंदिराच्या पायऱ्यांजवळ "
                "गर्दीत हरवली आहे. तिने पिवळा फ्रॉक घातला असून डोक्यात लाल रिबीन बांधली आहे. "
                "कृपया तातडीने शोध घ्या, ती खूप लहान आणि घाबरलेली आहे."
            ),
            "english_translation": (
                "My young daughter Godavari Jadhav (age 8 years) has gone missing near "
                "the steps of Pundalik Temple in the crowd. She is wearing a yellow floral "
                "frock with red hair ribbons. Please search urgently, she is very young and frightened."
            ),
            "confidence": 0.98,
            "extracted_attributes": {
                "name": "Godavari Jadhav (गोदावरी जाधव)",
                "age": 8,
                "gender": "F",
                "clothing_description": "Yellow floral frock with red ribbons",
                "physical_description": None,
                "accessories": None,
                "last_seen_location": "Pundalik Temple Steps (Pandharpur)",
                "urgency": "CRITICAL"
            },
            "source": "DEMO"
        },
        "hindi_pilgrim_alandi": {
            "id": "hindi_pilgrim_alandi",
            "title": "Hindi-speaking Pilgrim at Alandi Ghat (हिन्दी)",
            "caller_phone": "+91 91580 44321",
            "caller_name": "Rameshwar Gupta",
            "dialed_line": "112 / National SOS",
            "language": "hi",
            "language_name": "हिन्दी (Hindi)",
            "native_transcript": (
                "नमस्ते कंट्रोल रूम, हमारे पिताजी रामकिशन गुप्ता (उम्र ७२) आलंदी घाट पर "
                "पालखी प्रस्थान के समय बिछड़ गए हैं। उन्होंने सफेद कुर्ता और सिर पर केसरिया पगड़ी "
                "बांधी है। उन्हें चलने में थोड़ी परेशानी होती है। कृपया मदद करें।"
            ),
            "english_translation": (
                "Hello Control Room, our father Ramkishan Gupta (age 72) got separated "
                "at Alandi Ghat during the Palkhi departure. He is wearing a white kurta "
                "and a saffron turban on his head. He has difficulty walking. Please assist."
            ),
            "confidence": 0.95,
            "extracted_attributes": {
                "name": "Ramkishan Gupta (रामकिशन गुप्ता)",
                "age": 72,
                "gender": "M",
                "clothing_description": "White kurta, Saffron turban",
                "physical_description": "Difficulty walking",
                "accessories": None,
                "last_seen_location": "Alandi Indrayani Ghat Corridor",
                "urgency": "CRITICAL"
            },
            "source": "DEMO"
        }
    }

    async def transcribe(self, audio_bytes: bytes, language: str = "mr") -> Dict[str, Any]:
        """
        Transcribe and translate raw audio bytes by explicitly delegating to the configured provider.
        Consumes real audio bytes.
        """
        if not audio_bytes or len(audio_bytes) == 0:
            raise ValueError("audio_bytes cannot be empty for transcription")
        return await self.provider.transcribe_audio(audio_bytes=audio_bytes, language=language)

    async def translate_text(self, text: str, source_lang: str = "mr", target_lang: str = "en") -> str:
        """Contextual neural/rule translation via provider."""
        return await self.provider.translate_text(text=text, source_lang=source_lang, target_lang=target_lang)

    def extract_attributes(self, text: str, language: str = "mr") -> Dict[str, Any]:
        """
        Structured entity extraction where unmentioned attributes are strictly None.
        """
        return self.provider.extract_entities(text=text, language=language)

    async def transcribe_and_translate(
        self,
        scenario_id: Optional[str] = None,
        custom_text: Optional[str] = None,
        audio_bytes: Optional[bytes] = None,
        language: str = "mr",
        caller_name: Optional[str] = None,
        caller_phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handles live voice bytes, custom text entry, or explicit preset demo scenario simulation.
        """
        if audio_bytes and len(audio_bytes) > 0:
            return await self.transcribe(audio_bytes=audio_bytes, language=language)

        if custom_text and custom_text.strip():
            text = custom_text.strip()
            english_text = await self.translate_text(text, source_lang=language, target_lang="en")
            entities = self.extract_attributes(text, language=language)
            return {
                "id": "live_user_input",
                "title": "Live Citizen Voice Intake Call",
                "caller_phone": caller_phone or "+91 98220 99881",
                "caller_name": caller_name or "Citizen Caller (Live SOS)",
                "dialed_line": "112 / Emergency Helpline",
                "language": language,
                "language_name": "मराठी (Marathi)" if language == "mr" else ("हिन्दी (Hindi)" if language == "hi" else "English"),
                "native_transcript": text,
                "english_translation": english_text,
                "confidence": 0.96,
                "extracted_attributes": entities,
                "source": "LIVE_TEXT_INPUT"
            }

        if scenario_id and scenario_id in self.SCENARIOS:
            return self.SCENARIOS[scenario_id]

        return self.SCENARIOS["marathi_senior_wakhri"]


speech_adapter = SpeechAdapter()
