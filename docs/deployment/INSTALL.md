# Authentication System Installation Guide

A production-ready authentication system built with FastAPI (backend) and Next.js 14 (frontend), featuring secure JWT authentication with refresh tokens, comprehensive security measures, and Docker deployment.

## 🚀 Quick Start

Get the system running with a single command:

```bash
# Copy environment configuration
cp .env.example .env

# Start all services with Docker Compose
cd docker && docker compose up --build
```

**Access Points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs (Swagger UI)
- Health Check: http://localhost:8000/healthz

## 📋 Prerequisites

- Docker & Docker Compose
- Git

## 🔐 Environment Configuration

Key environment variables in `.env`:

```bash
# Database
POSTGRES_DB=datairis
POSTGRES_USER=jackchan
POSTGRES_PASSWORD=secure_password_123

# Security
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
ACCESS_TTL=900    # 15 minutes
REFRESH_TTL=604800 # 7 days

# CORS (adjust for your domain)
CORS_ORIGINS=http://web:3000,http://localhost:3000

# Frontend
NEXT_PUBLIC_API_BASE=http://api:8000
```

**Production Security Notes:**
- Change `JWT_SECRET` to a cryptographically secure random string
- Set `COOKIE_SECURE=true` when using HTTPS
- Configure `COOKIE_DOMAIN` for your domain
- Use strong database passwords

## 🧪 Testing the System

### Manual Testing Flow

1. **Health Check:**
```bash
curl http://localhost:8000/healthz
```

2. **Register a User:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -H "X-Requested-With: XMLHttpRequest" \
  -d '{"email": "test@example.com", "password": "TestPass123"}'
```

3. **Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -H "X-Requested-With: XMLHttpRequest" \
  -c cookies.txt \
  -d '{"email": "test@example.com", "password": "TestPass123"}'
```

4. **Access Protected Resource:**
```bash
curl -X GET http://localhost:8000/api/me \
  -b cookies.txt
```

5. **Refresh Token:**
```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -b cookies.txt \
  -c cookies.txt
```

6. **Logout:**
```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -b cookies.txt
```

### Frontend Testing

1. Visit http://localhost:3000
2. Click "Create Account" → Register with email/password
3. Login with credentials
4. Access dashboard (protected route)
5. Logout and verify redirect to login

## 🚨 Common Issues & Troubleshooting

### Port Conflicts
If ports 3000, 8000, or 5432 are in use:
```bash
# Check what's using the ports
sudo lsof -i :3000
sudo lsof -i :8000
sudo lsof -i :5432

# Stop conflicting services or modify docker/docker-compose.yml ports
```

### CORS Issues
If frontend can't reach backend:
1. Check `CORS_ORIGINS` in `.env` includes your frontend URL
2. Verify `NEXT_PUBLIC_API_BASE` points to correct backend URL
3. Ensure custom headers are being sent (`X-Requested-With`)

### Cookie Issues
If authentication cookies aren't working:
1. Check `COOKIE_SECURE` setting (should be `false` for HTTP development)
2. Verify `SameSite` policy (`Lax` for cross-tab compatibility)
3. Ensure domains match between frontend and backend

### Database Migration Issues
```bash
# Run migrations manually
cd docker && docker compose exec api alembic upgrade head

# Create new migration
cd docker && docker compose exec api alembic revision --autogenerate -m "description"
```