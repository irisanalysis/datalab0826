from fastapi import APIRouter, status
from datetime import datetime, timezone
from app.schemas import HealthResponse
from app.db import check_db_connection
import structlog

router = APIRouter(tags=["Health"])
logger = structlog.get_logger()


@router.get("/healthz", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint"""
    
    db_healthy = check_db_connection()
    
    health_status = "healthy" if db_healthy else "unhealthy"
    
    response = HealthResponse(
        status=health_status,
        database=db_healthy,
        timestamp=datetime.now(timezone.utc)
    )
    
    if not db_healthy:
        logger.warning("Health check failed - database unhealthy")
    
    return response


@router.get("/readyz", response_model=HealthResponse)
async def readiness_check():
    """Readiness check - same as health check for this simple API"""
    
    db_healthy = check_db_connection()
    
    ready_status = "ready" if db_healthy else "not_ready"
    
    response = HealthResponse(
        status=ready_status,
        database=db_healthy,
        timestamp=datetime.now(timezone.utc)
    )
    
    if not db_healthy:
        logger.warning("Readiness check failed - database not ready")
    
    return response