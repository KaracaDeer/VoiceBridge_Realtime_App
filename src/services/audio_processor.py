"""
Audio Processing Service

This service handles audio file processing, validation, and preprocessing
for speech recognition. It provides:

- Audio format validation (WAV, MP3, M4A, FLAC, WebM)
- File size validation and limits
- Audio preprocessing (noise reduction, normalization)
- Sample rate conversion for ML models
- Audio quality analysis and enhancement
"""
import logging
import os
from typing import Any, Dict, List

import librosa
import numpy as np

from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioProcessor:
    """Service for processing audio files and streams."""

    def __init__(self):
        self.supported_formats = settings.supported_audio_formats.split(",")
        self.max_size_mb = settings.max_audio_size_mb
        self.target_sample_rate = settings.sample_rate

    def is_valid_audio_format(self, filename: str) -> bool:
        """
        Check if the audio file format is supported.

        Args:
            filename: Name of the audio file

        Returns:
            True if format is supported, False otherwise
        """
        if not filename:
            return False

        # Extract file extension
        _, ext = os.path.splitext(filename.lower())
        ext = ext.lstrip(".")

        return ext in self.supported_formats

    def validate_audio_size(self, content: bytes) -> bool:
        """
        Validate audio file size.

        Args:
            content: Audio file content as bytes

        Returns:
            True if size is valid, False otherwise
        """
        size_mb = len(content) / (1024 * 1024)
        return size_mb <= self.max_size_mb

    def get_audio_info(self, audio_path: str) -> Dict[str, Any]:
        """
        Get information about an audio file.

        Args:
            audio_path: Path to the audio file

        Returns:
            Dictionary with audio information
        """
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=None)

            # Calculate duration
            duration = len(y) / sr

            # Get audio properties
            info = {
                "sample_rate": sr,
                "duration": duration,
                "channels": 1 if y.ndim == 1 else y.shape[0],
                "samples": len(y),
                "dtype": str(y.dtype),
                "file_size": os.path.getsize(audio_path),
            }

            return info

        except Exception as e:
            logger.error(f"Error getting audio info: {e}")
            return {}

    def preprocess_audio(self, audio_array: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Preprocess audio for speech recognition.

        Args:
            audio_array: Raw audio data
            sample_rate: Original sample rate

        Returns:
            Preprocessed audio array
        """
        try:
            # Resample to target sample rate if needed
            if sample_rate != self.target_sample_rate:
                audio_array = librosa.resample(audio_array, orig_sr=sample_rate, target_sr=self.target_sample_rate)
                sample_rate = self.target_sample_rate

            # Convert to mono if stereo
            if audio_array.ndim > 1:
                audio_array = librosa.to_mono(audio_array)

            # Normalize audio
            audio_array = librosa.util.normalize(audio_array)

            # Remove silence from beginning and end
            audio_array, _ = librosa.effects.trim(audio_array)

            return audio_array

        except Exception as e:
            logger.error(f"Error preprocessing audio: {e}")
            return audio_array

    def detect_speech_segments(self, audio_array: np.ndarray, sample_rate: int) -> List[Dict[str, Any]]:
        """
        Detect speech segments in audio.

        Args:
            audio_array: Audio data
            sample_rate: Sample rate

        Returns:
            List of speech segments with start/end times
        """
        try:
            # Calculate RMS energy
            frame_length = int(0.025 * sample_rate)  # 25ms frames
            hop_length = int(0.010 * sample_rate)  # 10ms hop

            rms = librosa.feature.rms(y=audio_array, frame_length=frame_length, hop_length=hop_length)[0]

            # Simple voice activity detection
            threshold = np.mean(rms) * 0.5
            voice_frames = rms > threshold

            # Find speech segments
            segments = []
            in_speech = False
            start_frame = 0

            for i, is_voice in enumerate(voice_frames):
                if is_voice and not in_speech:
                    # Start of speech
                    start_frame = i
                    in_speech = True
                elif not is_voice and in_speech:
                    # End of speech
                    end_frame = i
                    start_time = start_frame * hop_length / sample_rate
                    end_time = end_frame * hop_length / sample_rate

                    if end_time - start_time > 0.1:  # Minimum 100ms segment
                        segments.append(
                            {
                                "start_time": start_time,
                                "end_time": end_time,
                                "duration": end_time - start_time,
                            }
                        )

                    in_speech = False

            # Handle case where speech continues to end
            if in_speech:
                end_time = len(voice_frames) * hop_length / sample_rate
                start_time = start_frame * hop_length / sample_rate
                if end_time - start_time > 0.1:
                    segments.append(
                        {
                            "start_time": start_time,
                            "end_time": end_time,
                            "duration": end_time - start_time,
                        }
                    )

            return segments

        except Exception as e:
            logger.error(f"Error detecting speech segments: {e}")
            return []

    def split_audio_by_segments(
        self, audio_array: np.ndarray, sample_rate: int, segments: List[Dict[str, Any]]
    ) -> List[np.ndarray]:
        """
        Split audio into segments.

        Args:
            audio_array: Audio data
            sample_rate: Sample rate
            segments: List of speech segments

        Returns:
            List of audio segments
        """
        audio_segments = []

        try:
            for segment in segments:
                start_sample = int(segment["start_time"] * sample_rate)
                end_sample = int(segment["end_time"] * sample_rate)

                segment_audio = audio_array[start_sample:end_sample]
                audio_segments.append(segment_audio)

            return audio_segments

        except Exception as e:
            logger.error(f"Error splitting audio: {e}")
            return []

    def calculate_audio_quality_metrics(self, audio_array: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """
        Calculate audio quality metrics.

        Args:
            audio_array: Audio data
            sample_rate: Sample rate

        Returns:
            Dictionary with quality metrics
        """
        try:
            # Signal-to-noise ratio (simplified)
            signal_power = np.mean(audio_array**2)
            noise_floor = np.percentile(audio_array**2, 10)
            snr = 10 * np.log10(signal_power / (noise_floor + 1e-10))

            # Dynamic range
            dynamic_range = 20 * np.log10(np.max(np.abs(audio_array)) / (np.mean(np.abs(audio_array)) + 1e-10))

            # Zero crossing rate (speech activity indicator)
            zcr = np.mean(librosa.feature.zero_crossing_rate(audio_array))

            # Spectral centroid (brightness)
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio_array, sr=sample_rate))

            return {
                "snr_db": snr,
                "dynamic_range_db": dynamic_range,
                "zero_crossing_rate": zcr,
                "spectral_centroid": spectral_centroid,
                "rms_energy": np.sqrt(np.mean(audio_array**2)),
            }

        except Exception as e:
            logger.error(f"Error calculating audio quality metrics: {e}")
            return {}
