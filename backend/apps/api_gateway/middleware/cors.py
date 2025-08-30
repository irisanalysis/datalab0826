"""
CORS Middleware Configuration
跨域资源共享中间件配置
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ..config import settings


def setup_cors(app: FastAPI):
    """配置CORS中间件"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
        expose_headers=["X-Request-ID", "X-Response-Time"]
    )