# DataLab Flask Authentication System

A Flask web application with JWT-based authentication, PostgreSQL database, and comprehensive API endpoints.

## Quick Start

1. **Setup Environment**
   ```bash
   # Create virtual environment
   uv venv
   
   # Install dependencies
   uv pip install -e .
   
   # Copy environment template
   cp .env.example .env
   # Edit .env with your database credentials
   ```

2. **Run Development Server**
   ```bash
   ./devserver.sh
   ```

3. **Run with Docker**
   ```bash
   cd docker
   docker-compose up -d
   ```

## Features

- 🔐 JWT Authentication (access & refresh tokens)
- 👤 User registration and login
- 🛡️ Password hashing with bcrypt
- 🗄️ PostgreSQL database with SQLAlchemy
- 🌐 CORS support
- 🏥 Health check endpoint
- 📊 Comprehensive API testing

## API Endpoints

- `GET /` - Serve static HTML frontend
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/logout` - User logout
- `GET /api/me` - Get current user info
- `GET /api/healthz` - Health check

## Project Structure

```
├── main.py              # Main Flask application
├── src/                 # Static HTML files
├── api/                 # FastAPI backend service
├── web/                 # Next.js frontend service
├── docs/                # Documentation
├── tests/               # Test scripts
├── scripts/             # Utility scripts
├── docker/              # Docker configuration
└── tools/               # CLI tools
```

## Documentation

- [Installation Guide](docs/INSTALL.md)
- [Security Guide](docs/SECURITY.md)
- [Authentication System](docs/AUTH_SYSTEM_README.md)
- [Development Guide](CLAUDE.md)

## Testing

```bash
# Test API endpoints
./tests/test_api.sh

# Run E2E tests
./tests/test_e2e.sh
```

## Environment Variables

See `.env.example` for required environment variables including database connection, JWT secrets, and token expiration settings.