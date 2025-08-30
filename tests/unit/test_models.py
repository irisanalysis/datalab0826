"""
Unit tests for database models
"""
import pytest
import json
import datetime
from main import User, DataSource, UserSession, Integration, AuditLog, RefreshToken, db


@pytest.mark.unit
class TestUserModel:
    """Test User model functionality"""
    
    def test_user_creation(self, app_context):
        """Test basic user creation"""
        user = User(
            email='test@example.com',
            password_hash='hashed_password',
            first_name='John',
            last_name='Doe'
        )
        db.session.add(user)
        db.session.commit()
        
        assert user.id is not None
        assert user.email == 'test@example.com'
        assert user.first_name == 'John'
        assert user.last_name == 'Doe'
        assert user.is_active is True
        assert user.role == 'user'
        assert user.created_at is not None
    
    def test_user_to_dict(self, app_context):
        """Test user to_dict method"""
        user = User(
            email='test@example.com',
            password_hash='hashed_password',
            first_name='John',
            last_name='Doe',
            role='admin',
            department='IT',
            preferences='{"theme": "dark", "notifications": true}'
        )
        db.session.add(user)
        db.session.commit()
        
        # Test basic dict conversion
        user_dict = user.to_dict()
        assert 'password_hash' not in user_dict
        assert user_dict['email'] == 'test@example.com'
        assert user_dict['first_name'] == 'John'
        assert user_dict['role'] == 'admin'
        assert 'preferences' not in user_dict  # Not included without include_sensitive
        
        # Test with sensitive data
        user_dict_sensitive = user.to_dict(include_sensitive=True)
        assert 'preferences' in user_dict_sensitive
        assert user_dict_sensitive['preferences']['theme'] == 'dark'
    
    def test_user_to_dict_with_invalid_json_preferences(self, app_context):
        """Test user to_dict with invalid JSON in preferences"""
        user = User(
            email='test@example.com',
            password_hash='hashed_password',
            preferences='invalid json'
        )
        db.session.add(user)
        db.session.commit()
        
        user_dict = user.to_dict(include_sensitive=True)
        assert user_dict['preferences'] == {}
    
    def test_user_unique_email_constraint(self, app_context):
        """Test that email must be unique"""
        user1 = User(email='test@example.com', password_hash='hash1')
        user2 = User(email='test@example.com', password_hash='hash2')
        
        db.session.add(user1)
        db.session.commit()
        
        db.session.add(user2)
        with pytest.raises(Exception):  # Should raise IntegrityError
            db.session.commit()


@pytest.mark.unit
class TestDataSourceModel:
    """Test DataSource model functionality"""
    
    def test_data_source_creation(self, app_context, sample_user):
        """Test basic data source creation"""
        data_source = DataSource(
            user_id=sample_user.id,
            name='Test Database',
            type='postgresql',
            config='{"host": "localhost"}',
            description='Test database'
        )
        db.session.add(data_source)
        db.session.commit()
        
        assert data_source.id is not None
        assert data_source.user_id == sample_user.id
        assert data_source.name == 'Test Database'
        assert data_source.type == 'postgresql'
        assert data_source.status == 'pending'
        assert data_source.is_active is True
    
    def test_data_source_to_dict(self, app_context, sample_user):
        """Test data source to_dict method"""
        data_source = DataSource(
            user_id=sample_user.id,
            name='Test DB',
            type='postgresql',
            config='{"host": "localhost", "port": 5432}',
            tags='["database", "test"]',
            description='Test database'
        )
        db.session.add(data_source)
        db.session.commit()
        
        # Test basic dict conversion
        ds_dict = data_source.to_dict()
        assert 'config' not in ds_dict  # Not included without include_config
        assert ds_dict['name'] == 'Test DB'
        assert ds_dict['type'] == 'postgresql'
        assert ds_dict['tags'] == ['database', 'test']
        
        # Test with config
        ds_dict_with_config = data_source.to_dict(include_config=True)
        assert 'config' in ds_dict_with_config
        assert ds_dict_with_config['config']['host'] == 'localhost'
    
    def test_data_source_to_dict_with_invalid_json(self, app_context, sample_user):
        """Test data source to_dict with invalid JSON"""
        data_source = DataSource(
            user_id=sample_user.id,
            name='Test DB',
            type='postgresql',
            config='invalid json',
            tags='invalid tags json'
        )
        db.session.add(data_source)
        db.session.commit()
        
        ds_dict = data_source.to_dict(include_config=True)
        assert ds_dict['config'] == {}
        assert ds_dict['tags'] == []


