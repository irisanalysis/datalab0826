#!/bin/bash

# Legacy development server (redirects to new backend structure)
echo "🔄 Redirecting to new backend structure..."
echo "   Use: ./start_backend.sh for new backend services"
echo "   Use: cd backend && python apps/legacy_flask/main.py for Flask app"
echo ""

# For backward compatibility, run the legacy Flask app
cd backend && python apps/legacy_flask/main.py