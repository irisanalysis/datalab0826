# Security Documentation

## I. Technical Decisions & Trade-offs

### CSRF Protection Choice: SameSite + Custom Header
**Decision**: Using SameSite=Lax cookies + X-Requested-With header validation
**Rationale**: 
- **SameSite=Lax** provides good cross-site request protection while maintaining usability (allows navigation from external sites)
- **Custom Header (X-Requested-With)** adds additional CSRF protection layer
- **Trade-off**: More complex than double-submit token but provides better security with good UX
- **Alternative Considered**: Double-submit token (rejected due to complexity in cookie management)

### Rate Limiting: Memory-based Implementation
**Decision**: In-memory sliding window rate limiting
**Rationale**: 
- **Simplicity**: No external dependencies for development/demo
- **Performance**: Fast lookups and updates
- **Limitations**: Single-instance only, not suitable for horizontal scaling
- **Production Alternative**: Redis-based distributed rate limiting recommended
- **Trade-off**: Development simplicity vs production scalability

### Cookie Settings: SameSite=Lax
**Decision**: SameSite=Lax instead of Strict
**Rationale**:
- **Cross-tab Functionality**: Users can navigate from external sites and remain logged in
- **Security**: Still prevents most CSRF attacks
- **UX**: Better user experience than Strict mode
- **Trade-off**: Slight security reduction for significant UX improvement

## II. Security Features Implementation

### 🔐 Authentication Security
- **Password Hashing**: bcrypt with cost factor 12 (2^12 iterations)
- **JWT Tokens**: HS256 algorithm with secure random secrets
- **Token Lifecycle**: 15-minute access tokens, 7-day refresh tokens
- **Token Storage**: httpOnly + Secure cookies (not accessible via JavaScript)
- **Refresh Token Rotation**: Old tokens automatically revoked on refresh

### 🛡️ API Security
- **CSRF Protection**: Custom header validation (X-Requested-With: XMLHttpRequest)
- **CORS Configuration**: Whitelist specific origins only
- **Rate Limiting**: 10 requests/minute on auth endpoints, 5 requests/minute on refresh
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **Error Handling**: Unified responses prevent information leakage
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, CSP

### 🚧 Infrastructure Security
- **Container Security**: Non-root users in Docker containers
- **Secrets Management**: Environment variables for sensitive configuration
- **Network Isolation**: Docker network isolation between services
- **Health Monitoring**: Automated health checks for service monitoring
- **Audit Logging**: Structured logging for all authentication events

## III. Password Policy

### Requirements
- **Minimum Length**: 8 characters
- **Character Types**: Must include uppercase, lowercase, and digit
- **Validation**: Both client-side (visual feedback) and server-side enforcement
- **Hashing**: bcrypt with cost factor 12 for secure storage

### Implementation
```python
# Server-side validation
@field_validator('password')
@classmethod
def validate_password(cls, v: str) -> str:
    if len(v) < 8:
        raise ValueError('Password must be at least 8 characters long')
    
    has_upper = any(c.isupper() for c in v)
    has_lower = any(c.islower() for c in v)
    has_digit = any(c.isdigit() for c in v)
    
    if not (has_upper and has_lower and has_digit):
        raise ValueError('Password must contain uppercase, lowercase, and digit')
    
    return v
```

## IV. JWT Configuration

### Token Structure
```json
{
  "sub": "user_id",
  "type": "access",
  "exp": 1641024000,
  "iat": 1641023100,
  "jti": "unique_token_id"
}
```

### Security Parameters
- **Algorithm**: HS256 (HMAC SHA-256)
- **Secret**: Configurable via JWT_SECRET environment variable
- **Access Token TTL**: 900 seconds (15 minutes)
- **Refresh Token TTL**: 604800 seconds (7 days)
- **Token Revocation**: Refresh tokens stored in database with revocation tracking

## V. Cookie Security Configuration

### Production Settings
```javascript
{
  httpOnly: true,      // Prevent XSS access
  secure: true,        // HTTPS only (set to false for development)
  sameSite: 'Lax',     // CSRF protection with good UX
  domain: 'yourdomain.com',  // Restrict to specific domain
  maxAge: 900          // Match token expiration
}
```

### Development Settings
```javascript
{
  httpOnly: true,
  secure: false,       // Allow HTTP for local development
  sameSite: 'Lax',
  domain: null,        // Allow any domain for local testing
  maxAge: 900
}
```

