"""
Rate limiting service for VoiceBridge API
Handles request rate limiting using Redis for distributed rate limiting
"""
import logging
import time
from typing import Dict, Optional

import redis
from fastapi import HTTPException, Request, status
from fastapi_limiter.depends import RateLimiter

from config import settings

logger = logging.getLogger(__name__)


class RateLimitingService:
    """Service for handling rate limiting across the API"""

    def __init__(self):
        self.redis_client = None
        self.rate_limits = {
            "transcription": {
                "requests": 10,  # 10 requests
                "window": 60,  # per minute
                "description": "Transcription endpoint rate limit",
            },
            "websocket": {
                "requests": 5,  # 5 connections
                "window": 60,  # per minute
                "description": "WebSocket connection rate limit",
            },
            "auth": {
                "requests": 5,  # 5 attempts
                "window": 300,  # per 5 minutes
                "description": "Authentication rate limit",
            },
            "general": {
                "requests": settings.rate_limit_requests,
                "window": settings.rate_limit_window,
                "description": "General API rate limit",
            },
        }

    async def initialize(self):
        """Initialize Redis connection for rate limiting"""
        try:
            # Parse Redis URL
            redis_url = settings.redis_url
            self.redis_client = redis.from_url(redis_url, decode_responses=True)

            # Test connection
            self.redis_client.ping()
            logger.info("Rate limiting service initialized with Redis")

        except Exception as e:
            logger.warning(f"Failed to connect to Redis for rate limiting: {e}")
            logger.warning("Rate limiting will use in-memory storage (not recommended for production)")
            self.redis_client = None

    def get_rate_limit_key(self, identifier: str, endpoint: str) -> str:
        """Generate rate limit key for Redis"""
        return f"rate_limit:{endpoint}:{identifier}"

    def get_rate_limit_info(self, endpoint: str) -> Dict:
        """Get rate limit configuration for an endpoint"""
        return self.rate_limits.get(endpoint, self.rate_limits["general"])

    async def check_rate_limit(self, identifier: str, endpoint: str) -> Dict:
        """
        Check if request is within rate limit

        Args:
            identifier: Unique identifier (IP, user_id, etc.)
            endpoint: Endpoint name for rate limiting

        Returns:
            Dict with rate limit status
        """
        if not self.redis_client:
            # If Redis is not available, allow all requests (not recommended for production)
            return {
                "allowed": True,
                "remaining": 999,
                "reset_time": int(time.time()) + 60,
            }

        try:
            rate_limit = self.get_rate_limit_info(endpoint)
            key = self.get_rate_limit_key(identifier, endpoint)

            # Get current count
            current_count = self.redis_client.get(key)
            current_count = int(current_count) if current_count else 0

            # Check if limit exceeded
            if current_count >= rate_limit["requests"]:
                # Get TTL to calculate reset time
                ttl = self.redis_client.ttl(key)
                reset_time = int(time.time()) + ttl if ttl > 0 else int(time.time()) + rate_limit["window"]

                return {
                    "allowed": False,
                    "remaining": 0,
                    "reset_time": reset_time,
                    "limit": rate_limit["requests"],
                    "window": rate_limit["window"],
                }

            # Increment counter
            if current_count == 0:
                # First request in window
                self.redis_client.setex(key, rate_limit["window"], 1)
            else:
                # Increment existing counter
                self.redis_client.incr(key)

            # Get updated count and TTL
            updated_count = int(self.redis_client.get(key))
            ttl = self.redis_client.ttl(key)
            reset_time = int(time.time()) + ttl if ttl > 0 else int(time.time()) + rate_limit["window"]

            return {
                "allowed": True,
                "remaining": rate_limit["requests"] - updated_count,
                "reset_time": reset_time,
                "limit": rate_limit["requests"],
                "window": rate_limit["window"],
            }

        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # On error, allow the request (fail open)
            return {
                "allowed": True,
                "remaining": 999,
                "reset_time": int(time.time()) + 60,
            }

    async def enforce_rate_limit(self, identifier: str, endpoint: str):
        """
        Enforce rate limit and raise exception if exceeded

        Args:
            identifier: Unique identifier
            endpoint: Endpoint name

        Raises:
            HTTPException: If rate limit exceeded
        """
        rate_limit_status = await self.check_rate_limit(identifier, endpoint)

        if not rate_limit_status["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": rate_limit_status["limit"],
                    "window": rate_limit_status["window"],
                    "reset_time": rate_limit_status["reset_time"],
                    "message": f"Too many requests. Limit: {rate_limit_status['limit']} requests per {rate_limit_status['window']} seconds",
                },
                headers={
                    "X-RateLimit-Limit": str(rate_limit_status["limit"]),
                    "X-RateLimit-Remaining": str(rate_limit_status["remaining"]),
                    "X-RateLimit-Reset": str(rate_limit_status["reset_time"]),
                },
            )

    def get_client_identifier(self, request: Request, user_id: Optional[int] = None) -> str:
        """
        Get unique identifier for rate limiting

        Args:
            request: FastAPI request object
            user_id: Optional user ID for authenticated requests

        Returns:
            Unique identifier string
        """
        if user_id:
            # For authenticated users, use user ID
            return f"user:{user_id}"
        else:
            # For anonymous users, use IP address
            client_ip = request.client.host
            # Handle forwarded IPs (from proxies/load balancers)
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                client_ip = forwarded_for.split(",")[0].strip()

            return f"ip:{client_ip}"

    async def cleanup_expired_limits(self):
        """Clean up expired rate limit entries (Redis handles this automatically)"""
        # Redis automatically expires keys, so no manual cleanup needed
        pass

    def get_rate_limit_status(self, identifier: str, endpoint: str) -> Dict:
        """Get current rate limit status without incrementing counter"""
        if not self.redis_client:
            return {
                "current": 0,
                "limit": self.rate_limits.get(endpoint, self.rate_limits["general"])["requests"],
                "window": self.rate_limits.get(endpoint, self.rate_limits["general"])["window"],
                "remaining": 999,
            }

        try:
            rate_limit = self.get_rate_limit_info(endpoint)
            key = self.get_rate_limit_key(identifier, endpoint)

            current_count = self.redis_client.get(key)
            current_count = int(current_count) if current_count else 0

            ttl = self.redis_client.ttl(key)
            reset_time = int(time.time()) + ttl if ttl > 0 else None

            return {
                "current": current_count,
                "limit": rate_limit["requests"],
                "window": rate_limit["window"],
                "remaining": max(0, rate_limit["requests"] - current_count),
                "reset_time": reset_time,
            }

        except Exception as e:
            logger.error(f"Error getting rate limit status: {e}")
            return {"current": 0, "limit": 999, "window": 60, "remaining": 999}


# Global rate limiting service instance
rate_limiting_service = RateLimitingService()


# Rate limiter dependencies for FastAPI
def get_transcription_rate_limiter():
    """Rate limiter for transcription endpoints"""
    return RateLimiter(
        times=10,
        seconds=60,
        identifier=lambda request: rate_limiting_service.get_client_identifier(request),
    )


def get_websocket_rate_limiter():
    """Rate limiter for WebSocket connections"""
    return RateLimiter(
        times=5,
        seconds=60,
        identifier=lambda request: rate_limiting_service.get_client_identifier(request),
    )


def get_auth_rate_limiter():
    """Rate limiter for authentication endpoints"""
    return RateLimiter(
        times=5,
        seconds=300,  # 5 minutes
        identifier=lambda request: rate_limiting_service.get_client_identifier(request),
    )


def get_general_rate_limiter():
    """General rate limiter for all endpoints"""
    return RateLimiter(
        times=settings.rate_limit_requests,
        seconds=settings.rate_limit_window,
        identifier=lambda request: rate_limiting_service.get_client_identifier(request),
    )
