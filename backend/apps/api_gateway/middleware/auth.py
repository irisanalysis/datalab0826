"""
Authentication Middleware
认证中间件 - 处理JWT token验证
"""
from fastapi import Request, Response, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import jwt
import structlog
from typing import Optional

from ..config import settings

logger = structlog.get_logger()
security = HTTPBearer()


class AuthMiddleware(BaseHTTPMiddleware):
    """JWT认证中间件"""
    
    # 不需要认证的路径
    SKIP_PATHS = {
        "/",
        "/health",
        "/metrics",
        "/api/v1/docs",
        "/api/v1/redoc", 
        "/api/v1/openapi.json",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh"
    }
    
    def __init__(self, app):
        super().__init__(app)
        self.jwt_secret = settings.jwt_secret_key
        self.jwt_algorithm = settings.jwt_algorithm
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        # 检查是否需要跳过认证
        if self._should_skip_auth(request):
            return await call_next(request)
        
        try:
            # 提取和验证token
            token = self._extract_token(request)
            if not token:
                return self._unauthorized_response("Missing authorization token")
            
            # 验证JWT token
            payload = self._verify_token(token)
            if not payload:
                return self._unauthorized_response("Invalid or expired token")
            
            # 将用户信息添加到请求状态
            request.state.user_id = payload.get("sub")
            request.state.user_email = payload.get("email") 
            request.state.user_roles = payload.get("roles", [])
            
            logger.debug(
                "Request authenticated",
                user_id=request.state.user_id,
                path=request.url.path
            )
            
            return await call_next(request)
            
        except Exception as e:
            logger.error("Authentication error", error=str(e), path=request.url.path)
            return self._unauthorized_response("Authentication failed")
    
    def _should_skip_auth(self, request: Request) -> bool:
        """检查是否应该跳过认证"""
        path = request.url.path
        
        # 静态路径跳过
        if path in self.SKIP_PATHS:
            return True
            
        # 健康检查路径跳过
        if path.startswith(("/health", "/metrics", "/.well-known")):
            return True
            
        # OPTIONS请求跳过(CORS预检)
        if request.method == "OPTIONS":
            return True
            
        return False
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """从请求中提取JWT token"""
        # 从Authorization header提取
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            return authorization.split(" ", 1)[1]
        
        # 从cookie中提取 (可选)
        token = request.cookies.get("access_token")
        if token:
            return token
            
        return None
    
    def _verify_token(self, token: str) -> Optional[dict]:
        """验证JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            
            # 检查必需字段
            if not payload.get("sub"):
                logger.warning("Token missing subject")
                return None
                
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.info("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid token", error=str(e))
            return None
        except Exception as e:
            logger.error("Token verification failed", error=str(e))
            return None
    
    def _unauthorized_response(self, message: str) -> Response:
        """返回401未授权响应"""
        return JSONResponse(
            status_code=401,
            content={
                "error": "Unauthorized",
                "message": message,
                "code": "AUTH_REQUIRED"
            }
        )


def get_current_user(request: Request) -> dict:
    """获取当前用户信息"""
    if not hasattr(request.state, 'user_id'):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "user_id": request.state.user_id,
        "email": request.state.user_email,
        "roles": request.state.user_roles
    }


def require_role(role: str):
    """要求特定角色的装饰器"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            user = get_current_user(request)
            if role not in user.get("roles", []):
                raise HTTPException(
                    status_code=403, 
                    detail=f"Role '{role}' required"
                )
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator