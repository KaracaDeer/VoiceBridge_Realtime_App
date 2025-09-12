"""
Kafka producer service for sending audio data to processing queues.
"""
import json
import logging
from typing import Any, Dict, Optional

from kafka import KafkaProducer as KafkaProducerClient
from kafka.errors import KafkaError

from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KafkaProducer:
    """Kafka producer for audio streaming."""

    def __init__(self):
        self.producer: Optional[KafkaProducerClient] = None
        self.is_connected_flag = False

    async def start(self):
        """Initialize and start the Kafka producer."""
        try:
            self.producer = KafkaProducerClient(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",  # Wait for all replicas to acknowledge
                retries=3,
                retry_backoff_ms=100,
                request_timeout_ms=30000,
                max_block_ms=10000,
            )

            # Test connection
            self.producer.flush(timeout=10)
            self.is_connected_flag = True
            logger.info("Kafka producer started successfully")

        except Exception as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            self.is_connected_flag = False
            raise

    async def stop(self):
        """Stop the Kafka producer."""
        try:
            if self.producer:
                self.producer.flush(timeout=10)
                self.producer.close()
                self.is_connected_flag = False
                logger.info("Kafka producer stopped")
        except Exception as e:
            logger.error(f"Error stopping Kafka producer: {e}")

    def is_connected(self) -> bool:
        """Check if producer is connected."""
        return self.is_connected_flag

    async def send_audio(self, audio_data: Dict[str, Any]) -> bool:
        """
        Send audio file data to Kafka for processing.

        Args:
            audio_data: Dictionary containing audio file information

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.producer or not self.is_connected_flag:
            logger.error("Kafka producer not connected")
            return False

        try:
            # Prepare message
            message = {
                "type": "audio_file",
                "data": audio_data,
                "timestamp": self._get_timestamp(),
            }

            # Send to audio processing topic
            future = self.producer.send(
                settings.kafka_audio_topic,
                value=message,
                key=audio_data.get("filename", "unknown"),
            )

            # Wait for confirmation
            record_metadata = future.get(timeout=10)

            logger.info(
                f"Audio sent to Kafka: topic={record_metadata.topic}, "
                f"partition={record_metadata.partition}, offset={record_metadata.offset}"
            )

            return True

        except KafkaError as e:
            logger.error(f"Kafka error sending audio: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending audio to Kafka: {e}")
            return False

    async def send_audio_stream(self, audio_data: Dict[str, Any]) -> bool:
        """
        Send real-time audio stream data to Kafka.

        Args:
            audio_data: Dictionary containing real-time audio stream information

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.producer or not self.is_connected_flag:
            logger.error("Kafka producer not connected")
            return False

        try:
            # Prepare message for real-time stream
            message = {
                "type": "audio_stream",
                "data": audio_data,
                "timestamp": self._get_timestamp(),
            }

            # Send to audio stream topic
            self.producer.send(
                settings.kafka_audio_topic,
                value=message,
                key=audio_data.get("client_id", "unknown"),
            )

            # Don't wait for confirmation in real-time scenarios for better performance
            # The future will be handled asynchronously

            logger.debug(f"Audio stream sent to Kafka for client: {audio_data.get('client_id')}")
            return True

        except KafkaError as e:
            logger.error(f"Kafka error sending audio stream: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending audio stream to Kafka: {e}")
            return False

    async def send_transcription_result(self, result: Dict[str, Any]) -> bool:
        """
        Send transcription result to Kafka.

        Args:
            result: Dictionary containing transcription results

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.producer or not self.is_connected_flag:
            logger.error("Kafka producer not connected")
            return False

        try:
            # Prepare message
            message = {
                "type": "transcription_result",
                "data": result,
                "timestamp": self._get_timestamp(),
            }

            # Send to transcription results topic
            future = self.producer.send(
                settings.kafka_transcription_topic,
                value=message,
                key=result.get("client_id", result.get("task_id", "unknown")),
            )

            # Wait for confirmation
            record_metadata = future.get(timeout=10)

            logger.info(
                f"Transcription result sent to Kafka: topic={record_metadata.topic}, "
                f"partition={record_metadata.partition}, offset={record_metadata.offset}"
            )

            return True

        except KafkaError as e:
            logger.error(f"Kafka error sending transcription result: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending transcription result to Kafka: {e}")
            return False

    def _get_timestamp(self) -> float:
        """Get current timestamp."""
        import time

        return time.time()