## VI. Rate Limiting Configuration

### Current Limits
- **Registration/Login**: 10 requests per minute per IP
- **Token Refresh**: 5 requests per minute per IP
- **Implementation**: Sliding window algorithm
- **Storage**: In-memory (development) / Redis (production)

### Rate Limit Response
```json
{
  "detail": "Rate limit exceeded. Maximum 10 requests per 60 seconds.",
  "error_code": "RATE_LIMIT_EXCEEDED"
}
```

## VII. Error Handling Strategy

### Unified Authentication Errors
All authentication failures return the same generic message:
```json
{
  "detail": "Invalid credentials",
  "error_code": "AUTHENTICATION_FAILED"
}
```

This prevents:
- **Account Enumeration**: Cannot determine if email exists
- **Timing Attacks**: Consistent response times via dummy operations
- **Information Leakage**: No detailed error information exposed

### Error Categories
1. **400 Bad Request**: Validation errors
2. **401 Unauthorized**: Authentication required or failed
3. **403 Forbidden**: CSRF protection or authorization failure
4. **429 Too Many Requests**: Rate limit exceeded
5. **500 Internal Server Error**: Unexpected errors (details logged, not exposed)

## VIII. Audit Logging

### Logged Events
- **Authentication Success**: User ID, IP, timestamp, user agent
- **Authentication Failure**: Email (hashed), IP, timestamp, failure reason
- **Token Refresh**: User ID, IP, timestamp
- **Logout**: User ID, IP, timestamp
- **Token Revocation**: User ID, reason, timestamp

### Log Format (Structured JSON)
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "event": "user_login",
  "user_id": 123,
  "email": "user@example.com",
  "ip": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "success": true
}
```

## IX. Security Headers

### Applied Headers
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY  
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'none'
```

### Rationale
- **X-Content-Type-Options**: Prevent MIME type sniffing attacks
- **X-Frame-Options**: Prevent clickjacking attacks  
- **X-XSS-Protection**: Browser XSS filtering
- **Referrer-Policy**: Control referrer information leakage
- **CSP**: Prevent code injection (strict policy for API responses)

## X. Production Security Checklist

### Pre-Deployment
- [ ] Change JWT_SECRET to cryptographically secure random string
- [ ] Set COOKIE_SECURE=true for HTTPS environments
- [ ] Configure proper COOKIE_DOMAIN for your domain
- [ ] Use strong database passwords
- [ ] Review and update CORS_ORIGINS for your domains
- [ ] Enable proper SSL/TLS certificates
- [ ] Set up Redis for distributed rate limiting
- [ ] Configure log aggregation and monitoring
- [ ] Set up automated security scanning
- [ ] Implement database backup strategy

### Monitoring & Maintenance
- [ ] Monitor authentication failure rates
- [ ] Set up alerts for rate limit violations
- [ ] Regular security dependency updates
- [ ] Periodic security audits
- [ ] Log analysis for suspicious patterns
- [ ] Token usage monitoring
- [ ] Database performance monitoring
- [ ] SSL certificate renewal automation

## XI. Threat Model

### Mitigated Threats
- **Password Attacks**: Strong hashing, rate limiting, account lockout
- **Session Hijacking**: Secure cookies, token rotation
- **CSRF Attacks**: SameSite cookies, custom headers
- **XSS Attacks**: httpOnly cookies, CSP headers
- **SQL Injection**: Parameterized queries via ORM
- **Timing Attacks**: Consistent response times
- **Account Enumeration**: Unified error messages
- **Brute Force**: Rate limiting, strong password policy

### Remaining Risks & Mitigations
- **Insider Threats**: Implement proper access controls and audit trails
- **Infrastructure Compromise**: Use secrets management, network segmentation
- **Social Engineering**: User education, multi-factor authentication (future enhancement)
- **Zero-day Exploits**: Keep dependencies updated, use security scanning tools

## XII. Security Testing

### Automated Tests
- CSRF protection validation
- Rate limiting verification  
- Authentication flow testing
- Authorization boundary testing
- Input validation testing

### Manual Security Testing
- Penetration testing checklist
- Cookie security verification
- CORS policy testing
- Error handling validation
- Logging verification

This security documentation should be reviewed and updated regularly as the system evolves and new threats emerge.