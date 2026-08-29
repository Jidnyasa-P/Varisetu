"""
Comprehensive Unit & Integration Test Suite for Helpline Call Session Lifecycle,
VAD Transitions, Audio Frame Ingestion, Operator HOLD/RESUME, and Case Registration.
"""

import pytest
from app.models.lost_person import CallState
from app.services.helpline_call_manager import HelplineSession, helpline_manager
from tests.fixtures.test_audio import generate_pcm16_sine_wave, generate_pcm16_silence, pcm16_to_wav


async def get_admin_headers(client):
    login_res = await client.post("/api/auth/login", json={
        "email": "test.commander@mahapolice.gov.in",
        "password": "varisetu2026"
    })
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_session_state_machine_and_vad_transitions():
    """Validates VAD transitions: SILENCE -> SPEAKING -> SILENCE_DETECTED -> PROCESSING_UTTERANCE -> LISTENING."""
    session = HelplineSession(
        session_id="test_session_001",
        caller_name="Vithoba Bhakt",
        caller_phone="+91 98221 11223",
        language="mr"
    )
    assert session.call_state == CallState.IDLE

    # 1. Start Call -> LISTENING
    session.start_call()
    assert session.call_state == CallState.LISTENING

    # 2. Ingest Voice Frame -> SPEAKING
    voice_pcm = generate_pcm16_sine_wave(freq_hz=440.0, duration_sec=0.2, amplitude=0.6)
    events = await session.ingest_audio_frame(sequence=0, timestamp_ms=1000, pcm16_bytes=voice_pcm)
    assert session.call_state == CallState.SPEAKING
    assert any(e["event"] == "vad_started" for e in events)

    # 3. Ingest Brief Silence Frame -> SILENCE_DETECTED
    silence_pcm = generate_pcm16_silence(duration_sec=0.2)
    events = await session.ingest_audio_frame(sequence=1, timestamp_ms=1200, pcm16_bytes=silence_pcm)
    assert session.call_state == CallState.SILENCE_DETECTED

    # 4. Ingest Prolonged Silence (Utterance Boundary) -> PROCESSING_UTTERANCE -> LISTENING
    long_silence_pcm = generate_pcm16_silence(duration_sec=1.0)
    events = await session.ingest_audio_frame(sequence=2, timestamp_ms=2200, pcm16_bytes=long_silence_pcm)
    assert session.call_state == CallState.LISTENING
    assert len(session.segments) >= 1
    assert session.segments[0].is_final is True
    assert any(e["event"] == "transcript_final" for e in events)
    assert any(e["event"] == "translation_final" for e in events)


@pytest.mark.asyncio
async def test_operator_hold_and_resume():
    """Validates that operator HOLD freezes audio processing while preserving session identity and transcripts."""
    session = HelplineSession(
        session_id="test_session_hold_002",
        caller_name="Anand Patil",
        caller_phone="+91 97654 33221",
        language="mr"
    )
    session.start_call()

    # Ingest speech
    voice_pcm = generate_pcm16_sine_wave(freq_hz=350.0, duration_sec=0.3, amplitude=0.5)
    await session.ingest_audio_frame(sequence=0, timestamp_ms=1000, pcm16_bytes=voice_pcm)
    assert session.call_state == CallState.SPEAKING

    # Place on Operator HOLD
    session.hold_call()
    assert session.call_state == CallState.OPERATOR_HOLD

    # Ingesting audio while on HOLD must be ignored
    ignored_events = await session.ingest_audio_frame(sequence=1, timestamp_ms=1300, pcm16_bytes=voice_pcm)
    assert len(ignored_events) == 0
    assert session.call_state == CallState.OPERATOR_HOLD

    # Resume from HOLD -> LISTENING
    session.resume_call()
    assert session.call_state == CallState.LISTENING


@pytest.mark.asyncio
async def test_dropped_sequence_detection():
    """Validates that missing audio sequence frames are tracked."""
    session = HelplineSession(session_id="test_session_seq_003")
    session.start_call()

    voice_pcm = generate_pcm16_sine_wave(freq_hz=440.0, duration_sec=0.1)
    await session.ingest_audio_frame(sequence=0, timestamp_ms=1000, pcm16_bytes=voice_pcm)
    assert session.dropped_chunks_count == 0

    # Skip to sequence 4 (dropped frames: 1, 2, 3)
    await session.ingest_audio_frame(sequence=4, timestamp_ms=1400, pcm16_bytes=voice_pcm)
    assert session.dropped_chunks_count == 3


@pytest.mark.asyncio
async def test_rest_helpline_session_lifecycle(client):
    """Integration test of REST call lifecycle endpoints (/calls, /hold, /resume, /report, /create-case, /end)."""
    headers = await get_admin_headers(client)

    # 1. Initialize Call Session
    init_res = await client.post("/api/helpline/calls", json={
        "caller_name": "Suresh Tukaram More",
        "caller_phone": "+91 98220 55441",
        "language": "mr"
    }, headers=headers)
    assert init_res.status_code == 201
    call_data = init_res.json()
    session_id = call_data["session_id"]
    assert call_data["call_state"] == "LISTENING"

    # 2. Operator Places Call on HOLD
    hold_res = await client.post(f"/api/helpline/calls/{session_id}/hold", headers=headers)
    assert hold_res.status_code == 200
    assert hold_res.json()["call_state"] == "OPERATOR_HOLD"

    # 3. Operator Resumes Call
    resume_res = await client.post(f"/api/helpline/calls/{session_id}/resume", headers=headers)
    assert resume_res.status_code == 200
    assert resume_res.json()["call_state"] == "LISTENING"

    # 4. Operator Updates Report Attributes
    report_res = await client.post(f"/api/helpline/calls/{session_id}/report", json={
        "name": "Tukaram More",
        "age": 64,
        "gender": "M",
        "clothing_description": "White Kurta with Saffron Turban",
        "last_seen_location": "Saswad Dive Ghat Junction"
    }, headers=headers)
    assert report_res.status_code == 200
    attrs = report_res.json()["extracted_attributes"]
    assert attrs["name"] == "Tukaram More"
    assert attrs["age"] == 64

    # 5. Create Case from Session with CCTV Scan
    case_res = await client.post(f"/api/helpline/calls/{session_id}/create-case", json={
        "name": "Tukaram More",
        "age": 64,
        "gender": "M",
        "clothing_description": "White Kurta with Saffron Turban",
        "last_seen_location": "Saswad Dive Ghat Junction",
        "trigger_cctv_scan": True
    }, headers=headers)
    assert case_res.status_code == 201
    case_data = case_res.json()
    assert case_data["case"]["name"] == "Tukaram More"
    assert len(case_data["cctv_candidates"]) >= 1

    # 6. End Call Session
    end_res = await client.post(f"/api/helpline/calls/{session_id}/end", headers=headers)
    assert end_res.status_code == 200
    assert end_res.json()["call_state"] == "CALL_ENDED"
