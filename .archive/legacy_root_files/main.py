import os
import datetime
import logging
import json
from functools import wraps
from urllib.parse import quote_plus

from flask import Flask, send_file, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        # Add file handler if LOG_FILE is specified
        *([logging.FileHandler(os.getenv('LOG_FILE'))] if os.getenv('LOG_FILE') else [])
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration - Security critical settings
# JWT Secret Key - MUST be set in production
jwt_secret = os.getenv('JWT_SECRET')
if not jwt_secret:
    if os.getenv('FLASK_ENV') == 'production':
        raise RuntimeError("JWT_SECRET environment variable is required in production")
    # Only use fallback in development
    jwt_secret = 'dev-only-jwt-secret-change-for-production'
    print("WARNING: Using default JWT secret. Set JWT_SECRET environment variable for production.")

app.config['JWT_SECRET_KEY'] = jwt_secret
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(seconds=int(os.getenv('ACCESS_TTL', 900)))
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(seconds=int(os.getenv('REFRESH_TTL', 604800)))

# Security headers and settings
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['SESSION_COOKIE_SECURE'] = os.getenv('COOKIE_SECURE', 'False').lower() == 'true'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Database configuration - All parameters required
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

# Validate required database configuration
required_db_vars = {
    'POSTGRES_HOST': POSTGRES_HOST,
    'POSTGRES_DB': POSTGRES_DB,
    'POSTGRES_USER': POSTGRES_USER,
    'POSTGRES_PASSWORD': POSTGRES_PASSWORD
}

missing_vars = [var for var, value in required_db_vars.items() if not value]
if missing_vars:
    raise RuntimeError(f"Missing required database environment variables: {', '.join(missing_vars)}")

# Build database URI with proper URL encoding for special characters
encoded_password = quote_plus(POSTGRES_PASSWORD)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{encoded_password}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 3600,
    'connect_args': {'connect_timeout': 10}
}

# Initialize extensions with security-conscious CORS
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:3001,http://localhost:8080').split(',')
CORS(app, 
     origins=cors_origins,
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'OPTIONS'])
jwt = JWTManager(app)
db = SQLAlchemy(app)

# Security headers middleware
@app.after_request
def add_security_headers(response):
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    # XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # Referrer policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    # Content Security Policy (basic)
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    return response

