#!/usr/bin/env python3
"""
Integration Tests for AI Data Platform API
Migrated and adapted from root test_saas_api.py
"""

import pytest
import requests
import json
import time
import os
import sys
from typing import Dict, Any

# Add backend to path for imports
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_path)

class TestAPIIntegration:
    """API Integration Test Suite"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup for each test"""
        self.base_url = os.getenv('TEST_API_URL', 'http://localhost:8000')
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.user_data = None
        self.test_user_email = f"testuser{int(time.time())}@example.com"
        self.test_password = "SecurePass123!"
        
    def headers(self) -> Dict[str, str]:
        """Get headers with authorization"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    def test_server_health(self):
        """Test server health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/healthz")
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "healthy"
            print("✅ Health check passed")
        except requests.ConnectionError:
            pytest.skip("Backend server not running")
    
    def test_user_registration(self):
        """Test user registration"""
        payload = {
            "email": self.test_user_email,
            "password": self.test_password
        }
        
        response = self.session.post(
            f"{self.base_url}/api/auth/register",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data.get("ok") is True
        print(f"✅ User registration successful: {self.test_user_email}")
    
    def test_user_login(self):
        """Test user login and token generation"""
        # First register the user (if not already done)
        self.test_user_registration()
        
        payload = {
            "email": self.test_user_email,
            "password": self.test_password
        }
        
        response = self.session.post(
            f"{self.base_url}/api/auth/login",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        
        # Store tokens for subsequent tests
        self.access_token = data["access_token"]
        self.refresh_token = data.get("refresh_token")
        self.user_data = data["user"]
        
        print(f"✅ User login successful, got access token")
    
    def test_get_user_profile(self):
        """Test getting user profile"""
        # Ensure we're logged in
        if not self.access_token:
            self.test_user_login()
        
        response = self.session.get(
            f"{self.base_url}/api/me",
            headers=self.headers()
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert data["email"] == self.test_user_email
        print("✅ User profile retrieval successful")
    
    def test_data_sources_crud(self):
        """Test data sources CRUD operations"""
        # Ensure we're logged in
        if not self.access_token:
            self.test_user_login()
        
        # Test GET empty list
        response = self.session.get(
            f"{self.base_url}/api/data-sources",
            headers=self.headers()
        )
        assert response.status_code == 200
        data = response.json()
        assert "data_sources" in data
        initial_count = len(data["data_sources"])
        
        # Test CREATE data source
        create_payload = {
            "name": f"Test PostgreSQL {int(time.time())}",
            "type": "postgresql",
            "description": "Test database connection",
            "config": {
                "host": "localhost",
                "port": 5432,
                "database": "test_db",
                "username": "test_user"
            },
            "tags": ["test", "postgresql"]
        }
        
        response = self.session.post(
            f"{self.base_url}/api/data-sources",
            json=create_payload,
            headers=self.headers()
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "data_source" in data
        data_source_id = data["data_source"]["id"]
        print(f"✅ Data source created with ID: {data_source_id}")
        
        # Test GET list with new item
        response = self.session.get(
            f"{self.base_url}/api/data-sources",
            headers=self.headers()
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data_sources"]) == initial_count + 1
        
        # Test connection test
        response = self.session.post(
            f"{self.base_url}/api/data-sources/{data_source_id}/test",
            headers=self.headers()
        )
        
        # Should return connection test result (may succeed or fail depending on mock)
        assert response.status_code in [200, 400]  # 400 for failed connection is also valid
        data = response.json()
        assert "status" in data
        print(f"✅ Data source test completed: {data.get('status')}")
    
    def test_authentication_flow(self):
        """Test complete authentication flow"""
        # Register
        self.test_user_registration()
        
        # Login
        self.test_user_login()
        
        # Access protected endpoint
        self.test_get_user_profile()
        
        # Test logout
        response = self.session.post(
            f"{self.base_url}/api/auth/logout",
            headers=self.headers()
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print("✅ Logout successful")
        
        # Test that token is now invalid
        response = self.session.get(
            f"{self.base_url}/api/me",
            headers=self.headers()
        )
        
        assert response.status_code == 401
        print("✅ Token invalidation confirmed")
    
    def test_invalid_requests(self):
        """Test various invalid request scenarios"""
        # Test invalid login
        response = self.session.post(
            f"{self.base_url}/api/auth/login",
            json={"email": "invalid@example.com", "password": "wrongpass"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 401
        
        # Test accessing protected endpoint without token
        response = self.session.get(f"{self.base_url}/api/me")
        assert response.status_code == 401
        
        # Test invalid data source type
        if not self.access_token:
            self.test_user_login()
        
        response = self.session.post(
            f"{self.base_url}/api/data-sources",
            json={"name": "Invalid", "type": "invalid_type"},
            headers=self.headers()
        )
        assert response.status_code == 400
        
        print("✅ Invalid request handling verified")

def run_tests():
    """Run all tests"""
    print("🧪 Running API Integration Tests")
    print("=" * 50)
    
    # Run pytest
    pytest_args = [
        __file__,
        "-v",
        "--tb=short"
    ]
    
    return pytest.main(pytest_args)

if __name__ == "__main__":
    run_tests()