#!/usr/bin/env python3
"""
Simple test script to verify basic login functionality
"""

import os
import sys
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Basic configuration
jwt_secret = os.getenv('JWT_SECRET', 'dev-only-jwt-secret-change-for-production')
app.config['JWT_SECRET_KEY'] = jwt_secret
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(seconds=900)

# Database configuration
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

if all([POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD]):
    encoded_password = quote_plus(POSTGRES_PASSWORD)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{encoded_password}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
else:
    print("Missing database configuration")
    sys.exit(1)

# Initialize extensions
CORS(app, origins=['*'], supports_credentials=True)
jwt = JWTManager(app)
db = SQLAlchemy(app)

# Simple User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), default='user')
    is_active = db.Column(db.Boolean, default=True)

def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

@app.route("/api/auth/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({"error": "Email and password are required"}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        if not verify_password(password, user.password_hash):
            return jsonify({"error": "Invalid password"}), 401
        
        if not user.is_active:
            return jsonify({"error": "Account disabled"}), 401
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            "access_token": access_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role
            }
        }), 200
    
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"error": "Login failed", "details": str(e)}), 500

@app.route("/api/healthz")
def health():
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503

if __name__ == "__main__":
    with app.app_context():
        port = int(os.getenv('PORT', 8001))
        print(f"Starting simple test server on port {port}")
        app.run(port=port, debug=True, host='0.0.0.0')