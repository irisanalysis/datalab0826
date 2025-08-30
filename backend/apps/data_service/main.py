import os
import datetime
import logging
import json
from functools import wraps
from urllib.parse import quote_plus

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from ...shared.database.connections.postgres import get_db, engine
from ...shared.database.models.user import User
from ...shared.database.models.dataset import DataSource
from ...shared.utils.security import hash_password, verify_password, create_access_token
from ...shared.utils.logging import setup_logging
from ...shared.utils.config import settings

# Setup logging
logger = setup_logging(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Data Platform - Data Service",
    description="Data management and processing service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class DataSourceCreate(BaseModel):
    name: str
    type: str
    config: Optional[dict] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    from ...shared.utils.auth import verify_jwt_token
    user_id = verify_jwt_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "data_service"}

@app.post("/auth/register")
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email.lower()).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email.lower(),
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"User registered: {new_user.email}")
    return {"message": "User registered successfully", "user_id": new_user.id}

@app.post("/auth/login")
async def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    # Find user
    user = db.query(User).filter(User.email == user_data.email.lower()).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account disabled")
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # Update last login
    user.last_login = datetime.datetime.utcnow()
    db.commit()
    
    logger.info(f"User logged in: {user.email}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
    }

@app.get("/users/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login
    }

@app.get("/data-sources")
async def get_data_sources(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data_sources = db.query(DataSource).filter(
        DataSource.user_id == current_user.id,
        DataSource.is_active == True
    ).all()
    
    return {
        "data_sources": [
            {
                "id": ds.id,
                "name": ds.name,
                "type": ds.type,
                "status": ds.status,
                "description": ds.description,
                "created_at": ds.created_at,
                "updated_at": ds.updated_at
            }
            for ds in data_sources
        ]
    }

@app.post("/data-sources")
async def create_data_source(
    data_source: DataSourceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate data source type
    allowed_types = ['postgresql', 'mysql', 'mongodb', 'csv', 'json', 'api', 'excel']
    if data_source.type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid data source type")
    
    # Create data source
    new_data_source = DataSource(
        user_id=current_user.id,
        name=data_source.name[:100],  # Truncate to max length
        type=data_source.type,
        description=data_source.description[:500] if data_source.description else None,
        tags=json.dumps(data_source.tags or []),
        config=json.dumps(data_source.config or {})
    )
    
    db.add(new_data_source)
    db.commit()
    db.refresh(new_data_source)
    
    logger.info(f"Data source created: {new_data_source.name} by user {current_user.email}")
    return {
        "message": "Data source created successfully",
        "data_source": {
            "id": new_data_source.id,
            "name": new_data_source.name,
            "type": new_data_source.type,
            "status": new_data_source.status,
            "created_at": new_data_source.created_at
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
