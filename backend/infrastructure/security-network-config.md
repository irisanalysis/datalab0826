# Security & Network Configuration

## 1. Network Security Architecture

### Network Segmentation Strategy
```yaml
# infrastructure/kubernetes/network/network-policies.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: datalab-ingress-policy
  namespace: datalab-production
spec:
  podSelector:
    matchLabels:
      app: api-gateway
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # Allow ingress from load balancer
  - from:
    - namespaceSelector:
        matchLabels:
          name: istio-system
    ports:
    - protocol: TCP
      port: 8000
  # Allow health checks
  - from:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: TCP
      port: 8000
  egress:
  # Allow egress to other services
  - to:
    - podSelector:
        matchLabels:
          tier: backend
    ports:
    - protocol: TCP
      port: 8001  # data-service
    - protocol: TCP
      port: 8002  # ai-service
    - protocol: TCP
      port: 8003  # compute-service
    - protocol: TCP
      port: 8004  # viz-service
  # Allow DNS resolution
  - to: []
    ports:
    - protocol: UDP
      port: 53
  # Allow HTTPS to external services
  - to: []
    ports:
    - protocol: TCP
      port: 443

---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: datalab-backend-services-policy
  namespace: datalab-production
spec:
  podSelector:
    matchLabels:
      tier: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # Allow ingress from API Gateway
  - from:
    - podSelector:
        matchLabels:
          app: api-gateway
  # Allow health checks from system
  - from:
    - namespaceSelector:
        matchLabels:
          name: kube-system
  egress:
  # Allow database access
  - to:
    - podSelector:
        matchLabels:
          app: postgres-cluster
    ports:
    - protocol: TCP
      port: 5432
  # Allow Redis access
  - to:
    - podSelector:
        matchLabels:
          app: redis-sentinel
    ports:
    - protocol: TCP
      port: 6379
    - protocol: TCP
      port: 26379
  # Allow DNS resolution
  - to: []
    ports:
    - protocol: UDP
      port: 53

---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: datalab-database-policy
  namespace: datalab-production
spec:
  podSelector:
    matchLabels:
      postgresql: postgres-cluster
  policyTypes:
  - Ingress
  ingress:
  # Allow access only from backend services
  - from:
    - podSelector:
        matchLabels:
          tier: backend
    ports:
    - protocol: TCP
      port: 5432
  # Allow backup jobs
  - from:
    - podSelector:
        matchLabels:
          job-name: database-backup
    ports:
    - protocol: TCP
      port: 5432

---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-default
  namespace: datalab-production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  # This policy denies all traffic by default
  # Specific allow policies above override this
```

### Istio Security Configuration
```yaml
# infrastructure/kubernetes/security/istio-security.yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: datalab-mtls
  namespace: datalab-production
spec:
  mtls:
    mode: STRICT  # Require mTLS for all communication

---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: api-gateway-authz
  namespace: datalab-production
spec:
  selector:
    matchLabels:
      app: api-gateway
  rules:
  # Allow authenticated requests
  - from:
    - source:
        requestPrincipals: ["*"]
    to:
    - operation:
        paths: ["/api/v1/*"]
    when:
    - key: request.headers[authorization]
      values: ["Bearer *"]
  # Allow health checks without auth
  - to:
    - operation:
        paths: ["/health", "/metrics"]

---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: backend-services-authz
  namespace: datalab-production
spec:
  selector:
    matchLabels:
      tier: backend
  rules:
  # Only allow requests from API Gateway
  - from:
    - source:
        principals: ["cluster.local/ns/datalab-production/sa/api-gateway"]
  # Allow health checks from system components
  - from:
    - source:
        namespaces: ["kube-system", "istio-system"]
    to:
    - operation:
        paths: ["/health"]

---
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: jwt-auth
  namespace: datalab-production
spec:
  selector:
    matchLabels:
      app: api-gateway
  jwtRules:
  - issuer: "https://auth.datalab.com"
    jwksUri: "https://auth.datalab.com/.well-known/jwks.json"
    audiences:
    - "datalab-api"
    forwardOriginalToken: true
```

## 2. Application Security Implementation

