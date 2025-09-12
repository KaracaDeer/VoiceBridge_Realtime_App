"""
Security middleware for VoiceBridge API
Adds security headers and handles security-related middleware
"""
import logging
import time
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Add CORS headers for security
        response.headers["Access-Control-Allow-Origin"] = "*"  # Configure appropriately for production
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Max-Age"] = "86400"

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log security-relevant requests"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Log request details
        client_ip = request.client.host
        method = request.method
        url = str(request.url)

        # Check for suspicious patterns
        suspicious_patterns = [
            "admin",
            "login",
            "password",
            "token",
            "auth",
            "sql",
            "script",
            "eval",
            "exec",
            "cmd",
        ]

        is_suspicious = any(pattern in url.lower() for pattern in suspicious_patterns)

        if is_suspicious:
            logger.warning(f"Suspicious request from {client_ip}: {method} {url}")

        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response details
        status_code = response.status_code

        # Log security-relevant events
        if status_code == 401:
            logger.warning(f"Unauthorized access attempt from {client_ip}: {method} {url}")
        elif status_code == 403:
            logger.warning(f"Forbidden access attempt from {client_ip}: {method} {url}")
        elif status_code == 429:
            logger.warning(f"Rate limit exceeded from {client_ip}: {method} {url}")
        elif status_code >= 500:
            logger.error(f"Server error for {client_ip}: {method} {url} - Status: {status_code}")

        # Add processing time header
        response.headers["X-Process-Time"] = str(round(process_time, 4))

        return response


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """Middleware to implement IP whitelisting (optional)"""

    def __init__(self, app, allowed_ips: list = None):
        super().__init__(app)
        self.allowed_ips = allowed_ips or []

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip IP checking for health checks and public endpoints
        if request.url.path in ["/", "/health", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host

        # Check forwarded IP (from proxies/load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        # Check if IP is whitelisted (if whitelist is configured)
        if self.allowed_ips and client_ip not in self.allowed_ips:
            logger.warning(f"Blocked request from non-whitelisted IP: {client_ip}")
            return JSONResponse(status_code=403, content={"detail": "Access denied: IP not whitelisted"})

        return await call_next(request)


class ContentSecurityPolicyMiddleware(BaseHTTPMiddleware):
    """Middleware to add Content Security Policy headers"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add CSP header
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' ws: wss:; "
            "media-src 'self' blob:; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none';"
        )

        response.headers["Content-Security-Policy"] = csp_policy

        return response


def setup_security_middleware(app):
    """Setup all security middleware"""

    # Add security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Add request logging
    app.add_middleware(RequestLoggingMiddleware)

    # Add Content Security Policy
    app.add_middleware(ContentSecurityPolicyMiddleware)

    # Add IP whitelist (optional - uncomment and configure if needed)
    # allowed_ips = ["127.0.0.1", "::1"]  # Add your allowed IPs here
    # app.add_middleware(IPWhitelistMiddleware, allowed_ips=allowed_ips)

    logger.info("Security middleware configured successfully")
