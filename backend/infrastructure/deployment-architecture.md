# FastAPI Microservices Deployment Architecture

## 1. Container-First Deployment Strategy (Recommended)

### Docker Compose for Development
```yaml
version: '3.8'

services:
  # Infrastructure Services
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: datalab
      POSTGRES_USER: user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d datalab"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  # API Gateway - Central routing and authentication
  api_gateway:
    build:
      context: .
      dockerfile: infrastructure/docker/Dockerfile.gateway
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - POSTGRES_HOST=postgres
      - REDIS_URL=redis://redis:6379
      - DATA_SERVICE_URL=http://data_service:8001
      - AI_SERVICE_URL=http://ai_service:8002
      - COMPUTE_SERVICE_URL=http://compute_service:8003
      - VIZ_SERVICE_URL=http://viz_service:8004
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Data Service - Data processing and management
  data_service:
    build:
      context: .
      dockerfile: infrastructure/docker/Dockerfile.data
    ports:
      - "8001:8001"
    environment:
      - POSTGRES_HOST=postgres
      - REDIS_URL=redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - data_uploads:/app/uploads
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # AI Service - ML and AI processing
  ai_service:
    build:
      context: .
      dockerfile: infrastructure/docker/Dockerfile.ai
    ports:
      - "8002:8002"
    environment:
      - POSTGRES_HOST=postgres
      - MODEL_CACHE_PATH=/app/models
    volumes:
      - ai_models:/app/models
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 60s
      timeout: 30s
      retries: 3

  # Compute Service - Heavy computational tasks
  compute_service:
    build:
      context: .
      dockerfile: infrastructure/docker/Dockerfile.compute
    ports:
      - "8003:8003"
    environment:
      - POSTGRES_HOST=postgres
      - WORKER_PROCESSES=4
    volumes:
      - compute_temp:/tmp/compute
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
      interval: 30s
      timeout: 15s
      retries: 3

  # Visualization Service
  viz_service:
    build:
      context: .
      dockerfile: infrastructure/docker/Dockerfile.viz
    ports:
      - "8004:8004"
    environment:
      - POSTGRES_HOST=postgres
    volumes:
      - viz_cache:/app/cache
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8004/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
  data_uploads:
  ai_models:
  compute_temp:
  viz_cache:

networks:
  default:
    driver: bridge
```

### Kubernetes Production Deployment
```yaml
# k8s-deployment.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: datalab-platform

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: datalab-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: datalab/api-gateway:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: POSTGRES_HOST
          value: "postgres-service"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10

---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway-service
  namespace: datalab-platform
spec:
  selector:
    app: api-gateway
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 2. Direct Server Deployment (Alternative)

### Systemd Service Configuration
```ini
# /etc/systemd/system/datalab-gateway.service
[Unit]
Description=DataLab API Gateway
After=network.target postgresql.service

[Service]
Type=exec
User=datalab
Group=datalab
WorkingDirectory=/opt/datalab/backend
Environment=PYTHONPATH=/opt/datalab/backend
ExecStart=/opt/datalab/.venv/bin/uvicorn apps.api_gateway.main:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Nginx Reverse Proxy Configuration
```nginx
# /etc/nginx/sites-available/datalab-platform
upstream api_gateway {
    server 127.0.0.1:8000;
    server 127.0.0.1:8000;  # Load balance multiple instances
    keepalive 32;
}

upstream data_service {
    server 127.0.0.1:8001;
    keepalive 16;
}

upstream ai_service {
    server 127.0.0.1:8002;
    keepalive 8;
}

upstream compute_service {
    server 127.0.0.1:8003;
    keepalive 8;
}

upstream viz_service {
    server 127.0.0.1:8004;
    keepalive 16;
}

server {
    listen 80;
    listen 443 ssl http2;
    server_name api.datalab.com;

    # SSL Configuration
    ssl_certificate /etc/ssl/certs/datalab.pem;
    ssl_certificate_key /etc/ssl/private/datalab.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    # Main API Gateway
    location /api/ {
        proxy_pass http://api_gateway;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 10s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Health checks (bypass gateway for direct service monitoring)
    location /health/gateway {
        proxy_pass http://api_gateway/health;
    }
    
    location /health/data {
        proxy_pass http://data_service/health;
    }
    
    location /health/ai {
        proxy_pass http://ai_service/health;
    }
    
    location /health/compute {
        proxy_pass http://compute_service/health;
    }
    
    location /health/viz {
        proxy_pass http://viz_service/health;
    }
}
```

## Resource Optimization Recommendations

### 1. API Gateway Optimization
- Use Gunicorn with multiple Uvicorn workers
- Implement connection pooling for downstream services
- Cache authentication tokens
- Use async/await throughout the codebase

### 2. Service-Specific Optimizations
- **Data Service**: Implement database connection pooling
- **AI Service**: Use model caching and batch processing
- **Compute Service**: Implement job queuing with Celery/RQ
- **Viz Service**: Cache rendered visualizations

### 3. Database Optimization
- Use read replicas for analytics queries
- Implement proper indexing strategy
- Use connection pooling (pgbouncer)
- Regular VACUUM and ANALYZE operations

### 4. Monitoring and Alerting
- Prometheus for metrics collection
- Grafana for visualization
- ELK stack for centralized logging
- Health check endpoints for all services