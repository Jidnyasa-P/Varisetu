"""
Helpline Call Session Manager & Realtime Audio Ingestion Engine.
Maintains authoritative server-side call state machine, VAD state, utterance segmentation,
audio buffering with sequence validation, and WebSocket broadcasting.
"""

import asyncio
import io
import json
import logging
import math
import struct
import time
import uuid
import wave
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from fastapi import WebSocket, WebSocketDisconnect

from app.core.config import settings
from app.models.lost_person import CallState
from app.schemas.helpline import TranscriptSegment
from app.integrations.speech_adapter import speech_adapter

logger = logging.getLogger("varisetu.helpline.manager")


class HelplineSession:
    """Stateful representation of an ongoing citizen helpline call session."""

    def __init__(self, session_id: str, caller_name: str = "Citizen Caller", caller_phone: str = "+91-112", language: str = "mr", is_demo: bool = False):
        self.session_id = session_id
        self.caller_name = caller_name
        self.caller_phone = caller_phone
        self.dialed_line = "112 Emergency Helpline"
        self.language = language
        self.is_demo = is_demo

        self.call_state = CallState.IDLE
        self.created_at = datetime.now(timezone.utc)
        self.started_at: Optional[datetime] = None
        self.ended_at: Optional[datetime] = None
        self.duration_seconds = 0
        self.hold_duration_seconds = 0
        self._hold_start_time: Optional[float] = None
        self._call_start_time: Optional[float] = None

        # Audio Stream & VAD State
        self.audio_buffer: bytearray = bytearray()
        self.utterance_audio_buffer: bytearray = bytearray()
        self.audio_file_url: Optional[str] = None
        self.expected_sequence: int = 0
        self.dropped_chunks_count: int = 0
        self.last_audio_chunk_at: float = time.time()
        self.last_speech_at: float = 0.0
        self._accumulated_silence_ms: float = 0.0
        self.is_voice_active: bool = False
        self.noise_floor: float = 0.01

        # Transcripts & Segments
        self.segments: List[TranscriptSegment] = []
        self.current_partial_text: str = ""
        self.native_transcript: str = ""
        self.english_translation: str = ""
        self.extracted_attributes: Dict[str, Any] = {
            "name": None, "age": None, "gender": None,
            "clothing_description": None, "physical_description": None,
            "accessories": None, "last_seen_location": None,
            "last_seen_time": None, "direction_of_travel": None,
            "companions": None, "special_identifiers": None,
            "urgency": "HIGH", "confidence": {}
        }

        # Sockets attached to this session
        self.active_websockets: Set[WebSocket] = set()

    def start_call(self):
        self.call_state = CallState.LISTENING
        self.started_at = datetime.now(timezone.utc)
        self._call_start_time = time.time()
        logger.info(f"[CALL] Session {self.session_id} started: state -> LISTENING")

    def hold_call(self):
        if self.call_state != CallState.CALL_ENDED:
            self.call_state = CallState.OPERATOR_HOLD
            self._hold_start_time = time.time()
            logger.info(f"[CALL] Session {self.session_id} placed on OPERATOR_HOLD")

    def resume_call(self):
        if self.call_state == CallState.OPERATOR_HOLD:
            if self._hold_start_time:
                self.hold_duration_seconds += int(time.time() - self._hold_start_time)
                self._hold_start_time = None
            self.call_state = CallState.LISTENING
            logger.info(f"[CALL] Session {self.session_id} resumed from hold -> LISTENING")

    def end_call(self):
        self.call_state = CallState.CALL_ENDED
        self.ended_at = datetime.now(timezone.utc)
        if self._call_start_time:
            self.duration_seconds = int(time.time() - self._call_start_time)
        logger.info(f"[CALL] Session {self.session_id} ended. Total duration: {self.duration_seconds}s")

    def compute_frame_energy(self, pcm16_bytes: bytes) -> float:
        """Compute normalized Root Mean Square (RMS) energy for 16-bit linear PCM audio."""
        count = len(pcm16_bytes) // 2
        if count == 0:
            return 0.0
        try:
            shorts = struct.unpack(f"<{count}h", pcm16_bytes)
            sum_squares = sum(s * s for s in shorts)
            rms = math.sqrt(sum_squares / count) / 32768.0
            return float(rms)
        except Exception:
            return 0.0

    async def ingest_audio_frame(self, sequence: int, timestamp_ms: int, pcm16_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Processes an incoming 16kHz PCM16 audio chunk with sequence checking,
        VAD analysis, and utterance boundary detection. Returns list of events to broadcast.
        """
        events_to_broadcast = []
        now = time.time()

        # Sequence validation
        if sequence != self.expected_sequence:
            dropped = sequence - self.expected_sequence
            if dropped > 0:
                self.dropped_chunks_count += dropped
                logger.warning(f"[MEDIA] Session {self.session_id}: Dropped {dropped} chunks (expected {self.expected_sequence}, got {sequence})")
        self.expected_sequence = sequence + 1
        self.last_audio_chunk_at = now

        # When on hold, do not accumulate or process speech
        if self.call_state == CallState.OPERATOR_HOLD:
            return events_to_broadcast

        # Buffer raw audio
        self.audio_buffer.extend(pcm16_bytes)
        self.utterance_audio_buffer.extend(pcm16_bytes)

        # Compute energy & update noise floor adaptively
        energy = self.compute_frame_energy(pcm16_bytes)
        self.noise_floor = 0.95 * self.noise_floor + 0.05 * min(energy, 0.05)
        attack_thresh = max(0.025, self.noise_floor * 2.5)
        release_thresh = max(0.015, self.noise_floor * 1.5)

        # VAD Decision Logic
        if energy >= attack_thresh:
            self.last_speech_at = now
            self._accumulated_silence_ms = 0.0
            if not self.is_voice_active:
                self.is_voice_active = True
                self.call_state = CallState.SPEAKING
                events_to_broadcast.append({
                    "event": "vad_started",
                    "data": {"session_id": self.session_id, "call_state": self.call_state.value, "energy": round(energy, 4)}
                })
        else:
            # Silence detected
            frame_ms = len(pcm16_bytes) / 32.0
            self._accumulated_silence_ms += frame_ms
            silence_ms = max((now - self.last_speech_at) * 1000.0 if self.last_speech_at > 0 else 0, self._accumulated_silence_ms)
            if self.is_voice_active and silence_ms >= settings.VAD_MIN_SPEECH_MS:
                self.is_voice_active = False
                self.call_state = CallState.SILENCE_DETECTED
                events_to_broadcast.append({
                    "event": "vad_stopped",
                    "data": {"session_id": self.session_id, "call_state": self.call_state.value, "silence_ms": int(silence_ms)}
                })

            # Check for utterance finalization boundary (e.g. 900ms silence after speech)
            if silence_ms >= settings.VAD_UTTERANCE_END_SILENCE_MS and len(self.utterance_audio_buffer) >= 3200:  # >= 100ms
                self._accumulated_silence_ms = 0.0
                finalized_events = await self._finalize_current_utterance()
                events_to_broadcast.extend(finalized_events)

        return events_to_broadcast

    async def _finalize_current_utterance(self) -> List[Dict[str, Any]]:
        """Finalizes accumulated utterance audio, runs ASR, translation, and incremental entity extraction."""
        events = []
        if len(self.utterance_audio_buffer) < 1600:
            self.utterance_audio_buffer.clear()
            self.call_state = CallState.LISTENING
            return events

        self.call_state = CallState.PROCESSING_UTTERANCE
        events.append({
            "event": "connection_state",
            "data": {"session_id": self.session_id, "call_state": self.call_state.value}
        })

        # Convert PCM16 buffer to WAV bytes in memory
        wav_io = io.BytesIO()
        with wave.open(wav_io, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(self.utterance_audio_buffer)
        wav_bytes = wav_io.getvalue()
        self.utterance_audio_buffer.clear()

        # Run ASR via speech_adapter
        try:
            res = await speech_adapter.transcribe(audio_bytes=wav_bytes, language=self.language)
            native_text = res.get("native_transcript", "").strip()
            english_text = res.get("english_translation", "").strip()

            if native_text:
                seg_id = f"seg_{len(self.segments) + 1:03d}"
                seg = TranscriptSegment(
                    id=seg_id,
                    start_ms=max(0, int((time.time() - (self._call_start_time or time.time())) * 1000) - int(res.get("audio_duration_sec", 1.0) * 1000)),
                    end_ms=int((time.time() - (self._call_start_time or time.time())) * 1000),
                    language=self.language,
                    native_text=native_text,
                    english_text=english_text,
                    is_final=True,
                    asr_confidence=res.get("asr_confidence", 0.95),
                    translation_confidence=res.get("translation_confidence", 0.92)
                )
                self.segments.append(seg)

                # Update cumulative texts
                self.native_transcript = " ".join(s.native_text for s in self.segments)
                self.english_translation = " ".join(s.english_text for s in self.segments if s.english_text)

                # Incremental entity extraction update
                new_attrs = res.get("extracted_attributes", {})
                for k, v in new_attrs.items():
                    if v is not None:
                        self.extracted_attributes[k] = v

                events.append({
                    "event": "transcript_final",
                    "data": {"session_id": self.session_id, "segment": seg.model_dump(), "native_transcript": self.native_transcript}
                })
                events.append({
                    "event": "translation_final",
                    "data": {"session_id": self.session_id, "segment_id": seg.id, "english_text": english_text, "english_translation": self.english_translation}
                })
                events.append({
                    "event": "attributes_updated",
                    "data": {"session_id": self.session_id, "extracted_attributes": self.extracted_attributes}
                })
        except Exception as e:
            logger.error(f"[ASR] Error transcribing utterance segment: {e}")
            events.append({
                "event": "provider_error",
                "data": {"session_id": self.session_id, "error": str(e), "message": "Translation temporarily unavailable"}
            })

        self.call_state = CallState.LISTENING
        events.append({
            "event": "connection_state",
            "data": {"session_id": self.session_id, "call_state": self.call_state.value}
        })
        return events


class HelplineCallManager:
    """Singleton manager tracking active helpline call sessions and their WebSockets."""

    def __init__(self):
        self._sessions: Dict[str, HelplineSession] = {}
        self._lock = asyncio.Lock()

    async def get_or_create_session(
        self,
        session_id: Optional[str] = None,
        caller_name: str = "Citizen Caller",
        caller_phone: str = "+91-112",
        language: str = "mr",
        is_demo: bool = False
    ) -> HelplineSession:
        async with self._lock:
            if not session_id:
                session_id = f"call_{uuid.uuid4().hex[:12]}"
            if session_id not in self._sessions:
                self._sessions[session_id] = HelplineSession(
                    session_id=session_id,
                    caller_name=caller_name,
                    caller_phone=caller_phone,
                    language=language,
                    is_demo=is_demo
                )
            return self._sessions[session_id]

    async def get_session(self, session_id: str) -> Optional[HelplineSession]:
        return self._sessions.get(session_id)

    async def connect_socket(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        session = await self.get_or_create_session(session_id)
        session.active_websockets.add(websocket)
        logger.info(f"[WS] Attached client socket to session {session_id} (Total: {len(session.active_websockets)})")

        # Send initial session state
        await websocket.send_json({
            "event": "session_started",
            "data": {
                "session_id": session.session_id,
                "call_state": session.call_state.value,
                "caller_name": session.caller_name,
                "caller_phone": session.caller_phone,
                "language": session.language,
                "segments": [s.model_dump() for s in session.segments],
                "extracted_attributes": session.extracted_attributes
            }
        })

    async def disconnect_socket(self, session_id: str, websocket: WebSocket):
        session = self._sessions.get(session_id)
        if session and websocket in session.active_websockets:
            session.active_websockets.remove(websocket)
            logger.info(f"[WS] Detached socket from session {session_id} (Remaining: {len(session.active_websockets)})")

    async def broadcast_event(self, session_id: str, event_data: Dict[str, Any]):
        session = self._sessions.get(session_id)
        if not session or not session.active_websockets:
            return

        dead_sockets = set()
        for ws in session.active_websockets:
            try:
                await ws.send_json(event_data)
            except Exception as e:
                logger.warning(f"[WS] Failed to send event to socket in session {session_id}: {e}")
                dead_sockets.add(ws)

        for ws in dead_sockets:
            session.active_websockets.discard(ws)


helpline_manager = HelplineCallManager()
