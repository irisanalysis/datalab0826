# SaaS数据分析平台系统架构设计

## 1. 系统架构概览

### 1.1 整体架构模式
采用**现代化全栈架构 + 微服务后端 + 事件驱动**的企业级架构模式，基于现有的Flask+FastAPI+Next.js技术栈，确保可扩展性、安全性和可维护性。

**当前技术基础**：
- 主应用：Flask + JWT + PostgreSQL + SQLAlchemy (main.py)
- 微服务后端：FastAPI服务 (api/目录)
- 现代前端：Next.js 14 + TypeScript (web/目录)
- 容器化部署：Docker Compose (docker/目录)
- 开发工具：uv包管理、自动化测试、代码格式化

```
┌─────────────────────────────────────────────────────────────────┐
│                        客户端层                                    │
├─────────────────────────────────────────────────────────────────┤
│  Web App (Next.js)  │  Mobile App  │  Third-party Integrations  │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  • Authentication & Authorization  • Rate Limiting               │
│  • Request Routing                • API Versioning              │
│  • Load Balancing                 • Request/Response Logging    │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      业务服务层                                    │
├─────────────────────────────────────────────────────────────────┤
│ Auth Service   │ Data Source    │ Analytics      │ Notification  │
│ (FastAPI)      │ Service        │ Service        │ Service       │
│                │ (FastAPI)      │ (FastAPI)      │ (FastAPI)     │
├────────────────┼────────────────┼────────────────┼───────────────┤
│ Tenant         │ Report         │ Integration    │ Audit         │
│ Service        │ Service        │ Service        │ Service       │
│ (FastAPI)      │ (FastAPI)      │ (FastAPI)      │ (FastAPI)     │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      数据处理层                                    │
├─────────────────────────────────────────────────────────────────┤
│ Message Queue  │ Stream         │ Task Queue     │ Cache Layer   │
│ (RabbitMQ)     │ Processing     │ (Celery+Redis) │ (Redis)       │
│                │ (Apache Kafka) │                │               │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      数据存储层                                    │
├─────────────────────────────────────────────────────────────────┤
│ Primary DB     │ Analytics DB   │ Document Store │ File Storage  │
│ (PostgreSQL)   │ (ClickHouse)   │ (MongoDB)      │ (AWS S3)      │
│                │                │                │               │
│ Tenant Data    │ Time Series    │ Configurations │ Reports/Files │
│ User Data      │ Analytics Data │ Metadata       │ Attachments   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 核心设计原则

1. **多租户隔离**: 数据库层面和应用层面的双重隔离，基于现有JWT+用户表扩展
2. **事件驱动**: 异步处理和解耦服务，利用FastAPI的异步特性
3. **可扩展性**: 水平扩展和自动伸缩，Docker容器化部署
4. **安全优先**: 基于现有JWT认证系统，端到端加密和审计追踪
5. **高可用**: 故障转移和灾难恢复，健康检查和监控
6. **开发效率**: 基于uv的现代Python开发体验，自动化测试和部署
7. **类型安全**: TypeScript前端 + Pydantic后端，全栈类型安全

## 2. 微服务架构设计

### 2.1 核心服务拆分

#### 认证授权服务 (Auth Service)
- **职责**: 用户认证、JWT管理、权限控制
- **技术栈**: Flask + FastAPI + PostgreSQL + Redis
- **现有基础**: 
  - Flask应用已实现完整JWT认证系统 (main.py)
  - 用户注册/登录/登出/刷新令牌
  - bcrypt密码加密，安全请求头
  - 用户表、刷新令牌表已建立
  - 输入验证、速率限制、审计日志
- **扩展功能**:
  - 多租户用户管理
  - SSO集成 (SAML, OAuth2)
  - 多因素认证 (MFA)
  - 设备管理和会话控制 (基于现有RefreshToken表)
  - 角色权限管理 (RBAC) - 扩展现有User表

#### 租户管理服务 (Tenant Service)
- **职责**: 多租户管理、资源隔离、计费管理
- **技术栈**: FastAPI + PostgreSQL
- **核心功能**:
  - 租户创建和配置
  - 资源限制和配额管理
  - 数据隔离策略
  - 计费和使用统计

#### 数据源服务 (Data Source Service)
- **职责**: 数据源连接、数据同步、数据校验
- **技术栈**: FastAPI + PostgreSQL + Celery
- **核心功能**:
  - 多种数据源连接器 (MySQL, PostgreSQL, MongoDB, APIs)
  - 数据模式识别和映射
  - 增量同步和全量同步
  - 数据质量检查

#### 分析服务 (Analytics Service)
- **职责**: 数据处理、报表生成、可视化
- **技术栈**: FastAPI + ClickHouse + Redis
- **核心功能**:
  - 实时数据分析
  - 自定义报表生成
  - 数据可视化引擎
  - 预设分析模板

#### 集成服务 (Integration Service)
- **职责**: 第三方系统集成、Webhook管理
- **技术栈**: FastAPI + MongoDB
- **核心功能**:
  - API集成管理
  - Webhook处理
  - 数据格式转换
  - 集成状态监控

#### 通知服务 (Notification Service)
- **职责**: 消息推送、邮件通知、警报管理
- **技术栈**: FastAPI + RabbitMQ + Redis
- **核心功能**:
  - 多渠道通知 (邮件、SMS、推送)
  - 通知模板管理
  - 订阅管理
  - 警报规则引擎

#### 审计服务 (Audit Service)
- **职责**: 操作审计、安全监控、合规管理
- **技术栈**: FastAPI + PostgreSQL + ClickHouse
- **核心功能**:
  - 用户操作记录
  - 数据访问审计
  - 安全事件监控
  - 合规报告生成

### 2.2 服务间通信

#### 同步通信
- **HTTP/REST**: 用户请求处理
- **gRPC**: 服务间高性能调用
- **GraphQL**: 复杂数据查询

#### 异步通信
- **RabbitMQ**: 可靠消息传递
- **Apache Kafka**: 高吞吐量事件流
- **Redis Pub/Sub**: 实时通知

## 3. 数据架构设计

### 3.1 数据库选型策略

#### 主数据库 - PostgreSQL
```sql
-- 用户和租户管理
-- 配置和元数据存储
-- 事务数据处理
-- 关系型数据建模
```

#### 分析数据库 - ClickHouse
```sql
-- 大数据量分析
-- 时序数据存储
-- 实时聚合查询
-- OLAP处理
```

#### 文档数据库 - MongoDB
```sql
-- 非结构化数据
-- 配置文件存储
-- 集成数据缓存
-- 灵活模式数据
```

#### 缓存层 - Redis
```sql
-- 会话管理
-- 查询缓存
-- 实时计数器
-- 限流控制
```

### 3.2 数据隔离策略

#### 租户数据隔离模式
1. **数据库级隔离** (推荐)
   - 每个租户独立数据库
   - 完全数据隔离
   - 独立扩展能力

2. **模式级隔离**
   - 共享数据库，独立模式
   - 中等隔离级别
   - 资源共享优化

3. **行级隔离**
   - 共享表，tenant_id标识
   - 最低隔离级别
   - 最高资源利用率

## 4. API架构规范

### 4.1 API设计标准

#### 现有API端点 (main.py)
```yaml
# 当前已实现的认证API
POST /api/auth/register    # 用户注册
POST /api/auth/login      # 用户登录  
POST /api/auth/refresh    # 刷新令牌
POST /api/auth/logout     # 用户登出
GET  /api/me              # 获取当前用户信息
GET  /api/healthz         # 健康检查

