"""
Rate Limiting Middleware
限流中间件
"""
import time
import asyncio
from collections import defaultdict, deque
from typing import Dict, Deque, Tuple
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import structlog

from ..config import settings

logger = structlog.get_logger()


class TokenBucket:
    """令牌桶算法实现"""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        初始化令牌桶
        
        Args:
            capacity: 桶容量
            refill_rate: 每秒补充令牌数
        """
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """
        消费令牌
        
        Args:
            tokens: 要消费的令牌数
            
        Returns:
            是否成功消费
        """
        now = time.time()
        
        # 补充令牌
        elapsed = now - self.last_refill
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.refill_rate
        )
        self.last_refill = now
        
        # 尝试消费令牌
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        
        return False


class SlidingWindowCounter:
    """滑动窗口计数器"""
    
    def __init__(self, window_size: int):
        """
        初始化滑动窗口
        
        Args:
            window_size: 窗口大小(秒)
        """
        self.window_size = window_size
        self.requests: Deque[float] = deque()
    
    def add_request(self) -> int:
        """
        添加请求记录
        
        Returns:
            当前窗口内请求数
        """
        now = time.time()
        
        # 移除过期请求
        cutoff = now - self.window_size
        while self.requests and self.requests[0] < cutoff:
            self.requests.popleft()
        
        # 添加当前请求
        self.requests.append(now)
        
        return len(self.requests)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        
        # 存储每个IP的限流状态
        self.ip_buckets: Dict[str, TokenBucket] = {}
        self.ip_windows: Dict[str, SlidingWindowCounter] = {}
        
        # 配置
        self.requests_per_minute = settings.rate_limit_requests
        self.window_size = settings.rate_limit_period
        
        # 令牌桶配置
        self.bucket_capacity = self.requests_per_minute
        self.refill_rate = self.requests_per_minute / 60.0  # 每秒补充令牌数
        
        # 清理任务
        self._cleanup_task = None
    
    async def dispatch(self, request: Request, call_next):
        """处理请求限流"""
        
        # 获取客户端IP
        client_ip = self._get_client_ip(request)
        
        # 检查限流
        if not self._check_rate_limit(client_ip, request):
            return self._rate_limit_response(client_ip)
        
        # 记录请求
        await self._log_request(request, client_ip)
        
        # 继续处理请求
        response = await call_next(request)
        
        # 添加限流头信息
        self._add_rate_limit_headers(response, client_ip)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 优先从X-Forwarded-For获取(代理情况)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # 从X-Real-IP获取
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 直连IP
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str, request: Request) -> bool:
        """检查是否触发限流"""
        
        # 跳过某些路径
        if self._should_skip_rate_limit(request):
            return True
        
        # 令牌桶检查
        bucket = self._get_or_create_bucket(client_ip)
        if not bucket.consume(1):
            logger.warning(
                "Rate limit exceeded (token bucket)",
                client_ip=client_ip,
                path=request.url.path
            )
            return False
        
        # 滑动窗口检查
        window = self._get_or_create_window(client_ip)
        current_requests = window.add_request()
        
        if current_requests > self.requests_per_minute:
            logger.warning(
                "Rate limit exceeded (sliding window)",
                client_ip=client_ip,
                path=request.url.path,
                requests=current_requests,
                limit=self.requests_per_minute
            )
            return False
        
        return True
    
    def _should_skip_rate_limit(self, request: Request) -> bool:
        """检查是否跳过限流"""
        # 健康检查路径
        if request.url.path in ["/health", "/metrics"]:
            return True
        
        # OPTIONS请求(CORS预检)
        if request.method == "OPTIONS":
            return True
        
        return False
    
    def _get_or_create_bucket(self, client_ip: str) -> TokenBucket:
        """获取或创建令牌桶"""
        if client_ip not in self.ip_buckets:
            self.ip_buckets[client_ip] = TokenBucket(
                self.bucket_capacity,
                self.refill_rate
            )
        return self.ip_buckets[client_ip]
    
    def _get_or_create_window(self, client_ip: str) -> SlidingWindowCounter:
        """获取或创建滑动窗口"""
        if client_ip not in self.ip_windows:
            self.ip_windows[client_ip] = SlidingWindowCounter(self.window_size)
        return self.ip_windows[client_ip]
    
    def _rate_limit_response(self, client_ip: str) -> Response:
        """返回限流响应"""
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "message": f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per {self.window_size} seconds.",
                "code": "RATE_LIMIT_EXCEEDED",
                "retry_after": 60
            },
            headers={
                "Retry-After": "60",
                "X-RateLimit-Limit": str(self.requests_per_minute),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time() + 60))
            }
        )
    
    async def _log_request(self, request: Request, client_ip: str):
        """记录请求信息"""
        logger.debug(
            "Request processed",
            client_ip=client_ip,
            method=request.method,
            path=request.url.path,
            user_agent=request.headers.get("User-Agent", "")[:100]
        )
    
    def _add_rate_limit_headers(self, response: Response, client_ip: str):
        """添加限流相关头信息"""
        try:
            bucket = self.ip_buckets.get(client_ip)
            window = self.ip_windows.get(client_ip)
            
            if bucket and window:
                remaining = min(
                    int(bucket.tokens),
                    self.requests_per_minute - len(window.requests)
                )
                
                response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
                response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
                response.headers["X-RateLimit-Reset"] = str(int(time.time() + self.window_size))
                
        except Exception as e:
            logger.error("Failed to add rate limit headers", error=str(e))
    
    async def cleanup_old_entries(self):
        """清理过期的限流记录"""
        try:
            current_time = time.time()
            cutoff_time = current_time - self.window_size * 2  # 保留2倍窗口时间
            
            # 清理空的窗口记录
            empty_ips = []
            for ip, window in self.ip_windows.items():
                if not window.requests or window.requests[-1] < cutoff_time:
                    empty_ips.append(ip)
            
            for ip in empty_ips:
                self.ip_windows.pop(ip, None)
                self.ip_buckets.pop(ip, None)
            
            if empty_ips:
                logger.debug(f"Cleaned up {len(empty_ips)} expired rate limit entries")
                
        except Exception as e:
            logger.error("Rate limit cleanup failed", error=str(e))