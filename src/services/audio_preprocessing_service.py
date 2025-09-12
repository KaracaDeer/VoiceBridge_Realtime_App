"""
Audio Preprocessing Service
Audio data preprocessing service using sklearn and librosa
"""
import io
import logging
from typing import Any, Dict, List

import librosa
import numpy as np
import soundfile as sf
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler, StandardScaler

logger = logging.getLogger(__name__)


class AudioPreprocessingService:
    """Audio data preprocessing service"""

    def __init__(self):
        """Initialize preprocessing service"""
        self.scaler = StandardScaler()
        self.minmax_scaler = MinMaxScaler()
        self.pca = PCA(n_components=13)  # 13 components for MFCC
        self.is_fitted = False

        logger.info("AudioPreprocessingService initialized")

    def extract_mfcc_features(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000,
        n_mfcc: int = 13,
        n_fft: int = 2048,
        hop_length: int = 512,
    ) -> np.ndarray:
        """
        Extract MFCC (Mel-frequency cepstral coefficients) features

        Args:
            audio_data: Audio data
            sample_rate: Sample rate
            n_mfcc: Number of MFCC coefficients
            n_fft: FFT window size
            hop_length: Hop length

        Returns:
            MFCC feature matrix
        """
        try:
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(
                y=audio_data,
                sr=sample_rate,
                n_mfcc=n_mfcc,
                n_fft=n_fft,
                hop_length=hop_length,
            )

            # Add delta and delta-delta features
            mfcc_delta = librosa.feature.delta(mfccs)
            mfcc_delta2 = librosa.feature.delta(mfccs, order=2)

            # Combine features
            features = np.vstack([mfccs, mfcc_delta, mfcc_delta2])

            logger.info(f"MFCC features extracted: {features.shape}")
            return features

        except Exception as e:
            logger.error(f"MFCC extraction failed: {e}")
            raise

    def extract_spectral_features(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Dict[str, np.ndarray]:
        """
        Extract spectral features

        Args:
            audio_data: Audio data
            sample_rate: Sample rate

        Returns:
            Dictionary of spectral features
        """
        try:
            features = {}

            # Spectral centroid
            features["spectral_centroid"] = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]

            # Spectral rolloff
            features["spectral_rolloff"] = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]

            # Spectral bandwidth
            features["spectral_bandwidth"] = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)[0]

            # Zero crossing rate
            features["zero_crossing_rate"] = librosa.feature.zero_crossing_rate(audio_data)[0]

            # Chroma features
            features["chroma"] = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)

            # Tonnetz features
            features["tonnetz"] = librosa.feature.tonnetz(y=audio_data, sr=sample_rate)

            logger.info("Spectral features extracted successfully")
            return features

        except Exception as e:
            logger.error(f"Spectral feature extraction failed: {e}")
            raise

    def normalize_audio(self, audio_data: np.ndarray, method: str = "standard") -> np.ndarray:
        """
        Normalize audio data

        Args:
            audio_data: Audio data
            method: Normalization method ("standard", "minmax", "peak")

        Returns:
            Normalized audio data
        """
        try:
            if method == "standard":
                # Z-score normalization
                normalized = (audio_data - np.mean(audio_data)) / np.std(audio_data)
            elif method == "minmax":
                # Min-Max normalization
                normalized = (audio_data - np.min(audio_data)) / (np.max(audio_data) - np.min(audio_data))
            elif method == "peak":
                # Peak normalization
                normalized = audio_data / np.max(np.abs(audio_data))
            else:
                raise ValueError(f"Unknown normalization method: {method}")

            logger.info(f"Audio normalized using {method} method")
            return normalized

        except Exception as e:
            logger.error(f"Audio normalization failed: {e}")
            raise

    def preprocess_audio_bytes(self, audio_bytes: bytes, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Preprocess raw audio data

        Args:
            audio_bytes: Raw audio data
            sample_rate: Target sample rate

        Returns:
            Preprocessed features
        """
        try:
            # Convert audio data to numpy array
            audio_array, original_sr = sf.read(io.BytesIO(audio_bytes))

            # Convert to mono
            if len(audio_array.shape) > 1:
                audio_array = np.mean(audio_array, axis=1)

            # Adjust sample rate
            if original_sr != sample_rate:
                audio_array = librosa.resample(audio_array, orig_sr=original_sr, target_sr=sample_rate)

            # Normalize
            audio_normalized = self.normalize_audio(audio_array, method="peak")

            # Extract MFCC features
            mfcc_features = self.extract_mfcc_features(audio_normalized, sample_rate)

            # Extract spectral features
            spectral_features = self.extract_spectral_features(audio_normalized, sample_rate)

            # Calculate feature statistics
            feature_stats = self._calculate_feature_statistics(mfcc_features, spectral_features)

            result = {
                "audio_data": audio_normalized,
                "sample_rate": sample_rate,
                "mfcc_features": mfcc_features,
                "spectral_features": spectral_features,
                "feature_statistics": feature_stats,
                "duration": len(audio_normalized) / sample_rate,
                "preprocessing_successful": True,
            }

            logger.info(
                f"Audio preprocessing completed: {len(audio_normalized)} samples, {result['duration']:.2f}s duration"
            )
            return result

        except Exception as e:
            logger.error(f"Audio preprocessing failed: {e}")
            return {"error": str(e), "preprocessing_successful": False}

    def _calculate_feature_statistics(
        self, mfcc_features: np.ndarray, spectral_features: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """Calculate feature statistics"""
        try:
            stats = {}

            # MFCC statistics
            stats["mfcc_mean"] = np.mean(mfcc_features, axis=1)
            stats["mfcc_std"] = np.std(mfcc_features, axis=1)
            stats["mfcc_min"] = np.min(mfcc_features, axis=1)
            stats["mfcc_max"] = np.max(mfcc_features, axis=1)

            # Spectral feature statistics
            for feature_name, feature_data in spectral_features.items():
                if feature_data.ndim == 1:
                    stats[f"{feature_name}_mean"] = np.mean(feature_data)
                    stats[f"{feature_name}_std"] = np.std(feature_data)
                    stats[f"{feature_name}_min"] = np.min(feature_data)
                    stats[f"{feature_name}_max"] = np.max(feature_data)
                else:
                    stats[f"{feature_name}_mean"] = np.mean(feature_data, axis=1)
                    stats[f"{feature_name}_std"] = np.std(feature_data, axis=1)

            return stats

        except Exception as e:
            logger.error(f"Feature statistics calculation failed: {e}")
            return {}

    def fit_scalers(self, feature_data: List[np.ndarray]):
        """Fit scalers with training data"""
        try:
            # Combine all feature data
            all_features = np.concatenate(feature_data, axis=1)

            # Fit scalers
            self.scaler.fit(all_features.T)
            self.minmax_scaler.fit(all_features.T)
            self.pca.fit(all_features.T)

            self.is_fitted = True
            logger.info("Scalers fitted successfully")

        except Exception as e:
            logger.error(f"Scaler fitting failed: {e}")
            raise

    def transform_features(self, features: np.ndarray, method: str = "standard") -> np.ndarray:
        """Transform features"""
        if not self.is_fitted:
            logger.warning("Scalers not fitted, returning original features")
            return features

        try:
            if method == "standard":
                return self.scaler.transform(features.T).T
            elif method == "minmax":
                return self.minmax_scaler.transform(features.T).T
            elif method == "pca":
                return self.pca.transform(features.T).T
            else:
                raise ValueError(f"Unknown transform method: {method}")

        except Exception as e:
            logger.error(f"Feature transformation failed: {e}")
            return features


# Global service instance
_preprocessing_service = None


def get_preprocessing_service() -> AudioPreprocessingService:
    """Get preprocessing service instance"""
    global _preprocessing_service
    if _preprocessing_service is None:
        _preprocessing_service = AudioPreprocessingService()
    return _preprocessing_service