# 扩展的RESTful API规范
/api/v1/users
/api/v2/users

# 多租户资源命名规范
GET    /api/v1/tenants/{tenant_id}/users
POST   /api/v1/tenants/{tenant_id}/users
PUT    /api/v1/tenants/{tenant_id}/users/{user_id}
DELETE /api/v1/tenants/{tenant_id}/users/{user_id}

# 数据源管理API
GET    /api/v1/tenants/{tenant_id}/data-sources
POST   /api/v1/tenants/{tenant_id}/data-sources
PUT    /api/v1/tenants/{tenant_id}/data-sources/{source_id}
DELETE /api/v1/tenants/{tenant_id}/data-sources/{source_id}

# 查询参数标准
GET /api/v1/users?page=1&limit=20&sort=created_at&order=desc&filter=active:true
```

#### 统一响应格式
```json
{
  "success": true,
  "data": {
    "users": [...],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 150,
      "pages": 8
    }
  },
  "message": "Users retrieved successfully",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_abc123xyz"
}
```

#### 错误处理标准
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_abc123xyz"
}
```

### 4.2 认证和授权

#### JWT Token结构
```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_123",
    "tenant_id": "tenant_456",
    "roles": ["admin", "analyst"],
    "permissions": ["read:users", "write:reports"],
    "iat": 1642243800,
    "exp": 1642247400
  }
}
```

