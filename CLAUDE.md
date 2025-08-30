# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Package Management - MANDATORY RULES

### CRITICAL: Backend Development Rules
- **ALWAYS use UV (uv)** for all Python package operations in backend
- **NEVER use pip directly** - UV is the only allowed package manager
- **ALWAYS use pyproject.toml** for dependency management, NOT requirements.txt
- **Backend directory**: ALL backend development must use UV and pyproject.toml

### UV Package Manager Commands
```bash
# BACKEND: Create virtual environment (from backend directory)
cd backend
uv venv

# BACKEND: Install all dependencies from pyproject.toml
uv install

# BACKEND: Add new dependency
uv add package-name

# BACKEND: Add development dependency
uv add --dev package-name

# BACKEND: Remove dependency
uv remove package-name

# BACKEND: Update all dependencies
uv update

# BACKEND: Run Python scripts with UV
uv run python script.py

# BACKEND: Run specific command with UV
uv run uvicorn app.main:app --reload
```

## Documentation Cross-References

### Context Management for Claude Code
- **Frontend Development**: [frontend/CLAUDE.md](frontend/CLAUDE.md) - Frontend architecture, UI components, user experience patterns
- **Backend Development**: [backend/CLAUDE.md](backend/CLAUDE.md) - Backend architecture, file relationships, database models
- **Development Guidelines**: [.claude/CLAUDE.md](.claude/CLAUDE.md) - Architecture principles and coding standards
- **Documentation Index**: [docs/README.md](docs/README.md) - Complete project documentation structure

### When to Use Each Guide
- **This file (CLAUDE.md)**: Package management, basic commands, project overview
- **frontend/CLAUDE.md**: Frontend architecture, React components, UI/UX patterns, design system
- **backend/CLAUDE.md**: Backend system architecture, API design, database relationships
- **.claude/CLAUDE.md**: Development philosophy, coding standards, best practices

## Development Commands

### Environment Setup
```bash
# Backend setup (MANDATORY)
cd backend
uv venv
uv install

# Root project setup (legacy)
uv venv
uv pip install -e .
```

### Running the Application
```bash
# BACKEND: Start development server (RECOMMENDED)
cd backend
uv run python dev_server.py legacy_flask

# BACKEND: Run specific service
cd backend
uv run uvicorn apps.api_gateway.main:app --reload --port 8000

# BACKEND: Database initialization
python init_database_compatible.py  # From project root

# Legacy: Start with shell script
./start_backend.sh

# Root project legacy commands
uv run python -u -m flask --app main run -p $PORT --debug
uv run python main.py
```

### Testing
```bash
# BACKEND: Run tests with UV
cd backend
uv run pytest tests/

# BACKEND: Run specific test
cd backend
uv run python tests/integration/test_api.py

# Legacy tests
./tests/test_api.sh
./tests/test_e2e.sh
```

### Code Formatting
```bash
# BACKEND: Format with UV
cd backend
uv run autopep8 --in-place --recursive .

# BACKEND: Lint with UV
cd backend
uv run flake8 .

# Legacy formatting
uv run autopep8 --in-place --recursive .
```

## Architecture - Updated

This is a microservices architecture with FastAPI backend and modern Python tooling:

