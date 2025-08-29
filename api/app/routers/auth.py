from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Cookie
from sqlalchemy.orm import Session
from typing import Optional
import structlog

from app.db import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, AuthResponse, MessageResponse
from app.security import PasswordManager, JWTManager, RefreshTokenManager
from app.deps import verify_csrf_protection, get_client_ip, get_user_agent
from app.rate_limit import check_auth_rate_limit, check_refresh_rate_limit
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
logger = structlog.get_logger()


@router.post("/register", response_model=MessageResponse)
async def register(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(check_auth_rate_limit),
    _csrf: None = Depends(verify_csrf_protection)
):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email.lower()).first()
    if existing_user:
        logger.warning("Registration attempt with existing email", email=user_data.email)
        # Use generic message to prevent email enumeration
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Please check your information and try again."
        )
    
    # Hash password
    password_hash = PasswordManager.hash_password(user_data.password)
    
    # Create new user
    new_user = User(
        email=user_data.email.lower(),
        password_hash=password_hash
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(
            "User registered successfully",
            user_id=new_user.id,
            email=new_user.email,
            ip=get_client_ip(request)
        )
        
        return MessageResponse(message="Registration successful")
    
    except Exception as e:
        db.rollback()
        logger.error("Registration failed", error=str(e), email=user_data.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    user_data: UserLogin,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    _: None = Depends(check_auth_rate_limit),
    _csrf: None = Depends(verify_csrf_protection)
):
    """Login user and set authentication cookies"""
    
    # Find user by email
    user = db.query(User).filter(User.email == user_data.email.lower()).first()
    
    # Verify password (always check to prevent timing attacks)
    password_valid = False
    if user:
        password_valid = PasswordManager.verify_password(user_data.password, user.password_hash)
    else:
        # Perform dummy hash check to prevent timing attacks
        PasswordManager.verify_password(user_data.password, "$2b$12$dummy.hash.to.prevent.timing.attacks")
    
    # Generic error message to prevent enumeration
    if not user or not password_valid:
        logger.warning(
            "Login attempt failed",
            email=user_data.email,
            ip=get_client_ip(request),
            user_exists=user is not None
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    try:
        # Generate tokens
        access_token = JWTManager.create_access_token(user.id)
        refresh_token = JWTManager.create_refresh_token()
        
        # Store refresh token in database
        RefreshTokenManager.create_refresh_token_record(
            db=db,
            user_id=user.id,
            token=refresh_token,
            user_agent=get_user_agent(request),
            ip_address=get_client_ip(request)
        )
        
        # Set secure cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=settings.access_ttl,
            httponly=True,
            secure=settings.cookie_secure,
            samesite=settings.cookie_samesite,
            domain=settings.cookie_domain
        )
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=settings.refresh_ttl,
            httponly=True,
            secure=settings.cookie_secure,
            samesite=settings.cookie_samesite,
            domain=settings.cookie_domain
        )
        
        logger.info(
            "User login successful",
            user_id=user.id,
            email=user.email,
            ip=get_client_ip(request)
        )
        
        return AuthResponse(user=user.to_dict())
    
    except Exception as e:
        logger.error("Login processing failed", error=str(e), user_id=user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )


@router.post("/refresh", response_model=MessageResponse)
async def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: Optional[str] = Cookie(None),
    _: None = Depends(check_refresh_rate_limit)
):
    """Refresh access token using refresh token"""
    
    if not refresh_token:
        logger.warning("Refresh attempt without token", ip=get_client_ip(request))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required"
        )
    
    # Verify refresh token
    token_record = RefreshTokenManager.verify_refresh_token(db, refresh_token)
    if not token_record:
        logger.warning("Invalid refresh token used", ip=get_client_ip(request))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    try:
        # Get user
        user = db.query(User).filter(User.id == token_record.user_id).first()
        if not user:
            logger.error("User not found for valid refresh token", user_id=token_record.user_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Generate new tokens
        new_access_token = JWTManager.create_access_token(user.id)
        new_refresh_token = JWTManager.create_refresh_token()
        
        # Revoke old refresh token
        RefreshTokenManager.revoke_refresh_token(db, token_record)
        
        # Create new refresh token record
        RefreshTokenManager.create_refresh_token_record(
            db=db,
            user_id=user.id,
            token=new_refresh_token,
            user_agent=get_user_agent(request),
            ip_address=get_client_ip(request)
        )
        
        # Set new cookies
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            max_age=settings.access_ttl,
            httponly=True,
            secure=settings.cookie_secure,
            samesite=settings.cookie_samesite,
            domain=settings.cookie_domain
        )
        
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            max_age=settings.refresh_ttl,
            httponly=True,
            secure=settings.cookie_secure,
            samesite=settings.cookie_samesite,
            domain=settings.cookie_domain
        )
        
        logger.info(
            "Token refresh successful",
            user_id=user.id,
            ip=get_client_ip(request)
        )
        
        return MessageResponse(message="Token refreshed successfully")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token refresh failed", error=str(e), user_id=token_record.user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed. Please try again."
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: Optional[str] = Cookie(None)
):
    """Logout user and revoke refresh token"""
    
    try:
        # Clear cookies first
        response.delete_cookie(
            key="access_token",
            httponly=True,
            secure=settings.cookie_secure,
            samesite=settings.cookie_samesite,
            domain=settings.cookie_domain
        )
        
        response.delete_cookie(
            key="refresh_token",
            httponly=True,
            secure=settings.cookie_secure,
            samesite=settings.cookie_samesite,
            domain=settings.cookie_domain
        )
        
        # Revoke refresh token if present
        if refresh_token:
            token_record = RefreshTokenManager.verify_refresh_token(db, refresh_token)
            if token_record:
                RefreshTokenManager.revoke_refresh_token(db, token_record)
                logger.info(
                    "User logout successful",
                    user_id=token_record.user_id,
                    ip=get_client_ip(request)
                )
            else:
                logger.info("Logout with invalid refresh token", ip=get_client_ip(request))
        else:
            logger.info("Logout without refresh token", ip=get_client_ip(request))
        
        return MessageResponse(message="Logout successful")
    
    except Exception as e:
        logger.error("Logout failed", error=str(e), ip=get_client_ip(request))
        # Still return success to avoid revealing internal errors
        return MessageResponse(message="Logout successful")