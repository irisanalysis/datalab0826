"""
Pytest configuration and fixtures for SaaS Data Analysis Platform
"""
import pytest
import os
import tempfile
import datetime
from unittest.mock import Mock, patch
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

# Import the app and models
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app, db, User, DataSource, UserSession, Integration, AuditLog, RefreshToken


@pytest.fixture(scope="session")
def test_app():
    """Create a Flask application configured for testing"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
    
    # Use in-memory SQLite for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configure test environment variables
    with patch.dict(os.environ, {
        'POSTGRES_HOST': 'test',
        'POSTGRES_DB': 'test',
        'POSTGRES_USER': 'test',
        'POSTGRES_PASSWORD': 'test',
        'FLASK_ENV': 'testing'
    }):
        yield app


@pytest.fixture(scope="function")
def client(test_app):
    """Create a test client"""
    with test_app.test_client() as client:
        with test_app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture(scope="function")
def app_context(test_app):
    """Create application context"""
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_user(app_context):
    """Create a sample user for testing"""
    user = User(
        email='test@example.com',
        password_hash='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj.UVbNcq2K2',  # 'password'
        first_name='Test',
        last_name='User',
        role='user',
        department='Engineering',
        organization='Test Corp',
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_user(app_context):
    """Create an admin user for testing"""
    user = User(
        email='admin@example.com',
        password_hash='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj.UVbNcq2K2',  # 'password'
        first_name='Admin',
        last_name='User',
        role='admin',
        department='IT',
        organization='Test Corp',
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_data_source(app_context, sample_user):
    """Create a sample data source for testing"""
    data_source = DataSource(
        user_id=sample_user.id,
        name='Test Database',
        type='postgresql',
        config='{"host": "localhost", "port": 5432}',
        description='Test PostgreSQL database',
        status='connected'
    )
    db.session.add(data_source)
    db.session.commit()
    return data_source


@pytest.fixture
def user_session(app_context, sample_user):
    """Create a user session for testing"""
    session = UserSession(
        user_id=sample_user.id,
        session_id='test-session-123',
        ip_address='127.0.0.1',
        user_agent='Test Agent',
        is_active=True
    )
    db.session.add(session)
    db.session.commit()
    return session


@pytest.fixture
def access_token(client, sample_user):
    """Get access token for authenticated requests"""
    from flask_jwt_extended import create_access_token
    
    with client.application.app_context():
        token = create_access_token(identity=sample_user.id)
    return token


@pytest.fixture
def auth_headers(access_token):
    """Get authorization headers with access token"""
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def mock_data_connector():
    """Mock data connector for testing data source operations"""
    connector = Mock()
    connector.test_connection.return_value = {'status': 'success', 'message': 'Connection successful'}
    connector.get_schema.return_value = {
        'status': 'success',
        'tables': [
            {'name': 'users', 'columns': [{'name': 'id', 'type': 'integer'}]}
        ]
    }
    connector.query_data.return_value = {
        'status': 'success',
        'data': [{'id': 1, 'name': 'Test'}],
        'columns': ['id', 'name']
    }
    return connector


@pytest.fixture(scope="session")
def test_database_url():
    """Create temporary database for integration tests"""
    db_fd, db_path = tempfile.mkstemp()
    yield f'sqlite:///{db_path}'
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def mock_encryption_key():
    """Mock encryption key for testing"""
    with patch('os.getenv') as mock_getenv:
        mock_getenv.return_value = 'test-encryption-key-32-chars-long'
        yield 'test-encryption-key-32-chars-long'


@pytest.fixture
def sample_audit_log(app_context, sample_user):
    """Create a sample audit log entry"""
    audit_log = AuditLog(
        user_id=sample_user.id,
        action='login',
        resource='user',
        resource_id=str(sample_user.id),
        ip_address='127.0.0.1',
        endpoint='/api/auth/login',
        method='POST',
        status='success'
    )
    db.session.add(audit_log)
    db.session.commit()
    return audit_log


@pytest.fixture
def performance_test_data():
    """Generate test data for performance tests"""
    return {
        'users': [
            {
                'email': f'user{i}@example.com',
                'password': 'TestPassword123!',
                'first_name': f'User{i}',
                'last_name': 'Test'
            } for i in range(100)
        ],
        'data_sources': [
            {
                'name': f'Test DataSource {i}',
                'type': 'postgresql',
                'description': f'Test data source number {i}'
            } for i in range(50)
        ]
    }


# Test utility functions
def create_test_user(email='test@example.com', password='password', role='user'):
    """Helper function to create test users"""
    from main import hash_password
    
    user = User(
        email=email,
        password_hash=hash_password(password),
        role=role,
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    return user


def login_user(client, email='test@example.com', password='password'):
    """Helper function to login a user and get tokens"""
    response = client.post('/api/auth/login', json={
        'email': email,
        'password': password
    })
    return response


def get_auth_headers(token):
    """Helper function to get authorization headers"""
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }


# Custom pytest markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as a security test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Test data fixtures
@pytest.fixture
def valid_user_data():
    """Valid user registration data"""
    return {
        'email': 'newuser@example.com',
        'password': 'SecurePassword123!',
        'first_name': 'New',
        'last_name': 'User'
    }


@pytest.fixture
def invalid_user_data():
    """Invalid user registration data for testing validation"""
    return [
        # Missing email
        {'password': 'SecurePassword123!'},
        # Invalid email format
        {'email': 'invalid-email', 'password': 'SecurePassword123!'},
        # Weak password
        {'email': 'weak@example.com', 'password': '123'},
        # Missing password
        {'email': 'nopass@example.com'}
    ]


@pytest.fixture
def valid_data_source_data():
    """Valid data source creation data"""
    return {
        'name': 'Test PostgreSQL',
        'type': 'postgresql',
        'description': 'Test database connection',
        'config': {
            'host': 'localhost',
            'port': 5432,
            'database': 'testdb',
            'username': 'testuser'
        },
        'tags': ['database', 'test']
    }


@pytest.fixture(autouse=True)
def reset_blacklisted_tokens():
    """Reset blacklisted tokens before each test"""
    from main import blacklisted_tokens
    blacklisted_tokens.clear()
    yield
    blacklisted_tokens.clear()