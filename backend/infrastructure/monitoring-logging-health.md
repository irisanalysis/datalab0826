# Monitoring, Logging & Health Checks Strategy

## 1. Comprehensive Monitoring Stack

### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alertmanager_config:
  alertmanagers:
  - static_configs:
    - targets:
      - alertmanager:9093

scrape_configs:
  # API Gateway monitoring
  - job_name: 'api-gateway'
    static_configs:
    - targets: ['api-gateway:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  # Individual service monitoring
  - job_name: 'data-service'
    static_configs:
    - targets: ['data-service:8001']
    metrics_path: '/metrics'

  - job_name: 'ai-service'
    static_configs:
    - targets: ['ai-service:8002']
    metrics_path: '/metrics'
    scrape_interval: 30s  # Less frequent due to heavy workloads

  - job_name: 'compute-service'
    static_configs:
    - targets: ['compute-service:8003']
    metrics_path: '/metrics'

  - job_name: 'viz-service'
    static_configs:
    - targets: ['viz-service:8004']
    metrics_path: '/metrics'

  # Infrastructure monitoring
  - job_name: 'node-exporter'
    static_configs:
    - targets: ['node-exporter:9100']

  - job_name: 'postgres-exporter'
    static_configs:
    - targets: ['postgres-exporter:9187']

  - job_name: 'redis-exporter'
    static_configs:
    - targets: ['redis-exporter:9121']
```

### Grafana Dashboard Configuration
```json
{
  "dashboard": {
    "title": "DataLab Platform Overview",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total[5m])) by (service)",
            "legendFormat": "{{service}}"
          }
        ]
      },
      {
        "title": "Response Times (P95)",
        "type": "graph", 
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) by (service)",
            "legendFormat": "{{service}} P95"
          }
        ]
      },
      {
        "title": "Error Rates",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{status=~'5..'}[5m])) by (service) / sum(rate(http_requests_total[5m])) by (service)",
            "legendFormat": "{{service}} Error Rate"
          }
        ]
      },
      {
        "title": "Service Health Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up",
            "legendFormat": "{{job}}"
          }
        ]
      }
    ]
  }
}
```

## 2. FastAPI Metrics Implementation

### Prometheus Metrics Middleware
```python
# shared/monitoring/prometheus_middleware.py
import time
import structlog
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status', 'service']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint', 'service'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_active',
    'Currently active HTTP requests',
    ['service']
)

DATABASE_CONNECTIONS = Gauge(
    'database_connections_active',
    'Active database connections',
    ['service']
)

MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes',
    ['service']
)

class PrometheusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, service_name: str):
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip metrics endpoint to avoid recursion
        if request.url.path == "/metrics":
            return await call_next(request)

        start_time = time.time()
        
        # Increment active requests
        ACTIVE_REQUESTS.labels(service=self.service_name).inc()
        
        try:
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code,
                service=self.service_name
            ).inc()
            
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.url.path,
                service=self.service_name
            ).observe(duration)
            
            return response
            
        except Exception as e:
            # Record error metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=500,
                service=self.service_name
            ).inc()
            
            logger.error(
                "Request processing failed",
                service=self.service_name,
                endpoint=request.url.path,
                error=str(e)
            )
            raise
            
        finally:
            # Decrement active requests
            ACTIVE_REQUESTS.labels(service=self.service_name).dec()


def update_system_metrics(service_name: str):
    """Update system-level metrics"""
    import psutil
    import gc
    
    # Memory usage
    memory_info = psutil.Process().memory_info()
    MEMORY_USAGE.labels(service=service_name).set(memory_info.rss)
    
    # Database connections (if using SQLAlchemy)
    try:
        from shared.database.connection import engine
        pool = engine.pool
        DATABASE_CONNECTIONS.labels(service=service_name).set(
            pool.checkedout() if hasattr(pool, 'checkedout') else 0
        )
    except ImportError:
        pass

# Metrics endpoint
async def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

