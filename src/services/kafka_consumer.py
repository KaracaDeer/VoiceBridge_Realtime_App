"""
Kafka consumer service for processing audio data and transcription results.
"""
import asyncio
import json
import logging
from typing import Any, Callable, Dict, Optional

from kafka import KafkaConsumer as KafkaConsumerClient
from kafka.errors import KafkaError

from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KafkaConsumer:
    """Kafka consumer for audio processing and transcription results."""

    def __init__(self):
        self.consumer: Optional[KafkaConsumerClient] = None
        self.is_connected_flag = False
        self.consuming = False
        self.audio_handlers: list[Callable] = []
        self.transcription_handlers: list[Callable] = []

    async def start(self):
        """Initialize and start the Kafka consumer."""
        try:
            self.consumer = KafkaConsumerClient(
                settings.kafka_audio_topic,
                settings.kafka_transcription_topic,
                bootstrap_servers=settings.kafka_bootstrap_servers,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                key_deserializer=lambda k: k.decode("utf-8") if k else None,
                group_id="voicebridge_consumer_group",
                auto_offset_reset="latest",
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000,
            )

            self.is_connected_flag = True
            logger.info("Kafka consumer started successfully")

        except Exception as e:
            logger.error(f"Failed to start Kafka consumer: {e}")
            self.is_connected_flag = False
            raise

    async def stop(self):
        """Stop the Kafka consumer."""
        try:
            self.consuming = False
            if self.consumer:
                self.consumer.close()
                self.is_connected_flag = False
                logger.info("Kafka consumer stopped")
        except Exception as e:
            logger.error(f"Error stopping Kafka consumer: {e}")

    def is_connected(self) -> bool:
        """Check if consumer is connected."""
        return self.is_connected_flag

    def add_audio_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """Add handler for audio messages."""
        self.audio_handlers.append(handler)

    def add_transcription_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """Add handler for transcription result messages."""
        self.transcription_handlers.append(handler)

    async def start_consuming(self):
        """Start consuming messages from Kafka topics."""
        if not self.consumer or not self.is_connected_flag:
            logger.error("Kafka consumer not connected")
            return

        self.consuming = True
        logger.info("Started consuming Kafka messages")

        try:
            for message in self.consumer:
                if not self.consuming:
                    break

                try:
                    await self._process_message(message)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue

        except KafkaError as e:
            logger.error(f"Kafka consumer error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in consumer: {e}")
        finally:
            logger.info("Stopped consuming Kafka messages")

    async def _process_message(self, message):
        """Process incoming Kafka message."""
        try:
            topic = message.topic
            value = message.value
            key = message.key

            logger.debug(f"Received message from topic {topic}: key={key}")

            if topic == settings.kafka_audio_topic:
                await self._handle_audio_message(value)
            elif topic == settings.kafka_transcription_topic:
                await self._handle_transcription_message(value)
            else:
                logger.warning(f"Unknown topic: {topic}")

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def _handle_audio_message(self, message_data: Dict[str, Any]):
        """Handle audio processing messages."""
        try:
            message_type = message_data.get("type")
            data = message_data.get("data", {})

            if message_type == "audio_file":
                # Handle file upload audio
                await self._process_audio_file(data)
            elif message_type == "audio_stream":
                # Handle real-time audio stream
                await self._process_audio_stream(data)
            else:
                logger.warning(f"Unknown audio message type: {message_type}")

        except Exception as e:
            logger.error(f"Error handling audio message: {e}")

    async def _handle_transcription_message(self, message_data: Dict[str, Any]):
        """Handle transcription result messages."""
        try:
            message_type = message_data.get("type")
            data = message_data.get("data", {})

            if message_type == "transcription_result":
                # Notify transcription handlers
                for handler in self.transcription_handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(data)
                        else:
                            handler(data)
                    except Exception as e:
                        logger.error(f"Error in transcription handler: {e}")
            else:
                logger.warning(f"Unknown transcription message type: {message_type}")

        except Exception as e:
            logger.error(f"Error handling transcription message: {e}")

    async def _process_audio_file(self, audio_data: Dict[str, Any]):
        """Process audio file data."""
        try:
            # Notify audio handlers
            for handler in self.audio_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(audio_data)
                    else:
                        handler(audio_data)
                except Exception as e:
                    logger.error(f"Error in audio handler: {e}")

        except Exception as e:
            logger.error(f"Error processing audio file: {e}")

    async def _process_audio_stream(self, audio_data: Dict[str, Any]):
        """Process real-time audio stream data."""
        try:
            # Notify audio handlers for real-time processing
            for handler in self.audio_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(audio_data)
                    else:
                        handler(audio_data)
                except Exception as e:
                    logger.error(f"Error in audio stream handler: {e}")

        except Exception as e:
            logger.error(f"Error processing audio stream: {e}")

    async def consume_forever(self):
        """Consume messages forever (blocking)."""
        while self.consuming:
            try:
                await self.start_consuming()
                if self.consuming:
                    # If we exit consuming loop but still should be consuming, wait a bit
                    await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error in consume_forever: {e}")
                await asyncio.sleep(5)  # Wait before retrying
