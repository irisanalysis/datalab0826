"""
Legacy Flask API - Backward compatibility layer
Migrated from root main.py
"""
import os
import sys
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

# Add backend to Python path for imports
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_path)

from shared.data_connectors import test_data_source_connection, get_connector

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
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'datalab')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')

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

# Import models from the main.py file structure
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
    provider = db.Column(db.String(50), nullable=False)
    provider_id = db.Column(db.String(100), nullable=False)
    access_token = db.Column(db.Text)  # Encrypted
    refresh_token = db.Column(db.Text)  # Encrypted
    token_expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False)
    resource = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.String(50))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    endpoint = db.Column(db.String(200))
    method = db.Column(db.String(10))
    details = db.Column(db.Text)  # JSON
    status = db.Column(db.String(20), default='success')
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
    return value.replace('\\x00', '').strip()[:max_length]

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

# Routes
@app.route("/")
def index():
    # Serve frontend from the correct path
    frontend_index = os.path.join(os.path.dirname(backend_path), 'src', 'index.html')
    if os.path.exists(frontend_index):
        return send_file(frontend_index)
    else:
        return jsonify({"message": "AI Data Platform Backend", "status": "running"}), 200

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
        
        logger.info(f"User registered: {email}")
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
            return jsonify({"error": "Invalid credentials"}), 401
        
        email = sanitize_input(data['email'], 254).lower().strip()
        password = sanitize_input(data['password'], 128)
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user or not verify_password(password, user.password_hash):
            return jsonify({"error": "Invalid credentials"}), 401
        
        if not user.is_active:
            return jsonify({"error": "Account disabled"}), 401
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # Update user last login
        user.last_login = datetime.datetime.utcnow()
        db.session.commit()
        
        logger.info(f"User logged in: {email}")
        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Login failed for email {email}: {str(e)}")
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
        
        return jsonify(user.to_dict()), 200
    
    except Exception as e:
        logger.error(f"Failed to get user info for user {current_user_id}: {str(e)}")
        return jsonify({"error": "Failed to get user info"}), 500

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
        
        data_source = DataSource(
            user_id=current_user_id,
            name=sanitize_input(data['name'], 100),
            type=data['type'],
            config=json.dumps(data.get('config', {})),
            description=sanitize_input(data.get('description', ''), 500),
            tags=json.dumps(data.get('tags', []))
        )
        
        db.session.add(data_source)
        db.session.commit()
        
        logger.info(f"Data source created: {data_source.name} by user {current_user_id}")
        return jsonify({"data_source": data_source.to_dict()}), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Data source creation failed for user {current_user_id}: {str(e)}")
        return jsonify({"error": "Data source creation failed"}), 500

@app.route("/api/data-sources/<int:ds_id>/test", methods=["POST"])
@jwt_required()
def test_data_source(ds_id):
    try:
        current_user_id = get_jwt_identity()
        data_source = DataSource.query.filter_by(id=ds_id, user_id=current_user_id).first()
        
        if not data_source:
            return jsonify({"error": "Data source not found"}), 404
        
        config = json.loads(data_source.config) if data_source.config else {}
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
        return jsonify({"error": "Connection test failed", "details": str(e)}), 500

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
    
    print(f"Starting Flask application on {host}:{port}")
    print(f"Debug mode: {debug_mode}")
    print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[0]}@[host]")
    
    app.run(port=port, debug=debug_mode, host=host)

if __name__ == "__main__":
    main()