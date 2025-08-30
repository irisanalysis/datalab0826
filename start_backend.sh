#!/bin/bash

# AI Data Platform - Backend Startup Script
echo "🌟 Starting AI Data Platform Backend Services"
echo "============================================="

# Check if we're in the right directory
if [ ! -f "backend/dev_server.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if .env exists in backend directory
if [ ! -f "backend/.env" ]; then
    echo "⚠️  No backend/.env file found. Copying from .env.example..."
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo "✅ Created backend/.env from template"
        echo "📝 Please edit backend/.env with your configuration"
    else
        echo "❌ No backend/.env.example found"
        exit 1
    fi
fi

# Check if root .env exists and use it as fallback
if [ -f ".env" ]; then
    echo "📋 Using root .env as additional configuration source"
    # Export variables from root .env
    set -a
    source .env
    set +a
fi

# Change to backend directory
cd backend

# Check if UV virtual environment exists
if [ ! -d ".uv-venv" ]; then
    echo "📦 Creating UV virtual environment..."
    uv venv .uv-venv
fi

# Install dependencies with UV if needed
if [ ! -f ".uv-venv/pyvenv.cfg" ] || [ "pyproject.toml" -nt ".uv-venv/pyvenv.cfg" ]; then
    echo "📥 Installing Python dependencies with UV..."
    source .uv-venv/bin/activate
    uv pip install -e .
    deactivate
fi

# Start the development server with UV
echo "🚀 Starting backend services with UV..."
echo ""
uv run python dev_server.py legacy_flask