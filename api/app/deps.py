from fastapi import Depends, HTTPException, status, Request, Cookie
from sqlalchemy.orm import Session
from typing import Optional
from app.db import get_db
from app.models import User
from app.security import JWTManager
import structlog

logger = structlog.get_logger()


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(None, alias="access_token")
) -> User:
    """
    Get current user from access token cookie
    """
    if not access_token:
        logger.warning("No access token provided", ip=request.client.host)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Verify token
    payload = JWTManager.verify_access_token(access_token)
    user_id = int(payload.get("sub"))
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning("User not found for token", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


def verify_csrf_protection(request: Request) -> None:
    """
    Verify CSRF protection using custom header approach
    """
    # Check for custom header (standard CSRF protection)
    custom_header = request.headers.get("X-Requested-With")
    if custom_header != "XMLHttpRequest":
        logger.warning("Missing CSRF protection header", ip=request.client.host)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF protection required"
        )


def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    # Check for forwarded headers first (if behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection
    if request.client:
        return request.client.host
    
    return "unknown"


def get_user_agent(request: Request) -> str:
    """Get user agent from request"""
    return request.headers.get("User-Agent", "unknown")