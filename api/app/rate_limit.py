from fastapi import HTTPException, status, Request
from typing import Dict, Optional
import time
import asyncio
from collections import defaultdict, deque
import structlog

logger = structlog.get_logger()


class MemoryRateLimiter:
    """
    Memory-based rate limiter using sliding window
    Production systems should use Redis for distributed rate limiting
    """
    
    def __init__(self):
        # Store request timestamps per key
        self._requests: Dict[str, deque] = defaultdict(deque)
        self._lock = asyncio.Lock()
    
    async def is_allowed(
        self, 
        key: str, 
        limit: int, 
        window_seconds: int = 60
    ) -> bool:
        """
        Check if request is allowed based on rate limit
        """
        async with self._lock:
            now = time.time()
            window_start = now - window_seconds
            
            # Get request queue for this key
            requests = self._requests[key]
            
            # Remove old requests outside the window
            while requests and requests[0] < window_start:
                requests.popleft()
            
            # Check if under limit
            if len(requests) >= limit:
                return False
            
            # Add current request
            requests.append(now)
            return True
    
    async def cleanup_old_entries(self, max_age_seconds: int = 3600):
        """
        Cleanup old entries to prevent memory leaks
        Should be called periodically
        """
        async with self._lock:
            cutoff = time.time() - max_age_seconds
            keys_to_delete = []
            
            for key, requests in self._requests.items():
                # Remove old requests
                while requests and requests[0] < cutoff:
                    requests.popleft()
                
                # If no recent requests, mark for deletion
                if not requests:
                    keys_to_delete.append(key)
            
            # Delete empty entries
            for key in keys_to_delete:
                del self._requests[key]


# Global rate limiter instance
rate_limiter = MemoryRateLimiter()


async def check_rate_limit(
    request: Request,
    limit: int,
    window_seconds: int = 60,
    key_prefix: str = "default"
) -> None:
    """
    Check rate limit and raise exception if exceeded
    """
    # Create rate limit key based on IP and optional prefix
    client_ip = request.client.host if request.client else "unknown"
    key = f"{key_prefix}:{client_ip}"
    
    # Check if request is allowed
    allowed = await rate_limiter.is_allowed(key, limit, window_seconds)
    
    if not allowed:
        logger.warning(
            "Rate limit exceeded",
            key=key,
            limit=limit,
            window_seconds=window_seconds,
            ip=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {limit} requests per {window_seconds} seconds."
        )


async def check_auth_rate_limit(request: Request) -> None:
    """Rate limit for authentication endpoints"""
    from app.config import settings
    await check_rate_limit(
        request,
        limit=settings.rate_limit_auth,
        window_seconds=60,
        key_prefix="auth"
    )


async def check_refresh_rate_limit(request: Request) -> None:
    """Rate limit for token refresh endpoint"""
    from app.config import settings
    await check_rate_limit(
        request,
        limit=settings.rate_limit_refresh,
        window_seconds=60,
        key_prefix="refresh"
    )