#### 权限控制模型
```yaml
# 角色定义
roles:
  super_admin:
    description: "系统超级管理员"
    permissions: ["*"]
  
  tenant_admin:
    description: "租户管理员"
    permissions: ["tenant:*"]
  
  analyst:
    description: "数据分析师"
    permissions: ["read:data", "create:reports", "read:dashboards"]
  
  viewer:
    description: "只读用户"
    permissions: ["read:dashboards", "read:reports"]

# 资源权限映射
resources:
  users:
    create: ["tenant_admin"]
    read: ["tenant_admin", "analyst", "viewer"]
    update: ["tenant_admin"]
    delete: ["tenant_admin"]
  
  data_sources:
    create: ["tenant_admin", "analyst"]
    read: ["tenant_admin", "analyst", "viewer"]
    update: ["tenant_admin", "analyst"]
    delete: ["tenant_admin"]
```

## 5. 安全架构

### 5.1 多层安全防护

#### 网络层安全
- WAF (Web Application Firewall)
- DDoS防护
- IP白名单/黑名单
- 地理位置访问控制

#### 应用层安全
- 输入验证和输出编码
- SQL注入防护
- XSS防护
- CSRF令牌验证
- 安全请求头

#### 数据层安全
- 数据库访问控制
- 敏感数据加密
- 字段级加密
- 数据脱敏

### 5.2 加密策略

#### 传输加密
```yaml
# TLS配置
tls:
  version: "1.3"
  cipher_suites:
    - "TLS_AES_256_GCM_SHA384"
    - "TLS_AES_128_GCM_SHA256"
  
# HTTPS强制
security_headers:
  strict_transport_security: "max-age=31536000; includeSubDomains"
  content_security_policy: "default-src 'self'"
```

#### 存储加密
```yaml
# 数据库加密
database_encryption:
  at_rest: "AES-256-GCM"
  in_transit: "TLS 1.3"
  key_management: "AWS KMS"

# 敏感字段加密
sensitive_fields:
  - password_hash
  - api_keys
  - personal_data
  - financial_data
```

### 5.3 审计和监控

#### 审计日志格式
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "event_type": "USER_LOGIN",
  "user_id": "user_123",
  "tenant_id": "tenant_456",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "resource": "/api/v1/auth/login",
  "action": "POST",
  "result": "SUCCESS",
  "metadata": {
    "session_id": "sess_789",
    "device_id": "dev_012"
  }
}
```

#### 安全监控指标
- 异常登录检测
- API调用异常监控
- 数据访问模式分析
- 权限变更追踪
- 安全事件告警

## 6. 性能优化策略

### 6.1 缓存架构

#### 多级缓存策略
```yaml
# L1 Cache - 应用内存缓存
application_cache:
  type: "in-memory"
  ttl: 300
  max_size: "512MB"

# L2 Cache - Redis分布式缓存
distributed_cache:
  type: "redis"
  ttl: 3600
  cluster: true
  persistence: false

# L3 Cache - CDN边缘缓存
edge_cache:
  type: "cloudflare"
  ttl: 86400
  static_resources: true
```

#### 缓存失效策略
- TTL过期
- 主动失效
- 标签失效
- 分层失效

### 6.2 数据库优化

#### 索引策略
```sql
-- 复合索引设计
CREATE INDEX idx_user_tenant_status ON users(tenant_id, status, created_at);

-- 部分索引
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- 函数索引
CREATE INDEX idx_user_email_lower ON users(LOWER(email));
```

#### 查询优化
- 查询计划分析
- 慢查询监控
- 连接池优化
- 读写分离

### 6.3 负载均衡和扩展

#### 水平扩展策略
```yaml
# 负载均衡配置
load_balancer:
  algorithm: "round_robin"
  health_check: "/api/health"
  failover: true
  sticky_sessions: false

# 自动扩展
auto_scaling:
  min_instances: 2
  max_instances: 10
  cpu_threshold: 70
  memory_threshold: 80
  scale_up_cooldown: 300
  scale_down_cooldown: 600
