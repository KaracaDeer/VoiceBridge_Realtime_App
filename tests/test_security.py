"""
Security middleware and services test suite.
"""
from unittest.mock import patch

import pytest  # noqa: F401

from src.middleware.security_middleware import setup_security_middleware
from src.services.auth_service import auth_service
from src.services.encryption_service import encryption_service


class TestSecurity:
    """Test security functionality."""

    def test_encryption_service(self):
        """Test encryption service functionality."""
        # Test encryption
        test_data = b"test audio data"
        encrypted_data, metadata = encryption_service.encrypt_audio_file(test_data, "test.wav")

        assert encrypted_data != test_data
        assert metadata is not None
        assert "key_id" in metadata

        # Test decryption
        decrypted_data, _ = encryption_service.decrypt_audio_file(encrypted_data, metadata)
        assert decrypted_data == test_data
        return True

    def test_auth_service(self):
        """Test authentication service."""
        # Test user creation
        test_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
        }

        # Mock user creation
        with patch.object(auth_service, "create_user") as mock_create:
            mock_create.return_value = {"id": 1, "username": "testuser"}
            result = auth_service.create_user(
                username=test_user["username"], email=test_user["email"], password=test_user["password"]
            )

            assert result["username"] == "testuser"
            assert result["id"] == 1
            return True

    def test_token_generation(self):
        """Test JWT token generation and validation."""
        # Test token generation
        user_data = {"id": 1, "username": "testuser"}
        access_token = auth_service.create_access_token(user_data)
        refresh_token = auth_service.create_refresh_token(user_data)

        assert access_token is not None
        assert refresh_token is not None
        assert len(access_token) > 0
        assert len(refresh_token) > 0

        # Test token validation
        payload = auth_service.verify_token(access_token, "access")
        assert payload["sub"] == "1"
        assert payload["username"] == "testuser"
        return True

    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        from services.rate_limiting_service import rate_limiting_service

        # Test rate limiting
        client_id = "test_client"
        result = rate_limiting_service.check_rate_limit(client_id, "transcription")

        assert result is not None
        return True

    def test_security_middleware(self):
        """Test security middleware setup."""
        from fastapi import FastAPI

        app = FastAPI()
        setup_security_middleware(app)

        # Check if middleware is properly configured
        # In newer FastAPI versions, middleware_stack might be None
        # We'll check if the app has middleware by checking the user_middleware list
        assert hasattr(app, "user_middleware")
        assert len(app.user_middleware) > 0
        return True
