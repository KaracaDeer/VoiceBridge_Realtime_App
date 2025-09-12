"""
Encryption service for VoiceBridge API
Handles AES-256 encryption and decryption of audio files and sensitive data
"""
import base64
import logging
import os
from typing import Tuple

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from config import settings

logger = logging.getLogger(__name__)


class EncryptionService:
    """Service for encrypting and decrypting audio files and sensitive data"""

    def __init__(self):
        self.encryption_key = self._derive_key(settings.encryption_key)
        self.cipher_suite = Fernet(self.encryption_key)

    def _derive_key(self, password: str) -> bytes:
        """Derive a key from password using PBKDF2"""
        # Convert password to bytes
        password_bytes = password.encode("utf-8")

        # Generate a salt (in production, store this securely)
        salt = b"voicebridge_salt_2024"  # In production, use a random salt per encryption

        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key

    def encrypt_audio_file(self, audio_data: bytes, filename: str = None) -> Tuple[bytes, str]:
        """
        Encrypt audio file data using AES-256

        Args:
            audio_data: Raw audio file bytes
            filename: Original filename (optional)

        Returns:
            Tuple of (encrypted_data, metadata_json)
        """
        try:
            # Encrypt the audio data
            encrypted_data = self.cipher_suite.encrypt(audio_data)

            # Create metadata
            import json
            import uuid

            metadata = {
                "key_id": str(uuid.uuid4()),
                "filename": filename,
                "original_size": len(audio_data),
                "encrypted_size": len(encrypted_data),
                "encryption_method": "AES-256",
                "timestamp": str(os.path.getctime(filename) if filename and os.path.exists(filename) else None),
            }

            metadata_json = json.dumps(metadata)

            logger.info(f"Encrypted audio file: {filename}, size: {len(audio_data)} -> {len(encrypted_data)} bytes")
            return encrypted_data, metadata_json

        except Exception as e:
            logger.error(f"Error encrypting audio file {filename}: {e}")
            raise Exception(f"Failed to encrypt audio file: {str(e)}")

    def decrypt_audio_file(self, encrypted_data: bytes, metadata_json: str = None) -> Tuple[bytes, dict]:
        """
        Decrypt audio file data

        Args:
            encrypted_data: Encrypted audio data
            metadata_json: JSON string containing metadata

        Returns:
            Tuple of (decrypted_data, metadata_dict)
        """
        try:
            # Decrypt the data
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)

            # Parse metadata if provided
            metadata = {}
            if metadata_json:
                import json

                metadata = json.loads(metadata_json)

            logger.info(f"Decrypted audio file, size: {len(encrypted_data)} -> {len(decrypted_data)} bytes")
            return decrypted_data, metadata

        except Exception as e:
            logger.error(f"Error decrypting audio file: {e}")
            raise Exception(f"Failed to decrypt audio file: {str(e)}")

    def encrypt_text(self, text: str) -> str:
        """
        Encrypt text data

        Args:
            text: Text to encrypt

        Returns:
            Base64 encoded encrypted text
        """
        try:
            text_bytes = text.encode("utf-8")
            encrypted_data = self.cipher_suite.encrypt(text_bytes)
            return base64.urlsafe_b64encode(encrypted_data).decode("utf-8")
        except Exception as e:
            logger.error(f"Error encrypting text: {e}")
            raise Exception(f"Failed to encrypt text: {str(e)}")

    def decrypt_text(self, encrypted_text: str) -> str:
        """
        Decrypt text data

        Args:
            encrypted_text: Base64 encoded encrypted text

        Returns:
            Decrypted text
        """
        try:
            encrypted_data = base64.urlsafe_b64decode(encrypted_text.encode("utf-8"))
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            return decrypted_data.decode("utf-8")
        except Exception as e:
            logger.error(f"Error decrypting text: {e}")
            raise Exception(f"Failed to decrypt text: {str(e)}")

    def encrypt_file_to_storage(self, file_path: str, output_path: str) -> str:
        """
        Encrypt a file and save to storage

        Args:
            file_path: Path to original file
            output_path: Path to save encrypted file

        Returns:
            Path to encrypted file
        """
        try:
            # Read original file
            with open(file_path, "rb") as f:
                file_data = f.read()

            # Encrypt the file
            encrypted_data, metadata_json = self.encrypt_audio_file(file_data, file_path)

            # Save encrypted file
            with open(output_path, "wb") as f:
                f.write(encrypted_data)

            # Save metadata
            metadata_path = output_path + ".meta"
            with open(metadata_path, "w") as f:
                f.write(metadata_json)

            logger.info(f"Encrypted file saved: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error encrypting file {file_path}: {e}")
            raise Exception(f"Failed to encrypt file: {str(e)}")

    def decrypt_file_from_storage(self, encrypted_file_path: str, output_path: str) -> str:
        """
        Decrypt a file from storage

        Args:
            encrypted_file_path: Path to encrypted file
            output_path: Path to save decrypted file

        Returns:
            Path to decrypted file
        """
        try:
            # Read encrypted file
            with open(encrypted_file_path, "rb") as f:
                encrypted_data = f.read()

            # Read metadata
            metadata_path = encrypted_file_path + ".meta"
            metadata_json = ""
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    metadata_json = f.read()

            # Decrypt the file
            decrypted_data, metadata = self.decrypt_audio_file(encrypted_data, metadata_json)

            # Save decrypted file
            with open(output_path, "wb") as f:
                f.write(decrypted_data)

            logger.info(f"Decrypted file saved: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error decrypting file {encrypted_file_path}: {e}")
            raise Exception(f"Failed to decrypt file: {str(e)}")

    def get_encryption_info(self) -> dict:
        """Get information about the encryption service"""
        return {
            "encryption_method": "AES-256",
            "key_derivation": "PBKDF2-HMAC-SHA256",
            "iterations": 100000,
            "status": "active",
        }


# Global encryption service instance
encryption_service = EncryptionService()