# Models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # Extended enterprise fields
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    avatar_url = db.Column(db.String(500))
    role = db.Column(db.String(50), default='user')  # user, admin, analyst, viewer
    department = db.Column(db.String(100))
    organization = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    timezone = db.Column(db.String(50), default='UTC')
    language = db.Column(db.String(10), default='en')
    
    # User preferences (JSON field)
    preferences = db.Column(db.Text)  # Store as JSON string
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dict for API responses"""
        data = {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "avatar_url": self.avatar_url,
            "role": self.role,
            "department": self.department,
            "organization": self.organization,
            "is_active": self.is_active,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "timezone": self.timezone,
            "language": self.language,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
        if include_sensitive:
            import json
            try:
                data["preferences"] = json.loads(self.preferences) if self.preferences else {}
            except (json.JSONDecodeError, TypeError):
                data["preferences"] = {}
        
        return data

class DataSource(db.Model):
    __tablename__ = 'data_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # postgresql, mysql, mongodb, csv, api, etc.
    
    # Connection configuration (encrypted)
    config = db.Column(db.Text)  # JSON string with connection details
    
    # Connection status
    status = db.Column(db.String(20), default='pending')  # pending, connected, failed, disabled
    last_test = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    
    # Metadata
    description = db.Column(db.Text)
    tags = db.Column(db.Text)  # JSON array as string
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def to_dict(self, include_config=False):
        """Convert data source to dict for API responses"""
        import json
        data = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "last_test": self.last_test.isoformat() if self.last_test else None,
            "error_message": self.error_message,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
        try:
            data["tags"] = json.loads(self.tags) if self.tags else []
        except (json.JSONDecodeError, TypeError):
            data["tags"] = []
        
        if include_config:
            try:
                data["config"] = json.loads(self.config) if self.config else {}
            except (json.JSONDecodeError, TypeError):
                data["config"] = {}
        
        return data

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(128), unique=True, nullable=False, index=True)
    device_info = db.Column(db.Text)  # JSON with device details
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    location = db.Column(db.String(100))  # City, Country
    is_active = db.Column(db.Boolean, default=True)
    last_activity = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def to_dict(self):
        """Convert session to dict for API responses"""
        import json
        data = {
            "id": self.id,
            "session_id": self.session_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "location": self.location,
            "is_active": self.is_active,
            "last_activity": self.last_activity.isoformat(),
            "created_at": self.created_at.isoformat()
        }
        
        try:
            data["device_info"] = json.loads(self.device_info) if self.device_info else {}
        except (json.JSONDecodeError, TypeError):
            data["device_info"] = {}
        
        return data

class Integration(db.Model):
    __tablename__ = 'integrations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    provider = db.Column(db.String(50), nullable=False)  # google, github, slack, etc.
    provider_user_id = db.Column(db.String(100))
    
    # OAuth tokens (encrypted)
    access_token = db.Column(db.Text)
    refresh_token_oauth = db.Column(db.Text)
    token_expires_at = db.Column(db.DateTime)
    
    # Integration metadata
    scopes = db.Column(db.Text)  # JSON array as string
    profile_data = db.Column(db.Text)  # JSON with user profile from provider
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def to_dict(self, include_tokens=False):
        """Convert integration to dict for API responses"""
        import json
        data = {
            "id": self.id,
            "provider": self.provider,
            "provider_user_id": self.provider_user_id,
            "token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
        try:
            data["scopes"] = json.loads(self.scopes) if self.scopes else []
            data["profile_data"] = json.loads(self.profile_data) if self.profile_data else {}
        except (json.JSONDecodeError, TypeError):
            data["scopes"] = []
            data["profile_data"] = {}
        
        if include_tokens:
            data["access_token"] = self.access_token
            data["refresh_token_oauth"] = self.refresh_token_oauth
        
        return data

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    session_id = db.Column(db.String(128))
    
    # Event details
    action = db.Column(db.String(100), nullable=False)  # login, logout, data_access, etc.
    resource = db.Column(db.String(100))  # user, data_source, etc.
    resource_id = db.Column(db.String(50))
    
    # Request context
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    endpoint = db.Column(db.String(200))
    method = db.Column(db.String(10))
    
    # Event metadata
    details = db.Column(db.Text)  # JSON with additional event data
    status = db.Column(db.String(20))  # success, failed, error
    error_message = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def to_dict(self):
        """Convert audit log to dict for API responses"""
        import json
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "action": self.action,
            "resource": self.resource,
            "resource_id": self.resource_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "endpoint": self.endpoint,
            "method": self.method,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat()
        }
        
        try:
            data["details"] = json.loads(self.details) if self.details else {}
        except (json.JSONDecodeError, TypeError):
            data["details"] = {}
        
        return data

class RefreshToken(db.Model):
    __tablename__ = 'refresh_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(128), db.ForeignKey('user_sessions.session_id'))
    token_hash = db.Column(db.String(256), nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked_at = db.Column(db.DateTime)
    user_agent = db.Column(db.String(500))
    ip = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# JWT blacklist
blacklisted_tokens = set()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return jwt_payload['jti'] in blacklisted_tokens

# Helper functions
def hash_password(password):
    # Use configurable bcrypt rounds for security/performance tuning
    rounds = int(os.getenv('BCRYPT_ROUNDS', 12))
    if rounds < 10:
        raise ValueError("BCRYPT_ROUNDS must be at least 10 for security")
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=rounds)).decode('utf-8')

def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def validate_email(email):
    import re
    if not email or len(email) > 254:  # RFC 5321 limit
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(value, max_length=255):
    """Sanitize user input to prevent various attacks"""
    if not isinstance(value, str):
        return str(value)[:max_length]
    # Remove null bytes and limit length
    return value.replace('\x00', '').strip()[:max_length]

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    return True, "Password is valid"

# Audit logging functions
def create_audit_log(action, resource=None, resource_id=None, status='success', details=None, error_message=None):
    """Create an audit log entry"""
    try:
        import json
        
        # Try to get current user ID safely
        user_id = None
        try:
            from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
            if hasattr(request, 'headers') and request.headers.get('Authorization'):
                verify_jwt_in_request(optional=True)
                user_id = get_jwt_identity()
        except:
            user_id = None
        
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=str(resource_id) if resource_id else None,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None,
            endpoint=request.endpoint if request else None,
            method=request.method if request else None,
            details=json.dumps(details) if details else None,
            status=status,
            error_message=error_message
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        logger.error(f"Failed to create audit log: {str(e)}")
        # Don't raise exception to avoid breaking main functionality
        pass

# Session management functions
def create_user_session(user_id, user_agent=None, ip_address=None):
    """Create a new user session"""
    import secrets
    import json
    
    session_id = secrets.token_urlsafe(32)
    
    # Parse user agent for device info
    device_info = {}
    if user_agent:
        # Simple parsing - in production, use a library like user-agents
        device_info = {
            "user_agent": user_agent,
            "browser": "unknown",
            "os": "unknown",
            "device": "unknown"
        }
    
    session = UserSession(
        user_id=user_id,
        session_id=session_id,
        device_info=json.dumps(device_info),
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db.session.add(session)
    db.session.commit()
    
    return session_id

def update_session_activity(session_id):
    """Update session last activity"""
    try:
        session = UserSession.query.filter_by(session_id=session_id, is_active=True).first()
        if session:
            session.last_activity = datetime.datetime.utcnow()
            db.session.commit()
    except Exception as e:
        logger.error(f"Failed to update session activity: {str(e)}")
        pass

# Data encryption helpers (for sensitive config data)
def encrypt_config(config_data):
    """Encrypt sensitive configuration data"""
    import json
    from cryptography.fernet import Fernet
    import base64
    
    try:
        # In production, use a proper key management system
        key = os.getenv('ENCRYPTION_KEY', Fernet.generate_key())
        if isinstance(key, str):
            key = key.encode()
        
        cipher_suite = Fernet(key)
        
        json_data = json.dumps(config_data).encode('utf-8')
        encrypted_data = cipher_suite.encrypt(json_data)
        return base64.b64encode(encrypted_data).decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to encrypt config: {str(e)}")
        # Fallback to JSON string (not encrypted)
        return json.dumps(config_data)

def decrypt_config(encrypted_data):
    """Decrypt sensitive configuration data"""
    import json
    from cryptography.fernet import Fernet
    import base64
    
    try:
        key = os.getenv('ENCRYPTION_KEY', Fernet.generate_key())
        if isinstance(key, str):
            key = key.encode()
        
        cipher_suite = Fernet(key)
        
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        decrypted_data = cipher_suite.decrypt(encrypted_bytes)
        return json.loads(decrypted_data.decode('utf-8'))
    except Exception as e:
        logger.error(f"Failed to decrypt config: {str(e)}")
        # Fallback to direct JSON parsing
        try:
            return json.loads(encrypted_data)
        except:
            return {}

# Decorator for audit logging
def audit_action(action, resource=None):
    """Decorator to automatically log actions"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                # Skip logging for successful actions - done manually in endpoints
                return result
            except Exception as e:
                # Log failed action
                try:
                    create_audit_log(action, resource, status='failed', error_message=str(e))
                except:
                    pass  # Don't break the main function if audit logging fails
                raise
        return wrapper
    return decorator