### Service-Specific Health Checks
```python
# shared/monitoring/health_checks.py
import asyncio
import time
import structlog
from typing import Dict, Any, List
from enum import Enum
from dataclasses import dataclass, field

logger = structlog.get_logger()

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class HealthCheck:
    name: str
    check_function: callable
    timeout: float = 5.0
    critical: bool = True
    last_result: Dict[str, Any] = field(default_factory=dict)
    last_check: float = 0

class HealthChecker:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.checks: List[HealthCheck] = []
        self.startup_time = time.time()
        
    def add_check(self, check: HealthCheck):
        """Add a health check"""
        self.checks.append(check)
        logger.info(
            "Health check added",
            service=self.service_name,
            check=check.name,
            critical=check.critical
        )
    
    async def run_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {
            "service": self.service_name,
            "status": HealthStatus.HEALTHY.value,
            "timestamp": time.time(),
            "uptime": time.time() - self.startup_time,
            "checks": {}
        }
        
        critical_failures = 0
        non_critical_failures = 0
        
        # Run checks concurrently
        check_tasks = []
        for check in self.checks:
            task = asyncio.create_task(self._run_single_check(check))
            check_tasks.append((check, task))
        
        # Collect results
        for check, task in check_tasks:
            try:
                check_result = await task
                results["checks"][check.name] = check_result
                
                if check_result["status"] != HealthStatus.HEALTHY.value:
                    if check.critical:
                        critical_failures += 1
                    else:
                        non_critical_failures += 1
                        
            except Exception as e:
                logger.error(
                    "Health check failed",
                    service=self.service_name,
                    check=check.name,
                    error=str(e)
                )
                
                results["checks"][check.name] = {
                    "status": HealthStatus.UNHEALTHY.value,
                    "message": f"Check failed: {str(e)}",
                    "duration": 0
                }
                
                if check.critical:
                    critical_failures += 1
                else:
                    non_critical_failures += 1
        
        # Determine overall status
        if critical_failures > 0:
            results["status"] = HealthStatus.UNHEALTHY.value
        elif non_critical_failures > 0:
            results["status"] = HealthStatus.DEGRADED.value
        
        return results
    
    async def _run_single_check(self, check: HealthCheck) -> Dict[str, Any]:
        """Run a single health check"""
        start_time = time.time()
        
        try:
            result = await asyncio.wait_for(
                check.check_function(),
                timeout=check.timeout
            )
            
            duration = time.time() - start_time
            check.last_check = time.time()
            
            if isinstance(result, dict):
                check_result = result
                check_result["duration"] = duration
            else:
                check_result = {
                    "status": HealthStatus.HEALTHY.value if result else HealthStatus.UNHEALTHY.value,
                    "duration": duration
                }
                
            check.last_result = check_result
            return check_result
            
        except asyncio.TimeoutError:
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "message": f"Check timed out after {check.timeout}s",
                "duration": check.timeout
            }

# Common health check functions
async def database_health_check() -> Dict[str, Any]:
    """Check database connectivity"""
    try:
        from shared.database.connection import get_database
        
        db = get_database()
        # Simple query to test connectivity
        result = await db.execute("SELECT 1")
        
        return {
            "status": HealthStatus.HEALTHY.value,
            "message": "Database connection successful"
        }
        
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY.value,
            "message": f"Database connection failed: {str(e)}"
        }

async def redis_health_check() -> Dict[str, Any]:
    """Check Redis connectivity"""
    try:
        import redis.asyncio as redis
        
        r = redis.Redis.from_url("redis://localhost:6379")
        await r.ping()
        
        return {
            "status": HealthStatus.HEALTHY.value,
            "message": "Redis connection successful"
        }
        
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY.value,
            "message": f"Redis connection failed: {str(e)}"
        }

async def disk_space_health_check() -> Dict[str, Any]:
    """Check disk space availability"""
    try:
        import psutil
        
        disk_usage = psutil.disk_usage('/')
        free_percent = (disk_usage.free / disk_usage.total) * 100
        
        if free_percent < 5:
            status = HealthStatus.UNHEALTHY.value
            message = f"Critical: Only {free_percent:.1f}% disk space remaining"
        elif free_percent < 15:
            status = HealthStatus.DEGRADED.value
            message = f"Warning: Only {free_percent:.1f}% disk space remaining"
        else:
            status = HealthStatus.HEALTHY.value
            message = f"Disk space OK: {free_percent:.1f}% free"
            
        return {
            "status": status,
            "message": message,
            "free_percent": free_percent
        }
        
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY.value,
            "message": f"Disk space check failed: {str(e)}"
        }

async def memory_health_check() -> Dict[str, Any]:
    """Check memory usage"""
    try:
        import psutil
        
        memory = psutil.virtual_memory()
        used_percent = memory.percent
        
        if used_percent > 90:
            status = HealthStatus.UNHEALTHY.value
            message = f"Critical: {used_percent:.1f}% memory usage"
        elif used_percent > 80:
            status = HealthStatus.DEGRADED.value
            message = f"Warning: {used_percent:.1f}% memory usage"
        else:
            status = HealthStatus.HEALTHY.value
            message = f"Memory usage OK: {used_percent:.1f}%"
            
        return {
            "status": status,
            "message": message,
            "used_percent": used_percent
        }
        
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY.value,
            "message": f"Memory check failed: {str(e)}"
        }
```

