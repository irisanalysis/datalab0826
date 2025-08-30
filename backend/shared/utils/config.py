"""
Configuration management for the backend services
"""
import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database settings
    postgres_host: str = os.getenv('POSTGRES_HOST', 'localhost')
    postgres_port: int = int(os.getenv('POSTGRES_PORT', '5432'))
    postgres_db: str = os.getenv('POSTGRES_DB', 'datalab')
    postgres_user: str = os.getenv('POSTGRES_USER', 'user')
    postgres_password: str = os.getenv('POSTGRES_PASSWORD', 'password')
    
    # JWT settings
    jwt_secret: str = os.getenv('JWT_SECRET', 'dev-secret-change-in-production')
    access_token_expire_minutes: int = int(os.getenv('ACCESS_TTL', '900')) // 60
    
    # CORS settings
    cors_origins: List[str] = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:3001').split(',')
    
    # Security settings
    bcrypt_rounds: int = int(os.getenv('BCRYPT_ROUNDS', '12'))
    cookie_secure: bool = os.getenv('COOKIE_SECURE', 'False').lower() == 'true'
    
    # Application settings
    environment: str = os.getenv('FLASK_ENV', 'development')
    debug: bool = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Service URLs
    ai_service_url: str = os.getenv('AI_SERVICE_URL', 'http://localhost:8002')
    compute_service_url: str = os.getenv('COMPUTE_SERVICE_URL', 'http://localhost:8003')
    viz_service_url: str = os.getenv('VIZ_SERVICE_URL', 'http://localhost:8004')
    
    @property
    def database_url(self) -> str:
        from urllib.parse import quote_plus
        encoded_password = quote_plus(self.postgres_password)
        return f'postgresql://{self.postgres_user}:{encoded_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}'
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()