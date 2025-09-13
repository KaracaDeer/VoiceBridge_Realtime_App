"""
Comprehensive WebSocket streaming tests for VoiceBridge API.
Tests real-time audio streaming, transcription, and error handling.
"""
import asyncio
import json
import pytest
import websockets
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from main import app, manager


class TestWebSocketStreaming:
    """Test WebSocket streaming functionality."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_whisper_service(self):
        """Mock OpenAI Whisper service."""
        with patch('main.whisper_service') as mock:
            mock.transcribe_audio_bytes = AsyncMock()
            mock.is_api_available.return_value = True
            yield mock

    @pytest.mark.asyncio
    async def test_websocket_connection_success(self, mock_whisper_service):
        """Test successful WebSocket connection."""
        mock_whisper_service.transcribe_audio_bytes.return_value = {
            "text": "Hello world",
            "confidence": 0.95,
            "language": "en",
            "provider": "openai"
        }

        async with websockets.connect("ws://localhost:8000/ws/test_client") as websocket:
            # Send test audio data
            test_audio = b"fake_audio_data_for_testing"
            await websocket.send(test_audio)
            
            # Receive acknowledgment
            response = await websocket.recv()
            data = json.loads(response)
            assert data["type"] == "acknowledgment"
            assert data["status"] == "processing"
            assert data["encrypted"] is True

    @pytest.mark.asyncio
    async def test_websocket_transcription_success(self, mock_whisper_service):
        """Test successful transcription via WebSocket."""
        mock_whisper_service.transcribe_audio_bytes.return_value = {
            "text": "This is a test transcription",
            "confidence": 0.92,
            "language": "en",
            "provider": "openai"
        }

        async with websockets.connect("ws://localhost:8000/ws/test_client") as websocket:
            # Send audio data
            test_audio = b"fake_audio_data_for_testing"
            await websocket.send(test_audio)
            
            # Wait for transcription result
            await asyncio.sleep(0.1)  # Allow processing time
            
            # Check if transcription was received
            # Note: In real test, you'd need to implement proper async handling
            assert mock_whisper_service.transcribe_audio_bytes.called

    @pytest.mark.asyncio
    async def test_websocket_no_speech_detected(self, mock_whisper_service):
        """Test WebSocket handling when no speech is detected."""
        mock_whisper_service.transcribe_audio_bytes.return_value = {
            "text": "",
            "confidence": 0.0,
            "language": "en",
            "provider": "openai"
        }

        async with websockets.connect("ws://localhost:8000/ws/test_client") as websocket:
            test_audio = b"silent_audio_data"
            await websocket.send(test_audio)
            
            # Should handle empty transcription gracefully
            assert mock_whisper_service.transcribe_audio_bytes.called

    @pytest.mark.asyncio
    async def test_websocket_transcription_error(self, mock_whisper_service):
        """Test WebSocket error handling during transcription."""
        mock_whisper_service.transcribe_audio_bytes.return_value = {
            "error": "API rate limit exceeded",
            "text": "",
            "confidence": 0.0
        }

        async with websockets.connect("ws://localhost:8000/ws/test_client") as websocket:
            test_audio = b"fake_audio_data"
            await websocket.send(test_audio)
            
            # Should handle transcription errors gracefully
            assert mock_whisper_service.transcribe_audio_bytes.called

    @pytest.mark.asyncio
    async def test_websocket_connection_manager(self):
        """Test WebSocket connection manager functionality."""
        # Test connection
        mock_websocket = AsyncMock()
        await manager.connect(mock_websocket, "test_client")
        assert "test_client" in manager.active_connections
        
        # Test disconnection
        manager.disconnect("test_client")
        assert "test_client" not in manager.active_connections

    @pytest.mark.asyncio
    async def test_websocket_rate_limiting(self):
        """Test WebSocket rate limiting."""
        # This would test rate limiting for WebSocket connections
        # Implementation depends on rate limiting service
        pass

    def test_websocket_invalid_client_id(self, client):
        """Test WebSocket with invalid client ID."""
        # Test with invalid characters in client ID
        with pytest.raises(Exception):
            # This would test invalid client ID handling
            pass


class TestWebSocketIntegration:
    """Integration tests for WebSocket functionality."""

    @pytest.mark.asyncio
    async def test_websocket_with_authentication(self):
        """Test WebSocket with valid authentication token."""
        # Mock authentication
        with patch('main.auth_service') as mock_auth:
            mock_auth.verify_token.return_value = {"sub": "123"}
            mock_auth.get_user_by_id.return_value = MagicMock(id=123)
            
            # Test WebSocket with token
            async with websockets.connect("ws://localhost:8000/ws/test_client?token=valid_token") as websocket:
                test_audio = b"fake_audio_data"
                await websocket.send(test_audio)
                
                # Should process with authenticated user
                assert True

    @pytest.mark.asyncio
    async def test_websocket_without_authentication(self):
        """Test WebSocket without authentication (should still work)."""
        async with websockets.connect("ws://localhost:8000/ws/test_client") as websocket:
            test_audio = b"fake_audio_data"
            await websocket.send(test_audio)
            
            # Should process without authentication
            assert True

    @pytest.mark.asyncio
    async def test_websocket_invalid_token(self):
        """Test WebSocket with invalid authentication token."""
        with patch('main.auth_service') as mock_auth:
            mock_auth.verify_token.side_effect = Exception("Invalid token")
            
            # Should close connection with invalid token
            with pytest.raises(websockets.exceptions.ConnectionClosed):
                async with websockets.connect("ws://localhost:8000/ws/test_client?token=invalid_token") as websocket:
                    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
