import os
import datetime
import logging
from functools import wraps
from urllib.parse import quote_plus

from flask import Flask, send_file, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
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
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class RefreshToken(db.Model):
    __tablename__ = 'refresh_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
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
            return jsonify({"error": "Invalid credentials"}), 401
        
        email = sanitize_input(data['email'], 254).lower().strip()
        password = sanitize_input(data['password'], 128)
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user or not verify_password(password, user.password_hash):
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # Store refresh token
        token_hash = hash_password(refresh_token)
        refresh_token_obj = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.datetime.utcnow() + app.config['JWT_REFRESH_TOKEN_EXPIRES'],
            user_agent=request.headers.get('User-Agent', ''),
            ip=request.remote_addr
        )
        db.session.add(refresh_token_obj)
        db.session.commit()
        
        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "created_at": user.created_at.isoformat()
            }
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
        
        return jsonify({
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to get user info for user {current_user_id}: {str(e)}")
        return jsonify({"error": "Failed to get user info"}), 500

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
