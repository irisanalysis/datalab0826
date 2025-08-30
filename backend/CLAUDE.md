# Backend Development Guide - Claude Code Instructions

> **Integration Note**: This document extends the root [CLAUDE.md](../CLAUDE.md) with backend-specific guidance. Always read the root CLAUDE.md first for mandatory package management rules and general development guidelines.

This document provides comprehensive backend-specific guidance for Claude Code when working with the AI Data Platform backend services.

## Cross-Reference Links
- **Root Development Guide**: [../CLAUDE.md](../CLAUDE.md) - MANDATORY package management rules
- **Development Guidelines**: [../.claude/CLAUDE.md](../.claude/CLAUDE.md) - Architecture principles and standards
- **Frontend Integration**: [../frontend/CLAUDE.md](../frontend/CLAUDE.md) - Frontend-backend coordination

---

## System Architecture Overview

### Architecture Pattern
The backend follows a **microservices architecture** with an API Gateway pattern, designed for:
- **Scalability**: Horizontal scaling of individual services
- **Maintainability**: Clear separation of concerns
- **Reliability**: Fault isolation and graceful degradation
- **Flexibility**: Independent service deployment and technology choices

**Core Services:**

- **API Gateway Service** (Port 8000) - Unified entry point with routing, authentication, and rate limiting
- **Data Service** (Port 8001) - Data management and processing  
- **Legacy Flask Service** - Backward compatibility layer for existing APIs
- **Shared Modules** - Common utilities, database models, and connectors

### Directory Structure
```
backend/
├── apps/                          # Application services
│   ├── api_gateway/              # API Gateway service (FastAPI)
│   │   ├── main.py              # Gateway entry point
│   │   ├── config.py            # Gateway configuration
│   │   ├── middleware/          # Authentication, CORS, rate limiting
│   │   ├── routers/             # Route handlers (auth, datasets, ai, etc.)
│   │   └── services/            # Service proxy and utilities
│   ├── data_service/            # Data management service (FastAPI)
│   │   └── main.py              # Data service entry point
│   └── legacy_flask/            # Backward compatibility layer
│       └── main.py              # Flask application
├── shared/                      # Shared modules across services
│   ├── database/                # Database configuration and models
│   │   ├── models/              # SQLAlchemy models
│   │   └── connections/         # Database connections
│   ├── utils/                   # Utility modules
│   └── data_connectors/         # Data source connectors
├── scripts/                     # Database and utility scripts
├── tests/                       # Integration tests
└── dev_server.py               # Development server launcher
```

---

## Technology Stack & Dependencies

### Core Technologies (Current)
- **FastAPI 0.104.1+** - Modern async Python web framework
- **SQLAlchemy 2.0.23+** - Database ORM with async support
- **PostgreSQL** - Primary database with connection pooling
- **PyJWT 2.8.0+** - JWT token management
- **bcrypt 4.0.1+** - Password hashing
- **Pydantic 2.5.0+** - Data validation and settings management
- **structlog 23.2.0+** - Structured JSON logging
- **httpx 0.25.2+** - Modern async HTTP client

### Legacy Support
- **Flask 3.0.0+** - Legacy API compatibility layer
- **Flask-JWT-Extended** - JWT integration for Flask
- **Flask-SQLAlchemy** - ORM integration for Flask services

### Development Tools & Package Management
- **UV Package Manager** - **MANDATORY** for all Python operations (see [../CLAUDE.md](../CLAUDE.md))
- **uvicorn[standard]** - Production ASGI server
- **pytest 7.4.3+** - Testing framework with async support
- **alembic 1.12.0+** - Database schema migrations
- **python-dotenv 1.0.0+** - Environment variable management
- **black/isort/flake8** - Code formatting and linting

### Critical Package Management Rules
> **From Root CLAUDE.md**: ALWAYS use UV for backend Python operations
```bash
# ✅ CORRECT: Use UV for all operations
cd backend
uv add fastapi
uv run python script.py

# ❌ WRONG: Never use pip directly
pip install fastapi  # FORBIDDEN
```

---

## Database Schema & Models

### Core Models

#### User Model (`shared/database/models/user.py`)
**Purpose**: Core user management with role-based access control