### JWT Authentication & Authorization
```python
# shared/security/auth.py
import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog

logger = structlog.get_logger()

class SecurityManager:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.bearer_scheme = HTTPBearer()
        
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
            
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(32),  # JWT ID for revocation
            "type": "access"
        })
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=30)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(32),
            "type": "refresh"
        })
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    async def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                credentials.credentials, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            # Verify token type
            if payload.get("type") != "access":
                raise HTTPException(status_code=401, detail="Invalid token type")
            
            # Check if token is blacklisted (implement redis check)
            jti = payload.get("jti")
            if await self.is_token_blacklisted(jti):
                raise HTTPException(status_code=401, detail="Token has been revoked")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired", token_id=credentials.credentials[-10:])
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError as e:
            logger.warning("Invalid token", error=str(e))
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def is_token_blacklisted(self, jti: str) -> bool:
        """Check if token is blacklisted in Redis"""
        # Implementation depends on your Redis setup
        return False
    
    async def blacklist_token(self, jti: str, exp: datetime):
        """Add token to blacklist"""
        # Implementation depends on your Redis setup
        pass

# Role-based access control
class RoleBasedAuth:
    def __init__(self, required_roles: list):
        self.required_roles = required_roles
    
    def __call__(self, user_payload: Dict[str, Any] = Depends(SecurityManager().verify_token)):
        user_roles = user_payload.get("roles", [])
        
        if not any(role in user_roles for role in self.required_roles):
            raise HTTPException(
                status_code=403, 
                detail="Insufficient permissions"
            )
        
        return user_payload

# Usage decorators
require_auth = Depends(SecurityManager().verify_token)
require_admin = RoleBasedAuth(["admin"])
require_data_analyst = RoleBasedAuth(["admin", "data_analyst"])
require_ai_researcher = RoleBasedAuth(["admin", "ai_researcher"])
```

### Input Validation & Sanitization
```python
# shared/security/validation.py
import re
import html
import bleach
from typing import Any, Dict, List
from pydantic import BaseModel, validator
from fastapi import HTTPException
import structlog

logger = structlog.get_logger()

class SecurityValidator:
    """Security validation utilities"""
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(ALTER|CREATE|DELETE|DROP|EXEC(UTE){0,1}|INSERT( +INTO){0,1}|MERGE|SELECT|UPDATE|UNION( +ALL){0,1})\b)",
        r"(--|\#|/\*)",
        r"(\b(AND|OR)\b.*(=|LIKE))",
        r"(\bWHERE\b.*\b(=|LIKE|\bIN\b))",
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"vbscript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>.*?</iframe>",
    ]
    
    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\.\/",
        r"\.\.\\",
        r"%2e%2e%2f",
        r"%2e%2e\\",
    ]
    
    @staticmethod
    def validate_sql_injection(value: str) -> str:
        """Check for SQL injection attempts"""
        for pattern in SecurityValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning("SQL injection attempt detected", value=value[:100])
                raise HTTPException(
                    status_code=400,
                    detail="Invalid input: potential SQL injection detected"
                )
        return value
    
    @staticmethod
    def validate_xss(value: str) -> str:
        """Check for XSS attempts"""
        for pattern in SecurityValidator.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning("XSS attempt detected", value=value[:100])
                raise HTTPException(
                    status_code=400,
                    detail="Invalid input: potential XSS detected"
                )
        return value
    
    @staticmethod
    def validate_path_traversal(value: str) -> str:
        """Check for path traversal attempts"""
        for pattern in SecurityValidator.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning("Path traversal attempt detected", value=value)
                raise HTTPException(
                    status_code=400,
                    detail="Invalid input: potential path traversal detected"
                )
        return value
    
    @staticmethod
    def sanitize_html(value: str) -> str:
        """Sanitize HTML input"""
        allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li']
        allowed_attributes = {}
        
        return bleach.clean(
            value,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        return email.lower()

# Secure Pydantic models
class SecureBaseModel(BaseModel):
    """Base model with security validations"""
    
    @validator('*', pre=True, always=True)
    def validate_strings(cls, v):
        if isinstance(v, str):
            # Apply security validations
            v = SecurityValidator.validate_sql_injection(v)
            v = SecurityValidator.validate_xss(v)
            v = SecurityValidator.validate_path_traversal(v)
        return v

class UserRegistrationRequest(SecureBaseModel):
    email: str
    password: str
    full_name: str
    
    @validator('email')
    def validate_email(cls, v):
        return SecurityValidator.validate_email(v)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class DatasetUploadRequest(SecureBaseModel):
    name: str
    description: str
    file_path: str
    
    @validator('file_path')
    def validate_file_path(cls, v):
        # Only allow specific file extensions
        allowed_extensions = ['.csv', '.xlsx', '.json', '.parquet']
        if not any(v.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError('Invalid file type')
        return v
```