### Core Files (Updated Structure)
- **backend/apps/legacy_flask/main.py**: Migrated Flask application with JWT authentication
- **backend/pyproject.toml**: **MANDATORY** - Python project configuration and dependencies
- **backend/shared/**: Shared modules and utilities
- **init_database_compatible.py**: Database initialization script (project root)
- **start_backend.sh**: Backend startup script
- **.env**: Environment configuration (not in repo)
- **.env.example**: Environment template

### Directory Structure (Current)
- **backend/**: **PRIMARY** - All backend development happens here
  - **apps/**: Microservices applications
    - **legacy_flask/**: Migrated Flask application
    - **api_gateway/**: FastAPI API Gateway
    - **data_service/**: Data processing service
    - **ai_service/**: AI/ML service
  - **shared/**: Shared modules
    - **database/**: Database models and connections
    - **data_connectors/**: Data source connectors
    - **utils/**: Utility functions
  - **tests/**: Backend tests
  - **pyproject.toml**: **MANDATORY** dependency management
- **frontend/**: Frontend applications
- **.archive/**: Archived legacy files
- **docs/**: Documentation

### Backend Development Workflow
```bash
# 1. Always work in backend directory
cd backend

# 2. Ensure UV environment is activated
uv venv  # if not exists
uv install

# 3. Add new dependencies to pyproject.toml
uv add flask sqlalchemy

# 4. Run applications with UV
uv run python apps/legacy_flask/main.py
uv run uvicorn apps.api_gateway.main:app --reload

# 5. Run tests
uv run pytest tests/
```

### Features
- **UV Package Management**: Modern, fast Python package manager
- **pyproject.toml**: Modern Python project configuration
- **Microservices Architecture**: Modular, scalable backend services
- **JWT Authentication**: Secure token-based authentication
- **PostgreSQL Database**: Reliable database with SQLAlchemy ORM
- **FastAPI + Flask**: Modern API framework + legacy compatibility
- **Automated Testing**: Comprehensive test suite
- **Environment Management**: Proper environment variable handling

## Key Files (Updated)

- **backend/pyproject.toml** - **MANDATORY** dependency management
- **backend/apps/legacy_flask/main.py** - Migrated Flask application
- **backend/shared/data_connectors/connectors.py** - Data source connections
- **init_database_compatible.py** - Database initialization (project root)
- **start_backend.sh** - Backend startup script
- **backend/dev_server.py** - Development server launcher

## Documentation Cross-References

### Specialized Context Documentation
- **[backend/CLAUDE.md](backend/CLAUDE.md)** - Comprehensive backend architecture, API design, database schema, and microservices patterns
- **[frontend/CLAUDE.md](frontend/CLAUDE.md)** - Frontend development guide with Next.js, React, and UI patterns
- **[.claude/CLAUDE.md](.claude/CLAUDE.md)** - Development philosophy, architecture principles, and quality standards

### When to Use Each Guide
- **Root CLAUDE.md (this file)**: Package management rules, basic commands, project structure overview
- **Backend CLAUDE.md**: Database models, API endpoints, authentication, service architecture, testing
- **Frontend CLAUDE.md**: React components, Next.js routing, state management, UI/UX patterns
- **Development CLAUDE.md**: Architecture decisions, code quality standards, security guidelines

## Development Rules

### MUST FOLLOW:
1. **USE UV ONLY**: Never use pip in backend development
2. **USE pyproject.toml**: All dependencies managed in pyproject.toml
3. **Work in backend/**: Primary development directory
4. **Use uv run**: Execute all Python scripts with `uv run`
5. **Test with UV**: All testing must use `uv run pytest` or `uv run python`

### Package Management Examples:
```bash
# ✅ CORRECT: Add Flask dependency
cd backend
uv add flask

# ✅ CORRECT: Add development tool
cd backend
uv add --dev pytest

# ✅ CORRECT: Run application
cd backend
uv run python apps/legacy_flask/main.py

# ❌ WRONG: Using pip
pip install flask

# ❌ WRONG: Using requirements.txt
pip install -r requirements.txt
```

### Quick Start Guide:
1. `cd backend`
2. `uv venv` (if needed)
3. `uv install`
4. `uv run python dev_server.py legacy_flask`

Remember: **UV + pyproject.toml is mandatory for all backend development!**

---

## Context Integration Notes for Claude Code

This root CLAUDE.md provides **mandatory package management rules** that override any conflicting instructions. The specialized documentation files provide deeper context:

**Architecture & Design**: See [.claude/CLAUDE.md](.claude/CLAUDE.md) for development philosophy, quality standards, and architectural decision-making frameworks.

**Backend Development**: See [backend/CLAUDE.md](backend/CLAUDE.md) for comprehensive backend context including microservices architecture, database schema, API design patterns, authentication systems, and deployment strategies.

**Frontend Development**: See [frontend/CLAUDE.md](frontend/CLAUDE.md) for React/Next.js patterns, component architecture, state management, and UI/UX implementation.

**File Placement**: Always follow the repository architecture guidelines in [.claude/CLAUDE.md](.claude/CLAUDE.md) for proper file organization and development script placement.