```python
class User(Base):
    __tablename__ = 'users'
    
    # Primary identifiers
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str]
    
    # User profile
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    avatar_url: Mapped[Optional[str]]
    
    # Role-based access control
    role: Mapped[str] = mapped_column(default='user')
    # Roles: 'user', 'admin', 'analyst', 'viewer'
    
    # Organization context
    department: Mapped[Optional[str]]
    organization: Mapped[Optional[str]]
    
    # Account status
    is_active: Mapped[bool] = mapped_column(default=True)
    last_login: Mapped[Optional[datetime]]
    
    # User preferences
    timezone: Mapped[str] = mapped_column(default='UTC')
    language: Mapped[str] = mapped_column(default='en')
    preferences: Mapped[Optional[str]]  # JSON string
    
    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    
    # Relationships
    data_sources: Mapped[List["DataSource"]] = relationship("DataSource", back_populates="owner")
```

#### DataSource Model (`shared/database/models/dataset.py`)
**Purpose**: Data source connection and configuration management

```python
class DataSource(Base):
    __tablename__ = 'data_sources'
    
    # Primary identifiers
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    name: Mapped[str] = mapped_column(index=True)
    
    # Data source type and configuration
    type: Mapped[str]  # postgresql, mysql, mongodb, csv, api, s3, etc.
    config: Mapped[Optional[str]]  # Encrypted JSON connection config
    
    # Connection status management
    status: Mapped[str] = mapped_column(default='pending')
    # Status values: 'pending', 'connected', 'failed', 'disabled'
    last_test: Mapped[Optional[datetime]]
    error_message: Mapped[Optional[str]]
    
    # Metadata and organization
    description: Mapped[Optional[str]]
    tags: Mapped[Optional[str]]  # JSON array as string
    is_active: Mapped[bool] = mapped_column(default=True)
    
    # Performance and usage tracking
    last_used: Mapped[Optional[datetime]]
    usage_count: Mapped[int] = mapped_column(default=0)
    
    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    
    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="data_sources")
```

#### Additional Models
- **UserSession** - Session tracking for security
- **AuditLog** - Action auditing (legacy Flask)
- **Integration** - Third-party integrations (legacy Flask)

### Database Relationships
- User -> DataSource (One-to-Many)
- User -> UserSession (One-to-Many)
- User -> AuditLog (One-to-Many)

---

## Authentication & Authorization Architecture

### JWT Token Strategy
**Design Goals**: Secure, scalable authentication with proper token lifecycle management

- **Access Tokens**: 15 minutes (configurable via `ACCESS_TTL`)
- **Refresh Tokens**: 7 days (configurable via `REFRESH_TTL`) 
- **Token Blacklisting**: Redis-based for secure logout (planned)
- **Role-Based Access Control**: Granular permissions per role

**Role Hierarchy:**
```
admin     → Full system access, user management
analyst   → Data analysis, create/modify datasets
user      → Basic access, own data only
viewer    → Read-only access to shared resources
```

### Security Flow
1. **Login** – User provides email/password
2. **Validation** – Credentials checked against database
3. **Token Generation** – JWT access + refresh tokens created
4. **Authentication** – Subsequent requests include Bearer token
5. **Authorization** – Middleware validates token and extracts user info

### Password Security
- **bcrypt hashing** - Configurable rounds (minimum 10, default 12)
- **Password validation** - Minimum 8 chars, mixed case, digits required
- **Secure storage** - No plaintext passwords stored

---

## API Gateway & Service Architecture

### Service Registry Configuration
**Location**: `apps/api_gateway/config.py`

```python
# Service discovery and routing
SERVICE_REGISTRY = {
    "data_service": "http://localhost:8001",     # Data management and ETL
    "ai_service": "http://localhost:8002",       # ML and AI processing  
    "compute_service": "http://localhost:8003",  # Heavy computation tasks
    "viz_service": "http://localhost:8004",      # Data visualization
    "user_service": "http://localhost:8005",     # User management
    "notification_service": "http://localhost:8006"  # Notifications
}

# Health check configuration
HEALTH_CHECK_INTERVAL = 30  # seconds
SERVICE_TIMEOUT = 10  # seconds
CIRCUIT_BREAKER_THRESHOLD = 5  # failures before opening circuit
```