### Rate Limiting Implementation
```python
# shared/security/rate_limiting.py
import asyncio
import time
from typing import Dict, Optional
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()

class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
        
    async def is_allowed(
        self, 
        key: str, 
        limit: int, 
        window: int, 
        identifier: str
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check if request is within rate limit
        Uses sliding window log algorithm
        """
        now = time.time()
        pipeline = self.redis.pipeline()
        
        # Remove old entries outside the window
        pipeline.zremrangebyscore(key, 0, now - window)
        
        # Count current entries
        pipeline.zcard(key)
        
        # Add current request
        pipeline.zadd(key, {identifier: now})
        
        # Set expiration
        pipeline.expire(key, window)
        
        results = await pipeline.execute()
        
        current_count = results[1]
        allowed = current_count < limit
        
        headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(max(0, limit - current_count - 1)),
            "X-RateLimit-Reset": str(int(now + window)),
            "X-RateLimit-Window": str(window)
        }
        
        if not allowed:
            # Remove the request we just added since it's not allowed
            await self.redis.zrem(key, identifier)
            logger.warning(
                "Rate limit exceeded",
                key=key,
                current_count=current_count,
                limit=limit,
                identifier=identifier[:20]  # Truncate for logging
            )
        
        return allowed, headers

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client, default_limit: int = 100, default_window: int = 3600):
        super().__init__(app)
        self.limiter = RateLimiter(redis_client)
        self.default_limit = default_limit
        self.default_window = default_window
        
        # Rate limit configurations per endpoint
        self.rate_limits = {
            "/api/v1/auth/login": {"limit": 5, "window": 900},  # 5 attempts per 15 minutes
            "/api/v1/auth/register": {"limit": 3, "window": 3600},  # 3 per hour
            "/api/v1/datasets/upload": {"limit": 10, "window": 3600},  # 10 per hour
            "/api/v1/ai/analyze": {"limit": 20, "window": 3600},  # 20 per hour
            "/api/v1/compute/process": {"limit": 50, "window": 3600},  # 50 per hour
        }
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
        
        # Get client identifier
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        auth_header = request.headers.get("authorization", "")
        
        # Extract user ID from JWT if available
        user_id = "anonymous"
        if auth_header.startswith("Bearer "):
            try:
                import jwt
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, options={"verify_signature": False})
                user_id = payload.get("user_id", "anonymous")
            except:
                pass
        
        identifier = f"{client_ip}:{user_id}:{hash(user_agent) % 10000}"
        
        # Get rate limit config for this endpoint
        path = request.url.path
        config = self.rate_limits.get(path, {
            "limit": self.default_limit,
            "window": self.default_window
        })
        
        # Check rate limit
        key = f"rate_limit:{path}:{identifier}"
        allowed, headers = await self.limiter.is_allowed(
            key=key,
            limit=config["limit"],
            window=config["window"],
            identifier=f"{identifier}:{time.time()}"
        )
        
        if not allowed:
            # Rate limit exceeded
            from starlette.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded. Please try again later."},
                headers=headers
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        for header, value in headers.items():
            response.headers[header] = value
        
        return response
```

## 3. SSL/TLS Configuration

### Certificate Management
```yaml
# infrastructure/kubernetes/security/cert-manager.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@datalab.com
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
    - http01:
        ingress:
          class: istio
      selector:
        dnsNames:
        - api.datalab.com
        - admin.datalab.com

---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: datalab-tls
  namespace: datalab-production
spec:
  secretName: datalab-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - api.datalab.com
  - admin.datalab.com
  - staging.datalab.com
```

### Security Headers Configuration
```python
# shared/security/headers.py
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' wss: https:; "
            "frame-ancestors 'none';"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), "
            "camera=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "payment=(), "
            "usb=()"
        )
        
        # Remove server information
        response.headers.pop("Server", None)
        
        return response

def setup_security_headers(app: FastAPI):
    """Setup security headers middleware"""
    app.add_middleware(SecurityHeadersMiddleware)
```

## 4. Secrets Management

### Kubernetes Secrets with External Secrets Operator
```yaml
# infrastructure/kubernetes/security/external-secrets.yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: datalab-production
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-west-2
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: database-credentials
  namespace: datalab-production
spec:
  refreshInterval: 15s
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: postgres-credentials
    creationPolicy: Owner
  data:
  - secretKey: username
    remoteRef:
      key: datalab/database
      property: username
  - secretKey: password
    remoteRef:
      key: datalab/database
      property: password

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: jwt-secret
  namespace: datalab-production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: jwt-secret
    creationPolicy: Owner
  data:
  - secretKey: secret
    remoteRef:
      key: datalab/jwt
      property: secret_key

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: api-keys
  namespace: datalab-production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: api-keys
    creationPolicy: Owner
  data:
  - secretKey: openai_api_key
    remoteRef:
      key: datalab/api-keys
      property: openai
  - secretKey: stripe_api_key
    remoteRef:
      key: datalab/api-keys
      property: stripe
```

