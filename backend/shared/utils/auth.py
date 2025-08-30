"""
Authentication utilities for FastAPI services
"""
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .security import verify_jwt_token
from ..database.connections.postgres import get_db
from ..database.models.user import User

security = HTTPBearer()

def verify_jwt_token_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[str]:
    """Verify JWT token from Authorization header"""
    user_id = verify_jwt_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id

async def get_current_user(
    user_id: str = Depends(verify_jwt_token_dependency),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    return user