### Middleware Stack (Order Matters)
1. **LoggingMiddleware** - Request/response logging
2. **RateLimitMiddleware** - API rate limiting
3. **AuthMiddleware** - JWT token validation
4. **CORS** - Cross-origin resource sharing

### Request Flow
```
Client Request → API Gateway → Authentication → Rate Limiting → 
Service Proxy → Target Microservice → Response → Client
```

---

## Inter-Service Communication

### Service Proxy Implementation
**File**: `apps/api_gateway/services/proxy.py`
**Purpose**: Centralized service communication with reliability patterns

**Key Features:**
- **HTTP Client**: httpx for modern async requests
- **Request Forwarding**: Preserves authentication context
- **Health Monitoring**: Automated service health checks
- **Circuit Breaker**: Fail-fast for unhealthy services
- **Load Balancing**: Round-robin for multi-instance services (planned)
- **Retry Logic**: Exponential backoff for transient failures

**Error Handling Strategy:**
```python
# Service communication patterns
try:
    response = await service_client.forward_request(service_name, request)
except ServiceUnavailableError:
    # Circuit breaker opened - return cached response or error
    return handle_service_degradation(service_name, request)
except TimeoutError:
    # Log timeout and return appropriate error
    logger.warning(f"Service {service_name} timeout", request_id=request.id)
    raise HTTPException(status_code=504, detail="Service timeout")
```

### Inter-Service Headers
- `Authorization` - JWT token forwarding
- `X-Request-ID` - Request correlation
- `X-Original-User-Agent` - Client information
- `Content-Type` - Request content type

---

## Code Organization & Dependencies

### Dependency Architecture
**Design Principle**: Shared modules provide common functionality across services

```
Microservices Layer
├── api_gateway/          # Central routing and auth
├── data_service/         # Data management
├── legacy_flask/         # Backward compatibility
└── [future_services]/    # Extensible architecture

Shared Layer (Common Dependencies)
├── database/
│   ├── models/           # SQLAlchemy models
│   └── connections/      # DB connection management
├── utils/
│   ├── security.py       # JWT, encryption, hashing
│   ├── auth.py          # Authentication helpers
│   ├── config.py        # Configuration management
│   └── logging.py       # Structured logging setup
└── data_connectors/      # External data source connectors
```

**Import Guidelines:**
- Services import from `shared/` modules only
- No direct service-to-service imports
- Use dependency injection for testability
- Follow the dependency inversion principle

### Key Import Patterns
```python
# API Gateway imports
from .config import settings
from .middleware.auth import AuthMiddleware
from .routers import auth, datasets, analysis
from ..shared.database.models import User, DataSource

# Service imports
from ...shared.utils.security import hash_password, verify_jwt_token
from ...shared.database.connections.postgres import get_db
```

---

## Configuration & Environment Management

### Environment Configuration
**Template**: `.env.example` (copy to `.env` for development)

```bash
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=datalab
POSTGRES_USER=datalab_user
POSTGRES_PASSWORD=secure_password_here

# Database Connection Pool
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_PRE_PING=true

# JWT Configuration (Security Critical)
JWT_SECRET=your-256-bit-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TTL=900     # 15 minutes
REFRESH_TTL=604800 # 7 days

# Service Discovery
DATA_SERVICE_URL=http://localhost:8001
AI_SERVICE_URL=http://localhost:8002
COMPUTE_SERVICE_URL=http://localhost:8003

# Security Configuration
BCRYPT_ROUNDS=12
COOKIE_SECURE=false  # true in production
COOKIE_SAMESITE=strict

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
CORS_CREDENTIALS=true

# Logging and Monitoring
LOG_LEVEL=INFO
STRUCTLOG_JSON=true
ENABLE_METRICS=true

# Development Settings
DEBUG=true
RELOAD=true
PROFILING_ENABLED=false
```

### Configuration Classes
- **API Gateway Config** (`apps/api_gateway/config.py`) - Pydantic settings with validation
- **Shared Config** (`shared/utils/config.py`) - Common configuration across services
- **Environment-specific** - Development vs production settings

---

## API Endpoints & Route Organization

