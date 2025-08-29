#!/usr/bin/env python3
"""
基础认证设置脚本
为Flask应用添加简单的认证机制
"""
import os
import secrets
from pathlib import Path

def generate_auth_config():
    """生成基础认证配置"""
    print("🔐 生成基础认证配置...")
    
    # 生成安全密钥
    secret_key = secrets.token_hex(32)
    
    # 创建环境变量文件
    env_content = f"""# Flask应用环境配置
SECRET_KEY={secret_key}
FLASK_ENV=development
PORT=80

# 基础认证配置（可选）
# BASIC_AUTH_USERNAME=admin
# BASIC_AUTH_PASSWORD={secrets.token_urlsafe(16)}

# 数据库配置（如需要）
# DATABASE_URL=sqlite:///app.db

# 调试模式
DEBUG=True
"""
    
    env_file = Path(".env")
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print(f"✅ 环境配置文件已创建: {env_file}")
    print("⚠️ 请勿将 .env 文件提交到版本控制系统")
    
    # 创建 .gitignore 条目
    gitignore = Path(".gitignore")
    gitignore_content = ""
    
    if gitignore.exists():
        with open(gitignore, "r") as f:
            gitignore_content = f.read()
    
    if ".env" not in gitignore_content:
        with open(gitignore, "a") as f:
            if gitignore_content and not gitignore_content.endswith('\n'):
                f.write('\n')
            f.write("# 环境变量文件\n.env\n")
        print("✅ 已更新 .gitignore 文件")

def create_auth_middleware():
    """创建认证中间件示例"""
    print("🛡️ 创建认证中间件示例...")
    
    auth_middleware = """# Flask认证中间件示例
# 在main.py中使用此代码添加基础认证

from functools import wraps
from flask import request, Response
import os

def check_auth(username, password):
    \"\"\"检查用户名和密码\"\"\"
    auth_user = os.environ.get('BASIC_AUTH_USERNAME', 'admin')
    auth_pass = os.environ.get('BASIC_AUTH_PASSWORD', 'password')
    return username == auth_user and password == auth_pass

def authenticate():
    \"\"\"发送401认证请求\"\"\"
    return Response(
        '需要认证才能访问此资源\\n'
        '请提供有效的用户名和密码。', 
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    \"\"\"认证装饰器\"\"\"
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# 使用方法：
# @app.route('/secure')
# @requires_auth
# def secure_route():
#     return 'This is a secure page!'
"""
    
    auth_file = Path(".scripts/auth-fixes/flask_auth_middleware.py")
    with open(auth_file, "w") as f:
        f.write(auth_middleware)
    
    print(f"✅ 认证中间件示例已创建: {auth_file}")

def main():
    """主函数"""
    print("🚀 开始设置基础认证...")
    
    try:
        generate_auth_config()
        create_auth_middleware()
        
        print("\n📋 设置完成！")
        print("==================")
        print("1. 环境配置文件 .env 已创建")
        print("2. 认证中间件示例已创建")
        print("3. .gitignore 已更新")
        print()
        print("💡 使用说明:")
        print("- 修改 .env 文件中的认证配置")
        print("- 在 main.py 中导入并使用认证中间件")
        print("- 重启应用使配置生效")
        
        return True
        
    except Exception as e:
        print(f"❌ 设置过程发生错误: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)