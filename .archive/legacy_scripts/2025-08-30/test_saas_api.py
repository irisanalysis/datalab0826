#!/usr/bin/env python3
"""
Test script for SaaS Data Analysis Platform API endpoints
Tests all the new enterprise features and data management capabilities
"""

import requests
import json
import time
from typing import Dict, Any

class SaaSAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.user_data = None
        
    def headers(self) -> Dict[str, str]:
        """Get headers with authorization"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    def test_user_registration(self) -> bool:
        """Test user registration with new enterprise fields"""
        print("🔧 Testing user registration...")
        
        payload = {
            "email": f"testuser{int(time.time())}@example.com",
            "password": "SecurePass123!"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/register",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                print("✅ User registration successful")
                return True
            else:
                print(f"❌ Registration failed: {response.json()}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {str(e)}")
            return False
    
    def test_user_login(self) -> bool:
        """Test user login with session management"""
        print("🔧 Testing user login with session management...")
        
        # First register a test user
        test_email = f"testlogin{int(time.time())}@example.com"
        register_payload = {
            "email": test_email,
            "password": "SecurePass123!"
        }
        
        try:
            # Register
            reg_response = self.session.post(
                f"{self.base_url}/api/auth/register",
                json=register_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if reg_response.status_code != 201:
                print(f"❌ Registration failed for login test: {reg_response.json()}")
                return False
            
            # Login
            login_response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json=register_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                self.access_token = login_data.get("access_token")
                self.refresh_token = login_data.get("refresh_token")
                self.user_data = login_data.get("user")
                
                print("✅ Login successful with session management")
                print(f"   Session ID: {login_data.get('session_id', 'N/A')}")
                print(f"   User Role: {self.user_data.get('role', 'N/A')}")
                return True
            else:
                print(f"❌ Login failed: {login_response.json()}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def test_profile_update(self) -> bool:
        """Test user profile update with enterprise fields"""
        print("🔧 Testing user profile update...")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        update_payload = {
            "first_name": "John",
            "last_name": "Doe",
            "department": "Data Analytics",
            "organization": "Test Corp",
            "timezone": "America/New_York",
            "language": "en",
            "preferences": {
                "theme": "dark",
                "notifications": True,
                "default_chart_type": "bar"
            }
        }
        
        try:
            response = self.session.put(
                f"{self.base_url}/api/user/profile",
                json=update_payload,
                headers=self.headers()
            )
            
            if response.status_code == 200:
                updated_user = response.json().get("user", {})
                print("✅ Profile update successful")
                print(f"   Name: {updated_user.get('first_name')} {updated_user.get('last_name')}")
                print(f"   Department: {updated_user.get('department')}")
                print(f"   Preferences: {json.dumps(updated_user.get('preferences', {}), indent=2)}")
                return True
            else:
                print(f"❌ Profile update failed: {response.json()}")
                return False
                
        except Exception as e:
            print(f"❌ Profile update error: {str(e)}")
            return False
    
    def test_data_source_creation(self) -> bool:
        """Test data source creation"""
        print("🔧 Testing data source creation...")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        data_sources = [
            {
                "name": "Test PostgreSQL DB",
                "type": "postgresql",
                "description": "Test PostgreSQL connection",
                "tags": ["database", "test"],
                "config": {
                    "host": "localhost",
                    "port": 5432,
                    "database": "testdb",
                    "username": "testuser",
                    "password": "testpass"
                }
            },
            {
                "name": "Sample CSV File",
                "type": "csv",
                "description": "Sample CSV data source",
                "tags": ["file", "csv"],
                "config": {
                    "file_path": "/tmp/sample.csv"
                }
            },
            {
                "name": "Weather API",
                "type": "api",
                "description": "Weather data API",
                "tags": ["api", "weather"],
                "config": {
                    "url": "https://api.openweathermap.org/data/2.5/weather",
                    "headers": {"Content-Type": "application/json"},
                    "auth_token": "sample_token"
                }
            }
        ]\n        \n        created_sources = []\n        \n        for ds_config in data_sources:\n            try:\n                response = self.session.post(\n                    f\"{self.base_url}/api/data-sources\",\n                    json=ds_config,\n                    headers=self.headers()\n                )\n                \n                if response.status_code == 201:\n                    data_source = response.json().get(\"data_source\", {})\n                    created_sources.append(data_source)\n                    print(f\"✅ Created data source: {data_source.get('name')} (ID: {data_source.get('id')})\")\n                else:\n                    print(f\"❌ Failed to create {ds_config['name']}: {response.json()}\")\n                    \n            except Exception as e:\n                print(f\"❌ Data source creation error for {ds_config['name']}: {str(e)}\")\n        \n        return len(created_sources) > 0\n    \n    def test_data_source_listing(self) -> bool:\n        \"\"\"Test data source listing\"\"\"\n        print(\"🔧 Testing data source listing...\")\n        \n        if not self.access_token:\n            print(\"❌ No access token available\")\n            return False\n        \n        try:\n            response = self.session.get(\n                f\"{self.base_url}/api/data-sources\",\n                headers=self.headers()\n            )\n            \n            if response.status_code == 200:\n                data = response.json()\n                data_sources = data.get(\"data_sources\", [])\n                print(f\"✅ Retrieved {len(data_sources)} data sources\")\n                \n                for ds in data_sources:\n                    print(f\"   - {ds.get('name')} ({ds.get('type')}) - Status: {ds.get('status')}\")\n                \n                return True\n            else:\n                print(f\"❌ Data source listing failed: {response.json()}\")\n                return False\n                \n        except Exception as e:\n            print(f\"❌ Data source listing error: {str(e)}\")\n            return False\n    \n    def test_session_management(self) -> bool:\n        \"\"\"Test user session management\"\"\"\n        print(\"🔧 Testing session management...\")\n        \n        if not self.access_token:\n            print(\"❌ No access token available\")\n            return False\n        \n        try:\n            # Get active sessions\n            response = self.session.get(\n                f\"{self.base_url}/api/user/sessions\",\n                headers=self.headers()\n            )\n            \n            if response.status_code == 200:\n                sessions_data = response.json()\n                sessions = sessions_data.get(\"sessions\", [])\n                print(f\"✅ Retrieved {len(sessions)} active sessions\")\n                \n                for session in sessions:\n                    print(f\"   - Session ID: {session.get('session_id')[:16]}...\")\n                    print(f\"     IP: {session.get('ip_address')}\")\n                    print(f\"     Last Activity: {session.get('last_activity')}\")\n                \n                return True\n            else:\n                print(f\"❌ Session listing failed: {response.json()}\")\n                return False\n                \n        except Exception as e:\n            print(f\"❌ Session management error: {str(e)}\")\n            return False\n    \n    def test_audit_logs(self) -> bool:\n        \"\"\"Test audit log retrieval\"\"\"\n        print(\"🔧 Testing audit log retrieval...\")\n        \n        if not self.access_token:\n            print(\"❌ No access token available\")\n            return False\n        \n        try:\n            response = self.session.get(\n                f\"{self.base_url}/api/user/audit-logs?page=1&per_page=10\",\n                headers=self.headers()\n            )\n            \n            if response.status_code == 200:\n                audit_data = response.json()\n                logs = audit_data.get(\"logs\", [])\n                pagination = audit_data.get(\"pagination\", {})\n                \n                print(f\"✅ Retrieved {len(logs)} audit log entries\")\n                print(f\"   Total logs: {pagination.get('total', 'N/A')}\")\n                \n                for log in logs[:3]:  # Show first 3 logs\n                    print(f\"   - {log.get('action')} on {log.get('resource')} at {log.get('created_at')}\")\n                \n                return True\n            else:\n                print(f\"❌ Audit log retrieval failed: {response.json()}\")\n                return False\n                \n        except Exception as e:\n            print(f\"❌ Audit log error: {str(e)}\")\n            return False\n    \n    def test_health_check(self) -> bool:\n        \"\"\"Test health check endpoint\"\"\"\n        print(\"🔧 Testing health check...\")\n        \n        try:\n            response = self.session.get(f\"{self.base_url}/api/healthz\")\n            \n            if response.status_code == 200:\n                health_data = response.json()\n                print(f\"✅ Health check passed: {health_data.get('status')}\")\n                print(f\"   Database: {health_data.get('database')}\")\n                return True\n            else:\n                print(f\"❌ Health check failed: {response.json()}\")\n                return False\n                \n        except Exception as e:\n            print(f\"❌ Health check error: {str(e)}\")\n            return False\n    \n    def run_all_tests(self) -> None:\n        \"\"\"Run all test cases\"\"\"\n        print(\"=\" * 60)\n        print(\"🚀 Starting SaaS Data Analysis Platform API Tests\")\n        print(\"=\" * 60)\n        \n        tests = [\n            (\"Health Check\", self.test_health_check),\n            (\"User Registration\", self.test_user_registration),\n            (\"User Login\", self.test_user_login),\n            (\"Profile Update\", self.test_profile_update),\n            (\"Data Source Creation\", self.test_data_source_creation),\n            (\"Data Source Listing\", self.test_data_source_listing),\n            (\"Session Management\", self.test_session_management),\n            (\"Audit Logs\", self.test_audit_logs)\n        ]\n        \n        results = []\n        \n        for test_name, test_func in tests:\n            print(f\"\\n📋 Running: {test_name}\")\n            print(\"-\" * 40)\n            \n            try:\n                result = test_func()\n                results.append((test_name, result))\n            except Exception as e:\n                print(f\"❌ Test {test_name} failed with exception: {str(e)}\")\n                results.append((test_name, False))\n            \n            time.sleep(0.5)  # Small delay between tests\n        \n        # Summary\n        print(\"\\n\" + \"=\" * 60)\n        print(\"📊 Test Results Summary\")\n        print(\"=\" * 60)\n        \n        passed = 0\n        total = len(results)\n        \n        for test_name, result in results:\n            status = \"✅ PASS\" if result else \"❌ FAIL\"\n            print(f\"{status} {test_name}\")\n            if result:\n                passed += 1\n        \n        print(f\"\\n📈 Overall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)\")\n        \n        if passed == total:\n            print(\"🎉 All tests passed! SaaS platform is ready.\")\n        else:\n            print(\"⚠️  Some tests failed. Please check the implementation.\")\n\ndef main():\n    \"\"\"Main test runner\"\"\"\n    import sys\n    \n    base_url = sys.argv[1] if len(sys.argv) > 1 else \"http://localhost:8000\"\n    \n    print(f\"🔗 Testing API at: {base_url}\")\n    \n    tester = SaaSAPITester(base_url)\n    tester.run_all_tests()\n\nif __name__ == \"__main__\":\n    main()