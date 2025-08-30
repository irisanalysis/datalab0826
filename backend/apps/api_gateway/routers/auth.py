"""
Authentication Router
认证路由 - 处理用户登录、注册、token刷新等
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends
from typing import Dict, Any
import structlog

from ..middleware.auth import get_current_user
from ..services.proxy import get_service_proxy

logger = structlog.get_logger()
router = APIRouter()


@router.post("/register")
async def register(
    request: Request,
    user_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    用户注册
    转发到用户服务处理
    """
    try:
        # 获取服务代理
        proxy = get_service_proxy(request)
        
        # 转发请求到用户服务
        response = await proxy.forward_request(
            service="user_service",
            path="auth/register",
            request=request,
            json_data=user_data
        )
        
        logger.info(
            "User registration request forwarded",
            email=user_data.get("email"),
            request_id=getattr(request.state, 'request_id', 'unknown')
        )
        
        return response
        
    except Exception as e:
        logger.error("Registration forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration service unavailable"
        )


@router.post("/login")
async def login(
    request: Request,
    credentials: Dict[str, Any]
) -> Dict[str, Any]:
    """
    用户登录
    转发到用户服务处理
    """
    try:
        # 获取服务代理
        proxy = get_service_proxy(request)
        
        # 转发请求到用户服务
        response = await proxy.forward_request(
            service="user_service",
            path="auth/login",
            request=request,
            json_data=credentials
        )
        
        logger.info(
            "User login request forwarded",
            email=credentials.get("email"),
            request_id=getattr(request.state, 'request_id', 'unknown')
        )
        
        return response
        
    except Exception as e:
        logger.error("Login forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service unavailable"
        )


@router.post("/refresh")
async def refresh_token(request: Request) -> Dict[str, Any]:
    """
    刷新访问令牌
    转发到用户服务处理
    """
    try:
        # 获取服务代理
        proxy = get_service_proxy(request)
        
        # 转发请求到用户服务
        response = await proxy.forward_request(
            service="user_service",
            path="auth/refresh",
            request=request
        )
        
        logger.info(
            "Token refresh request forwarded",
            request_id=getattr(request.state, 'request_id', 'unknown')
        )
        
        return response
        
    except Exception as e:
        logger.error("Token refresh forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service unavailable"
        )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    用户登出
    转发到用户服务处理
    """
    try:
        # 获取服务代理
        proxy = get_service_proxy(request)
        
        # 转发请求到用户服务
        response = await proxy.forward_request(
            service="user_service",
            path="auth/logout",
            request=request
        )
        
        logger.info(
            "User logout request forwarded",
            user_id=current_user["user_id"],
            request_id=getattr(request.state, 'request_id', 'unknown')
        )
        
        return response
        
    except Exception as e:
        logger.error("Logout forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service unavailable"
        )


@router.get("/profile")
async def get_profile(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取用户资料
    转发到用户服务处理
    """
    try:
        # 获取服务代理
        proxy = get_service_proxy(request)
        
        # 转发请求到用户服务
        response = await proxy.forward_request(
            service="user_service",
            path=f"users/{current_user['user_id']}/profile",
            request=request
        )
        
        logger.debug(
            "User profile request forwarded",
            user_id=current_user["user_id"],
            request_id=getattr(request.state, 'request_id', 'unknown')
        )
        
        return response
        
    except Exception as e:
        logger.error("Profile fetch forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User service unavailable"
        )


@router.put("/profile")
async def update_profile(
    request: Request,
    profile_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    更新用户资料
    转发到用户服务处理
    """
    try:
        # 获取服务代理
        proxy = get_service_proxy(request)
        
        # 转发请求到用户服务
        response = await proxy.forward_request(
            service="user_service",
            path=f"users/{current_user['user_id']}/profile",
            request=request,
            json_data=profile_data
        )
        
        logger.info(
            "User profile update request forwarded",
            user_id=current_user["user_id"],
            request_id=getattr(request.state, 'request_id', 'unknown')
        )
        
        return response
        
    except Exception as e:
        logger.error("Profile update forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User service unavailable"
        )


@router.post("/change-password")
async def change_password(
    request: Request,
    password_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    修改密码
    转发到用户服务处理
    """
    try:
        # 获取服务代理
        proxy = get_service_proxy(request)
        
        # 转发请求到用户服务
        response = await proxy.forward_request(
            service="user_service",
            path=f"users/{current_user['user_id']}/change-password",
            request=request,
            json_data=password_data
        )
        
        logger.info(
            "Password change request forwarded",
            user_id=current_user["user_id"],
            request_id=getattr(request.state, 'request_id', 'unknown')
        )
        
        return response
        
    except Exception as e:
        logger.error("Password change forwarding failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User service unavailable"
        )