#!/usr/bin/env python3
"""
JWT认证设置脚本
为Flask应用添加JSON Web Token认证
"""
import os
import secrets
from pathlib import Path

def create_jwt_auth_module():
    """创建JWT认证模块"""
    print("🔐 创建JWT认证模块...")
    
    jwt_auth_code = '''"""
JWT认证模块
提供基于JWT的用户认证功能
使用前需要安装: uv pip install PyJWT
"""
import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
import os

class JWTAuth:
    def __init__(self, app=None, secret_key=None):
        self.app = app
        self.secret_key = secret_key or os.environ.get('SECRET_KEY', 'your-secret-key')
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化Flask应用"""
        app.config.setdefault('JWT_EXPIRATION_HOURS', 24)
        app.config.setdefault('JWT_ALGORITHM', 'HS256')
    
    def generate_token(self, user_id, username=None):
        """生成JWT令牌"""
        payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(
                hours=current_app.config.get('JWT_EXPIRATION_HOURS', 24)
            ),
            'iat': datetime.datetime.utcnow()
        }
        
        token = jwt.encode(
            payload,
            self.secret_key,
            algorithm=current_app.config.get('JWT_ALGORITHM', 'HS256')
        )
        return token
    
    def verify_token(self, token):
        """验证JWT令牌"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[current_app.config.get('JWT_ALGORITHM', 'HS256')]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return {'error': 'Token has expired'}
        except jwt.InvalidTokenError:
            return {'error': 'Invalid token'}
    
    def token_required(self, f):
        """JWT令牌验证装饰器"""
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            auth_header = request.headers.get('Authorization')
            
            if auth_header:
                try:
                    # Bearer <token> 格式
                    token = auth_header.split(" ")[1]
                except IndexError:
                    pass
            
            if not token:
                return jsonify({'message': 'Token is missing'}), 401
            
            payload = self.verify_token(token)
            if 'error' in payload:
                return jsonify({'message': payload['error']}), 401
            
            # 将用户信息添加到请求上下文
            request.current_user = payload
            return f(*args, **kwargs)
        
        return decorated

# 使用示例:
# from flask import Flask
# app = Flask(__name__)
# jwt_auth = JWTAuth(app)
#
# @app.route('/login', methods=['POST'])
# def login():
#     # 验证用户凭证
#     user_id = 1  # 从数据库获取
#     username = "admin"
#     token = jwt_auth.generate_token(user_id, username)
#     return jsonify({'token': token})
#
# @app.route('/protected')
# @jwt_auth.token_required
# def protected():
#     return jsonify({'message': f'Hello {request.current_user["username"]}!'})
'''
    
    jwt_file = Path(".scripts/auth-fixes/jwt_auth.py")
    with open(jwt_file, "w") as f:
        f.write(jwt_auth_code)
    
    print(f"✅ JWT认证模块已创建: {jwt_file}")

def create_jwt_example():
    """创建JWT使用示例"""
    print("📝 创建JWT使用示例...")
    
    example_code = '''#!/usr/bin/env python3
"""
JWT认证使用示例
演示如何在Flask应用中集成JWT认证
"""
from flask import Flask, request, jsonify
import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth_fixes.jwt_auth import JWTAuth

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# 初始化JWT认证
jwt_auth = JWTAuth(app)

# 模拟用户数据
users = {
    'admin': {'id': 1, 'username': 'admin', 'password': 'password'},
    'user': {'id': 2, 'username': 'user', 'password': '123456'}
}

@app.route('/login', methods=['POST'])
def login():
    """用户登录端点"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password required'}), 400
    
    username = data['username']
    password = data['password']
    
    # 验证用户凭证
    user = users.get(username)
    if user and user['password'] == password:
        token = jwt_auth.generate_token(user['id'], user['username'])
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {'id': user['id'], 'username': user['username']}
        })
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/protected')
@jwt_auth.token_required
def protected():
    """受保护的端点"""
    return jsonify({
        'message': f'Hello {request.current_user["username"]}!',
        'user_id': request.current_user['user_id'],
        'token_issued': request.current_user['iat']
    })

@app.route('/user/profile')
@jwt_auth.token_required
def user_profile():
    """用户资料端点"""
    user_id = request.current_user['user_id']
    username = request.current_user['username']
    
    return jsonify({
        'profile': {
            'id': user_id,
            'username': username,
            'created_at': '2024-01-01',  # 示例数据
            'role': 'admin' if username == 'admin' else 'user'
        }
    })

if __name__ == '__main__':
    print("🚀 启动JWT认证示例应用...")
    print("📋 测试端点:")
    print("  POST /login - 用户登录")
    print("  GET /protected - 受保护的资源")
    print("  GET /user/profile - 用户资料")
    print()
    print("💡 测试命令:")
    print("curl -X POST http://localhost:5000/login \\\\")
    print('     -H "Content-Type: application/json" \\\\')
    print('     -d \'{"username":"admin","password":"password"}\'')
    
    app.run(debug=True, port=5000)
'''
    
    example_file = Path(".scripts/auth-fixes/jwt_auth_example.py")
    with open(example_file, "w") as f:
        f.write(example_code)
    
    print(f"✅ JWT使用示例已创建: {example_file}")

def update_requirements():
    """更新依赖要求"""
    print("📦 更新依赖要求...")
    
    # 检查pyproject.toml是否存在
    pyproject_file = Path("pyproject.toml")
    if pyproject_file.exists():
        print("💡 建议在 pyproject.toml 中添加JWT依赖:")
        print('    PyJWT = "*"')
        print('    或者运行: uv pip install PyJWT')
    else:
        print("💡 运行以下命令安装JWT依赖:")
        print("    uv pip install PyJWT")

def main():
    """主函数"""
    print("🚀 开始设置JWT认证...")
    
    try:
        create_jwt_auth_module()
        create_jwt_example()
        update_requirements()
        
        print("\n📋 JWT认证设置完成！")
        print("========================")
        print("1. JWT认证模块已创建")
        print("2. 使用示例已创建")
        print("3. 请安装PyJWT依赖")
        print()
        print("💡 使用说明:")
        print("- 运行示例: uv run python .scripts/auth-fixes/jwt_auth_example.py")
        print("- 在主应用中导入 jwt_auth 模块")
        print("- 使用 @jwt_auth.token_required 装饰器保护路由")
        
        return True
        
    except Exception as e:
        print(f"❌ 设置过程发生错误: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
'''