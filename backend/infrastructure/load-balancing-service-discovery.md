# Load Balancing & Service Discovery Strategy

## 1. Load Balancing Architecture

### HAProxy Configuration (Recommended for Production)
```haproxy
# /etc/haproxy/haproxy.cfg
global
    daemon
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin
    stats timeout 30s
    user haproxy
    group haproxy

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms
    option httplog
    option dontlognull
    errorfile 400 /etc/haproxy/errors/400.http
    errorfile 403 /etc/haproxy/errors/403.http
    errorfile 408 /etc/haproxy/errors/408.http
    errorfile 500 /etc/haproxy/errors/500.http
    errorfile 502 /etc/haproxy/errors/502.http
    errorfile 503 /etc/haproxy/errors/503.http
    errorfile 504 /etc/haproxy/errors/504.http

# Statistics page
listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 30s
    stats admin if TRUE

# Frontend - Entry point
frontend datalab_frontend
    bind *:80
    bind *:443 ssl crt /etc/ssl/certs/datalab.pem
    
    # HTTP to HTTPS redirect
    redirect scheme https code 301 if !{ ssl_fc }
    
    # ACL for different service routes
    acl is_api_gateway path_beg /api/v1/
    acl is_direct_data path_beg /data/
    acl is_direct_ai path_beg /ai/
    acl is_direct_compute path_beg /compute/
    acl is_direct_viz path_beg /viz/
    
    # Health checks
    acl is_health_check path_beg /health/
    
    # Route to backends
    use_backend api_gateway_backend if is_api_gateway
    use_backend data_service_backend if is_direct_data
    use_backend ai_service_backend if is_direct_ai
    use_backend compute_service_backend if is_direct_compute
    use_backend viz_service_backend if is_direct_viz
    use_backend health_check_backend if is_health_check
    
    # Default to API Gateway
    default_backend api_gateway_backend

# API Gateway Backend - Primary entry point
backend api_gateway_backend
    balance roundrobin
    option httpchk GET /health
    http-check expect status 200
    
    # Multiple instances for high availability
    server gateway1 10.0.1.10:8000 check inter 10s rise 2 fall 3
    server gateway2 10.0.1.11:8000 check inter 10s rise 2 fall 3
    server gateway3 10.0.1.12:8000 check inter 10s rise 2 fall 3

# Direct service backends (for bypassing gateway when needed)
backend data_service_backend
    balance roundrobin
    option httpchk GET /health
    http-check expect status 200
    
    server data1 10.0.2.10:8001 check inter 15s rise 2 fall 3
    server data2 10.0.2.11:8001 check inter 15s rise 2 fall 3

backend ai_service_backend
    balance leastconn  # AI workloads benefit from least connections
    option httpchk GET /health
    http-check expect status 200
    timeout server 300s  # AI operations may take longer
    
    server ai1 10.0.3.10:8002 check inter 20s rise 2 fall 3
    server ai2 10.0.3.11:8002 check inter 20s rise 2 fall 3

backend compute_service_backend
    balance leastconn
    option httpchk GET /health
    http-check expect status 200
    timeout server 600s  # Long-running computations
    
    server compute1 10.0.4.10:8003 check inter 30s rise 2 fall 3
    server compute2 10.0.4.11:8003 check inter 30s rise 2 fall 3

backend viz_service_backend
    balance roundrobin
    option httpchk GET /health
    http-check expect status 200
    
    server viz1 10.0.5.10:8004 check inter 10s rise 2 fall 3
    server viz2 10.0.5.11:8004 check inter 10s rise 2 fall 3

# Health check aggregation backend
backend health_check_backend
    balance roundrobin
    server health_monitor 127.0.0.1:8090 check
```

## 2. Service Discovery Implementation