### API Gateway Routes (`/api/v1/`)
**Design**: RESTful API with consistent response formats and error handling

#### Authentication Routes (`/api/v1/auth`)
**Purpose**: User authentication and profile management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | User registration | No |
| POST | `/login` | User authentication | No |
| POST | `/refresh` | JWT token refresh | Refresh Token |
| POST | `/logout` | User logout (token blacklist) | Access Token |
| GET | `/profile` | Get user profile | Access Token |
| PUT | `/profile` | Update user profile | Access Token |
| POST | `/change-password` | Change password | Access Token |
| POST | `/reset-password` | Password reset request | No |

#### Data Source Routes (`/api/v1/data-sources`)
**Purpose**: Data source connection management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | List user data sources | Access Token |
| POST | `/` | Create new data source | Access Token |
| GET | `/{id}` | Get data source details | Access Token |
| PUT | `/{id}` | Update data source config | Access Token |
| DELETE | `/{id}` | Delete data source | Access Token |
| POST | `/{id}/test` | Test connection | Access Token |
| GET | `/{id}/schema` | Get data source schema | Access Token |
| POST | `/{id}/query` | Execute query | Access Token |

#### Service Proxy Routes
**Purpose**: Route requests to appropriate microservices

- `/api/v1/analysis/*` → Analysis Service (8002)
- `/api/v1/ai/*` → AI/ML Service (8003)
- `/api/v1/visualizations/*` → Visualization Service (8004)
- `/api/v1/compute/*` → Compute Service (8005)

### Data Service Routes
- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication
- `GET /users/me` - Current user info
- `GET /data-sources` - List data sources
- `POST /data-sources` - Create data source

### Legacy Flask Routes (`/api/`)
- Full compatibility with existing API endpoints
- Same authentication and data models
- Gradual migration path to FastAPI services

---

## Data Connectors & Integration

### Data Source Connectors
**Location**: `shared/data_connectors/connectors.py`
**Purpose**: Unified interface for external data sources

#### Supported Data Sources

**Databases:**
- PostgreSQL (psycopg2, asyncpg)
- MySQL (PyMySQL, aiomysql) 
- MongoDB (pymongo, motor)
- SQLite (sqlite3, aiosqlite)

**File Formats:**
- CSV (pandas, aiofiles)
- JSON (json, orjson)
- Excel (openpyxl) - Optional dependency
- Parquet (pyarrow) - Planned

**APIs & Web:**
- REST APIs (httpx)
- GraphQL (gql) - Planned
- WebSockets (websockets) - Planned

**Cloud Sources:**
- AWS S3 (boto3) - Planned
- Google Cloud Storage (google-cloud-storage) - Planned
- Azure Blob Storage (azure-storage-blob) - Planned

### Connector Interface Design
**Pattern**: Abstract base class with consistent interface across all data sources

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class ConnectionResult(BaseModel):
    """Standardized connection test result"""
    success: bool
    message: str
    latency_ms: Optional[float] = None
    metadata: Dict[str, Any] = {}

class SchemaInfo(BaseModel):
    """Standardized schema information"""
    tables: List[Dict[str, Any]]
    columns: Dict[str, List[Dict[str, Any]]]
    indexes: Dict[str, List[str]] = {}
    constraints: Dict[str, List[Dict[str, Any]]] = {}

class QueryResult(BaseModel):
    """Standardized query result"""
    data: List[Dict[str, Any]]
    columns: List[str]
    row_count: int
    execution_time_ms: float
    has_more: bool = False

class BaseConnector(ABC):
    """Base class for all data source connectors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
    
    @abstractmethod
    async def test_connection(self) -> ConnectionResult:
        """Test connectivity to the data source"""
        pass
    
    @abstractmethod 
    async def get_schema(self) -> SchemaInfo:
        """Retrieve schema information"""
        pass
    
    @abstractmethod
    async def execute_query(self, query: str, limit: int = 100) -> QueryResult:
        """Execute query and return results"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Clean up resources"""
        pass
```

### Connection Testing Flow
1. **Validation** - Check required configuration fields
2. **Connection** - Attempt actual connection to data source  
3. **Schema Discovery** - Extract schema information
4. **Status Update** - Update DataSource status in database

---

## Development Workflow & Commands

### Development Server Management
**Primary Script**: `dev_server.py` - Orchestrates all backend services

```bash
# MANDATORY: Use UV for all Python operations (from root CLAUDE.md)
cd backend
uv install  # Install dependencies

