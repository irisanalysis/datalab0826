from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://jackchan:secure_password_123@db:5432/datairis"
    
    # JWT
    jwt_secret: str = "please_change_me"
    access_ttl: int = 900  # 15 minutes
    refresh_ttl: int = 604800  # 7 days
    jwt_algorithm: str = "HS256"
    
    # CORS
    cors_origins: List[str] = ["http://web:3000", "http://localhost:3000"]
    
    # Security
    bcrypt_cost: int = 12
    
    # Rate limiting (requests per minute)
    rate_limit_auth: int = 10
    rate_limit_refresh: int = 5
    
    # Cookie settings
    cookie_domain: str = None
    cookie_secure: bool = True
    cookie_samesite: str = "lax"
    
    # Environment
    environment: str = "production"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_cors_origins(self) -> List[str]:
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.cors_origins


settings = Settings()