### Consul-Based Service Discovery
```python
# shared/service_discovery/consul_client.py
import consul
import asyncio
import structlog
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = structlog.get_logger()

@dataclass
class ServiceInfo:
    name: str
    address: str
    port: int
    health: str
    tags: List[str]

class ConsulServiceDiscovery:
    def __init__(self, consul_host: str = "localhost", consul_port: int = 8500):
        self.consul = consul.Consul(host=consul_host, port=consul_port)
        self.services_cache = {}
        self.cache_ttl = 30  # seconds
        
    async def register_service(
        self, 
        name: str, 
        port: int, 
        health_check_url: str,
        tags: List[str] = None
    ):
        """Register service with Consul"""
        try:
            service_id = f"{name}-{port}"
            
            self.consul.agent.service.register(
                name=name,
                service_id=service_id,
                port=port,
                tags=tags or [],
                check=consul.Check.http(
                    url=health_check_url,
                    interval="10s",
                    timeout="5s",
                    deregister="30s"
                )
            )
            
            logger.info(
                "Service registered with Consul",
                service=name,
                service_id=service_id,
                port=port
            )
            
        except Exception as e:
            logger.error(
                "Failed to register service with Consul",
                service=name,
                error=str(e)
            )
            raise

    async def discover_service(self, service_name: str) -> List[ServiceInfo]:
        """Discover healthy service instances"""
        try:
            # Check cache first
            if service_name in self.services_cache:
                cached_data, timestamp = self.services_cache[service_name]
                if asyncio.get_event_loop().time() - timestamp < self.cache_ttl:
                    return cached_data
            
            # Query Consul for healthy services
            _, services = self.consul.health.service(
                service_name, 
                passing=True  # Only return healthy services
            )
            
            service_instances = []
            for service in services:
                service_info = service['Service']
                health_info = service['Checks']
                
                # Determine health status
                health_status = "passing"
                for check in health_info:
                    if check['Status'] != 'passing':
                        health_status = check['Status']
                        break
                
                service_instances.append(ServiceInfo(
                    name=service_info['Service'],
                    address=service_info['Address'],
                    port=service_info['Port'],
                    health=health_status,
                    tags=service_info.get('Tags', [])
                ))
            
            # Update cache
            self.services_cache[service_name] = (
                service_instances, 
                asyncio.get_event_loop().time()
            )
            
            return service_instances
            
        except Exception as e:
            logger.error(
                "Service discovery failed",
                service=service_name,
                error=str(e)
            )
            return []

    async def get_service_url(self, service_name: str) -> Optional[str]:
        """Get URL for a healthy service instance (with load balancing)"""
        services = await self.discover_service(service_name)
        
        if not services:
            return None
        
        # Simple round-robin load balancing
        # In production, consider more sophisticated algorithms
        import random
        service = random.choice(services)
        
        return f"http://{service.address}:{service.port}"

# Global service discovery instance
service_discovery = ConsulServiceDiscovery()
```

### Integration with FastAPI Services
```python
# apps/api_gateway/services/service_registry.py
import asyncio
from typing import Dict, Optional
from shared.service_discovery.consul_client import service_discovery
import structlog

logger = structlog.get_logger()

class DynamicServiceRegistry:
    def __init__(self):
        self.service_urls = {}
        self.refresh_interval = 30  # seconds
        self.running = False
        
    async def start(self):
        """Start the service registry with periodic refresh"""
        self.running = True
        asyncio.create_task(self._refresh_services())
        
    async def stop(self):
        """Stop the service registry"""
        self.running = False
        
    async def _refresh_services(self):
        """Periodically refresh service URLs from Consul"""
        services = [
            'data-service',
            'ai-service', 
            'compute-service',
            'viz-service'
        ]
        
        while self.running:
            try:
                for service_name in services:
                    url = await service_discovery.get_service_url(service_name)
                    if url:
                        self.service_urls[service_name] = url
                        logger.debug(
                            "Service URL updated",
                            service=service_name,
                            url=url
                        )
                    else:
                        logger.warning(
                            "No healthy instances found",
                            service=service_name
                        )
                        
                await asyncio.sleep(self.refresh_interval)
                
            except Exception as e:
                logger.error(
                    "Service refresh failed",
                    error=str(e)
                )
                await asyncio.sleep(5)  # Retry after 5 seconds on error
    
    async def get_service_url(self, service_name: str) -> Optional[str]:
        """Get current URL for a service"""
        return self.service_urls.get(service_name)
        
    async def health_check_all(self) -> Dict[str, dict]:
        """Check health of all registered services"""
        results = {}
        
        for service_name, url in self.service_urls.items():
            try:
                # This would typically use httpx or aiohttp
                import httpx
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{url}/health")
                    
                results[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "url": url,
                    "response_time": response.elapsed.total_seconds()
                    if hasattr(response, 'elapsed') else 0
                }
                
            except Exception as e:
                results[service_name] = {
                    "status": "unreachable",
                    "url": url,
                    "error": str(e)
                }
                
        return results

# Global registry instance
dynamic_registry = DynamicServiceRegistry()
```