# Start all services in development mode
uv run python dev_server.py

# Start specific services
uv run python dev_server.py legacy_flask data_service
uv run python dev_server.py api_gateway  # API Gateway only

# Individual service startup (for debugging)
uv run uvicorn apps.api_gateway.main:app --reload --port 8000
uv run uvicorn apps.data_service.main:app --reload --port 8001
uv run python apps/legacy_flask/main.py

# Service health check
curl http://localhost:8000/health
curl http://localhost:8001/health
```

**Service Startup Order:**
1. Database connection verification
2. Legacy Flask service (8080)
3. Data Service (8001) 
4. API Gateway (8000) - Always starts last

### Database Operations
**IMPORTANT**: Always use UV for Python scripts in backend

```bash
# Database initialization (from backend directory)
cd backend
uv run python scripts/init_database.py

# Database migrations with Alembic
uv run alembic revision --autogenerate -m "Description"
uv run alembic upgrade head
uv run alembic downgrade -1  # Rollback one migration

# Data quality assessment
uv run python scripts/quality_assessment.py

# Database backup and restore (planned)
uv run python scripts/backup_database.py
uv run python scripts/restore_database.py --file backup.sql

# Connection testing
uv run python scripts/test_db_connections.py
```

**Migration Best Practices:**
- Always review auto-generated migrations
- Test migrations on development data
- Create rollback plan for production
- Use descriptive migration messages

### Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Install dependencies with UV (MANDATORY)
cd backend
uv install

# Install optional dependencies
uv install --extra dev     # Development tools
uv install --extra mongo   # MongoDB support
uv install --extra redis   # Redis caching
```

---

## Testing Strategy & Implementation

### Test Organization
**Framework**: pytest with async support
**Structure**: Following the test pyramid principle

```
tests/
├── unit/                    # Fast, isolated unit tests
│   ├── test_models.py      # SQLAlchemy model tests
│   ├── test_auth.py        # Authentication utility tests
│   ├── test_connectors.py  # Data connector tests
│   └── test_utils.py       # Utility function tests
├── integration/            # Integration tests with external dependencies
│   ├── test_api.py         # API endpoint tests
│   ├── test_database.py    # Database integration tests
│   └── test_services.py    # Service communication tests
├── e2e/                   # End-to-end workflow tests
│   ├── test_auth_flow.py   # Complete authentication flow
│   └── test_data_flow.py   # Data source to analysis flow
├── fixtures/              # Test data and fixtures
│   ├── sample_data.json
│   └── test_configs.py
└── conftest.py           # pytest configuration and fixtures
```

### Test Execution Commands
**MANDATORY**: Use UV for all test operations

```bash
# Run all tests with UV
cd backend
uv run pytest tests/

# Run specific test categories
uv run pytest tests/unit/           # Fast unit tests only
uv run pytest tests/integration/    # Integration tests
uv run pytest tests/e2e/           # End-to-end tests

# Run specific test files
uv run pytest tests/integration/test_api.py -v
uv run pytest tests/unit/test_auth.py::test_jwt_creation

# Coverage reporting
uv run pytest --cov=apps --cov=shared --cov-report=html tests/
uv run pytest --cov=apps --cov=shared --cov-report=term-missing tests/

# Performance and load testing
uv run pytest tests/performance/ --benchmark-only

# Parallel test execution (for CI)
uv run pytest -n auto tests/  # Requires pytest-xdist
```

**Test Configuration (pytest.ini_options in pyproject.toml):**
- Async test support enabled
- Test discovery patterns configured
- Coverage thresholds enforced

---

## Error Handling & Observability

### Structured Logging Implementation
**Library**: structlog 23.2.0+ for consistent JSON logging
**Configuration**: `shared/utils/logging.py`

**Logging Standards:**
- **JSON Format**: All logs in structured JSON for parsing
- **Correlation IDs**: Track requests across service boundaries
- **Context Preservation**: Service name, user ID, request ID in all logs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Performance Logging**: Execution time for critical operations