```

## 7. 监控和可观测性

### 7.1 监控体系

#### 应用性能监控 (APM)
- 请求响应时间
- 错误率监控
- 吞吐量统计
- 资源使用率

#### 业务指标监控
- 用户活跃度
- 数据处理量
- 报表生成速度
- 集成成功率

#### 基础设施监控
- 服务器性能
- 数据库性能
- 网络状况
- 存储使用率

### 7.2 日志管理

#### 结构化日志格式
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "service": "auth-service",
  "request_id": "req_abc123",
  "user_id": "user_456",
  "tenant_id": "tenant_789",
  "message": "User authentication successful",
  "metadata": {
    "duration_ms": 150,
    "endpoint": "/api/v1/auth/login"
  }
}
```

#### 日志聚合和分析
- 集中式日志收集
- 实时日志分析
- 异常模式检测
- 日志保留策略

## 8. 部署和运维

### 8.1 容器化部署

#### 现有Docker Compose架构
当前项目已配置完整的多服务Docker部署 (docker/docker-compose.yml)：

```yaml
version: '3.8'
services:
  # PostgreSQL数据库
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: datairis
      POSTGRES_USER: jackchan  
      POSTGRES_PASSWORD: secure_password_123
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U jackchan -d datairis"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI后端服务
  api:
    build: ../api
    environment:
      DATABASE_URL: postgresql://jackchan:secure_password_123@db:5432/datairis
      JWT_SECRET: please_change_me
      ACCESS_TTL: 900
      REFRESH_TTL: 604800
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]

  # Next.js前端服务
  web:
    build: ../web
    environment:
      NODE_ENV: production
      NEXT_PUBLIC_API_BASE: http://api:8000
    ports:
      - "3000:3000"
    depends_on:
      api:
        condition: service_healthy
```

#### 开发环境启动脚本
```bash
# 当前开发服务器启动 (devserver.sh)
#!/bin/bash
uv run python -u -m flask --app main run -p $PORT --debug

# Docker环境启动
cd docker && docker-compose up -d
```

### 8.2 CI/CD流水线

#### GitHub Actions配置
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          docker build -t saas-platform .
          docker push ${{ secrets.DOCKER_REGISTRY }}/saas-platform
```

## 9. 技术选型总结

### 9.1 后端技术栈 (基于现有实现)
- **主应用框架**: Flask + JWT + SQLAlchemy (已实现，main.py)
- **微服务框架**: FastAPI (高性能异步框架，api/目录)
- **数据库**: PostgreSQL 15 (主数据库，已配置) + ClickHouse (分析数据库)
- **包管理**: uv (现代Python包管理器)
- **ORM**: SQLAlchemy (已实现User、RefreshToken模型)
- **认证**: JWT + bcrypt密码加密 (已实现)
- **缓存**: Redis (分布式缓存，计划扩展)
- **消息队列**: RabbitMQ + Apache Kafka (计划实现)
- **任务队列**: Celery + Redis (计划实现)
- **搜索引擎**: Elasticsearch (计划实现)

### 9.2 前端技术栈 (基于现有实现)
- **框架**: Next.js 14 (SSR/SSG支持，web/目录已配置)
- **类型安全**: TypeScript (推荐配置)
- **UI库**: Tailwind CSS + Headless UI
- **状态管理**: Zustand (推荐轻量级状态管理)
- **图表库**: Chart.js / D3.js (数据可视化)
- **表格组件**: TanStack Table (企业级表格)
- **表单处理**: React Hook Form + Zod验证
- **HTTP客户端**: Axios / SWR (数据获取)

### 9.3 基础设施 (基于现有配置)
- **容器化**: Docker Compose (已配置，docker/docker-compose.yml)
- **部署**: 支持本地开发 + 生产环境部署
- **健康检查**: 已配置数据库和服务健康检查
- **网络**: Docker bridge网络，服务间通信
- **数据持久化**: PostgreSQL数据卷
- **云平台**: AWS / Google Cloud / Vercel (推荐)
- **CDN**: CloudFlare (静态资源加速)
- **监控**: Prometheus + Grafana (计划实现)
- **日志**: 结构化日志记录 (已在main.py中实现)

### 9.4 选型理由

#### FastAPI vs Flask
- **性能**: FastAPI基于异步处理，性能更优
- **类型安全**: 内置Pydantic类型验证
- **文档**: 自动生成OpenAPI文档
- **现代性**: 支持最新Python特性

#### PostgreSQL vs MySQL
- **JSON支持**: 原生JSON类型和操作符
- **扩展性**: 丰富的扩展生态
- **并发性**: 更好的并发读写性能
- **数据完整性**: 严格的ACID特性

#### ClickHouse vs Traditional OLAP
- **性能**: 列式存储，查询速度快
- **压缩率**: 高压缩比，存储成本低
- **实时性**: 支持实时数据写入和查询
- **SQL兼容**: 标准SQL语法支持

#### 开发工具和流程
- **包管理**: uv (现代Python包管理器，已配置)
- **代码格式化**: autopep8 (已配置自动格式化脚本)
- **测试框架**: pytest + API测试脚本 (tests/目录)
- **开发服务器**: 热重载开发服务器 (devserver.sh)
- **环境管理**: .env配置文件 + Docker环境变量

## 10. 数据分析平台特定架构

### 10.1 数据处理管道架构

#### 数据摄取层
```yaml
# 数据源连接器配置
data_connectors:
  database:
    - type: postgresql
      connection_pool: 10
      timeout: 30s
    - type: mysql  
      connection_pool: 10
      timeout: 30s
    - type: mongodb
      connection_pool: 5
      timeout: 30s
  
  api:
    - type: rest_api
      rate_limit: 1000/hour
      retry_policy: exponential_backoff
    - type: graphql
      query_complexity_limit: 1000
      timeout: 60s
  
  file:
    - type: csv
      max_file_size: 100MB
      encoding: utf-8
    - type: json
      max_file_size: 50MB
      validation: json_schema
