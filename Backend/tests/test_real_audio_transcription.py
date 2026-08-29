"""
Integration Test Suite validating genuine raw audio bytes consumption in SpeechAdapter,
WAV/PCM16 header inspection, Marathi/Hindi neural translation, and truthful entity extraction.
"""

import pytest
from app.integrations.speech_adapter import speech_adapter
from tests.fixtures.test_audio import generate_pcm16_sine_wave, generate_speech_with_pauses, pcm16_to_wav


@pytest.mark.asyncio
async def test_transcribe_consumes_real_wav_audio_bytes():
    """Asserts that speech_adapter.transcribe actually inspects and consumes WAV audio bytes."""
    # Generate 1.5 seconds of 16kHz mono audio
    pcm = generate_pcm16_sine_wave(freq_hz=440.0, duration_sec=1.5, sample_rate=16000)
    wav_bytes = pcm16_to_wav(pcm, sample_rate=16000)

    assert len(wav_bytes) > 44
    assert wav_bytes[:4] == b"RIFF"

    res = await speech_adapter.transcribe(audio_bytes=wav_bytes, language="mr")
    assert res is not None
    assert "native_transcript" in res
    assert "english_translation" in res
    assert res["audio_duration_sec"] >= 1.45
    assert res["audio_duration_sec"] <= 1.55
    assert res["language"] == "mr"


@pytest.mark.asyncio
async def test_transcribe_rejects_empty_audio_bytes():
    """Validates that empty audio bytes fail explicitly rather than returning fabricated output."""
    with pytest.raises(ValueError, match="audio_bytes cannot be empty"):
        await speech_adapter.transcribe(audio_bytes=b"", language="mr")


@pytest.mark.asyncio
async def test_translation_preserves_names_and_landmarks():
    """Validates that proper nouns, landmarks, and pilgrimage terminology are preserved in English translation."""
    marathi_text = "आमचे आजोबा मारुती शिंदे वाखरी फाट्याजवळ हरवले आहेत. त्यांनी पांढरा कुर्ता आणि धोती घातली आहे."
    eng = await speech_adapter.translate_text(marathi_text, source_lang="mr", target_lang="en")

    assert "Maruti Shinde" in eng
    assert "Wakhri Phata" in eng
    assert "white" in eng.lower()
    assert ("kurta" in eng.lower() or "dhoti" in eng.lower())


@pytest.mark.asyncio
async def test_entity_extraction_strict_null_defaults():
    """
    Validates that unmentioned entity fields strictly remain None (never fabricated arbitrary defaults like 55).
    """
    sparse_text = "माझी लहान मुलगी हरवली आहे."
    entities = speech_adapter.extract_attributes(sparse_text, language="mr")

    assert entities["gender"] == "F"
    assert entities["age"] is None  # Must NOT be 55 or any hardcoded default
    assert entities["name"] is None  # Must NOT be "Reported Pilgrim"
    assert entities["physical_description"] is None
    assert entities["accessories"] is None


@pytest.mark.asyncio
async def test_entity_extraction_populates_stated_attributes():
    """Validates that explicitly stated attributes in transcript are accurately extracted."""
    full_text = "गोदावरी जाधव (वय ८ वर्षे) पुंडलिक मंदिराजवळ हरवली आहे. तिने पिवळा फ्रॉक आणि लाल रिबीन घातली आहे."
    entities = speech_adapter.extract_attributes(full_text, language="mr")

    assert entities["age"] == 8
    assert entities["gender"] == "F"
    assert "Godavari Jadhav" in (entities["name"] or "")
    assert "Pundalik Temple" in (entities["last_seen_location"] or "")
    assert "Yellow Frock" in (entities["clothing_description"] or "")
    assert entities["urgency"] == "CRITICAL"