```python
# Example logging usage
import structlog

logger = structlog.get_logger(__name__)

# Request logging with context
logger.info(
    "User authentication successful",
    user_id=user.id,
    email=user.email,
    request_id=request.headers.get("X-Request-ID"),
    service="api_gateway",
    endpoint="/api/v1/auth/login",
    execution_time_ms=125.3
)

# Error logging with traceback
logger.error(
    "Database connection failed", 
    error=str(e),
    database_url=config.database_url_masked,
    retry_count=3,
    request_id=request_id,
    exc_info=True
)
```

### Standardized Error Response Format
**Purpose**: Consistent error handling across all services and endpoints

```json
{
  "error": {
    "type": "ValidationError",
    "code": "INVALID_EMAIL_FORMAT", 
    "message": "Please provide a valid email address",
    "details": {
      "field": "email",
      "value": "invalid-email",
      "constraint": "email_format"
    },
    "request_id": "req_123456789",
    "timestamp": "2024-01-01T10:30:00Z",
    "service": "api_gateway"
  }
}
```

**Error Categories:**
- **4xx Client Errors**: Authentication, validation, not found
- **5xx Server Errors**: Internal errors, service unavailable, timeouts
- **Custom Business Errors**: Domain-specific error codes

### Common Error Patterns
- **401 Unauthorized** - Invalid or missing authentication
- **403 Forbidden** - Insufficient permissions
- **404 Not Found** - Resource not found
- **429 Too Many Requests** - Rate limit exceeded
- **503 Service Unavailable** - Downstream service failure

---

## Security Implementation & Best Practices

### Security Headers & Middleware
**Implementation**: Applied across all services (FastAPI and Flask)

**Security Headers:**
```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY  
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
Strict-Transport-Security: max-age=31536000; includeSubDomains
Permissions-Policy: microphone=(), camera=(), geolocation=()
```

**FastAPI Security Middleware:**
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware

# Trusted host validation
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "*.yourdomain.com"]
)

# CORS with strict settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"]
)
```

### Input Validation
- Pydantic models for FastAPI services
- Length limits and sanitization
- SQL injection prevention via ORM
- XSS prevention via proper escaping

### Configuration Security
- Environment variables for sensitive data
- No hardcoded secrets in code
- Encryption for stored configurations
- Secure cookie settings in production

---

## Migration Strategy & Legacy Support

### Phased Migration Approach
**Goal**: Zero-downtime migration from monolithic Flask to microservices

**Phase 1: Foundation (Current)**
- ✅ Shared modules established
- ✅ Database models unified
- ✅ Authentication system standardized
- ✅ API Gateway implemented

**Phase 2: Service Extraction (In Progress)**
- 🔄 Data Service separation
- 🔄 User management service
- 🔄 Legacy Flask compatibility layer
- ⏳ Authentication service extraction

**Phase 3: Feature Migration (Planned)**
- ⏳ AI/ML service implementation
- ⏳ Visualization service
- ⏳ Compute service for heavy workloads
- ⏳ Notification service

**Phase 4: Legacy Deprecation (Future)**
- ⏳ Flask service retirement
- ⏳ Direct FastAPI client integration
- ⏳ Performance optimization
- ⏳ Full microservices architecture

### Compatibility Layer
- Shared database models work with both Flask and FastAPI
- Common authentication utilities
- Unified configuration management
- Consistent error handling patterns

---

## Development Standards & Guidelines

### Code Organization Principles
**Based on**: Clean Architecture and Domain-Driven Design

**Module Boundaries:**
```
apps/[service]/
├── main.py              # FastAPI application setup
├── config.py            # Service-specific configuration
├── dependencies.py      # FastAPI dependencies
├── routers/            # API route handlers
│   ├── auth.py         # Authentication routes
│   └── data.py         # Data management routes  
├── services/           # Business logic layer
│   ├── auth_service.py # Authentication business logic
│   └── data_service.py # Data processing business logic
└── schemas/            # Pydantic models for validation
    ├── requests.py     # Request models
    └── responses.py    # Response models
```

**Dependency Injection Pattern:**
```python
# FastAPI dependency injection
from fastapi import Depends
from shared.database.connections.postgres import get_db

