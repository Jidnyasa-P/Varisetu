"""
Helpline Call Session Manager & Realtime Audio Ingestion Engine.
Maintains authoritative server-side call state machine, single authoritative ASR streaming
with Sarvam Realtime WebSocket, VAD signal handling, natural pause resilience, and WebSocket broadcasting.
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
from app.integrations.speech_provider import (
    BaseSpeechProvider,
    MockSpeechProvider,
    SarvamRealtimeSpeechProvider,
    SarvamStreamingSession,
    SpeechProviderError,
    SpeechProviderUnavailableError,
    SpeechTranslationUnavailableError,
)

logger = logging.getLogger("varisetu.helpline.manager")


class HelplineSession:
    """Stateful representation of an ongoing citizen helpline call session."""

    def __init__(
        self,
        session_id: str,
        caller_name: str = "Citizen Caller",
        caller_phone: str = "+91-112",
        language: str = "mr",
        is_demo: bool = False
    ):
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
        self.is_paused: bool = False

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

        # Streaming Provider Session
        self.streaming_session: Optional[SarvamStreamingSession] = None
        self._streaming_init_lock = asyncio.Lock()

        # Sockets attached to this session
        self.active_websockets: Set[WebSocket] = set()

    async def init_streaming_provider(self):
        """Initializes Sarvam Realtime streaming session if in LIVE mode."""
        if self.is_demo:
            logger.info(f"[CALL] Session {self.session_id}: Operating in DEMO SIMULATION mode.")
            return

        provider = speech_adapter.provider
        if isinstance(provider, SarvamRealtimeSpeechProvider):
            if not settings.SARVAM_API_KEY:
                logger.warning(f"[CALL] Session {self.session_id}: SARVAM_API_KEY is unconfigured.")
                self.call_state = CallState.PROVIDER_DEGRADED
                await self.broadcast({
                    "event": "provider_error",
                    "data": {
                        "session_id": self.session_id,
                        "code": "SPEECH_PROVIDER_UNCONFIGURED",
                        "message": "SPEECH PROVIDER NOT CONFIGURED. Please set SARVAM_API_KEY or use DEMO mode."
                    }
                })
                return

            async with self._streaming_init_lock:
                if self.streaming_session and self.streaming_session.is_connected:
                    return

                try:
                    self.streaming_session = provider.create_streaming_session(
                        language=self.language,
                        on_partial_transcript=self._on_provider_partial,
                        on_final_transcript=self._on_provider_final,
                        on_vad_event=self._on_provider_vad,
                        on_error=self._on_provider_error
                    )
                    await self.streaming_session.connect()
                    logger.info(f"[ASR] [SARVAM] Streaming WebSocket session ready for call {self.session_id}")
                except Exception as e:
                    logger.error(f"[ASR] [SARVAM] Failed to initialize streaming session: {e}")
                    self.call_state = CallState.PROVIDER_DEGRADED
                    await self.broadcast({
                        "event": "provider_error",
                        "data": {
                            "session_id": self.session_id,
                            "code": "PROVIDER_CONNECT_FAILED",
                            "message": f"Realtime speech provider connect failed: {e}"
                        }
                    })

    def _on_provider_partial(self, partial_text: str):
        """Handles incoming partial transcript from Sarvam."""
        self.current_partial_text = partial_text
        asyncio.create_task(self.broadcast({
            "event": "partial_transcript",
            "type": "interim_transcript",
            "data": {
                "session_id": self.session_id,
                "transcript": partial_text
            },
            "transcript": partial_text
        }))

    def _on_provider_final(self, final_text: str, confidence: float):
        """Handles incoming authoritative final transcript segment from Sarvam."""
        asyncio.create_task(self._handle_final_utterance(final_text, confidence))

    def _on_provider_vad(self, signal: str, payload: Dict[str, Any]):
        """Handles authoritative VAD events from Sarvam."""
        if signal == "speech_start":
            self.is_voice_active = True
            if self.call_state not in (CallState.OPERATOR_HOLD, CallState.CALL_ENDED):
                self.call_state = CallState.SPEAKING
            asyncio.create_task(self.broadcast({
                "event": "vad_started",
                "type": "vad_event",
                "is_speech": True,
                "vad_state": "SPEAKING",
                "data": {
                    "session_id": self.session_id,
                    "call_state": self.call_state.value
                }
            }))
        elif signal == "speech_end":
            self.is_voice_active = False
            if self.call_state not in (CallState.OPERATOR_HOLD, CallState.CALL_ENDED):
                self.call_state = CallState.SILENCE_DETECTED
            asyncio.create_task(self.broadcast({
                "event": "vad_stopped",
                "type": "vad_event",
                "is_speech": False,
                "vad_state": "SILENCE_DETECTED",
                "data": {
                    "session_id": self.session_id,
                    "call_state": self.call_state.value
                }
            }))
            # Return to LISTENING state after natural pause
            asyncio.create_task(self._return_to_listening_after_pause())

    async def _return_to_listening_after_pause(self):
        await asyncio.sleep(0.6)
        if not self.is_voice_active and self.call_state == CallState.SILENCE_DETECTED:
            self.call_state = CallState.LISTENING
            await self.broadcast({
                "event": "connection_state",
                "type": "state_change",
                "state": self.call_state.value,
                "data": {
                    "session_id": self.session_id,
                    "call_state": self.call_state.value
                }
            })

    def _on_provider_error(self, exc: Exception):
        logger.warning(f"[ASR] [SARVAM] Provider error in session {self.session_id}: {exc}")
        asyncio.create_task(self.broadcast({
            "event": "provider_error",
            "data": {
                "session_id": self.session_id,
                "error": str(exc),
                "message": "Speech provider error"
            }
        }))

    async def _handle_final_utterance(self, native_text: str, confidence: float) -> List[Dict[str, Any]]:
        """Processes finalized native utterance segment, performs neural translation & entity extraction."""
        events = []
        if not native_text or not native_text.strip():
            return events

        seg_id = f"seg_{len(self.segments) + 1:03d}"
        now_ms = int((time.time() - (self._call_start_time or time.time())) * 1000)

        # Contextual Neural Translation
        english_text = ""
        translation_status = "OK"
        try:
            english_text = await speech_adapter.translate_text(native_text, source_lang=self.language, target_lang="en")
        except SpeechTranslationUnavailableError:
            logger.warning(f"[TRANSLATE] Translation unavailable for segment {seg_id}")
            english_text = ""
            translation_status = "UNAVAILABLE"
        except Exception as te:
            logger.warning(f"[TRANSLATE] Neural translation error for segment {seg_id}: {te}")
            english_text = ""
            translation_status = "ERROR"

        # Construct single authoritative segment
        seg = TranscriptSegment(
            id=seg_id,
            start_ms=max(0, now_ms - 2500),
            end_ms=now_ms,
            language=self.language,
            native_text=native_text,
            english_text=english_text,
            is_final=True,
            asr_confidence=confidence,
            translation_confidence=0.94 if english_text else 0.0
        )
        self.segments.append(seg)
        self.current_partial_text = ""

        # Update cumulative transcript
        self.native_transcript = " ".join(s.native_text for s in self.segments)
        self.english_translation = " ".join(s.english_text for s in self.segments if s.english_text)

        # Truthful incremental entity extraction
        new_attrs = speech_adapter.extract_attributes(native_text, language=self.language)
        for k, v in new_attrs.items():
            if v is not None:
                self.extracted_attributes[k] = v

        logger.info(f"[EXTRACTION] Segment {seg_id} finalized. Attributes updated: {[k for k,v in new_attrs.items() if v is not None]}")

        # Broadcast events
        ev_transcript = {
            "event": "transcript_final",
            "type": "final_segment",
            "segment": {
                "segment_id": seg.id,
                "text": seg.native_text,
                "confidence": seg.asr_confidence,
                "language": seg.language
            },
            "data": {
                "session_id": self.session_id,
                "segment": seg.model_dump(),
                "native_transcript": self.native_transcript
            }
        }
        events.append(ev_transcript)
        await self.broadcast(ev_transcript)

        if english_text or translation_status != "OK":
            ev_translation = {
                "event": "translation_final",
                "type": "translation_segment",
                "segment": {
                    "segment_id": seg.id,
                    "english_text": english_text if english_text else "TRANSLATION TEMPORARILY UNAVAILABLE",
                    "status": translation_status
                },
                "data": {
                    "session_id": self.session_id,
                    "segment_id": seg.id,
                    "english_text": english_text,
                    "translation_status": translation_status,
                    "english_translation": self.english_translation
                }
            }
            events.append(ev_translation)
            await self.broadcast(ev_translation)

        ev_attrs = {
            "event": "attributes_updated",
            "type": "attributes_updated",
            "attributes": self.extracted_attributes,
            "data": {
                "session_id": self.session_id,
                "extracted_attributes": self.extracted_attributes
            }
        }
        events.append(ev_attrs)
        await self.broadcast(ev_attrs)

        return events

    def start_call(self):
        self.call_state = CallState.LISTENING
        self.started_at = datetime.now(timezone.utc)
        self._call_start_time = time.time()
        logger.info(f"[CALL] Session {self.session_id} started: state -> LISTENING")

    def pause_listening(self):
        self.is_paused = True
        logger.info(f"[CALL] Session {self.session_id}: AI listening paused.")

    def resume_listening(self):
        self.is_paused = False
        logger.info(f"[CALL] Session {self.session_id}: AI listening resumed.")

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

    async def end_call(self):
        self.call_state = CallState.CALL_ENDING
        logger.info(f"[CALL] Session {self.session_id} ending call...")

        if self.streaming_session and self.streaming_session.is_connected:
            try:
                await self.streaming_session.send_flush()
                await asyncio.sleep(0.3)
                await self.streaming_session.close()
            except Exception as e:
                logger.warning(f"[ASR] [SARVAM] Error during session flush/close: {e}")

        # If offline/demo mode, finalize any remaining buffer
        if self.is_demo and len(self.utterance_audio_buffer) >= 1600:
            await self._finalize_mock_utterance()

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
        VAD analysis, and streaming to Sarvam Realtime WebSocket.
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

        # When on hold or listening is paused, do not accumulate or stream audio
        if self.call_state == CallState.OPERATOR_HOLD or self.is_paused:
            return events_to_broadcast

        # Buffer raw audio for session archive
        self.audio_buffer.extend(pcm16_bytes)

        # Stream directly to Sarvam Realtime WebSocket if connected
        if self.streaming_session and self.streaming_session.is_connected:
            await self.streaming_session.send_audio_chunk(pcm16_bytes)
            return events_to_broadcast

        # In offline / demo mode, operate with local VAD & mock utterance segmentation
        if self.is_demo or isinstance(speech_adapter.provider, MockSpeechProvider):
            self.utterance_audio_buffer.extend(pcm16_bytes)
            energy = self.compute_frame_energy(pcm16_bytes)
            self.noise_floor = 0.95 * self.noise_floor + 0.05 * min(energy, 0.05)
            attack_thresh = max(0.025, self.noise_floor * 2.5)

            if energy >= attack_thresh:
                self.last_speech_at = now
                self._accumulated_silence_ms = 0.0
                if not self.is_voice_active:
                    self.is_voice_active = True
                    self.call_state = CallState.SPEAKING
                    events_to_broadcast.append({
                        "event": "vad_started",
                        "type": "vad_event",
                        "is_speech": True,
                        "vad_state": "SPEAKING",
                        "data": {"session_id": self.session_id, "call_state": self.call_state.value, "energy": round(energy, 4)}
                    })
            else:
                frame_ms = len(pcm16_bytes) / 32.0
                self._accumulated_silence_ms += frame_ms
                silence_ms = max((now - self.last_speech_at) * 1000.0 if self.last_speech_at > 0 else 0, self._accumulated_silence_ms)

                if self.is_voice_active and silence_ms >= settings.VAD_MIN_SPEECH_MS:
                    self.is_voice_active = False
                    self.call_state = CallState.SILENCE_DETECTED
                    events_to_broadcast.append({
                        "event": "vad_stopped",
                        "type": "vad_event",
                        "is_speech": False,
                        "vad_state": "SILENCE_DETECTED",
                        "data": {"session_id": self.session_id, "call_state": self.call_state.value, "silence_ms": int(silence_ms)}
                    })

                if silence_ms >= settings.VAD_UTTERANCE_END_SILENCE_MS and len(self.utterance_audio_buffer) >= 3200:
                    self._accumulated_silence_ms = 0.0
                    finalized_events = await self._finalize_mock_utterance()
                    events_to_broadcast.extend(finalized_events)

        return events_to_broadcast

    async def _finalize_mock_utterance(self) -> List[Dict[str, Any]]:
        """Used exclusively in demo/offline mode for mock utterance finalization."""
        events = []
        if len(self.utterance_audio_buffer) < 1600:
            self.utterance_audio_buffer.clear()
            self.call_state = CallState.LISTENING
            return events

        wav_io = io.BytesIO()
        with wave.open(wav_io, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(self.utterance_audio_buffer)
        wav_bytes = wav_io.getvalue()
        self.utterance_audio_buffer.clear()

        try:
            res = await speech_adapter.transcribe(audio_bytes=wav_bytes, language=self.language)
            native_text = res.get("native_transcript", "").strip()
            confidence = float(res.get("asr_confidence", 0.95))
            if native_text:
                sub_events = await self._handle_final_utterance(native_text, confidence)
                events.extend(sub_events)
        except Exception as e:
            logger.error(f"[ASR] [MOCK] Error finalizing utterance: {e}")

        self.call_state = CallState.LISTENING
        events.append({
            "event": "connection_state",
            "type": "state_change",
            "state": self.call_state.value,
            "data": {"session_id": self.session_id, "call_state": self.call_state.value}
        })
        return events

    async def broadcast(self, event_data: Dict[str, Any]):
        """Broadcasts event payload to all attached WebSockets for this session."""
        if not self.active_websockets:
            return

        dead_sockets = set()
        for ws in self.active_websockets:
            try:
                await ws.send_json(event_data)
            except Exception as e:
                logger.warning(f"[WS] Failed to send to socket in session {self.session_id}: {e}")
                dead_sockets.add(ws)

        for ws in dead_sockets:
            self.active_websockets.discard(ws)


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

        # Initialize streaming provider if not already running
        asyncio.create_task(session.init_streaming_provider())

        # Send initial session state
        await websocket.send_json({
            "event": "session_started",
            "type": "session_started",
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
        if session:
            await session.broadcast(event_data)


helpline_manager = HelplineCallManager()
