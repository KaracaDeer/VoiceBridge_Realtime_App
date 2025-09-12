"""
Kafka streaming service for VoiceBridge API
Handles real-time audio streaming and processing with Kafka
"""
import asyncio
import json
import logging
import time
import uuid
from typing import Any, Dict, Optional

try:
    from aiokafka import AIOKafkaConsumer, AIOKafkaProducer  # type: ignore
    from aiokafka.errors import KafkaError  # type: ignore

    KAFKA_AVAILABLE = True
except Exception:  # ImportError or environment issues
    AIOKafkaProducer = None  # type: ignore
    AIOKafkaConsumer = None  # type: ignore
    KafkaError = Exception  # type: ignore
    KAFKA_AVAILABLE = False
import io

import avro.schema
from avro.io import BinaryDecoder, BinaryEncoder, DatumReader, DatumWriter

from config import settings
from src.services.model_monitoring_service import model_monitoring_service
from src.services.openai_whisper_service import get_openai_whisper_service

logger = logging.getLogger(__name__)

# Avro schemas for Kafka messages
AUDIO_CHUNK_SCHEMA = {
    "type": "record",
    "name": "AudioChunk",
    "fields": [
        {"name": "session_id", "type": "string"},
        {"name": "user_id", "type": "string"},
        {"name": "chunk_id", "type": "string"},
        {"name": "audio_data", "type": "bytes"},
        {"name": "sample_rate", "type": "int"},
        {"name": "channels", "type": "int"},
        {"name": "format", "type": "string"},
        {"name": "timestamp", "type": "long"},
        {"name": "language", "type": "string"},
        {"name": "chunk_index", "type": "int"},
        {"name": "is_final", "type": "boolean"},
    ],
}

TRANSCRIPTION_RESULT_SCHEMA = {
    "type": "record",
    "name": "TranscriptionResult",
    "fields": [
        {"name": "session_id", "type": "string"},
        {"name": "user_id", "type": "string"},
        {"name": "chunk_id", "type": "string"},
        {"name": "text", "type": "string"},
        {"name": "confidence", "type": "float"},
        {"name": "language", "type": "string"},
        {"name": "timestamp", "type": "long"},
        {"name": "processing_time", "type": "float"},
        {"name": "model_name", "type": "string"},
        {"name": "status", "type": "string"},
        {"name": "error_message", "type": ["null", "string"]},
    ],
}


