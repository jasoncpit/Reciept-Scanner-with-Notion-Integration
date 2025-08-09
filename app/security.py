from fastapi import HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import logging
import re

# Configure logging with sensitive data filtering
class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'msg'):
            # Remove Bearer tokens from logs
            record.msg = re.sub(r'Bearer [a-zA-Z0-9]+', 'Bearer ***', str(record.msg))
            # Remove API keys from logs
            record.msg = re.sub(r'[a-zA-Z0-9]{32,}', '***', str(record.msg))
        return True

# Add filter to root logger
logging.getLogger().addFilter(SensitiveDataFilter())

def setup_security_middleware(app):
    """
    Set up security middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    
    Returns:
        Limiter: Rate limiter instance
    """
    
    # CORS Configuration
    cors_origins = os.getenv("CORS_ORIGINS", "").split(",")
    if cors_origins and cors_origins[0]:  # Only add if CORS_ORIGINS is set
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST"],
            allow_headers=["*"],
        )
    
    # Trusted Hosts Configuration
    allowed_hosts = os.getenv("ALLOWED_HOSTS", "").split(",")
    if allowed_hosts and allowed_hosts[0]:  # Only add if ALLOWED_HOSTS is set
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=allowed_hosts
        )
    
    # Rate Limiting Configuration
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    return limiter

def validate_file_upload(file, max_size_mb=10):
    """
    Validate file upload for security.
    
    Args:
        file: UploadFile object
        max_size_mb: Maximum file size in MB
    
    Raises:
        HTTPException: If file is invalid
    """
    # Check file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400, 
            detail="Only image files are allowed. Supported formats: JPEG, PNG, GIF, WebP"
        )
    
    # Check file size (if available)
    if hasattr(file, 'size') and file.size:
        max_size_bytes = max_size_mb * 1024 * 1024
        if file.size > max_size_bytes:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size is {max_size_mb}MB"
            )

def validate_auth_token(authorization: str, required_token: str):
    """
    Validate authentication token.
    
    Args:
        authorization: Authorization header value
        required_token: Required AUTH_TOKEN from environment
    
    Raises:
        HTTPException: If authentication fails
    """
    if not required_token:
        return  # No token required
    
    if not authorization:
        raise HTTPException(
            status_code=401, 
            detail="Authorization header required"
        )
    
    expected_auth = f"Bearer {required_token}"
    if authorization != expected_auth:
        raise HTTPException(
            status_code=401, 
            detail="Invalid authorization token"
        )

def log_security_event(event_type: str, request: Request, details: dict = None):
    """
    Log security events for monitoring.
    
    Args:
        event_type: Type of security event
        request: FastAPI request object
        details: Additional details to log
    """
    logger = logging.getLogger("security")
    
    log_data = {
        "event_type": event_type,
        "client_ip": request.client.host,
        "user_agent": request.headers.get("user-agent", ""),
        "method": request.method,
        "path": request.url.path,
    }
    
    if details:
        log_data.update(details)
    
    logger.warning(f"Security event: {log_data}") 