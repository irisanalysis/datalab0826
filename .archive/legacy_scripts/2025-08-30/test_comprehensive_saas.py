#!/usr/bin/env python3
"""
SaaS数据分析平台综合测试套件
包含API测试、数据库测试、安全测试和性能测试
"""

import pytest
import requests
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import subprocess
import os
import sys

# 测试配置
BASE_URL = "http://localhost:5000"
TEST_USER = {
    "email": "test@example.com",
    "password": "TestPass123!"
}

class TestSaaSPlatform:
    """SaaS平台综合测试套件"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """测试前设置"""
        self.session = requests.Session()
        self.auth_token = None
        
    def test_server_health(self):
        """测试服务器健康状态"""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "healthy"
        except requests.ConnectionError:
            pytest.skip("服务器未运行，跳过测试")

    def test_user_registration_and_login(self):
        """测试用户注册和登录流程"""
        # 注册新用户
        register_data = {
            "email": f"test_{int(time.time())}@example.com",
            "password": "TestPass123!"
        }
        
        response = self.session.post(f"{BASE_URL}/register", json=register_data)
        assert response.status_code == 201
        
        # 登录
        login_response = self.session.post(f"{BASE_URL}/login", json=register_data)
        assert login_response.status_code == 200
        
        data = login_response.json()
        assert "access_token" in data
        self.auth_token = data["access_token"]
        
    def test_jwt_token_validation(self):
        """测试JWT令牌验证"""
        if not self.auth_token:
            self.test_user_registration_and_login()
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = self.session.get(f"{BASE_URL}/api/user/profile", headers=headers)
        assert response.status_code == 200
        
    def test_user_profile_management(self):
        """测试用户资料管理"""
        if not self.auth_token:
            self.test_user_registration_and_login()
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # 更新用户资料
        profile_data = {
            "first_name": "Test",
            "last_name": "User",
            "role": "analyst",
            "department": "Data Science"
        }
        
        response = self.session.put(
            f"{BASE_URL}/api/user/profile", 
            json=profile_data, 
            headers=headers
        )
        assert response.status_code == 200
        
    def test_data_source_management(self):
        """测试数据源管理功能"""
        if not self.auth_token:
            self.test_user_registration_and_login()
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # 创建数据源
        datasource_data = {
            "name": "Test Database",
            "type": "postgresql",
            "config": {
                "host": "localhost",
                "port": 5432,
                "database": "test_db",
                "username": "test_user"
            }
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/data-sources", 
            json=datasource_data, 
            headers=headers
        )
        # 可能失败（数据库连接），但应该返回400而不是500
        assert response.status_code in [201, 400]
        
    def test_session_management(self):
        """测试会话管理功能"""
        if not self.auth_token:
            self.test_user_registration_and_login()
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # 获取活跃会话
        response = self.session.get(f"{BASE_URL}/api/user/sessions", headers=headers)
        assert response.status_code == 200
        
        sessions = response.json()
        assert isinstance(sessions, list)
        assert len(sessions) >= 1  # 至少有当前会话
        
    def test_audit_log_functionality(self):
        """测试审计日志功能"""
        if not self.auth_token:
            self.test_user_registration_and_login()
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # 获取审计日志
        response = self.session.get(f"{BASE_URL}/api/user/audit-logs", headers=headers)
        assert response.status_code == 200
        
        logs = response.json()
        assert "logs" in logs
        assert "total" in logs
        
    def test_api_error_handling(self):
        """测试API错误处理"""
        # 测试未认证访问
        response = self.session.get(f"{BASE_URL}/api/user/profile")
        assert response.status_code == 401
        
        # 测试无效令牌
        headers = {"Authorization": "Bearer invalid_token"}
        response = self.session.get(f"{BASE_URL}/api/user/profile", headers=headers)
        assert response.status_code == 401
        
        # 测试不存在的端点
        response = self.session.get(f"{BASE_URL}/api/nonexistent")
        assert response.status_code == 404

class TestPerformance:
    """性能测试套件"""
    
    def test_api_response_time(self):
        """测试API响应时间"""
        start_time = time.time()
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response_time < 1.0, f"响应时间过长: {response_time}秒"
        except requests.ConnectionError:
            pytest.skip("服务器未运行")
            
    def test_concurrent_requests(self):
        """测试并发请求处理能力"""
        def make_request():
            try:
                response = requests.get(f"{BASE_URL}/health", timeout=10)
                return response.status_code == 200
            except:
                return False
                
        # 并发10个请求
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]
            
        # 至少80%的请求应该成功
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.8, f"并发测试成功率过低: {success_rate}"

class TestSecurity:
    """安全测试套件"""
    
    def test_sql_injection_protection(self):
        """测试SQL注入防护"""
        malicious_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'/*",
            "' UNION SELECT * FROM users --"
        ]
        
        for payload in malicious_payloads:
            login_data = {
                "email": payload,
                "password": "test"
            }
            
            try:
                response = requests.post(f"{BASE_URL}/login", json=login_data, timeout=5)
                # 应该返回400(无效输入)而不是500(服务器错误)
                assert response.status_code != 500, f"可能存在SQL注入漏洞: {payload}"
            except requests.ConnectionError:
                pytest.skip("服务器未运行")
                
    def test_xss_protection(self):
        """测试XSS防护"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>"
        ]
        
        for payload in xss_payloads:
            register_data = {
                "email": f"test@example.com",
                "password": payload
            }
            
            try:
                response = requests.post(f"{BASE_URL}/register", json=register_data, timeout=5)
                # 应该拒绝恶意输入
                assert response.status_code in [400, 422], f"可能存在XSS漏洞: {payload}"
            except requests.ConnectionError:
                pytest.skip("服务器未运行")

class TestDataIntegrity:
    """数据完整性测试"""
    
    def test_database_constraints(self):
        """测试数据库约束"""
        # 测试重复邮箱注册
        user_data = {
            "email": "duplicate@example.com",
            "password": "TestPass123!"
        }
        
        try:
            # 第一次注册
            response1 = requests.post(f"{BASE_URL}/register", json=user_data, timeout=5)
            
            # 第二次注册相同邮箱
            response2 = requests.post(f"{BASE_URL}/register", json=user_data, timeout=5)
            
            # 第二次应该失败
            assert response2.status_code == 400, "数据库约束未生效"
        except requests.ConnectionError:
            pytest.skip("服务器未运行")

def generate_test_report():
    """生成测试报告"""
    print("=" * 50)
    print("SaaS数据分析平台测试报告")
    print("=" * 50)
    
    # 运行测试并收集结果
    test_results = {}
    
    try:
        # 检查服务器状态
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        test_results["server_status"] = "运行中" if response.status_code == 200 else "异常"
    except:
        test_results["server_status"] = "未启动"
        
    # 检查必要文件
    required_files = [
        "/home/user/datalab0826/main.py",
        "/home/user/datalab0826/requirements.txt",
        "/home/user/datalab0826/devserver.sh"
    ]
    
    test_results["files_exist"] = all(os.path.exists(f) for f in required_files)
    
    # 打印结果
    print(f"服务器状态: {test_results['server_status']}")
    print(f"必要文件: {'完整' if test_results['files_exist'] else '缺失'}")
    
    print("\n测试套件包含:")
    print("✓ API功能测试")
    print("✓ 认证和权限测试")
    print("✓ 性能测试")
    print("✓ 安全测试")
    print("✓ 数据完整性测试")
    
    print("\n运行方法:")
    print("pytest test_comprehensive_saas.py -v --tb=short")
    
    return test_results

if __name__ == "__main__":
    # 如果直接运行，生成测试报告
    generate_test_report()