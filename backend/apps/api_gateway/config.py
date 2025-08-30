"""
API Gateway Configuration
API网关配置管理
"""
import os
from typing import Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """API网关配置"""
    
    # 应用基础配置
    app_name: str = "AI Data Platform API Gateway"
    environment: str = "development"
    debug: bool = False
    
    # 服务端口
    port: int = 8000
    host: str = "0.0.0.0"
    
    # JWT配置
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # 数据库配置
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    
    # 微服务地址配置
    data_service_url: str = "http://localhost:8001"
    ai_service_url: str = "http://localhost:8002"
    compute_service_url: str = "http://localhost:8003"
    viz_service_url: str = "http://localhost:8004"
    user_service_url: str = "http://localhost:8005"
    notification_service_url: str = "http://localhost:8006"
    
    # CORS配置
    cors_origins: list = ["http://localhost:3000", "http://localhost:3001"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    cors_allow_headers: list = ["*"]
    
    # 限流配置
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # 秒
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "json"
    
    # 监控配置
    enable_metrics: bool = True
    metrics_path: str = "/metrics"
    
    # 安全配置
    enable_https: bool = False
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    
    # 超时配置
    request_timeout: int = 30
    service_timeout: int = 60
    
    @validator('jwt_secret_key')
    def jwt_secret_must_be_set(cls, v):
        if not v:
            raise ValueError('JWT_SECRET_KEY must be set')
        return v
    
    @validator('environment')
    def environment_must_be_valid(cls, v):
        if v not in ['development', 'staging', 'production']:
            raise ValueError('Environment must be development, staging, or production')
        return v
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        env_prefix = "API_GATEWAY_"
        case_sensitive = False


# 全局设置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings


# 配置验证
def validate_config():
    """验证配置有效性"""
    errors = []
    
    # 检查必需的服务URL
    required_services = [
        'data_service_url',
        'ai_service_url', 
        'compute_service_url'
    ]
    
    for service in required_services:
        url = getattr(settings, service)
        if not url or not url.startswith('http'):
            errors.append(f"{service} must be a valid HTTP URL")
    
    # 检查生产环境配置
    if settings.environment == 'production':
        if settings.debug:
            errors.append("Debug mode should be disabled in production")
        if not settings.enable_https:
            errors.append("HTTPS should be enabled in production")
        if 'localhost' in str(settings.cors_origins):
            errors.append("CORS origins should not include localhost in production")
    
    if errors:
        raise ValueError(f"Configuration errors: {'; '.join(errors)}")
    
    return True


# 在导入时验证配置
if __name__ != "__main__":
    try:
        validate_config()
    except ValueError as e:
        import structlog
        logger = structlog.get_logger()
        logger.warning("Configuration validation failed", error=str(e))