你是一名资深全栈与安全架构工程师。请从零实现一个「用户登录验证系统」，并给出 **完整可运行** 的代码与文档，满足以下技术栈与部署要求：

# 0. 技术栈与总体目标
- 前端：Next.js 14（App Router）+ TypeScript
- 后端：Python FastAPI
- 数据库：PostgreSQL
- 部署：Docker Compose 一键启动（web=Next.js，api=FastAPI，db=Postgres，(可选) nginx 反代）
- 认证：邮箱 + 密码（bcrypt 存储），JWT（httpOnly + Secure Cookie）+ Refresh Token 轮换与撤销
- 安全：参数化/ORM 防注入、CORS 白名单、CSRF 方案、速率限制、统一错误、日志审计、密码策略

# 1. 功能范围（必须实现）
1) 注册：email、password；校验邮箱唯一；bcrypt 哈希；可留出“发送验证邮件”的挂钩（伪实现即可）
2) 登录：邮箱+密码；验证后签发 access & refresh；access 通过 httpOnly+Secure Cookie 下发；返回基础用户信息（不包含敏感字段）
3) 刷新：/api/auth/refresh 轮换 refresh（旧的标记 revoked + 失效时间），签发新 access；防止重放
4) 退出：撤销当前 refresh，清空 cookie
5) 受保护资源：/api/me 返回当前用户资料（需 access token）
6) 速率限制：对 /auth/* 路由应用（IP + 用户名维度）；返回一致的错误信息避免账户枚举
7) 健康检查：/healthz（api）、/readyz（api）；db 也有简单探针（如迁移完成标志/连通性）
8) 统一错误处理：不泄露“账号不存在/密码错误”细节，统一提示

# 2. 数据模型与迁移（必须提供）
- ORM：SQLAlchemy + Alembic（或 Tortoise ORM + Aerich，二选一但请**只选一个**并全程使用）
- 表：
  - users(id, email(unique, lowercase), password_hash, created_at, updated_at)
  - refresh_tokens(id, user_id, token_hash, expires_at, revoked_at, user_agent, ip, created_at)
- 提供 Alembic 迁移脚本与命令：
  - `alembic init`、env 配置、`alembic revision --autogenerate`、`alembic upgrade head`
- 读 `.env`：`DATABASE_URL`、`JWT_SECRET`、`ACCESS_TTL`、`REFRESH_TTL`、`CORS_ORIGIN` 等

# 3. 后端 FastAPI 详细要求
- 目录建议：
api/
app/
main.py
config.py
db.py
models.py
schemas.py
security.py # bcrypt、JWT、CSRF、cookie设定
deps.py # 依赖/鉴权
rate_limit.py # 速率限制(示例实现)
routers/
auth.py # register/login/refresh/logout
me.py # /api/me
health.py # /healthz /readyz
middleware.py # CORS、异常、日志
alembic/...
pyproject.toml 或 requirements.txt

- API 合约（全部实现）：
- `POST /api/auth/register`：{email, password}；重复邮箱报错；返回 {ok: true}
- `POST /api/auth/login`：签发 access & refresh（均用 httpOnly+Secure；可设置 SameSite=Lax/Strict 的取舍与理由），返回 {user}
- `POST /api/auth/refresh`：轮换 refresh，新发 access，撤销旧 refresh；处理重放
- `POST /api/auth/logout`：撤销当前 refresh，清空 cookie
- `GET /api/me`：需要 access token
- 安全实现要点（必须给出代码）：
- bcrypt（说明 cost 参数，给默认值）
- JWT：HS256、短期 access（如 15m）+ 较长 refresh（如 7d），存 httpOnly+Secure Cookie
- CSRF：在使用 cookie 方案时，提供一个简单 **双提交 Token** 或 **SameSite + POST Only + 自定义 Header** 的校验示例与中间件，并解释权衡
- CORS：仅允许 Next.js 域名/端口；预检
- 速率限制：提供朴素内存版或 Redis 版（选**一种**并给出代码；若用 Redis，请在 compose 中加 redis 服务）
- 日志：结构化日志，认证事件审计（登录成功/失败、刷新、登出、撤销）
- 统一错误：不暴露枚举信息（“账号不存在/密码错误”合并）

# 4. 前端 Next.js 详细要求
- 目录建议：
web/
app/
(auth)/
login/page.tsx
register/page.tsx
dashboard/page.tsx # 受保护页面
lib/api.ts # 基础 fetch，credentials: 'include'
lib/auth.ts # 服务器端鉴权工具（从 /api/me 判定）
next.config.ts
package.json

- 要点：
- 使用 `fetch` 调用后端 API，`credentials: 'include'`
- Server Components 示例：在 `dashboard/page.tsx` 中做服务端鉴权（若未登录重定向 /login）
- 表单校验：React Hook Form 或原生均可
- 友好的错误与 Loading 态
- .env 使用：`NEXT_PUBLIC_API_BASE`（或写死 compose 网络名）

# 5. Docker & 部署（必须提供完整文件）
- `docker-compose.yml`（**必须可一键启动**）：
- services：`db`(postgres)、`api`(fastapi+uvicorn)、`web`(next.js)、（可选）`nginx`
- 网络：同一自定义网络
- 卷：postgres 数据持久化
- 依赖与健康检查：
  - db: `pg_isready` 健康检查
  - api: 依赖 db，启动时执行 alembic upgrade；健康检查请求 `/healthz`
  - web: 依赖 api（可选健康检查 `/` 或自测路由）
- 环境变量从 `.env` 注入（提供 `.env.example`）
- `api/Dockerfile`：
- 多阶段构建；设置非 root 用户；仅暴露 8000；`CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`
- `web/Dockerfile`：
- 多阶段构建（依赖安装 → 构建 → 运行）；`next start` 产物
- （可选）`nginx` 反代（统一 80/443，路由到 web/api），如添加需给出 nginx.conf
- 启动文档（README 节点）：
- 首次运行：`cp .env.example .env && cd docker && docker compose up --build`
- 本地开发（不经 docker）亦给出命令（poetry/pip、pnpm/npm）

# 6. 配置与环境（必须提供）
- `.env.example`：
POSTGRES_DB=datairis
POSTGRES_USER=jackchan
POSTGRES_PASSWORD=secure_password_123
POSTGRES_PORT=5432
POSTGRES_HOST=47.79.87.199
JWT_SECRET=please_change_me
ACCESS_TTL=900 # 15m
REFRESH_TTL=604800 # 7d
CORS_ORIGIN=http://web:3000,http://localhost:3000

NODE_ENV=production
NEXT_PUBLIC_API_BASE=http://api:8000
- 任何需要的额外变量（如 REDIS_URL）请一并加入 `.env.example` 并在 compose 中体现

# 7. 输出格式与交付清单（顺序严格遵循）
A. **架构与时序**：用文字画出注册/登录/刷新/登出/访问受保护资源的交互时序  
B. **后端**：完整代码块（不省略 import），包含 `main.py / models.py / schemas.py / security.py / deps.py / rate_limit.py / routers/*.py / middleware.py / db.py / alembic/* / pyproject.toml 或 requirements.txt`  
C. **前端**：`package.json / next.config.ts / app/(auth)/login/page.tsx / app/(auth)/register/page.tsx / app/dashboard/page.tsx / lib/api.ts / lib/auth.ts` 的完整代码  
D. **Docker**：`docker/docker-compose.yml / api/Dockerfile / web/Dockerfile / (可选) nginx.conf` 完整代码  
E. **环境**：`.env.example` 完整内容  
F. **运行说明**：从零到起服务的命令；健康检查与常见问题（端口冲突、CORS、cookie 域/跨域、SameSite 设置）  
G. **安全检查清单**：密码策略、哈希参数、JWT 声明与过期、Cookie 属性、CORS、CSRF、速率限制、审计日志、错误处理  
H. **端到端测试脚本**：使用 curl/HTTPie（任选其一）给出“注册→登录→访问 /api/me→刷新→访问 /api/me→登出→访问 /api/me 失败”的完整命令序列；再补一个 Playwright（或 Vitest+supertest）最小可运行用例  
I. **取舍说明**：对 SameSite(Lax/Strict)、CSRF 方案、速率限制实现（内存 vs Redis）做明确选择与理由

# 8. 质量门槛（必须满足）
- clone/粘贴到本地后，只需 `cp .env.example .env && cd docker && docker compose up --build` 即可成功启动并通过健康检查
- 代码通过基本 lint/type check（给出 ruff/mypy 或 eslint/tsconfig 基础配置可加分）
- 访问流程可验证：注册 → 登录 → /dashboard 可访问 → 刷新 → 登出 → /dashboard 被重定向至 /login

请严格遵照以上规范，一次性输出所有文件与代码，不要省略任何关键部分。若存在实现路径选择，请先在文档开头给出“决策与理由”，然后只提供**单一版本**的完整实现（避免混用多套方案）。
