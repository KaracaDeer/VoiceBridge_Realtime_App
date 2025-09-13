"""
Secure storage service for VoiceBridge API
Handles encrypted storage and retrieval of audio files and sensitive data
"""
import hashlib
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Tuple

# from src.database.mysql_models import get_database_manager  # Temporarily disabled
from src.services.encryption_service import encryption_service

logger = logging.getLogger(__name__)


class SecureStorageService:
    """Service for secure storage of encrypted audio files and metadata"""

    def __init__(self):
        self.storage_base_path = "secure_storage"
        self.audio_storage_path = os.path.join(self.storage_base_path, "audio")
        self.metadata_storage_path = os.path.join(self.storage_base_path, "metadata")

        # Create storage directories
        self._ensure_storage_directories()

    def _ensure_storage_directories(self):
        """Ensure storage directories exist"""
        for path in [
            self.storage_base_path,
            self.audio_storage_path,
            self.metadata_storage_path,
        ]:
            os.makedirs(path, exist_ok=True)

    def _generate_file_id(self, user_id: int, filename: str) -> str:
        """Generate unique file ID"""
        timestamp = datetime.utcnow().isoformat()
        content = f"{user_id}_{filename}_{timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _get_file_paths(self, file_id: str) -> Tuple[str, str]:
        """Get file paths for encrypted file and metadata"""
        encrypted_file_path = os.path.join(self.audio_storage_path, f"{file_id}.enc")
        metadata_file_path = os.path.join(self.metadata_storage_path, f"{file_id}.json")
        return encrypted_file_path, metadata_file_path

    def store_encrypted_audio(
        self,
        audio_data: bytes,
        user_id: int,
        filename: str,
        session_id: str = None,
        additional_metadata: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Store encrypted audio file with metadata

        Args:
            audio_data: Raw audio data
            user_id: User ID
            filename: Original filename
            session_id: Optional session ID
            additional_metadata: Additional metadata to store

        Returns:
            Dict with file information
        """
        try:
            # Generate unique file ID
            file_id = self._generate_file_id(user_id, filename)

            # Encrypt audio data
            encrypted_data, encryption_metadata = encryption_service.encrypt_audio_file(audio_data, filename)

            # Get file paths
            encrypted_file_path, metadata_file_path = self._get_file_paths(file_id)

            # Store encrypted file
            with open(encrypted_file_path, "wb") as f:
                f.write(encrypted_data)

            # Create comprehensive metadata
            metadata = {
                "file_id": file_id,
                "user_id": user_id,
                "session_id": session_id,
                "original_filename": filename,
                "file_size": len(audio_data),
                "encrypted_size": len(encrypted_data),
                "created_at": datetime.utcnow().isoformat(),
                "encryption_metadata": encryption_metadata,
                "storage_path": encrypted_file_path,
                "status": "stored",
                **(additional_metadata or {}),
            }

            # Store metadata
            with open(metadata_file_path, "w") as f:
                json.dump(metadata, f, indent=2)

            # Store in database
            self._store_file_metadata_in_db(metadata)

            logger.info(f"Stored encrypted audio file: {file_id} for user {user_id}")

            return {
                "file_id": file_id,
                "status": "stored",
                "encrypted_size": len(encrypted_data),
                "created_at": metadata["created_at"],
            }

        except Exception as e:
            logger.error(f"Error storing encrypted audio file: {e}")
            raise Exception(f"Failed to store encrypted audio file: {str(e)}")

    def retrieve_encrypted_audio(self, file_id: str, user_id: int) -> Tuple[bytes, Dict[str, Any]]:
        """
        Retrieve and decrypt audio file

        Args:
            file_id: File ID
            user_id: User ID (for authorization)

        Returns:
            Tuple of (decrypted_audio_data, metadata)
        """
        try:
            # Get file paths
            encrypted_file_path, metadata_file_path = self._get_file_paths(file_id)

            # Check if files exist
            if not os.path.exists(encrypted_file_path) or not os.path.exists(metadata_file_path):
                raise Exception("File not found")

            # Load metadata
            with open(metadata_file_path, "r") as f:
                metadata = json.load(f)

            # Check authorization
            if metadata.get("user_id") != user_id:
                raise Exception("Unauthorized access to file")

            # Read encrypted file
            with open(encrypted_file_path, "rb") as f:
                encrypted_data = f.read()

            # Decrypt audio data
            decrypted_data, _ = encryption_service.decrypt_audio_file(
                encrypted_data, metadata.get("encryption_metadata", "")
            )

            # Update access time
            metadata["last_accessed"] = datetime.utcnow().isoformat()
            with open(metadata_file_path, "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Retrieved encrypted audio file: {file_id} for user {user_id}")

            return decrypted_data, metadata

        except Exception as e:
            logger.error(f"Error retrieving encrypted audio file {file_id}: {e}")
            raise Exception(f"Failed to retrieve encrypted audio file: {str(e)}")

    def delete_encrypted_audio(self, file_id: str, user_id: int) -> bool:
        """
        Delete encrypted audio file and metadata

        Args:
            file_id: File ID
            user_id: User ID (for authorization)

        Returns:
            True if successful
        """
        try:
            # Get file paths
            encrypted_file_path, metadata_file_path = self._get_file_paths(file_id)

            # Check if metadata exists and verify authorization
            if os.path.exists(metadata_file_path):
                with open(metadata_file_path, "r") as f:
                    metadata = json.load(f)

                if metadata.get("user_id") != user_id:
                    raise Exception("Unauthorized access to file")

            # Delete files
            if os.path.exists(encrypted_file_path):
                os.remove(encrypted_file_path)

            if os.path.exists(metadata_file_path):
                os.remove(metadata_file_path)

            # Update database
            self._delete_file_metadata_from_db(file_id)

            logger.info(f"Deleted encrypted audio file: {file_id} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting encrypted audio file {file_id}: {e}")
            return False

    def list_user_files(self, user_id: int, session_id: str = None) -> list:
        """
        List encrypted files for a user

        Args:
            user_id: User ID
            session_id: Optional session ID filter

        Returns:
            List of file metadata
        """
        try:
            files = []

            # Scan metadata directory
            for filename in os.listdir(self.metadata_storage_path):
                if filename.endswith(".json"):
                    metadata_path = os.path.join(self.metadata_storage_path, filename)

                    try:
                        with open(metadata_path, "r") as f:
                            metadata = json.load(f)

                        # Filter by user and session
                        if metadata.get("user_id") == user_id:
                            if session_id is None or metadata.get("session_id") == session_id:
                                # Remove sensitive information
                                safe_metadata = {
                                    "file_id": metadata.get("file_id"),
                                    "original_filename": metadata.get("original_filename"),
                                    "file_size": metadata.get("file_size"),
                                    "created_at": metadata.get("created_at"),
                                    "last_accessed": metadata.get("last_accessed"),
                                    "status": metadata.get("status"),
                                }
                                files.append(safe_metadata)

                    except Exception as e:
                        logger.warning(f"Error reading metadata file {filename}: {e}")
                        continue

            # Sort by creation time (newest first)
            files.sort(key=lambda x: x.get("created_at", ""), reverse=True)

            return files

        except Exception as e:
            logger.error(f"Error listing user files: {e}")
            return []

    def _store_file_metadata_in_db(self, metadata: Dict[str, Any]):
        """Store file metadata in database"""
        try:
            from src.database.mysql_models import Transcription

            db_manager = get_database_manager()
            db = db_manager.get_session()

            # Create transcription record
            transcription = Transcription(
                user_id=metadata["user_id"],
                session_id=metadata.get("session_id"),
                audio_file_path=metadata["storage_path"],
                audio_size_bytes=metadata["file_size"],
                original_text="",  # Will be updated after transcription
                created_at=datetime.fromisoformat(metadata["created_at"].replace("Z", "+00:00")),
            )

            db.add(transcription)
            db.commit()
            db.refresh(transcription)

            # Update metadata with database ID
            metadata["db_id"] = transcription.id
            metadata_file_path = os.path.join(self.metadata_storage_path, f"{metadata['file_id']}.json")
            with open(metadata_file_path, "w") as f:
                json.dump(metadata, f, indent=2)

        except Exception as e:
            logger.error(f"Error storing file metadata in database: {e}")
        finally:
            if "db" in locals():
                db.close()

    def _delete_file_metadata_from_db(self, file_id: str):
        """Delete file metadata from database"""
        try:
            from src.database.mysql_models import Transcription

            db_manager = get_database_manager()
            db = db_manager.get_session()

            # Find and delete transcription record
            transcription = (
                db.query(Transcription).filter(Transcription.audio_file_path.like(f"%{file_id}.enc")).first()
            )

            if transcription:
                db.delete(transcription)
                db.commit()

        except Exception as e:
            logger.error(f"Error deleting file metadata from database: {e}")
        finally:
            if "db" in locals():
                db.close()

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            total_files = 0
            total_size = 0

            # Count files and calculate total size
            for filename in os.listdir(self.audio_storage_path):
                if filename.endswith(".enc"):
                    file_path = os.path.join(self.audio_storage_path, filename)
                    total_files += 1
                    total_size += os.path.getsize(file_path)

            return {
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "storage_path": self.storage_base_path,
                "encryption_status": "active",
            }

        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {
                "total_files": 0,
                "total_size_bytes": 0,
                "total_size_mb": 0,
                "storage_path": self.storage_base_path,
                "encryption_status": "error",
            }


# Global secure storage service instance
secure_storage_service = SecureStorageService()
