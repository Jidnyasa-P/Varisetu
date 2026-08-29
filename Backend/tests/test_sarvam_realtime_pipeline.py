"""
Comprehensive Test Suite for VariSetu Single Authoritative Sarvam Realtime Speech Pipeline,
VAD State Transitions, Natural Pause Handling, Truthful Entity Extraction, and Audio Worklet Compliance.
"""

import asyncio
import io
import math
import struct
import wave
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.config import settings
from app.models.lost_person import CallState
from app.schemas.helpline import TranscriptSegment
from app.integrations.speech_provider import (
    SarvamRealtimeSpeechProvider,
    SarvamStreamingSession,
    MockSpeechProvider,
    SpeechProviderUnavailableError,
    SpeechTranslationUnavailableError,
    get_speech_provider
)
from app.integrations.speech_adapter import speech_adapter
from app.services.helpline_call_manager import HelplineSession, HelplineCallManager


class TestAudioFormatCompliance:
    """Verifies that all audio capture parameters strictly match 16kHz mono PCM16."""

    def test_audio_format_pcm16_inspection(self):
        prov = MockSpeechProvider()
        # 16000 samples (1 second of 16kHz mono audio = 32000 bytes)
        raw_pcm16 = bytes([0x00, 0x00] * 16000)
        info = prov._inspect_audio(raw_pcm16)
        assert info["format"] == "pcm16"
        assert info["samples_count"] == 16000
        assert math.isclose(info["duration_sec"], 1.0, rel_tol=1e-3)

    def test_audio_format_wav_inspection(self):
        prov = MockSpeechProvider()
        wav_io = io.BytesIO()
        with wave.open(wav_io, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(bytes([0x10, 0x20] * 3200)) # 0.2s
        wav_bytes = wav_io.getvalue()

        info = prov._inspect_audio(wav_bytes)
        assert info["format"] == "wav"
        assert info["samples_count"] == 3200
        assert math.isclose(info["duration_sec"], 0.2, rel_tol=1e-3)


class TestTruthfulEntityExtraction:
    """Verifies that unmentioned missing person attributes strictly default to None (no fake defaults)."""

    def test_entity_extraction_strict_nulls(self):
        prov = MockSpeechProvider()
        # Utterance mentions only name and location, no age, no clothes
        text = "हॅलो, आमचे मारुती शिंदे वाखरी फाट्याजवळ हरवले आहेत."
        attrs = prov.extract_entities(text, language="mr")

        assert attrs["name"] is not None
        assert "Maruti Shinde" in attrs["name"]
        assert attrs["last_seen_location"] == "Wakhri Phata Dindi Confluence"
        assert attrs["age"] is None  # Must NOT default to 55 or any arbitrary number
        assert attrs["clothing_description"] is None
        assert attrs["accessories"] is None

    def test_entity_extraction_full_attributes(self):
        prov = MockSpeechProvider()
        text = "माझी लहान मुलगी गोदावरी जाधव (वय ८ वर्षे) पुंडलिक मंदिराजवळ हरवली आहे. तिने पिवळा फ्रॉक घातला आहे."
        attrs = prov.extract_entities(text, language="mr")

        assert attrs["name"] is not None
        assert "Godavari" in attrs["name"]
        assert attrs["age"] == 8
        assert attrs["gender"] == "F"
        assert attrs["clothing_description"] is not None
        assert "Yellow Frock" in attrs["clothing_description"]
        assert attrs["urgency"] == "CRITICAL"  # Child under 12 triggers critical urgency


class TestSarvamRealtimeSpeechProvider:
    """Verifies Sarvam Realtime WebSocket provider behavior and error handling."""

    @pytest.mark.asyncio
    async def test_sarvam_unconfigured_error(self):
        """In LIVE mode without SARVAM_API_KEY, transcribe_audio MUST raise SpeechProviderUnavailableError (never fake)."""
        prov = SarvamRealtimeSpeechProvider()
        prov.api_key = None  # Unconfigured

        with pytest.raises(SpeechProviderUnavailableError) as exc:
            await prov.transcribe_audio(b"fake_audio_bytes", language="mr")
        assert "SARVAM_API_KEY is not configured" in str(exc.value)

    @pytest.mark.asyncio
    async def test_sarvam_translation_unconfigured_error(self):
        """In LIVE mode without SARVAM_API_KEY, translate_text MUST raise SpeechTranslationUnavailableError (no regex fallback)."""
        prov = SarvamRealtimeSpeechProvider()
        prov.api_key = None

        with pytest.raises(SpeechTranslationUnavailableError) as exc:
            await prov.translate_text("मारुती शिंदे हरवले आहेत", source_lang="mr", target_lang="en")
        assert "SARVAM_API_KEY is not configured" in str(exc.value)

    def test_sarvam_create_streaming_session(self):
        prov = SarvamRealtimeSpeechProvider()
        prov.api_key = "test_sarvam_key"
        session = prov.create_streaming_session(language="mr")

        assert isinstance(session, SarvamStreamingSession)
        assert session.language_code == "mr-IN"
        assert session.model == "saaras:v3"
        assert session.sample_rate == 16000
        assert session.input_audio_codec == "pcm_s16le"


class TestHelplineSessionLifecycle:
    """Verifies server-side state machine, natural pauses, hold, pause listening, and flush."""

    @pytest.mark.asyncio
    async def test_session_lifecycle_states(self):
        session = HelplineSession(session_id="test_sess_001", language="mr", is_demo=True)
        assert session.call_state == CallState.IDLE

        session.start_call()
        assert session.call_state == CallState.LISTENING

        session.hold_call()
        assert session.call_state == CallState.OPERATOR_HOLD

        session.resume_call()
        assert session.call_state == CallState.LISTENING

        session.pause_listening()
        assert session.is_paused is True

        session.resume_listening()
        assert session.is_paused is False

        await session.end_call()
        assert session.call_state == CallState.CALL_ENDED

    @pytest.mark.asyncio
    async def test_natural_pause_resilience(self):
        """Natural pause (0.5s - 3s) must NOT terminate the call or session."""
        session = HelplineSession(session_id="test_pause_002", language="mr", is_demo=True)
        session.start_call()

        # Ingest speech audio chunk (high energy tone)
        speech_chunk = bytearray()
        for i in range(800):  # 50ms at 16kHz
            val = int(0.5 * 32767.0 * math.sin(2.0 * math.pi * 300.0 * (i / 16000)))
            speech_chunk.extend(struct.pack("<h", val))

        events1 = await session.ingest_audio_frame(0, 0, bytes(speech_chunk))
        assert session.call_state == CallState.SPEAKING
        assert session.is_voice_active is True

        # Ingest silence chunks for 1.0 second (20 chunks of 50ms)
        silence_chunk = bytes([0x00, 0x00] * 800)
        for i in range(1, 21):
            events = await session.ingest_audio_frame(i, i * 50, silence_chunk)

        # Call must remain alive and transition to SILENCE_DETECTED / LISTENING without ending
        assert session.call_state in (CallState.SILENCE_DETECTED, CallState.LISTENING)
        assert session.call_state != CallState.CALL_ENDED
        assert session.call_state != CallState.ERROR