## 5. Security Monitoring & Auditing

### Audit Logging Configuration
```python
# shared/security/audit.py
import json
import time
from typing import Any, Dict, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()

class AuditEvent:
    def __init__(
        self,
        event_type: str,
        user_id: Optional[str],
        resource: str,
        action: str,
        outcome: str,
        request_id: str,
        ip_address: str,
        user_agent: str,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        self.timestamp = time.time()
        self.event_type = event_type
        self.user_id = user_id
        self.resource = resource
        self.action = action
        self.outcome = outcome
        self.request_id = request_id
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.additional_data = additional_data or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "user_id": self.user_id,
            "resource": self.resource,
            "action": self.action,
            "outcome": self.outcome,
            "request_id": self.request_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "additional_data": self.additional_data
        }

class AuditLogger:
    def __init__(self, log_sensitive_data: bool = False):
        self.log_sensitive_data = log_sensitive_data
    
    async def log_audit_event(self, event: AuditEvent):
        """Log audit event"""
        audit_data = event.to_dict()
        
        # Sanitize sensitive data if needed
        if not self.log_sensitive_data:
            audit_data = self._sanitize_data(audit_data)
        
        logger.info(
            "AUDIT_EVENT",
            **audit_data
        )
        
        # Also send to external audit system
        await self._send_to_audit_system(audit_data)
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from audit logs"""
        sensitive_keys = ['password', 'token', 'secret', 'key']
        
        def sanitize_dict(d):
            if isinstance(d, dict):
                return {
                    k: "[REDACTED]" if any(sens in k.lower() for sens in sensitive_keys)
                    else sanitize_dict(v)
                    for k, v in d.items()
                }
            elif isinstance(d, list):
                return [sanitize_dict(item) for item in d]
            return d
        
        return sanitize_dict(data)
    
    async def _send_to_audit_system(self, data: Dict[str, Any]):
        """Send audit event to external system (e.g., Elasticsearch, Splunk)"""
        # Implementation depends on your audit system
        pass

class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, audit_logger: AuditLogger):
        super().__init__(app)
        self.audit_logger = audit_logger
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = request.headers.get("x-request-id", "unknown")
        
        # Extract user information
        user_id = None
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                import jwt
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, options={"verify_signature": False})
                user_id = payload.get("user_id")
            except:
                pass
        
        response = await call_next(request)
        
        # Log audit event for sensitive operations
        if self._should_audit(request):
            event = AuditEvent(
                event_type="API_ACCESS",
                user_id=user_id,
                resource=f"{request.method} {request.url.path}",
                action=request.method,
                outcome="SUCCESS" if response.status_code < 400 else "FAILURE",
                request_id=request_id,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", ""),
                additional_data={
                    "status_code": response.status_code,
                    "response_time": time.time() - start_time,
                    "query_params": dict(request.query_params)
                }
            )
            
            await self.audit_logger.log_audit_event(event)
        
        return response
    
    def _should_audit(self, request: Request) -> bool:
        """Determine if request should be audited"""
        audit_paths = [
            "/api/v1/auth/",
            "/api/v1/datasets/",
            "/api/v1/users/",
            "/admin/"
        ]
        
        return any(request.url.path.startswith(path) for path in audit_paths)
```

### Security Scanning Integration
```yaml
# .github/workflows/security-scan.yml
name: Security Scanning

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  push:
    branches: [main]

jobs:
  dependency-check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run Snyk to check for vulnerabilities
      uses: snyk/actions/python@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      with:
        args: --severity-threshold=medium
        
    - name: Upload Snyk results to GitHub Code Scanning
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: snyk.sarif

  container-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Build test image
      run: |
        docker build -t datalab/api-gateway:test -f backend/infrastructure/docker/Dockerfile.api-gateway backend/
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'datalab/api-gateway:test'
        format: 'sarif'
        output: 'trivy-results.sarif'
        
    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

  secrets-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0
    
    - name: TruffleHog OSS
      uses: trufflesecurity/trufflehog@main
      with:
        path: ./
        base: main
        head: HEAD
        extra_args: --debug --only-verified
```

This comprehensive security strategy provides:

1. **Network segmentation** with Kubernetes NetworkPolicies
2. **mTLS encryption** for service-to-service communication
3. **Robust authentication** with JWT and role-based access control
4. **Input validation** and sanitization to prevent common attacks
5. **Rate limiting** to prevent abuse
6. **Proper SSL/TLS** configuration with automated certificate management
7. **Secrets management** with external secret providers
8. **Comprehensive audit logging** for compliance and monitoring
9. **Automated security scanning** in CI/CD pipeline