```

#### 数据转换引擎
```python
# 数据处理流水线
class DataPipeline:
    def __init__(self):
        self.extractors = {}
        self.transformers = {}
        self.loaders = {}
    
    async def process_data_source(self, source_id: str, config: dict):
        # 1. 数据抽取
        raw_data = await self.extract_data(source_id, config)
        
        # 2. 数据清洗和转换
        clean_data = await self.transform_data(raw_data, config.transformations)
        
        # 3. 数据验证
        validated_data = await self.validate_data(clean_data, config.schema)
        
        # 4. 数据加载到分析数据库
        await self.load_data(validated_data, config.target)
        
        return {
            "status": "success",
            "records_processed": len(validated_data),
            "duration": processing_time
        }
```

### 10.2 实时分析架构

#### 流处理引擎
```yaml
# Apache Kafka + Kafka Streams配置
streaming_processing:
  kafka:
    brokers: ["kafka-1:9092", "kafka-2:9092", "kafka-3:9092"]
    topics:
      - name: "raw-events"
        partitions: 12
        replication_factor: 3
      - name: "processed-events"
        partitions: 6
        replication_factor: 3
  
  kafka_streams:
    application_id: "data-analysis-streams"
    processing_guarantee: "exactly_once"
    state_store: "rocksdb"
    
  windowing:
    - type: "tumbling"
      size: "5 minutes"
    - type: "sliding" 
      size: "1 hour"
      advance: "15 minutes"
```

#### 实时仪表板更新
```typescript
// WebSocket连接管理
class RealtimeDashboard {
  private ws: WebSocket;
  private reconnectAttempts = 0;
  
  constructor(dashboardId: string) {
    this.connect(dashboardId);
  }
  
  private connect(dashboardId: string) {
    this.ws = new WebSocket(`ws://api:8000/ws/dashboard/${dashboardId}`);
    
    this.ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      this.updateCharts(update);
    };
    
    this.ws.onclose = () => {
      this.handleReconnection();
    };
  }
  
  private updateCharts(data: RealtimeUpdate) {
    // 更新图表数据
    data.metrics.forEach(metric => {
      const chart = this.charts.get(metric.chartId);
      chart?.updateData(metric.data);
    });
  }
}
```

### 10.3 报表生成引擎

#### 模板引擎架构
```python
# 报表模板管理
class ReportTemplateEngine:
    def __init__(self):
        self.template_store = TemplateStore()
        self.data_processor = DataProcessor()
        self.renderer = ReportRenderer()
    
    async def generate_report(self, template_id: str, parameters: dict, format: str):
        # 1. 获取报表模板
        template = await self.template_store.get_template(template_id)
        
        # 2. 执行数据查询
        data = await self.data_processor.execute_queries(
            template.queries, 
            parameters
        )
        
        # 3. 渲染报表
        report = await self.renderer.render(
            template=template,
            data=data,
            format=format
        )
        
        return report

