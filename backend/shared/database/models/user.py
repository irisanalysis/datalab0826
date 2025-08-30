"""
User model for the AI Data Analysis Platform
"""
import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from .base import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    
    # Extended enterprise fields
    first_name = Column(String(50))
    last_name = Column(String(50))
    avatar_url = Column(String(500))
    role = Column(String(50), default='user')  # user, admin, analyst, viewer
    department = Column(String(100))
    organization = Column(String(100))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    timezone = Column(String(50), default='UTC')
    language = Column(String(10), default='en')
    
    # User preferences (JSON field)
    preferences = Column(Text)  # Store as JSON string
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dict for API responses"""
        data = {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "avatar_url": self.avatar_url,
            "role": self.role,
            "department": self.department,
            "organization": self.organization,
            "is_active": self.is_active,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "timezone": self.timezone,
            "language": self.language,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
        if include_sensitive:
            import json
            try:
                data["preferences"] = json.loads(self.preferences) if self.preferences else {}
            except (json.JSONDecodeError, TypeError):
                data["preferences"] = {}
        
        return data