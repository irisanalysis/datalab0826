# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Create virtual environment with uv
uv venv

# Install project dependencies
uv pip install -e .
```

### Running the Application
```bash
# Start development server with hot reload
./devserver.sh

# Or manually with uv:
uv run python -u -m flask --app main run -p $PORT --debug

# Run without debug mode
uv run python main.py

# Run with Docker (from docker/ directory)
cd docker && docker-compose up -d
```

### Testing
```bash
# Run API tests
./tests/test_api.sh

# Run E2E tests
./tests/test_e2e.sh
```

### Code Formatting
```bash
# Format Python code
uv run autopep8 --in-place --recursive .
```

## Architecture

This is a Flask web application with JWT authentication and PostgreSQL database:

### Core Files
- **main.py**: Flask application with JWT authentication, SQLAlchemy models, and API endpoints
- **src/index.html**: Static HTML frontend served at root route
- **pyproject.toml**: Python project configuration and dependencies
- **devserver.sh**: Development server startup script
- **requirements.txt**: Python dependencies
- **.env**: Environment configuration (not in repo)
- **.env.example**: Environment template

### Directory Structure
- **api/**: FastAPI backend (separate service)
- **web/**: Next.js frontend (separate service)
- **src/**: Static HTML files for Flask app
- **docs/**: Documentation (README, SECURITY, INSTALL guides)
- **tests/**: Test scripts and files
- **scripts/**: Utility and deployment scripts
- **docker/**: Docker-related files (docker-compose.yml)
- **tools/**: CLI tools and dependencies

### Features
- JWT access and refresh tokens
- PostgreSQL database with SQLAlchemy
- User authentication (register, login, logout)
- Password hashing with bcrypt
- CORS support
- Health check endpoint

## Key Files

- `main.py:90` - Main route handler serving HTML file
- `main.py:246` - Port configuration and app startup
- `main.py:94-230` - Authentication API endpoints
- `devserver.sh` - Development server command using uv with Flask debug mode
- `docker/docker-compose.yml` - Multi-service Docker setup
- `tests/test_api.sh` - API testing script