"""
API Gateway Service - Main Entry Point
统一入口，负责路由分发、认证、限流等
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import structlog
from typing import Dict, Any

from .middleware.auth import AuthMiddleware
from .middleware.cors import setup_cors
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.logging import LoggingMiddleware
from .routers import auth, datasets, analysis, ai, visualizations
from .services.proxy import ServiceProxy
from .config import settings

logger = structlog.get_logger()

# Service registry - 微服务地址映射
SERVICE_REGISTRY = {
    "data_service": settings.data_service_url,
    "ai_service": settings.ai_service_url,
    "compute_service": settings.compute_service_url,
    "viz_service": settings.viz_service_url,
    "user_service": settings.user_service_url,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    logger.info(
        "Starting API Gateway",
        environment=settings.environment,
        services=SERVICE_REGISTRY
    )
    
    # 初始化服务代理
    app.state.service_proxy = ServiceProxy(SERVICE_REGISTRY)
    
    # 启动健康检查任务
    health_check_task = asyncio.create_task(periodic_health_check(app))
    
    yield
    
    # 关闭
    logger.info("Shutting down API Gateway")
    health_check_task.cancel()
    try:
        await health_check_task
    except asyncio.CancelledError:
        pass
    finally:
        await app.state.service_proxy.close()


async def periodic_health_check(app: FastAPI):
    """定期健康检查微服务"""
    while True:
        try:
            await asyncio.sleep(30)  # 每30秒检查一次
            await app.state.service_proxy.health_check_all()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error("Health check failed", error=str(e))


# 创建FastAPI应用
app = FastAPI(
    title="AI Data Platform - API Gateway",
    description="统一API网关，提供路由分发、认证、限流等功能",
    version="1.0.0",
    lifespan=lifespan,
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)

# 添加中间件 (顺序很重要)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)
setup_cors(app)

# 路由注册
app.include_router(
    auth.router, 
    prefix="/api/v1/auth", 
    tags=["Authentication"]
)
app.include_router(
    datasets.router, 
    prefix="/api/v1/datasets", 
    tags=["Datasets"]
)
app.include_router(
    analysis.router, 
    prefix="/api/v1/analysis", 
    tags=["Analysis"]
)
app.include_router(
    ai.router, 
    prefix="/api/v1/ai", 
    tags=["AI Services"]
)
app.include_router(
    visualizations.router, 
    prefix="/api/v1/visualizations", 
    tags=["Visualizations"]
)


@app.get("/")
async def root():
    """根路径 - API网关信息"""
    return {
        "service": "AI Data Platform API Gateway",
        "version": "1.0.0",
        "status": "running",
        "services": list(SERVICE_REGISTRY.keys()),
        "docs": "/api/v1/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    try:
        service_health = await app.state.service_proxy.health_check_all()
        
        overall_status = "healthy" if all(
            status["status"] == "healthy" 
            for status in service_health.values()
        ) else "degraded"
        
        return {
            "status": overall_status,
            "timestamp": asyncio.get_event_loop().time(),
            "services": service_health,
            "gateway": {
                "status": "healthy",
                "uptime": "running"
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=500, detail="Health check failed")


@app.get("/metrics")
async def metrics():
    """指标端点 - 供Prometheus抓取"""
    # 这里可以添加Prometheus指标
    return {
        "message": "Metrics endpoint - integrate with Prometheus",
        "requests_total": "TODO",
        "response_time": "TODO",
        "error_rate": "TODO"
    }


# 通用代理端点 - 用于转发到微服务
@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_to_service(service: str, path: str, request: Request):
    """
    通用服务代理
    将请求转发到对应的微服务
    """
    if service not in SERVICE_REGISTRY:
        raise HTTPException(
            status_code=404, 
            detail=f"Service '{service}' not found"
        )
    
    return await app.state.service_proxy.forward_request(
        service=service,
        path=path,
        request=request
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
        log_level="info"
    )