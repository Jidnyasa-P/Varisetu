"""
Audio Test Fixtures for VariSetu Helpline Test Suites.
Generates genuine 16kHz mono Linear PCM16 and WAV audio buffers with speech patterns,
pauses, background noise, and silence.
"""

import io
import math
import struct
import wave
from typing import List, Tuple


def generate_pcm16_sine_wave(freq_hz: float = 440.0, duration_sec: float = 1.0, sample_rate: int = 16000, amplitude: float = 0.5) -> bytes:
    """Generates 16kHz mono PCM16 sine wave simulating tonal vocal energy."""
    total_samples = int(sample_rate * duration_sec)
    max_amp = int(32767 * amplitude)
    samples = []
    for i in range(total_samples):
        t = float(i) / sample_rate
        val = int(max_amp * math.sin(2.0 * math.pi * freq_hz * t))
        samples.append(val)
    return struct.pack(f"<{len(samples)}h", *samples)


def generate_pcm16_silence(duration_sec: float = 1.0, sample_rate: int = 16000) -> bytes:
    """Generates pure digital silence (zero samples) as 16kHz mono PCM16."""
    total_samples = int(sample_rate * duration_sec)
    return struct.pack(f"<{total_samples}h", *([0] * total_samples))


def generate_speech_with_pauses(
    burst_durations: List[float] = [0.8, 1.2, 0.6],
    pause_durations: List[float] = [0.3, 0.9],
    sample_rate: int = 16000
) -> bytes:
    """
    Generates a realistic sequence of speech bursts interleaved with natural pauses.
    """
    buffer = bytearray()
    for idx, burst_dur in enumerate(burst_durations):
        # Speech burst with harmonized frequencies
        freq = 300.0 + (idx * 50.0)
        buffer.extend(generate_pcm16_sine_wave(freq_hz=freq, duration_sec=burst_dur, sample_rate=sample_rate, amplitude=0.4))

        if idx < len(pause_durations):
            # Interleaved silence/pause
            buffer.extend(generate_pcm16_silence(duration_sec=pause_durations[idx], sample_rate=sample_rate))

    return bytes(buffer)


def pcm16_to_wav(pcm_bytes: bytes, sample_rate: int = 16000, channels: int = 1) -> bytes:
    """Encapsulates raw PCM16 bytes with standard RIFF/WAV header."""
    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    return wav_io.getvalue()
