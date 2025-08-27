#!/usr/bin/env python3
"""
API端点测试脚本
用于测试各种API接口的可用性和响应
"""
import requests
import json
import sys
from typing import Dict, Any, List

class APITester:
    def __init__(self, base_url: str = "http://localhost:80"):
        self.base_url = base_url
        self.results = []
    
    def test_endpoint(self, path: str, method: str = "GET", 
                     data: Dict[Any, Any] = None, 
                     expected_status: int = 200) -> bool:
        """测试单个API端点"""
        url = f"{self.base_url}{path}"
        print(f"🔍 测试 {method} {path}")
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, timeout=10)
            else:
                print(f"❌ 不支持的HTTP方法: {method}")
                return False
            
            success = response.status_code == expected_status
            result = {
                "endpoint": path,
                "method": method,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "success": success,
                "response_time": response.elapsed.total_seconds(),
                "content_length": len(response.content)
            }
            
            self.results.append(result)
            
            if success:
                print(f"✅ {path} - 状态码: {response.status_code}, "
                      f"响应时间: {result['response_time']:.3f}s")
            else:
                print(f"❌ {path} - 期望: {expected_status}, "
                      f"实际: {response.status_code}")
            
            return success
            
        except requests.exceptions.RequestException as e:
            print(f"❌ {path} - 连接错误: {e}")
            self.results.append({
                "endpoint": path,
                "method": method,
                "error": str(e),
                "success": False
            })
            return False
    
    def run_basic_tests(self) -> bool:
        """运行基本API测试"""
        print("🚀 开始API端点测试...")
        
        # 基本路由测试
        tests = [
            ("/", "GET", None, 200),  # 主页
        ]
        
        # 如果发现其他常见的API路径，添加到测试中
        # 这里可以根据实际项目扩展
        
        all_passed = True
        for path, method, data, expected in tests:
            if not self.test_endpoint(path, method, data, expected):
                all_passed = False
        
        return all_passed
    
    def generate_report(self) -> str:
        """生成测试报告"""
        passed = sum(1 for r in self.results if r.get('success', False))
        total = len(self.results)
        
        report = f"""
📊 API测试报告
===============
总测试数: {total}
通过: {passed}
失败: {total - passed}
成功率: {(passed/total*100):.1f}% (如果 total > 0)

详细结果:
"""
        
        for result in self.results:
            if result.get('success', False):
                report += f"✅ {result['method']} {result['endpoint']} - {result['status_code']}\n"
            else:
                report += f"❌ {result['method']} {result['endpoint']} - {result.get('status_code', 'ERROR')}\n"
        
        return report

def main():
    """主测试函数"""
    tester = APITester()
    
    try:
        # 运行测试
        success = tester.run_basic_tests()
        
        # 生成报告
        report = tester.generate_report()
        print(report)
        
        # 保存报告到文件
        with open(".scripts/testing/api_test_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        
        print("📄 测试报告已保存到 .scripts/testing/api_test_report.txt")
        
        return success
        
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
        return False
    except Exception as e:
        print(f"❌ 测试过程发生错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)