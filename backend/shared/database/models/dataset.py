"""
Dataset and DataSource models for the AI Data Analysis Platform
"""
import datetime
import json
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from .base import Base

class DataSource(Base):
    __tablename__ = 'data_sources'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # postgresql, mysql, mongodb, csv, api, etc.
    
    # Connection configuration (encrypted)
    config = Column(Text)  # JSON string with connection details
    
    # Connection status
    status = Column(String(20), default='pending')  # pending, connected, failed, disabled
    last_test = Column(DateTime)
    error_message = Column(Text)
    
    # Metadata
    description = Column(Text)
    tags = Column(Text)  # JSON array as string
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def to_dict(self, include_config=False):
        """Convert data source to dict for API responses"""
        data = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "last_test": self.last_test.isoformat() if self.last_test else None,
            "error_message": self.error_message,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
        try:
            data["tags"] = json.loads(self.tags) if self.tags else []
        except (json.JSONDecodeError, TypeError):
            data["tags"] = []
        
        if include_config:
            try:
                data["config"] = json.loads(self.config) if self.config else {}
            except (json.JSONDecodeError, TypeError):
                data["config"] = {}
        
        return data

class UserSession(Base):
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_id = Column(String(128), unique=True, nullable=False, index=True)
    device_info = Column(Text)  # JSON with device details
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    location = Column(String(100))  # City, Country
    is_active = Column(Boolean, default=True)
    last_activity = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    def to_dict(self):
        """Convert session to dict for API responses"""
        data = {
            "id": self.id,
            "session_id": self.session_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "location": self.location,
            "is_active": self.is_active,
            "last_activity": self.last_activity.isoformat(),
            "created_at": self.created_at.isoformat()
        }
        
        try:
            data["device_info"] = json.loads(self.device_info) if self.device_info else {}
        except (json.JSONDecodeError, TypeError):
            data["device_info"] = {}
        
        return data