@app.get("/users/me")
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return current_user
```

### API Design
- **RESTful** - Standard HTTP methods and status codes  
- **Consistent** - Uniform request/response patterns
- **Versioned** - `/api/v1/` namespace for versioning
- **Documented** - Auto-generated OpenAPI documentation

### Database Design
- **Normalized** - Proper database normalization
- **Indexed** - Performance-critical fields indexed
- **Audit Trail** - Created/updated timestamps
- **Soft Deletes** - is_active flags instead of hard deletes

---

## Performance Optimization & Scalability

### Database Performance Strategy
**Focus**: Scalable database operations with proper resource management

**Connection Pool Configuration:**
```python
# SQLAlchemy async engine configuration
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    database_url,
    pool_size=10,           # Base connection pool size
    max_overflow=20,        # Additional connections under load
    pool_pre_ping=True,     # Validate connections before use
    pool_recycle=3600,      # Recycle connections every hour
    echo=settings.DEBUG     # SQL query logging in debug mode
)
```

**Query Optimization Guidelines:**
- Use async queries with `await` for all database operations
- Implement proper indexing on frequently queried columns
- Use `select_related()` equivalent for eager loading
- Batch operations using `bulk_insert()` for large datasets
- Monitor query performance with SQLAlchemy logging

### Service Communication
- **Connection Reuse** - Persistent HTTP connections
- **Timeout Management** - Prevent hanging requests
- **Circuit Breakers** - Fail fast for unhealthy services
- **Health Checks** - Regular service health monitoring

### Caching Architecture (Planned)
**Strategy**: Multi-layer caching for optimal performance

**Layer 1 - Application Cache:**
- In-memory caching for frequently accessed data
- TTL-based cache invalidation
- Cache warming strategies

**Layer 2 - Redis Cache:**
```python
# Redis configuration (planned)
REDIS_CONFIG = {
    "host": "localhost", 
    "port": 6379,
    "db": 0,
    "password": None,
    "socket_timeout": 5,
    "connection_pool_max_connections": 50
}

# Cache patterns
@cache(ttl=300)  # 5 minute cache
async def get_user_data_sources(user_id: int):
    return await db.query(DataSource).filter_by(user_id=user_id).all()
```

**Layer 3 - CDN/Static Cache:**
- Static asset caching for frontend resources
- API response caching for read-heavy endpoints
- Geographic distribution for global performance

---

## Monitoring, Metrics & Observability

### Health Check Implementation
**Purpose**: Comprehensive service health monitoring for load balancers and orchestration

**Health Endpoint Structure:**
```python
# /health endpoint implementation
from fastapi import APIRouter
from shared.database.connections.postgres import engine
import time

health_router = APIRouter()

@health_router.get("/health")
async def health_check():
    start_time = time.time()
    
    checks = {
        "database": await check_database_health(),
        "redis": await check_redis_health(),  # When implemented
        "external_apis": await check_external_services()
    }
    
    response_time = (time.time() - start_time) * 1000
    
    all_healthy = all(check["status"] == "healthy" for check in checks.values())
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "service": "api_gateway",  # or service name
        "version": "1.0.0",
        "uptime_seconds": get_uptime(),
        "response_time_ms": round(response_time, 2),
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Metrics Collection
- Request/response times (P50, P95, P99)
- Error rates by endpoint
- Service availability metrics
- Database query performance

### Logging Strategy
- **Structured Logging** - JSON format for parsing
- **Correlation IDs** - Track requests across services
- **Log Levels** - Appropriate log levels (DEBUG, INFO, WARN, ERROR)
- **Log Rotation** - Prevent disk space issues

---

## Troubleshooting & Common Issues

### Database Connection Issues
**Symptoms**: Service startup failures, 500 errors, connection timeouts

**Diagnostic Commands:**
```bash
# Check database connectivity
cd backend
uv run python -c "from shared.database.connections.postgres import engine; print('DB OK')"

# Test database with raw connection
uv run python scripts/test_db_connection.py

# Check connection pool status
psql -h localhost -U datalab_user -d datalab -c "SELECT count(*) FROM pg_stat_activity WHERE datname='datalab';"
```