# 支持的报表格式
class ReportFormats:
    PDF = "pdf"
    EXCEL = "xlsx"
    CSV = "csv"
    HTML = "html"
    JSON = "json"
```

## 11. 扩展性和弹性设计

### 11.1 微服务治理

#### 服务注册和发现
```yaml
# Consul服务发现配置
service_discovery:
  consul:
    address: "consul:8500"
    datacenter: "dc1"
    
  services:
    - name: "auth-service"
      port: 8001
      health_check: "/health"
      tags: ["auth", "security"]
      
    - name: "data-source-service"
      port: 8002
      health_check: "/health"
      tags: ["data", "ingestion"]
      
    - name: "analytics-service"
      port: 8003
      health_check: "/health"
      tags: ["analytics", "processing"]
```

#### API网关配置
```yaml
# Kong API网关配置
api_gateway:
  kong:
    admin_api: "http://kong:8001"
    proxy_port: 8000
    
  routes:
    - name: "auth-routes"
      paths: ["/api/auth/*"]
      service: "auth-service"
      plugins:
        - name: "jwt"
        - name: "rate-limiting"
          config:
            minute: 100
            hour: 1000
            
    - name: "data-routes"
      paths: ["/api/v1/data/*"]
      service: "data-source-service"
      plugins:
        - name: "jwt"
        - name: "request-size-limiting"
          config:
            allowed_payload_size: 10
```

### 11.2 数据分片和分布式存储

#### 租户数据分片策略
```sql
-- 基于租户ID的数据分片
CREATE TABLE user_data (
    id BIGSERIAL,
    tenant_id UUID NOT NULL,
    user_id UUID NOT NULL,
    data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (tenant_id, id)
) PARTITION BY HASH (tenant_id);

-- 创建分片表
CREATE TABLE user_data_0 PARTITION OF user_data
    FOR VALUES WITH (modulus 4, remainder 0);
    
CREATE TABLE user_data_1 PARTITION OF user_data
    FOR VALUES WITH (modulus 4, remainder 1);
    
CREATE TABLE user_data_2 PARTITION OF user_data
    FOR VALUES WITH (modulus 4, remainder 2);
    
CREATE TABLE user_data_3 PARTITION OF user_data
    FOR VALUES WITH (modulus 4, remainder 3);

-- 时间序列数据分片
CREATE TABLE analytics_events (
    id BIGSERIAL,
    tenant_id UUID NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    
    PRIMARY KEY (tenant_id, timestamp, id)
) PARTITION BY RANGE (timestamp);

-- 按月分片
CREATE TABLE analytics_events_2024_01 PARTITION OF analytics_events
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### 11.3 缓存策略优化

#### 多层缓存实现
```python
class MultiLevelCache:
    def __init__(self):
        self.l1_cache = {}  # 进程内缓存
        self.l2_cache = RedisClient()  # Redis分布式缓存
        self.l3_cache = MemcachedClient()  # Memcached集群缓存
    
    async def get(self, key: str, ttl: int = 3600):
        # L1: 进程内缓存
        if key in self.l1_cache:
            return self.l1_cache[key]
        
        # L2: Redis缓存
        value = await self.l2_cache.get(key)
        if value:
            self.l1_cache[key] = value
            return value
        
        # L3: Memcached缓存
        value = await self.l3_cache.get(key)
        if value:
            await self.l2_cache.set(key, value, ttl)
            self.l1_cache[key] = value
            return value
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        # 同时更新所有缓存层
        self.l1_cache[key] = value
        await self.l2_cache.set(key, value, ttl)
        await self.l3_cache.set(key, value, ttl)

# 智能缓存失效
class CacheInvalidationManager:
    def __init__(self):
        self.cache = MultiLevelCache()
        self.dependency_graph = {}
    
    async def invalidate_by_tags(self, tags: List[str]):
        # 基于标签的缓存失效
        keys_to_invalidate = []
        for tag in tags:
            keys_to_invalidate.extend(self.get_keys_by_tag(tag))
        
        for key in keys_to_invalidate:
            await self.cache.delete(key)
```

## 12. 企业级集成和扩展

### 12.1 第三方集成架构

