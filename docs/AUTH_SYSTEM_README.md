# 用户认证系统 User Authentication System

基于Flask + PostgreSQL的完整用户认证系统，包含注册、登录、令牌刷新和用户管理功能。

A complete user authentication system built with Flask + PostgreSQL, featuring registration, login, token refresh, and user management.

## 🚀 快速开始 Quick Start

### 1. 安装依赖 Install Dependencies

```bash
# 使用 uv 安装依赖 (推荐)
uv venv
uv pip install -r requirements.txt

# 或使用 pip
pip install -r requirements.txt
```

### 2. 配置环境 Configure Environment

环境配置文件 `.env` 已包含外部PostgreSQL数据库连接信息：

```bash
POSTGRES_HOST=47.79.87.199
POSTGRES_PORT=5432
POSTGRES_DB=iris
POSTGRES_USER=jackchan
POSTGRES_PASSWORD=secure_password_123
JWT_SECRET=your-super-secret-jwt-key-please-change-in-production
ACCESS_TTL=900
REFRESH_TTL=604800
```

### 3. 启动应用 Start Application

```bash
# 使用开发服务器 (推荐)
./devserver.sh

# 或直接运行
uv run python main.py

# 或使用pip安装的Python
python main.py
```

应用将在 http://localhost 启动 (默认端口80)

### 4. 访问系统 Access System

打开浏览器访问: http://localhost

## 📱 功能特性 Features

### 🔐 安全认证 Security & Authentication
- ✅ **邮箱密码注册** Email/password registration
- ✅ **bcrypt密码哈希** bcrypt password hashing (cost=12)
- ✅ **JWT访问令牌** JWT access tokens (15分钟过期)
- ✅ **刷新令牌轮换** Refresh token rotation (7天过期)
- ✅ **密码强度验证** Password strength validation
- ✅ **令牌黑名单** Token blacklisting on logout

### 🎨 用户界面 User Interface
- ✅ **响应式设计** Responsive design
- ✅ **中英双语界面** Bilingual UI (Chinese/English)
- ✅ **实时密码强度指示** Real-time password strength indicator
- ✅ **表单验证和错误处理** Form validation and error handling
- ✅ **用户友好的加载状态** User-friendly loading states

### 🗄️ 数据管理 Data Management
- ✅ **外部PostgreSQL数据库** External PostgreSQL database
- ✅ **自动表创建** Automatic table creation
- ✅ **用户信息管理** User profile management
- ✅ **令牌历史追踪** Token history tracking

## 🔌 API 接口 API Endpoints

### 认证接口 Authentication

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 User registration |
| POST | `/api/auth/login` | 用户登录 User login |
| POST | `/api/auth/refresh` | 刷新令牌 Refresh token |
| POST | `/api/auth/logout` | 用户登出 User logout |

### 用户接口 User

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/me` | 获取当前用户信息 Get current user info |

### 健康检查 Health Check

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/healthz` | 系统健康检查 System health check |

## 🧪 API 测试 API Testing

使用提供的测试脚本：

```bash
# 测试所有API端点
./test_api.sh

# 测试指定服务器
./test_api.sh http://your-server.com
```

测试流程包括：
1. 健康检查
2. 用户注册
3. 用户登录
4. 获取用户信息
5. 刷新令牌
6. 使用新令牌获取用户信息
7. 用户登出
8. 登出后访问保护资源（应该失败）

## 🏗️ 数据库结构 Database Schema

### users 表
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### refresh_tokens 表
```sql
CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    token_hash VARCHAR(256) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    revoked_at TIMESTAMP,
    user_agent VARCHAR(500),
    ip VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🛡️ 安全特性 Security Features

- **密码策略**: 最少8字符，包含大小写字母和数字
- **bcrypt哈希**: 12轮加密保护密码
- **JWT令牌**: 安全的无状态认证
- **令牌轮换**: 防止令牌重放攻击
- **CORS保护**: 限制跨域访问
- **统一错误处理**: 避免信息泄露
- **数据库连接**: 使用SQLAlchemy ORM防止注入

## 🔧 开发说明 Development Notes

### 项目结构
```
/home/user/datalab0826/
├── main.py              # Flask应用主文件
├── src/index.html       # 前端单页应用
├── requirements.txt     # Python依赖
├── .env                 # 环境配置
├── test_api.sh         # API测试脚本
├── devserver.sh        # 开发服务器启动脚本
└── AUTH_SYSTEM_README.md # 项目文档
```

### 技术栈
- **后端**: Python Flask + SQLAlchemy + JWT
- **前端**: 原生HTML/CSS/JavaScript
- **数据库**: PostgreSQL
- **安全**: bcrypt + JWT + CORS

### 环境要求
- Python 3.8+
- PostgreSQL 12+ (外部数据库)
- 现代浏览器支持

## 🐛 故障排除 Troubleshooting

### 常见问题

1. **数据库连接失败**
   - 检查 `.env` 文件中的数据库连接信息
   - 确认PostgreSQL服务正在运行且可访问

2. **端口冲突**
   - 修改 `PORT` 环境变量更改端口
   - 默认端口为80

3. **CORS错误**
   - 检查前端请求的域名是否在允许列表中
   - 开发环境默认允许 `localhost` 访问

4. **JWT令牌错误**
   - 检查 `JWT_SECRET` 是否设置
   - 确认令牌未过期

### 日志查看
应用启动时会显示详细的错误信息，检查控制台输出获取调试信息。

## 📄 许可证 License

此项目仅用于学习和开发目的。
This project is for learning and development purposes only.

## 🤝 贡献 Contributing

欢迎提交问题和改进建议！
Welcome to submit issues and improvements!