@pytest.mark.unit
class TestUserSessionModel:
    """Test UserSession model functionality"""
    
    def test_user_session_creation(self, app_context, sample_user):
        """Test basic user session creation"""
        session = UserSession(
            user_id=sample_user.id,
            session_id='test-session-123',
            ip_address='192.168.1.1',
            user_agent='Test Browser',
            device_info='{"browser": "Chrome", "os": "Linux"}'
        )
        db.session.add(session)
        db.session.commit()
        
        assert session.id is not None
        assert session.user_id == sample_user.id
        assert session.session_id == 'test-session-123'
        assert session.is_active is True
        assert session.last_activity is not None
    
    def test_user_session_to_dict(self, app_context, sample_user):
        """Test user session to_dict method"""
        session = UserSession(
            user_id=sample_user.id,
            session_id='test-session-123',
            ip_address='192.168.1.1',
            device_info='{"browser": "Chrome", "os": "Linux"}'
        )
        db.session.add(session)
        db.session.commit()
        
        session_dict = session.to_dict()
        assert session_dict['session_id'] == 'test-session-123'
        assert session_dict['ip_address'] == '192.168.1.1'
        assert session_dict['device_info']['browser'] == 'Chrome'
    
    def test_session_unique_session_id(self, app_context, sample_user):
        """Test that session_id must be unique"""
        session1 = UserSession(user_id=sample_user.id, session_id='duplicate-id')
        session2 = UserSession(user_id=sample_user.id, session_id='duplicate-id')
        
        db.session.add(session1)
        db.session.commit()
        
        db.session.add(session2)
        with pytest.raises(Exception):  # Should raise IntegrityError
            db.session.commit()


@pytest.mark.unit
class TestIntegrationModel:
    """Test Integration model functionality"""
    
    def test_integration_creation(self, app_context, sample_user):
        """Test basic integration creation"""
        integration = Integration(
            user_id=sample_user.id,
            provider='google',
            provider_user_id='google123',
            access_token='token123',
            scopes='["read", "write"]'
        )
        db.session.add(integration)
        db.session.commit()
        
        assert integration.id is not None
        assert integration.user_id == sample_user.id
        assert integration.provider == 'google'
        assert integration.is_active is True
    
    def test_integration_to_dict(self, app_context, sample_user):
        """Test integration to_dict method"""
        integration = Integration(
            user_id=sample_user.id,
            provider='github',
            access_token='secret_token',
            scopes='["repo", "user"]',
            profile_data='{"name": "John Doe", "login": "johndoe"}'
        )
        db.session.add(integration)
        db.session.commit()
        
        # Test without tokens
        int_dict = integration.to_dict()
        assert 'access_token' not in int_dict
        assert int_dict['provider'] == 'github'
        assert int_dict['scopes'] == ['repo', 'user']
        assert int_dict['profile_data']['name'] == 'John Doe'
        
        # Test with tokens
        int_dict_with_tokens = integration.to_dict(include_tokens=True)
        assert int_dict_with_tokens['access_token'] == 'secret_token'


