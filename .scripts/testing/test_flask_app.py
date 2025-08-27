#!/usr/bin/env python3
"""
Flask应用集成测试脚本
测试主要路由和功能
"""
import sys
import os
import requests
import subprocess
import time
from pathlib import Path

def test_flask_app():
    """测试Flask应用的基本功能"""
    print("🧪 开始Flask应用测试...")
    
    # 检查应用文件是否存在
    if not Path("main.py").exists():
        print("❌ main.py 文件不存在")
        return False
    
    # 检查HTML文件是否存在
    html_file = Path("src/index.html")
    if not html_file.exists():
        print("❌ src/index.html 文件不存在")
        return False
    
    print("✅ 应用文件检查通过")
    
    try:
        # 启动Flask应用进程
        print("🚀 启动Flask应用...")
        env = os.environ.copy()
        env['PORT'] = '8888'  # 使用测试端口
        
        process = subprocess.Popen(
            ['uv', 'run', 'python', 'main.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 等待应用启动
        time.sleep(3)
        
        # 测试根路由
        response = requests.get('http://localhost:8888/', timeout=5)
        
        if response.status_code == 200:
            print("✅ 根路由响应正常")
            print(f"📊 响应长度: {len(response.text)} 字符")
            
            # 检查是否包含HTML内容
            if '<html' in response.text.lower():
                print("✅ 返回有效的HTML内容")
            else:
                print("⚠️ 响应不包含HTML标签")
            
            return True
        else:
            print(f"❌ 根路由响应异常，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试过程发生错误: {e}")
        return False
    finally:
        # 清理：终止Flask进程
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()

if __name__ == "__main__":
    success = test_flask_app()
    sys.exit(0 if success else 1)