class KafkaStreamService:
    """Service for Kafka-based audio streaming and processing"""

    def __init__(self):
        self.bootstrap_servers = settings.kafka_bootstrap_servers
        self.audio_topic = settings.kafka_audio_topic
        self.transcription_topic = settings.kafka_transcription_topic

        self.producer: Optional[AIOKafkaProducer] = None
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.kafka_available: bool = KAFKA_AVAILABLE

        self.whisper_service = get_openai_whisper_service(settings.openai_api_key)

        # Session management
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_lock = asyncio.Lock()

        # Avro schemas
        self.audio_schema = avro.schema.parse(json.dumps(AUDIO_CHUNK_SCHEMA))
        self.transcription_schema = avro.schema.parse(json.dumps(TRANSCRIPTION_RESULT_SCHEMA))

        # Processing stats
        self.processing_stats = {
            "total_chunks_processed": 0,
            "successful_transcriptions": 0,
            "failed_transcriptions": 0,
            "average_processing_time": 0.0,
            "total_audio_duration": 0.0,
        }

    async def start(self):
        """Start Kafka producer and consumer"""
        try:
            if not self.kafka_available:
                logger.warning("Kafka not available. Running in direct-processing (mock) mode.")
                return False
            # Start producer
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=self._serialize_audio_chunk,
                key_serializer=lambda x: x.encode("utf-8") if x else None,
                compression_type="gzip",
                retry_backoff_ms=100,
                request_timeout_ms=30000,
            )
            await self.producer.start()
            logger.info("Kafka producer started")

            # Start consumer
            self.consumer = AIOKafkaConsumer(
                self.audio_topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id="voicebridge-transcription-group",
                value_deserializer=self._deserialize_audio_chunk,
                key_deserializer=lambda x: x.decode("utf-8") if x else None,
                auto_offset_reset="latest",
                enable_auto_commit=True,
                max_poll_records=10,
            )
            await self.consumer.start()
            logger.info("Kafka consumer started")

            # Start processing loop
            asyncio.create_task(self._process_audio_streams())

            return True

        except Exception as e:
            logger.error(f"Failed to start Kafka service: {e}")
            return False

    async def stop(self):
        """Stop Kafka producer and consumer"""
        try:
            if self.producer:
                await self.producer.stop()
                logger.info("Kafka producer stopped")

            if self.consumer:
                await self.consumer.stop()
                logger.info("Kafka consumer stopped")

        except Exception as e:
            logger.error(f"Error stopping Kafka service: {e}")

    def _serialize_audio_chunk(self, data: Dict[str, Any]) -> bytes:
        """Serialize audio chunk data to Avro format"""
        try:
            writer = DatumWriter(self.audio_schema)
            bytes_writer = io.BytesIO()
            encoder = BinaryEncoder(bytes_writer)
            writer.write(data, encoder)
            return bytes_writer.getvalue()
        except Exception as e:
            logger.error(f"Error serializing audio chunk: {e}")
            return b""

    def _deserialize_audio_chunk(self, data: bytes) -> Dict[str, Any]:
        """Deserialize audio chunk data from Avro format"""
        try:
            reader = DatumReader(self.audio_schema)
            bytes_reader = io.BytesIO(data)
            decoder = BinaryDecoder(bytes_reader)
            result = reader.read(decoder)
            return dict(result) if result is not None else {}
        except Exception as e:
            logger.error(f"Error deserializing audio chunk: {e}")
            return {}

    def _serialize_transcription_result(self, data: Dict[str, Any]) -> bytes:
        """Serialize transcription result to Avro format"""
        try:
            writer = DatumWriter(self.transcription_schema)
            bytes_writer = io.BytesIO()
            encoder = BinaryEncoder(bytes_writer)
            writer.write(data, encoder)
            return bytes_writer.getvalue()
        except Exception as e:
            logger.error(f"Error serializing transcription result: {e}")
            return b""

    async def send_audio_chunk(
        self,
        session_id: str,
        user_id: str,
        audio_data: bytes,
        sample_rate: int = 16000,
        channels: int = 1,
        format: str = "wav",
        language: str = "en",
        chunk_index: int = 0,
        is_final: bool = False,
    ) -> bool:
        """Send audio chunk to Kafka for processing"""
        try:
            if not self.producer:
                # Fallback: process directly without Kafka
                logger.info("Kafka producer not started. Processing audio chunk directly (fallback mode).")
                chunk_id = str(uuid.uuid4())
                timestamp = int(time.time() * 1000)
                audio_chunk_data = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "chunk_id": chunk_id,
                    "audio_data": audio_data,
                    "sample_rate": sample_rate,
                    "channels": channels,
                    "format": format,
                    "timestamp": timestamp,
                    "language": language,
                    "chunk_index": chunk_index,
                    "is_final": is_final,
                }
                await self._process_audio_chunk(audio_chunk_data)
                return True

            chunk_id = str(uuid.uuid4())
            timestamp = int(time.time() * 1000)

            audio_chunk_data = {
                "session_id": session_id,
                "user_id": user_id,
                "chunk_id": chunk_id,
                "audio_data": audio_data,
                "sample_rate": sample_rate,
                "channels": channels,
                "format": format,
                "timestamp": timestamp,
                "language": language,
                "chunk_index": chunk_index,
                "is_final": is_final,
            }

            # Send to Kafka
            await self.producer.send(self.audio_topic, key=session_id, value=audio_chunk_data)

            # Update session info
            async with self.session_lock:
                if session_id not in self.active_sessions:
                    self.active_sessions[session_id] = {
                        "user_id": user_id,
                        "start_time": time.time(),
                        "chunks_sent": 0,
                        "chunks_processed": 0,
                        "total_audio_duration": 0.0,
                    }

                self.active_sessions[session_id]["chunks_sent"] += 1

            logger.debug(f"Sent audio chunk {chunk_id} for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error sending audio chunk: {e}")
            return False

    async def _process_audio_streams(self):
        """Process audio streams from Kafka"""
        if not self.consumer:
            logger.warning("Kafka consumer not started. Skipping stream processing loop.")
            return
        logger.info("Started audio stream processing")

        try:
            async for message in self.consumer:
                try:
                    audio_chunk = message.value
                    if not audio_chunk:
                        continue

                    # Process audio chunk
                    await self._process_audio_chunk(audio_chunk)

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error in audio stream processing: {e}")

    async def _process_audio_chunk(self, audio_chunk: Dict[str, Any]):
        """Process a single audio chunk"""
        session_id = audio_chunk["session_id"]
        user_id = audio_chunk["user_id"]
        chunk_id = audio_chunk["chunk_id"]
        audio_data = audio_chunk["audio_data"]
        language = audio_chunk.get("language", settings.default_language)

        start_time = time.time()

        try:
            # Process audio with Whisper
            result = await self.whisper_service.transcribe_audio_bytes(audio_data, language=language)

            processing_time = time.time() - start_time

            # Record metrics
            model_monitoring_service.record_model_performance(
                model_name="whisper_kafka",
                accuracy=result.get("confidence", 0.0),
                confidence=result.get("confidence", 0.0),
                processing_time=processing_time,
                error_occurred="error" in result,
            )

            # Update processing stats
            self.processing_stats["total_chunks_processed"] += 1
            self.processing_stats["total_audio_duration"] += processing_time

            if "error" not in result:
                self.processing_stats["successful_transcriptions"] += 1
            else:
                self.processing_stats["failed_transcriptions"] += 1

            # Calculate average processing time
            total_processed = self.processing_stats["total_chunks_processed"]
            if total_processed > 0:
                self.processing_stats["average_processing_time"] = (
                    self.processing_stats["total_audio_duration"] / total_processed
                )

            # Create transcription result
            transcription_result = {
                "session_id": session_id,
                "user_id": user_id,
                "chunk_id": chunk_id,
                "text": result.get("text", ""),
                "confidence": result.get("confidence", 0.0),
                "language": result.get("language", language),
                "timestamp": int(time.time() * 1000),
                "processing_time": processing_time,
                "model_name": "whisper",
                "status": "success" if "error" not in result else "error",
                "error_message": result.get("error") if "error" in result else None,
            }

            # Send transcription result to Kafka
            await self._send_transcription_result(transcription_result)

            # Update session info
            async with self.session_lock:
                if session_id in self.active_sessions:
                    self.active_sessions[session_id]["chunks_processed"] += 1
                    self.active_sessions[session_id]["total_audio_duration"] += processing_time

            logger.debug(f"Processed audio chunk {chunk_id} for session {session_id}")

        except Exception as e:
            logger.error(f"Error processing audio chunk {chunk_id}: {e}")

            # Send error result
            error_result = {
                "session_id": session_id,
                "user_id": user_id,
                "chunk_id": chunk_id,
                "text": "",
                "confidence": 0.0,
                "language": language,
                "timestamp": int(time.time() * 1000),
                "processing_time": time.time() - start_time,
                "model_name": "whisper",
                "status": "error",
                "error_message": str(e),
            }

            await self._send_transcription_result(error_result)

    async def _send_transcription_result(self, result: Dict[str, Any]):
        """Send transcription result to Kafka"""
        try:
            if not self.producer:
                return

            # Serialize result
            serialized_result = self._serialize_transcription_result(result)

            # Send to transcription topic
            await self.producer.send(
                self.transcription_topic,
                key=result["session_id"],
                value=serialized_result,
            )

            logger.debug(f"Sent transcription result for session {result['session_id']}")

        except Exception as e:
            logger.error(f"Error sending transcription result: {e}")

    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a streaming session"""
        async with self.session_lock:
            return self.active_sessions.get(session_id)

    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            **self.processing_stats,
            "active_sessions": len(self.active_sessions),
            "timestamp": int(time.time() * 1000),
        }

    async def cleanup_session(self, session_id: str):
        """Clean up a streaming session"""
        async with self.session_lock:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                logger.info(f"Cleaned up session {session_id}")


# Global Kafka stream service instance
kafka_stream_service = KafkaStreamService()
