"""
Speech test fixtures and audio utilities for VariSetu Helpline test suite.
"""

import io
import os
import wave
import pytest

FIXTURES_DIR = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture
def marathi_normal_wav_bytes() -> bytes:
    path = os.path.join(FIXTURES_DIR, "marathi_normal_speech.wav")
    with open(path, "rb") as f:
        return f.read()

@pytest.fixture
def marathi_pause_wav_bytes() -> bytes:
    path = os.path.join(FIXTURES_DIR, "marathi_pause_speech.wav")
    with open(path, "rb") as f:
        return f.read()

@pytest.fixture
def silence_wav_bytes() -> bytes:
    path = os.path.join(FIXTURES_DIR, "silence_only.wav")
    with open(path, "rb") as f:
        return f.read()

@pytest.fixture
def pcm16_chunk_100ms() -> bytes:
    """100ms of 16kHz mono PCM16 audio (1600 samples = 3200 bytes)."""
    return bytes([0x10, 0x20] * 1600)