#### 集成适配器模式
```python
from abc import ABC, abstractmethod

class DataSourceAdapter(ABC):
    @abstractmethod
    async def connect(self, config: dict) -> bool:
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        pass
    
    @abstractmethod
    async def fetch_data(self, query: dict) -> List[dict]:
        pass
    
    @abstractmethod
    async def get_schema(self) -> dict:
        pass

# Salesforce集成适配器
class SalesforceAdapter(DataSourceAdapter):
    def __init__(self):
        self.client = None
    
    async def connect(self, config: dict) -> bool:
        try:
            self.client = SalesforceClient(
                username=config['username'],
                password=config['password'],
                security_token=config['security_token']
            )
            await self.client.login()
            return True
        except Exception as e:
            logger.error(f"Salesforce connection failed: {e}")
            return False
    
    async def fetch_data(self, query: dict) -> List[dict]:
        soql_query = self.build_soql_query(query)
        result = await self.client.query(soql_query)
        return result.records

# Google Analytics集成适配器
class GoogleAnalyticsAdapter(DataSourceAdapter):
    def __init__(self):
        self.client = None
    
    async def connect(self, config: dict) -> bool:
        try:
            credentials = GoogleCredentials.from_service_account_info(
                config['service_account_key']
            )
            self.client = AnalyticsClient(credentials)
            return True
        except Exception as e:
            logger.error(f"Google Analytics connection failed: {e}")
            return False
```

#### Webhook处理引擎
```python
class WebhookProcessor:
    def __init__(self):
        self.handlers = {}
        self.queue = AsyncQueue()
        self.workers = []
    
    def register_handler(self, event_type: str, handler: Callable):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    async def process_webhook(self, payload: dict, headers: dict):
        # 验证签名
        if not self.verify_signature(payload, headers):
            raise SecurityError("Invalid webhook signature")
        
        # 解析事件类型
        event_type = self.extract_event_type(payload)
        
        # 添加到处理队列
        await self.queue.put({
            'event_type': event_type,
            'payload': payload,
            'timestamp': datetime.utcnow(),
            'retry_count': 0
        })
    
    async def worker(self):
        while True:
            try:
                event = await self.queue.get()
                await self.handle_event(event)
            except Exception as e:
                logger.error(f"Webhook processing failed: {e}")
                await self.handle_retry(event)
```

### 12.2 API限流和配额管理

#### 分布式限流器
```python
class DistributedRateLimiter:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.lua_script = """
        local key = KEYS[1]
        local window = tonumber(ARGV[1])
        local limit = tonumber(ARGV[2])
        local current_time = tonumber(ARGV[3])
        
        local window_start = current_time - window
        
        -- 清理过期的请求记录
        redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)
        
        -- 获取当前窗口内的请求数
        local current_count = redis.call('ZCARD', key)
        
        if current_count < limit then
            -- 记录当前请求
            redis.call('ZADD', key, current_time, current_time)
            redis.call('EXPIRE', key, window)
            return {1, limit - current_count - 1}
        else
            return {0, 0}
        end
        """
    
    async def is_allowed(self, 
                        key: str, 
                        limit: int, 
                        window: int) -> Tuple[bool, int]:
        current_time = time.time()
        result = await self.redis.eval(
            self.lua_script, 
            1, 
            key, 
            window, 
            limit, 
            current_time
        )
        
        return bool(result[0]), result[1]

# 租户配额管理
class TenantQuotaManager:
    def __init__(self, db: Database):
        self.db = db
        self.rate_limiter = DistributedRateLimiter()
    
    async def check_quota(self, tenant_id: str, resource_type: str, amount: int = 1):
        quota = await self.get_tenant_quota(tenant_id, resource_type)
        usage = await self.get_current_usage(tenant_id, resource_type)
        
        if usage + amount > quota.limit:
            raise QuotaExceededException(
                f"Quota exceeded for {resource_type}: {usage}/{quota.limit}"
            )
        
        # 更新使用量
        await self.update_usage(tenant_id, resource_type, amount)
```

这个扩展的系统架构设计为您的SaaS数据分析平台提供了完整的企业级功能支持，包括：

1. **现有技术栈的充分利用**：基于当前Flask+FastAPI+Next.js的架构
2. **数据分析平台特定功能**：实时数据处理、报表生成、可视化引擎
3. **企业级扩展性**：微服务治理、数据分片、多级缓存
4. **第三方集成能力**：适配器模式、Webhook处理、API限流
5. **运维和监控**：容器化部署、健康检查、结构化日志

架构采用渐进式升级策略，在保持现有系统稳定运行的基础上，逐步引入新的企业级功能，确保系统能够支持大规模用户和高并发场景。