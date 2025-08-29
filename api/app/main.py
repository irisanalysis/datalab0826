from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from app.config import settings
from app.middleware import (
    setup_cors, 
    setup_exception_handlers, 
    RequestLoggingMiddleware, 
    SecurityHeadersMiddleware
)
from app.routers import auth, me, health
from app.rate_limit import rate_limiter
import structlog

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    
    # Startup
    logger.info("Starting authentication API", environment=settings.environment)
    
    # Start background task for rate limiter cleanup
    cleanup_task = asyncio.create_task(periodic_cleanup())
    
    yield
    
    # Shutdown
    logger.info("Shutting down authentication API")
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


async def periodic_cleanup():
    """Periodic cleanup task for rate limiter"""
    while True:
        try:
            await asyncio.sleep(3600)  # Every hour
            await rate_limiter.cleanup_old_entries()
            logger.debug("Rate limiter cleanup completed")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error("Rate limiter cleanup failed", error=str(e))


# Create FastAPI app
app = FastAPI(
    title="Authentication API",
    description="Secure user authentication system with JWT tokens",
    version="1.0.0",
    lifespan=lifespan
)

# Setup middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
setup_cors(app)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(me.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Authentication API",
        "version": "1.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development"
    )