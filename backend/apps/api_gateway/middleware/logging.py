"""
Logging Middleware
请求日志中间件
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable):
        """处理请求日志"""
        
        # 生成请求ID
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 添加请求ID到request state
        request.state.request_id = request_id
        
        # 记录请求开始
        logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client_ip=self._get_client_ip(request),
            user_agent=request.headers.get("User-Agent", "")[:200],
            content_type=request.headers.get("Content-Type", ""),
            content_length=request.headers.get("Content-Length", "0")
        )
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{process_time:.4f}"
            
            # 记录请求完成
            logger.info(
                "Request completed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                response_time=f"{process_time:.4f}s",
                content_length=response.headers.get("content-length", "unknown")
            )
            
            return response
            
        except Exception as e:
            # 计算错误处理时间
            process_time = time.time() - start_time
            
            # 记录请求错误
            logger.error(
                "Request failed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                error=str(e),
                error_type=type(e).__name__,
                response_time=f"{process_time:.4f}s"
            )
            
            # 重新抛出异常
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 优先从X-Forwarded-For获取
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # 从X-Real-IP获取
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 直连IP
        return request.client.host if request.client else "unknown"
    
    def _should_log_request_body(self, request: Request) -> bool:
        """判断是否记录请求体"""
        # 敏感路径不记录请求体
        sensitive_paths = ["/api/v1/auth/login", "/api/v1/auth/register"]
        if request.url.path in sensitive_paths:
            return False
        
        # 大文件上传不记录请求体
        content_length = request.headers.get("Content-Length")
        if content_length and int(content_length) > 1024 * 1024:  # 1MB
            return False
        
        return True