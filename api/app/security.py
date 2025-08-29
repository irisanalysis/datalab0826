import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.config import settings
from app.models import User, RefreshToken
import hashlib
import secrets
import structlog

logger = structlog.get_logger()


class PasswordManager:
    """Handle password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=settings.bcrypt_cost)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


class JWTManager:
    """Handle JWT token creation and verification"""
    
    @staticmethod
    def create_access_token(user_id: int) -> str:
        """Create access token"""
        expire = datetime.now(timezone.utc) + timedelta(seconds=settings.access_ttl)
        payload = {
            "sub": str(user_id),
            "type": "access",
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "jti": secrets.token_urlsafe(16)
        }
        return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    
    @staticmethod
    def create_refresh_token() -> str:
        """Create refresh token (random string)"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def verify_access_token(token: str) -> Dict[str, Any]:
        """Verify and decode access token"""
        try:
            payload = jwt.decode(
                token, 
                settings.jwt_secret, 
                algorithms=[settings.jwt_algorithm]
            )
            
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            return payload
        
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    @staticmethod
    def hash_token(token: str) -> str:
        """Hash refresh token for storage"""
        return hashlib.sha256(token.encode()).hexdigest()


class RefreshTokenManager:
    """Handle refresh token operations"""
    
    @staticmethod
    def create_refresh_token_record(
        db: Session,
        user_id: int,
        token: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> RefreshToken:
        """Create refresh token record in database"""
        token_hash = JWTManager.hash_token(token)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.refresh_ttl)
        
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        db.add(refresh_token)
        db.commit()
        db.refresh(refresh_token)
        
        logger.info("Refresh token created", user_id=user_id, expires_at=expires_at)
        return refresh_token
    
    @staticmethod
    def verify_refresh_token(db: Session, token: str) -> Optional[RefreshToken]:
        """Verify refresh token and return record if valid"""
        token_hash = JWTManager.hash_token(token)
        
        refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash
        ).first()
        
        if not refresh_token:
            logger.warning("Refresh token not found", token_hash=token_hash[:16])
            return None
        
        if refresh_token.is_revoked:
            logger.warning("Refresh token is revoked", user_id=refresh_token.user_id)
            return None
        
        if refresh_token.is_expired:
            logger.warning("Refresh token is expired", user_id=refresh_token.user_id)
            return None
        
        return refresh_token
    
    @staticmethod
    def revoke_refresh_token(db: Session, refresh_token: RefreshToken) -> None:
        """Revoke refresh token"""
        refresh_token.revoked_at = datetime.now(timezone.utc)
        db.commit()
        
        logger.info("Refresh token revoked", user_id=refresh_token.user_id)
    
    @staticmethod
    def revoke_all_user_tokens(db: Session, user_id: int) -> None:
        """Revoke all refresh tokens for a user"""
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None)
        ).update({
            "revoked_at": datetime.now(timezone.utc)
        })
        db.commit()
        
        logger.info("All refresh tokens revoked for user", user_id=user_id)