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
```

### Code Formatting
```bash
# Format Python code
uv run autopep8 --in-place --recursive .
```

## Architecture

This is a minimal Flask web application with the following structure:

- **main.py**: Flask application entry point with single route serving static HTML
- **src/index.html**: Static HTML content served at root route
- **pyproject.toml**: Python project configuration and dependencies managed by uv
- **devserver.sh**: Development server startup script using uv
- **.idx/dev.nix**: IDX workspace configuration with Python 3, Node.js 20, and automatic setup

The application follows a simple pattern:
- Single Flask route (`/`) serves static HTML file
- No templates, database, or complex routing
- Development environment uses uv to manage dependencies and run Flask's development server with debug mode
- Port configured via environment variable (defaults to 80)

## Key Files

- `main.py:8` - Main route handler serving HTML file
- `main.py:12` - Port configuration from environment
- `devserver.sh:2` - Development server command using uv with Flask debug mode