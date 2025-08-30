#!/bin/bash

# AI Data Analysis Platform - Complete Setup Script  
# Updated for new backend architecture

set -e  # Exit on any error

echo "======================================================================"
echo "🚀 AI Data Analysis Platform - Complete Setup"
echo "======================================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running from correct directory
if [ ! -f "start_backend.sh" ] || [ ! -d "backend" ]; then
    print_error "Please run this script from the project root directory"
    print_error "Expected files: start_backend.sh, backend/ directory"
    exit 1
fi

print_status "Checking prerequisites..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed. Please install uv first:"
    print_error "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

print_success "uv is installed"

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found, creating from .env.example"
    
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Please edit .env file and set your database credentials and secrets"
        print_warning "Important: Change JWT_SECRET and ENCRYPTION_KEY to secure values"
    else
        print_error ".env.example file not found"
        exit 1
    fi
fi

print_status "Setting up Python virtual environment..."

# Create virtual environment
uv venv

print_success "Virtual environment created"

print_status "Installing Python dependencies..."

# Install dependencies
uv pip install -e .

# Install additional dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    uv pip install -r requirements.txt
fi

print_success "Python dependencies installed"

print_status "Setting up database..."

# Check if database is accessible
if ! uv run python -c "from main import db; from main import app; app.app_context().push(); db.session.execute(db.text('SELECT 1'))" 2>/dev/null; then
    print_error "Cannot connect to database. Please check your .env configuration:"
    print_error "- POSTGRES_HOST"
    print_error "- POSTGRES_PORT" 
    print_error "- POSTGRES_DB"
    print_error "- POSTGRES_USER"
    print_error "- POSTGRES_PASSWORD"
    exit 1
fi

print_success "Database connection successful"

print_status "Running database migrations..."

# Run migrations
if ! uv run python migrate_database.py; then
    print_error "Database migration failed"
    exit 1
fi

print_success "Database migrations completed"

print_status "Initializing database with sample data..."

# Initialize database
if ! uv run python init_saas_database.py; then
    print_error "Database initialization failed"
    exit 1
fi

print_success "Database initialization completed"

print_status "Setting file permissions..."

# Make scripts executable
chmod +x devserver.sh
chmod +x tests/test_api.sh
chmod +x tests/test_e2e.sh
chmod +x setup_saas_platform.sh

if [ -f "test_saas_api.py" ]; then
    chmod +x test_saas_api.py
fi

print_success "File permissions set"

echo ""
echo "======================================================================"
echo "✅ SaaS Data Analysis Platform Setup Complete!"
echo "======================================================================"

echo ""
echo "📋 Next Steps:"
echo ""
echo "1. 🔧 Configure Environment:"
echo "   - Edit .env file with your actual database credentials"
echo "   - Generate secure JWT_SECRET and ENCRYPTION_KEY"
echo ""
echo "2. 🚀 Start the Development Server:"
echo "   ./devserver.sh"
echo "   # OR manually:"
echo "   uv run python main.py"
echo ""
echo "3. 🧪 Test the API:"
echo "   python test_saas_api.py"
echo ""
echo "4. 🌐 Access the Platform:"
echo "   - API Base URL: http://localhost:8000"
echo "   - Health Check: http://localhost:8000/api/healthz"
echo "   - Frontend: http://localhost:8000/ (static HTML)"
echo ""
echo "5. 👥 Sample Users (for testing):"
echo "   - Admin: admin@example.com (Password: AdminPass123!)"
echo "   - Analyst: analyst@example.com (Password: AnalystPass123!)"  
echo "   - Viewer: viewer@example.com (Password: ViewerPass123!)"
echo ""
echo "6. 🔐 Security Reminders:"
echo "   - Change default passwords in production"
echo "   - Update JWT_SECRET and ENCRYPTION_KEY"
echo "   - Configure CORS_ORIGINS for your domain"
echo "   - Set FLASK_ENV=production for production deployment"
echo ""
echo "📚 Available Endpoints:"
echo ""
echo "Authentication:"
echo "  POST /api/auth/register    - User registration"
echo "  POST /api/auth/login       - User login with session tracking"
echo "  POST /api/auth/refresh     - Refresh access token"
echo "  POST /api/auth/logout      - Logout"
echo ""
echo "User Management:"
echo "  GET  /api/me               - Get current user info"
echo "  PUT  /api/user/profile     - Update user profile"
echo "  GET  /api/user/sessions    - Get active sessions"
echo "  DEL  /api/user/sessions/{id} - Revoke session"
echo ""
echo "Data Sources:"
echo "  GET  /api/data-sources     - List user's data sources"
echo "  POST /api/data-sources     - Create new data source"
echo "  POST /api/data-sources/{id}/test - Test connection"
echo "  GET  /api/data-sources/{id}/schema - Get data schema"
echo "  POST /api/data-sources/{id}/query - Query data"
echo ""
echo "Monitoring:"
echo "  GET  /api/user/audit-logs  - Get audit logs"
echo "  GET  /api/user/integrations - Get integrations"
echo "  GET  /api/healthz          - Health check"
echo ""
echo "🎉 Happy coding! Your SaaS Data Analysis Platform is ready to use."
echo "======================================================================"