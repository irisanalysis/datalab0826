from fastapi import APIRouter, Depends
from app.models import User
from app.schemas import UserResponse
from app.deps import get_current_user
import structlog

router = APIRouter(prefix="/api", tags=["User"])
logger = structlog.get_logger()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information"""
    
    logger.info("User profile accessed", user_id=current_user.id)
    
    return UserResponse.model_validate(current_user)