## 3. Circuit Breaker Pattern Implementation

### Circuit Breaker for Service Resilience
```python
# shared/resilience/circuit_breaker.py
import asyncio
import time
from enum import Enum
from typing import Callable, Any
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit breaker activated
    HALF_OPEN = "half_open"  # Testing if service recovered

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    timeout_duration: int = 60  # seconds
    success_threshold: int = 3  # for half-open state
    call_timeout: int = 10  # seconds per call

class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        
        # Check if circuit should be half-open
        if (self.state == CircuitState.OPEN and 
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.config.timeout_duration):
            
            self.state = CircuitState.HALF_OPEN
            self.success_count = 0
            logger.info("Circuit breaker moving to HALF_OPEN state")
        
        # If circuit is open, fail fast
        if self.state == CircuitState.OPEN:
            raise Exception("Circuit breaker is OPEN - failing fast")
        
        try:
            # Execute the function with timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.config.call_timeout
            )
            
            # Success handling
            await self._on_success()
            return result
            
        except Exception as e:
            # Failure handling  
            await self._on_failure()
            raise e
    
    async def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            
            if self.success_count >= self.config.success_threshold:
                # Reset circuit breaker
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info("Circuit breaker CLOSED - service recovered")
        else:
            # Reset failure count on success
            self.failure_count = 0
    
    async def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.config.failure_threshold:
            if self.state != CircuitState.OPEN:
                self.state = CircuitState.OPEN
                logger.warning(
                    "Circuit breaker OPENED",
                    failure_count=self.failure_count,
                    threshold=self.config.failure_threshold
                )

# Service-specific circuit breakers
service_breakers = {
    'data-service': CircuitBreaker(CircuitBreakerConfig(
        failure_threshold=5,
        timeout_duration=30
    )),
    'ai-service': CircuitBreaker(CircuitBreakerConfig(
        failure_threshold=3,
        timeout_duration=60,
        call_timeout=30  # AI calls may take longer
    )),
    'compute-service': CircuitBreaker(CircuitBreakerConfig(
        failure_threshold=3,
        timeout_duration=120,
        call_timeout=60  # Compute calls take longer
    )),
    'viz-service': CircuitBreaker(CircuitBreakerConfig(
        failure_threshold=5,
        timeout_duration=30
    ))
}
```

## 4. Load Balancing Strategies by Service Type

### API Gateway Load Balancing
- **Algorithm**: Round-robin with health checks
- **Sticky Sessions**: Not required (stateless)
- **Instance Count**: 3-5 instances behind load balancer

### Data Service Load Balancing  
- **Algorithm**: Round-robin or least connections
- **Consideration**: Database connection pooling
- **Instance Count**: 2-4 instances

### AI Service Load Balancing
- **Algorithm**: Least connections (CPU/GPU intensive)
- **Consideration**: Model loading time
- **Instance Count**: 2-3 GPU-optimized instances

### Compute Service Load Balancing
- **Algorithm**: Least connections or weighted round-robin
- **Consideration**: Long-running tasks
- **Instance Count**: 2-4 high-CPU instances

### Visualization Service Load Balancing
- **Algorithm**: Round-robin with caching
- **Consideration**: Chart generation caching
- **Instance Count**: 2-3 instances