# Routes
@app.route("/")
def index():
    return send_file('src/index.html')

@app.route("/api/auth/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({"error": "Email and password are required"}), 400
        
        email = sanitize_input(data['email'], 254).lower().strip()
        password = sanitize_input(data['password'], 128)
        
        # Validate email format
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        
        # Validate password strength
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({"error": message}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "Email already registered"}), 409
        
        # Create new user
        password_hash = hash_password(password)
        new_user = User(email=email, password_hash=password_hash)
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"ok": True, "message": "User registered successfully"}), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration failed for email {email}: {str(e)}")
        return jsonify({"error": "Registration failed"}), 500

@app.route("/api/auth/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            create_audit_log('login_failed', 'user', status='failed', error_message='Missing credentials')
            return jsonify({"error": "Invalid credentials"}), 401
        
        email = sanitize_input(data['email'], 254).lower().strip()
        password = sanitize_input(data['password'], 128)
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user or not verify_password(password, user.password_hash):
            create_audit_log('login_failed', 'user', resource_id=email, status='failed', error_message='Invalid credentials')
            return jsonify({"error": "Invalid credentials"}), 401
        
        if not user.is_active:
            create_audit_log('login_failed', 'user', resource_id=user.id, status='failed', error_message='Account disabled')
            return jsonify({"error": "Account disabled"}), 401
        
        # Create session
        session_id = create_user_session(
            user_id=user.id,
            user_agent=request.headers.get('User-Agent'),
            ip_address=request.remote_addr
        )
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # Store refresh token with session reference
        token_hash = hash_password(refresh_token)
        refresh_token_obj = RefreshToken(
            user_id=user.id,
            session_id=session_id,
            token_hash=token_hash,
            expires_at=datetime.datetime.utcnow() + app.config['JWT_REFRESH_TOKEN_EXPIRES'],
            user_agent=request.headers.get('User-Agent', ''),
            ip=request.remote_addr
        )
        db.session.add(refresh_token_obj)
        
        # Update user last login
        user.last_login = datetime.datetime.utcnow()
        
        db.session.commit()
        
        # Log successful login
        create_audit_log('login_success', 'user', resource_id=user.id, 
                        details={'session_id': session_id})
        
        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "session_id": session_id,
            "user": user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Login failed for email {email}: {str(e)}")
        create_audit_log('login_error', 'user', status='error', error_message=str(e))
        return jsonify({"error": "Login failed"}), 500

@app.route("/api/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user_id = get_jwt_identity()
        jti = get_jwt()['jti']
        
        # Revoke old refresh token
        blacklisted_tokens.add(jti)
        
        # Create new tokens
        new_access_token = create_access_token(identity=current_user_id)
        new_refresh_token = create_refresh_token(identity=current_user_id)
        
        return jsonify({
            "access_token": new_access_token,
            "refresh_token": new_refresh_token
        }), 200
    
    except Exception as e:
        logger.error(f"Token refresh failed for user {current_user_id}: {str(e)}")
        return jsonify({"error": "Token refresh failed"}), 500

@app.route("/api/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    try:
        jti = get_jwt()['jti']
        blacklisted_tokens.add(jti)
        return jsonify({"message": "Successfully logged out"}), 200
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        return jsonify({"error": "Logout failed"}), 500

@app.route("/api/me", methods=["GET"])
@jwt_required()
def get_me():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to get user info for user {current_user_id}: {str(e)}")
        return jsonify({"error": "Failed to get user info"}), 500

# User Profile Management
@app.route("/api/user/profile", methods=["PUT"])
@jwt_required()
@audit_action('update_profile', 'user')
def update_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        updatable_fields = ['first_name', 'last_name', 'avatar_url', 'department', 'organization', 'timezone', 'language']
        for field in updatable_fields:
            if field in data:
                setattr(user, field, sanitize_input(str(data[field]), 100))
        
        # Update preferences
        if 'preferences' in data:
            import json
            user.preferences = json.dumps(data['preferences'])
        
        db.session.commit()
        
        return jsonify({"user": user.to_dict(include_sensitive=True)}), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Profile update failed for user {current_user_id}: {str(e)}")
        return jsonify({"error": "Profile update failed"}), 500

# Data Source Management
@app.route("/api/data-sources", methods=["GET"])
@jwt_required()
def get_data_sources():
    try:
        current_user_id = get_jwt_identity()
        data_sources = DataSource.query.filter_by(user_id=current_user_id, is_active=True).all()
        
        return jsonify({
            "data_sources": [ds.to_dict() for ds in data_sources]
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to get data sources for user {current_user_id}: {str(e)}")
        return jsonify({"error": "Failed to get data sources"}), 500

@app.route("/api/data-sources", methods=["POST"])
@jwt_required()
@audit_action('create_data_source', 'data_source')
def create_data_source():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        required_fields = ['name', 'type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400
        
        # Validate data source type
        allowed_types = ['postgresql', 'mysql', 'mongodb', 'csv', 'json', 'api', 'excel']
        if data['type'] not in allowed_types:
            return jsonify({"error": "Invalid data source type"}), 400
        
        # Encrypt configuration if provided
        config_encrypted = None
        if data.get('config'):
            config_encrypted = encrypt_config(data['config'])
        
        data_source = DataSource(
            user_id=current_user_id,
            name=sanitize_input(data['name'], 100),
            type=data['type'],
            config=config_encrypted,
            description=sanitize_input(data.get('description', ''), 500),
            tags=json.dumps(data.get('tags', []))
        )
        
        db.session.add(data_source)
        db.session.commit()
        
        return jsonify({"data_source": data_source.to_dict()}), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Data source creation failed for user {current_user_id}: {str(e)}")
        return jsonify({"error": "Data source creation failed"}), 500

@app.route("/api/data-sources/<int:ds_id>/test", methods=["POST"])
@jwt_required()
@audit_action('test_data_source', 'data_source')
def test_data_source(ds_id):
    try:
        current_user_id = get_jwt_identity()
        data_source = DataSource.query.filter_by(id=ds_id, user_id=current_user_id).first()
        
        if not data_source:
            return jsonify({"error": "Data source not found"}), 404
        
        # Decrypt and test connection using appropriate connector
        from backend.shared.data_connectors.connectors import test_data_source_connection
        
        config = decrypt_config(data_source.config) if data_source.config else {}
        test_result = test_data_source_connection(data_source.type, config)
        
        # Add timestamp
        test_result["tested_at"] = datetime.datetime.utcnow().isoformat()
        
        # Update data source status
        data_source.status = test_result['status']
        data_source.last_test = datetime.datetime.utcnow()
        data_source.error_message = test_result.get('message') if test_result['status'] == 'failed' else None
        
        db.session.commit()
        
        return jsonify(test_result), 200 if test_result['status'] in ['connected', 'success'] else 400
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Data source test failed for user {current_user_id}, ds_id {ds_id}: {str(e)}")
        
        # Update data source with error
        if 'data_source' in locals():
            data_source.status = 'failed'
            data_source.last_test = datetime.datetime.utcnow()
            data_source.error_message = str(e)
            db.session.commit()
        
        return jsonify({"error": "Connection test failed", "details": str(e)}), 500

@app.route("/api/data-sources/<int:ds_id>/schema", methods=["GET"])
@jwt_required()
@audit_action('get_data_source_schema', 'data_source')
def get_data_source_schema(ds_id):
    try:
        current_user_id = get_jwt_identity()
        data_source = DataSource.query.filter_by(id=ds_id, user_id=current_user_id).first()
        
        if not data_source:
            return jsonify({"error": "Data source not found"}), 404
        
        from backend.shared.data_connectors.connectors import get_connector
        
        config = decrypt_config(data_source.config) if data_source.config else {}
        connector = get_connector(data_source.type, config)
        
        if not connector:
            return jsonify({"error": "Unsupported data source type"}), 400
        
        schema_result = connector.get_schema()
        return jsonify(schema_result), 200 if schema_result['status'] == 'success' else 400
    
    except Exception as e:
        logger.error(f"Schema retrieval failed for user {current_user_id}, ds_id {ds_id}: {str(e)}")
        return jsonify({"error": "Schema retrieval failed", "details": str(e)}), 500

@app.route("/api/data-sources/<int:ds_id>/query", methods=["POST"])
@jwt_required()
@audit_action('query_data_source', 'data_source')
def query_data_source(ds_id):
    try:
        current_user_id = get_jwt_identity()
        data_source = DataSource.query.filter_by(id=ds_id, user_id=current_user_id).first()
        
        if not data_source:
            return jsonify({"error": "Data source not found"}), 404
        
        data = request.get_json() or {}
        query = data.get('query')
        limit = min(data.get('limit', 100), 1000)  # Max 1000 rows
        
        from backend.shared.data_connectors.connectors import get_connector
        
        config = decrypt_config(data_source.config) if data_source.config else {}
        connector = get_connector(data_source.type, config)
        
        if not connector:
            return jsonify({"error": "Unsupported data source type"}), 400
        
        query_result = connector.query_data(query, limit)
        return jsonify(query_result), 200 if query_result['status'] == 'success' else 400
    
    except Exception as e:
        logger.error(f"Data query failed for user {current_user_id}, ds_id {ds_id}: {str(e)}")
        return jsonify({"error": "Data query failed", "details": str(e)}), 500

# Session Management
@app.route("/api/user/sessions", methods=["GET"])
@jwt_required()
def get_user_sessions():
    try:
        current_user_id = get_jwt_identity()
        sessions = UserSession.query.filter_by(user_id=current_user_id, is_active=True).order_by(UserSession.last_activity.desc()).all()
        
        return jsonify({
            "sessions": [session.to_dict() for session in sessions]
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to get sessions for user {current_user_id}: {str(e)}")
        return jsonify({"error": "Failed to get sessions"}), 500

@app.route("/api/user/sessions/<session_id>", methods=["DELETE"])
@jwt_required()
@audit_action('revoke_session', 'session')
def revoke_session(session_id):
    try:
        current_user_id = get_jwt_identity()
        session = UserSession.query.filter_by(session_id=session_id, user_id=current_user_id).first()
        
        if not session:
            return jsonify({"error": "Session not found"}), 404
        
        # Mark session as inactive
        session.is_active = False
        
        # Revoke associated refresh tokens
        refresh_tokens = RefreshToken.query.filter_by(session_id=session_id, user_id=current_user_id).all()
        for token in refresh_tokens:
            token.revoked_at = datetime.datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({"message": "Session revoked successfully"}), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Session revocation failed for user {current_user_id}, session {session_id}: {str(e)}")
        return jsonify({"error": "Session revocation failed"}), 500

# Integration Management
@app.route("/api/user/integrations", methods=["GET"])
@jwt_required()
def get_integrations():
    try:
        current_user_id = get_jwt_identity()
        integrations = Integration.query.filter_by(user_id=current_user_id, is_active=True).all()
        
        return jsonify({
            "integrations": [integration.to_dict() for integration in integrations]
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to get integrations for user {current_user_id}: {str(e)}")
        return jsonify({"error": "Failed to get integrations"}), 500

# Audit Logs
@app.route("/api/user/audit-logs", methods=["GET"])
@jwt_required()
def get_audit_logs():
    try:
        current_user_id = get_jwt_identity()
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        logs = AuditLog.query.filter_by(user_id=current_user_id).order_by(AuditLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            "logs": [log.to_dict() for log in logs.items],
            "pagination": {
                "page": logs.page,
                "pages": logs.pages,
                "per_page": logs.per_page,
                "total": logs.total
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to get audit logs for user {current_user_id}: {str(e)}")
        return jsonify({"error": "Failed to get audit logs"}), 500

@app.route("/api/healthz")
def health():
    try:
        # Simple database connectivity check
        db.session.execute(db.text('SELECT 1'))
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "database": "disconnected"}), 503

def create_tables():
    """Create database tables"""
    with app.app_context():
        db.create_all()

def main():
    create_tables()
    
    # Security: Only enable debug mode in development
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    if debug_mode and os.getenv('FLASK_ENV') == 'production':
        print("WARNING: Debug mode disabled in production for security")
        debug_mode = False
    
    port = int(os.getenv('PORT', 8000))
    host = os.getenv('HOST', '0.0.0.0')
    
    app.run(port=port, debug=debug_mode, host=host)

if __name__ == "__main__":
    main()