## 3. Structured Logging Implementation

### Centralized Logging Configuration
```python
# shared/logging/config.py
import structlog
import logging
import sys
from typing import Any, Dict
import json
import time

def configure_logging(service_name: str, log_level: str = "INFO"):
    """Configure structured logging for the service"""
    
    def add_service_name(logger, method_name, event_dict):
        event_dict["service"] = service_name
        return event_dict
    
    def add_timestamp(logger, method_name, event_dict):
        event_dict["timestamp"] = time.time()
        event_dict["iso_timestamp"] = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime())
        return event_dict
    
    def add_correlation_id(logger, method_name, event_dict):
        # This would typically extract correlation ID from context
        # For now, we'll add a placeholder
        event_dict["correlation_id"] = getattr(structlog.contextvars, 'correlation_id', None)
        return event_dict

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            add_service_name,
            add_timestamp,
            add_correlation_id,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.JSONRenderer() if log_level != "DEBUG" else structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

# Correlation ID middleware for FastAPI
class CorrelationIdMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Extract or generate correlation ID
            headers = dict(scope["headers"])
            correlation_id = headers.get(b"x-correlation-id", b"").decode()
            
            if not correlation_id:
                import uuid
                correlation_id = str(uuid.uuid4())
            
            # Set correlation ID in context
            token = structlog.contextvars.bind_contextvars(
                correlation_id=correlation_id
            )
            
            try:
                await self.app(scope, receive, send)
            finally:
                token.__exit__(None, None, None)
        else:
            await self.app(scope, receive, send)
```

## 4. Alert Rules Configuration

### Prometheus Alert Rules
```yaml
# alert_rules.yml
groups:
- name: datalab_platform_alerts
  rules:
  
  # High-level service alerts
  - alert: ServiceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Service {{ $labels.job }} is down"
      description: "Service {{ $labels.job }} has been down for more than 1 minute"

  - alert: HighErrorRate
    expr: sum(rate(http_requests_total{status=~"5.."}[5m])) by (service) / sum(rate(http_requests_total[5m])) by (service) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate on {{ $labels.service }}"
      description: "Error rate is {{ $value | humanizePercentage }} on {{ $labels.service }}"

  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time on {{ $labels.service }}"
      description: "95th percentile response time is {{ $value }}s on {{ $labels.service }}"

  # Resource alerts
  - alert: HighMemoryUsage
    expr: memory_usage_bytes / (1024^3) > 8  # 8GB threshold
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage on {{ $labels.service }}"
      description: "Memory usage is {{ $value }}GB on {{ $labels.service }}"

  - alert: DatabaseConnectionHigh
    expr: database_connections_active > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High database connection count"
      description: "Database connections: {{ $value }} on {{ $labels.service }}"

  # Business logic alerts
  - alert: AIServiceProcessingDelay
    expr: increase(http_request_duration_seconds_sum{service="ai-service"}[5m]) / increase(http_requests_total{service="ai-service"}[5m]) > 30
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "AI Service experiencing processing delays"
      description: "Average processing time is {{ $value }}s for AI Service"
```

### Health Check Integration
```python
# Integration in FastAPI services
from shared.monitoring.health_checks import HealthChecker, HealthCheck
from shared.monitoring.health_checks import (
    database_health_check,
    redis_health_check,
    disk_space_health_check,
    memory_health_check
)

# Initialize health checker for each service
def setup_health_checks(app: FastAPI, service_name: str):
    health_checker = HealthChecker(service_name)
    
    # Add common checks
    health_checker.add_check(HealthCheck(
        name="database",
        check_function=database_health_check,
        critical=True
    ))
    
    health_checker.add_check(HealthCheck(
        name="memory",
        check_function=memory_health_check,
        critical=False
    ))
    
    health_checker.add_check(HealthCheck(
        name="disk_space", 
        check_function=disk_space_health_check,
        critical=True
    ))
    
    # Service-specific checks
    if service_name == "api-gateway":
        health_checker.add_check(HealthCheck(
            name="redis",
            check_function=redis_health_check,
            critical=False
        ))
    
    # Store health checker in app state
    app.state.health_checker = health_checker
    
    # Add health endpoint
    @app.get("/health")
    async def health_endpoint():
        return await health_checker.run_checks()
```

This comprehensive monitoring strategy provides:

1. **Real-time metrics** via Prometheus and Grafana
2. **Structured logging** with correlation IDs
3. **Comprehensive health checks** for all services
4. **Proactive alerting** based on SLIs/SLOs
5. **Business logic monitoring** specific to AI and data processing workloads