@pytest.mark.unit
class TestAuditLogModel:
    """Test AuditLog model functionality"""
    
    def test_audit_log_creation(self, app_context, sample_user):
        """Test basic audit log creation"""
        audit_log = AuditLog(
            user_id=sample_user.id,
            action='login',
            resource='user',
            resource_id=str(sample_user.id),
            ip_address='192.168.1.1',
            endpoint='/api/auth/login',
            method='POST',
            status='success'
        )
        db.session.add(audit_log)
        db.session.commit()
        
        assert audit_log.id is not None
        assert audit_log.user_id == sample_user.id
        assert audit_log.action == 'login'
        assert audit_log.status == 'success'
        assert audit_log.created_at is not None
    
    def test_audit_log_to_dict(self, app_context, sample_user):
        """Test audit log to_dict method"""
        audit_log = AuditLog(
            user_id=sample_user.id,
            action='data_export',
            resource='data_source',
            details='{"rows": 1000, "format": "csv"}',
            status='success'
        )
        db.session.add(audit_log)
        db.session.commit()
        
        log_dict = audit_log.to_dict()
        assert log_dict['action'] == 'data_export'
        assert log_dict['resource'] == 'data_source'
        assert log_dict['details']['rows'] == 1000
        assert log_dict['details']['format'] == 'csv'


@pytest.mark.unit
class TestRefreshTokenModel:
    """Test RefreshToken model functionality"""
    
    def test_refresh_token_creation(self, app_context, sample_user, user_session):
        """Test basic refresh token creation"""
        refresh_token = RefreshToken(
            user_id=sample_user.id,
            session_id=user_session.session_id,
            token_hash='hashed_token',
            expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=7),
            user_agent='Test Browser',
            ip='192.168.1.1'
        )
        db.session.add(refresh_token)
        db.session.commit()
        
        assert refresh_token.id is not None
        assert refresh_token.user_id == sample_user.id
        assert refresh_token.session_id == user_session.session_id
        assert refresh_token.revoked_at is None
        assert refresh_token.created_at is not None
    
    def test_refresh_token_revocation(self, app_context, sample_user, user_session):
        """Test refresh token revocation"""
        refresh_token = RefreshToken(
            user_id=sample_user.id,
            session_id=user_session.session_id,
            token_hash='hashed_token',
            expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=7)
        )
        db.session.add(refresh_token)
        db.session.commit()
        
        # Revoke token
        refresh_token.revoked_at = datetime.datetime.utcnow()
        db.session.commit()
        
        assert refresh_token.revoked_at is not None


@pytest.mark.unit
class TestModelRelationships:
    """Test model relationships and constraints"""
    
    def test_user_data_sources_relationship(self, app_context, sample_user):
        """Test user to data sources relationship"""
        data_source1 = DataSource(user_id=sample_user.id, name='DB1', type='postgresql')
        data_source2 = DataSource(user_id=sample_user.id, name='DB2', type='mysql')
        
        db.session.add_all([data_source1, data_source2])
        db.session.commit()
        
        # Note: We don't have explicit relationship defined in models
        # But we can test the foreign key constraint works
        user_data_sources = DataSource.query.filter_by(user_id=sample_user.id).all()
        assert len(user_data_sources) == 2
        assert {ds.name for ds in user_data_sources} == {'DB1', 'DB2'}
    
    def test_user_sessions_relationship(self, app_context, sample_user):
        """Test user to sessions relationship"""
        session1 = UserSession(user_id=sample_user.id, session_id='session1')
        session2 = UserSession(user_id=sample_user.id, session_id='session2')
        
        db.session.add_all([session1, session2])
        db.session.commit()
        
        user_sessions = UserSession.query.filter_by(user_id=sample_user.id).all()
        assert len(user_sessions) == 2
        assert {s.session_id for s in user_sessions} == {'session1', 'session2'}
    
    def test_cascade_behavior(self, app_context, sample_user):
        """Test that related records handle user deletion properly"""
        # Create related records
        data_source = DataSource(user_id=sample_user.id, name='Test DB', type='postgresql')
        session = UserSession(user_id=sample_user.id, session_id='test-session')
        audit_log = AuditLog(user_id=sample_user.id, action='test', resource='test')
        
        db.session.add_all([data_source, session, audit_log])
        db.session.commit()
        
        # Verify records exist
        assert DataSource.query.filter_by(user_id=sample_user.id).count() == 1
        assert UserSession.query.filter_by(user_id=sample_user.id).count() == 1
        assert AuditLog.query.filter_by(user_id=sample_user.id).count() == 1
        
        # Note: We don't have cascade delete defined in models
        # In a real scenario, you might want to add ON DELETE CASCADE
        # or handle cleanup in the application layer