**Common Solutions:**
- Verify PostgreSQL is running: `sudo systemctl status postgresql`
- Check connection string in `.env` file
- Ensure database exists: `createdb datalab`
- Check firewall settings for port 5432
- Verify user permissions: `GRANT ALL PRIVILEGES ON DATABASE datalab TO datalab_user;`

#### Authentication Issues  
```python
# Verify JWT token
from shared.utils.security import verify_jwt_token
user_id = verify_jwt_token(token)
```

#### Service Communication Issues
```python
# Check service health
curl http://localhost:8001/health
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with debug mode
uv run uvicorn apps.api_gateway.main:app --reload --log-level debug
```

---

## Integration Points & Cross-References

### Internal Documentation Links
**Primary References:**
- **[Root CLAUDE.md](../CLAUDE.md)**: MANDATORY package management and basic commands
- **[Development Guidelines](../.claude/CLAUDE.md)**: Architecture principles and code standards
- **[Frontend CLAUDE.md](../frontend/CLAUDE.md)**: Frontend-backend integration patterns

**Specialized Documentation:**
- **[Database Schema](./docs/database_schema.md)**: Complete database documentation
- **[API Specification](../docs/api_specification.md)**: OpenAPI documentation
- **[Security Guidelines](../docs/security/SECURITY.md)**: Security implementation details

### External Technical References
- **FastAPI**: https://fastapi.tiangolo.com/ - Modern Python web framework
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/ - Python SQL toolkit
- **Pydantic V2**: https://docs.pydantic.dev/ - Data validation library
- **UV Package Manager**: https://github.com/astral-sh/uv - Fast Python package manager
- **Alembic**: https://alembic.sqlalchemy.org/ - Database migrations

### Development Tools
- **VS Code Extensions**: Python, FastAPI, SQLAlchemy
- **Database Tools**: pgAdmin, DataGrip
- **API Testing**: Postman, HTTPie, curl

---

## Quick Start Checklist

### Prerequisites
- [ ] Read [Root CLAUDE.md](../CLAUDE.md) for mandatory UV usage rules
- [ ] PostgreSQL 12+ installed and running
- [ ] Python 3.10+ installed
- [ ] UV package manager installed

### 1. Environment Setup
```bash
cd backend
# Copy and configure environment
cp .env.example .env
# Edit .env with your database credentials

# Install dependencies with UV (MANDATORY)
uv install

# Install optional dependencies if needed
uv install --extra dev    # Development tools
uv install --extra mongo  # MongoDB support
```

### 2. Database Initialization
```bash
# Initialize database schema
uv run python scripts/init_database.py

# Run migrations if any
uv run alembic upgrade head

# Verify database connection
uv run python scripts/test_db_connection.py
```

### 3. Start Development Services
```bash
# Start all backend services
uv run python dev_server.py

# Or start specific services
uv run python dev_server.py api_gateway data_service
```

### 4. Verify Service Health
- [ ] API Gateway: http://localhost:8000/health
- [ ] API Documentation: http://localhost:8000/docs
- [ ] Data Service: http://localhost:8001/health
- [ ] Legacy Flask: http://localhost:8080/api/health

### 5. Test Authentication Flow
```bash
# Register test user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123", "first_name": "Test", "last_name": "User"}'

# Login and get JWT token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'

# Test protected endpoint with token
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" http://localhost:8000/api/v1/auth/profile
```

### 6. Run Test Suite
```bash
# Run all tests
uv run pytest tests/

# Run with coverage report
uv run pytest --cov=apps --cov=shared --cov-report=html tests/
```

---

## Context Management for Claude Code

This document provides comprehensive backend context for Claude Code AI. Key integration points:

1. **Package Management**: Always follow UV rules from [../CLAUDE.md](../CLAUDE.md)
2. **Architecture Standards**: Apply principles from [../.claude/CLAUDE.md](../.claude/CLAUDE.md)
3. **Frontend Coordination**: Reference [../frontend/CLAUDE.md](../frontend/CLAUDE.md) for full-stack features
4. **Database Operations**: Use shared models and connections consistently
5. **Security First**: Implement authentication and authorization at every layer
6. **Performance Awareness**: Consider scalability in all architectural decisions

This guide enables effective backend development while maintaining consistency with the overall project architecture and standards.