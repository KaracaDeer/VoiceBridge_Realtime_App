"""
Audio stream processor for real-time audio handling.
Processes audio chunks, buffers, and manages audio streaming.
"""
import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AudioStreamProcessor:
    """Processes audio streams in real-time."""

    def __init__(self, buffer_size: int = 10, chunk_duration: float = 1.0):
        """
        Initialize audio stream processor.
        
        Args:
            buffer_size: Maximum number of audio chunks to buffer
            chunk_duration: Duration of each audio chunk in seconds
        """
        self.buffer_size = buffer_size
        self.chunk_duration = chunk_duration
        
        # Audio buffers for each session
        self.audio_buffers: Dict[str, List[bytes]] = {}
        self.buffer_lock = asyncio.Lock()
        
        # Processing stats
        self.stats = {
            "total_chunks_processed": 0,
            "total_audio_duration": 0.0,
            "average_chunk_size": 0.0,
            "buffer_overflows": 0
        }
        
        logger.info("AudioStreamProcessor initialized")

    async def add_audio_chunk(self, session_id: str, audio_chunk: bytes) -> bool:
        """
        Add audio chunk to session buffer.
        
        Args:
            session_id: Session ID
            audio_chunk: Audio data chunk
            
        Returns:
            True if chunk was added successfully
        """
        try:
            async with self.buffer_lock:
                # Initialize buffer if needed
                if session_id not in self.audio_buffers:
                    self.audio_buffers[session_id] = []
                
                # Check buffer size
                if len(self.audio_buffers[session_id]) >= self.buffer_size:
                    # Remove oldest chunk
                    self.audio_buffers[session_id].pop(0)
                    self.stats["buffer_overflows"] += 1
                    logger.warning(f"Buffer overflow for session {session_id}")
                
                # Add new chunk
                self.audio_buffers[session_id].append(audio_chunk)
                
                # Update stats
                self.stats["total_chunks_processed"] += 1
                chunk_size = len(audio_chunk)
                total_chunks = self.stats["total_chunks_processed"]
                
                # Update average chunk size
                current_avg = self.stats["average_chunk_size"]
                self.stats["average_chunk_size"] = (
                    (current_avg * (total_chunks - 1) + chunk_size) / total_chunks
                )
                
                logger.debug(f"Added audio chunk for session {session_id}: {chunk_size} bytes")
                return True
                
        except Exception as e:
            logger.error(f"Error adding audio chunk: {e}")
            return False

    async def get_audio_chunks(self, session_id: str, clear_buffer: bool = True) -> List[bytes]:
        """
        Get all audio chunks for a session.
        
        Args:
            session_id: Session ID
            clear_buffer: Whether to clear the buffer after getting chunks
            
        Returns:
            List of audio chunks
        """
        try:
            async with self.buffer_lock:
                if session_id not in self.audio_buffers:
                    return []
                
                chunks = self.audio_buffers[session_id].copy()
                
                if clear_buffer:
                    self.audio_buffers[session_id].clear()
                
                return chunks
                
        except Exception as e:
            logger.error(f"Error getting audio chunks: {e}")
            return []

    async def get_combined_audio(self, session_id: str, clear_buffer: bool = True) -> bytes:
        """
        Get combined audio data for a session.
        
        Args:
            session_id: Session ID
            clear_buffer: Whether to clear the buffer after getting audio
            
        Returns:
            Combined audio data
        """
        try:
            chunks = await self.get_audio_chunks(session_id, clear_buffer)
            return b"".join(chunks)
            
        except Exception as e:
            logger.error(f"Error combining audio: {e}")
            return b""

    async def clear_buffer(self, session_id: str) -> bool:
        """
        Clear audio buffer for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if buffer was cleared successfully
        """
        try:
            async with self.buffer_lock:
                if session_id in self.audio_buffers:
                    self.audio_buffers[session_id].clear()
                    logger.debug(f"Cleared audio buffer for session {session_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error clearing buffer: {e}")
            return False

    def get_buffer_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get buffer information for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Buffer information dictionary
        """
        try:
            if session_id not in self.audio_buffers:
                return {
                    "session_id": session_id,
                    "chunk_count": 0,
                    "total_size": 0,
                    "buffer_size": self.buffer_size,
                    "is_full": False
                }
            
            chunks = self.audio_buffers[session_id]
            total_size = sum(len(chunk) for chunk in chunks)
            
            return {
                "session_id": session_id,
                "chunk_count": len(chunks),
                "total_size": total_size,
                "buffer_size": self.buffer_size,
                "is_full": len(chunks) >= self.buffer_size,
                "average_chunk_size": total_size / len(chunks) if chunks else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting buffer info: {e}")
            return {"error": str(e)}

    def get_all_buffers_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all audio buffers."""
        return {
            session_id: self.get_buffer_info(session_id)
            for session_id in self.audio_buffers.keys()
        }

    async def process_audio_stream(self, session_id: str, 
                                 processing_callback: callable) -> Dict[str, Any]:
        """
        Process audio stream for a session.
        
        Args:
            session_id: Session ID
            processing_callback: Callback function to process audio data
            
        Returns:
            Processing result
        """
        try:
            # Get combined audio
            audio_data = await self.get_combined_audio(session_id, clear_buffer=True)
            
            if not audio_data:
                return {
                    "success": False,
                    "error": "No audio data available",
                    "session_id": session_id
                }
            
            # Process audio
            start_time = time.time()
            result = await processing_callback(audio_data)
            processing_time = time.time() - start_time
            
            # Update stats
            self.stats["total_audio_duration"] += processing_time
            
            return {
                "success": True,
                "result": result,
                "processing_time": processing_time,
                "audio_size": len(audio_data),
                "session_id": session_id,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error processing audio stream: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "timestamp": time.time()
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics."""
        return {
            **self.stats,
            "active_sessions": len(self.audio_buffers),
            "timestamp": time.time()
        }

    async def cleanup_session(self, session_id: str) -> bool:
        """
        Clean up audio buffer for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if cleanup was successful
        """
        try:
            async with self.buffer_lock:
                if session_id in self.audio_buffers:
                    del self.audio_buffers[session_id]
                    logger.debug(f"Cleaned up audio buffer for session {session_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error cleaning up session: {e}")
            return False

    async def cleanup_all_sessions(self) -> int:
        """
        Clean up all audio buffers.
        
        Returns:
            Number of sessions cleaned up
        """
        try:
            async with self.buffer_lock:
                session_count = len(self.audio_buffers)
                self.audio_buffers.clear()
                logger.info(f"Cleaned up {session_count} audio buffers")
                return session_count
                
        except Exception as e:
            logger.error(f"Error cleaning up all sessions: {e}")
            return 0

    def is_session_active(self, session_id: str) -> bool:
        """
        Check if a session has an active audio buffer.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if session has active buffer
        """
        return session_id in self.audio_buffers

    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs."""
        return list(self.audio_buffers.keys())
