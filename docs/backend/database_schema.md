# SaaS数据分析平台数据库架构设计

## 1. 数据库设计概览

### 1.1 数据库分层架构

```
┌─────────────────────────────────────────────────────┐
│                    数据存储层                          │
├─────────────────────────────────────────────────────┤
│  PostgreSQL     │  ClickHouse    │  MongoDB  │ Redis │
│  (主数据库)      │  (分析数据库)    │ (文档库)   │(缓存)  │
├─────────────────────────────────────────────────────┤
│  • 用户管理      │  • 事件追踪     │ • 配置管理 │• 会话 │
│  • 租户管理      │  • 行为分析     │ • 集成数据 │• 缓存 │
│  • 权限控制      │  • 业务指标     │ • 非结构化 │• 限流 │
│  • 事务数据      │  • 时序数据     │   数据    │• 队列 │
└─────────────────────────────────────────────────────┘
```

### 1.2 数据库选型策略

#### PostgreSQL - 主数据库
- **用途**: 用户管理、租户管理、权限控制、事务数据
- **优势**: ACID特性、JSON支持、扩展性、成熟生态
- **版本**: PostgreSQL 15+

#### ClickHouse - 分析数据库
- **用途**: 大数据分析、时序数据、行为追踪、业务指标
- **优势**: 列式存储、高压缩比、实时查询、SQL支持
- **版本**: ClickHouse 23+

#### MongoDB - 文档数据库
- **用途**: 配置管理、集成数据、非结构化数据存储
- **优势**: 灵活模式、水平扩展、地理空间查询
- **版本**: MongoDB 6+

#### Redis - 缓存和会话存储
- **用途**: 会话管理、查询缓存、限流控制、消息队列
- **优势**: 高性能、多数据结构、持久化、集群支持
- **版本**: Redis 7+

## 2. PostgreSQL 主数据库设计

### 2.1 核心业务表结构

#### 2.1.1 用户和认证管理

```sql
-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url VARCHAR(500),
    phone VARCHAR(20),
    timezone VARCHAR(50) DEFAULT 'UTC',
    locale VARCHAR(10) DEFAULT 'en',
    status user_status DEFAULT 'active',
    email_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMP WITH TIME ZONE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    last_login_ip INET,
    password_changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 用户状态枚举
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended', 'pending');

-- 刷新令牌表
CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked_at TIMESTAMP WITH TIME ZONE,
    user_agent TEXT,
    ip_address INET,
    device_fingerprint VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 用户会话表
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    device_name VARCHAR(255),
    device_type VARCHAR(50),
    os_name VARCHAR(100),
    browser_name VARCHAR(100),
    ip_address INET,
    location JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 密码重置表
CREATE TABLE password_resets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 2.1.2 多租户管理

```sql
-- 租户表
CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    domain VARCHAR(255),
    description TEXT,
    logo_url VARCHAR(500),
    settings JSONB DEFAULT '{}',
    plan_type tenant_plan DEFAULT 'free',
    status tenant_status DEFAULT 'active',
    trial_ends_at TIMESTAMP WITH TIME ZONE,
    subscription_ends_at TIMESTAMP WITH TIME ZONE,
    max_users INTEGER DEFAULT 5,
    max_data_sources INTEGER DEFAULT 3,
    max_storage_gb INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 租户计划枚举
CREATE TYPE tenant_plan AS ENUM ('free', 'starter', 'professional', 'enterprise');

-- 租户状态枚举
CREATE TYPE tenant_status AS ENUM ('active', 'suspended', 'trial', 'expired');

-- 租户用户关联表
CREATE TABLE tenant_users (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role tenant_role DEFAULT 'member',
    permissions JSONB DEFAULT '[]',
    invited_by INTEGER REFERENCES users(id),
    invited_at TIMESTAMP WITH TIME ZONE,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status invitation_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, user_id)
);

-- 租户角色枚举
CREATE TYPE tenant_role AS ENUM ('owner', 'admin', 'editor', 'analyst', 'viewer');

-- 邀请状态枚举
CREATE TYPE invitation_status AS ENUM ('pending', 'active', 'suspended');

-- 租户邀请表
CREATE TABLE tenant_invitations (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    role tenant_role DEFAULT 'member',
    invited_by INTEGER NOT NULL REFERENCES users(id),
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    accepted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, email)
);
```

#### 2.1.3 权限和角色管理

```sql
-- 权限表
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    category permission_category,
    resource VARCHAR(100),
    action VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 权限分类枚举
CREATE TYPE permission_category AS ENUM ('user', 'tenant', 'data', 'report', 'integration', 'system');

-- 角色表
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    is_system_role BOOLEAN DEFAULT FALSE,
    is_default BOOLEAN DEFAULT FALSE,
    permissions JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, name)
);

-- 角色权限关联表
CREATE TABLE role_permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(role_id, permission_id)
);

-- 用户角色关联表
CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    assigned_by INTEGER REFERENCES users(id),
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, role_id, tenant_id)
);
```

#### 2.1.4 数据源管理

```sql
-- 数据源表
CREATE TABLE data_sources (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type data_source_type NOT NULL,
    connection_config JSONB NOT NULL DEFAULT '{}',
    credentials_encrypted TEXT,
    schema_info JSONB DEFAULT '{}',
    sync_config JSONB DEFAULT '{}',
    status connection_status DEFAULT 'disconnected',
    last_sync_at TIMESTAMP WITH TIME ZONE,
    next_sync_at TIMESTAMP WITH TIME ZONE,
    sync_frequency INTEGER DEFAULT 3600, -- seconds
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 数据源类型枚举
CREATE TYPE data_source_type AS ENUM (
    'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
    'api_rest', 'api_graphql', 'webhook', 'file_csv', 'file_excel',
    'google_analytics', 'salesforce', 'hubspot', 'stripe', 'shopify'
);

-- 连接状态枚举
CREATE TYPE connection_status AS ENUM ('connected', 'disconnected', 'error', 'syncing');

-- 数据同步记录表
CREATE TABLE sync_records (
    id SERIAL PRIMARY KEY,
    data_source_id INTEGER NOT NULL REFERENCES data_sources(id) ON DELETE CASCADE,
    sync_type sync_type DEFAULT 'incremental',
    status sync_status DEFAULT 'running',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    records_processed INTEGER DEFAULT 0,
    records_success INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    error_message TEXT,
    logs JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}'
);

-- 同步类型枚举
CREATE TYPE sync_type AS ENUM ('full', 'incremental', 'manual');

-- 同步状态枚举
CREATE TYPE sync_status AS ENUM ('running', 'completed', 'failed', 'cancelled');
```

#### 2.1.5 报表和仪表板管理

```sql
-- 仪表板表
CREATE TABLE dashboards (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    layout JSONB DEFAULT '{}',
    settings JSONB DEFAULT '{}',
    is_public BOOLEAN DEFAULT FALSE,
    is_template BOOLEAN DEFAULT FALSE,
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 报表表
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    dashboard_id INTEGER REFERENCES dashboards(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type report_type NOT NULL,
    config JSONB NOT NULL DEFAULT '{}',
    query_config JSONB DEFAULT '{}',
    visualization_config JSONB DEFAULT '{}',
    refresh_frequency INTEGER DEFAULT 3600, -- seconds
    last_refresh_at TIMESTAMP WITH TIME ZONE,
    is_public BOOLEAN DEFAULT FALSE,
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 报表类型枚举
CREATE TYPE report_type AS ENUM (
    'chart_line', 'chart_bar', 'chart_pie', 'chart_area',
    'table', 'metric', 'gauge', 'map', 'funnel', 'cohort'
);

-- 报表分享表
CREATE TABLE report_shares (
    id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    shared_by INTEGER NOT NULL REFERENCES users(id),
    shared_with INTEGER REFERENCES users(id),
    share_token VARCHAR(255) UNIQUE,
    permissions JSONB DEFAULT '["view"]',
    expires_at TIMESTAMP WITH TIME ZONE,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2.2 系统管理表结构

#### 2.2.1 审计和日志

```sql
-- 审计日志表
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id) ON DELETE SET NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(100),
    action VARCHAR(100) NOT NULL,
    description TEXT,
    ip_address INET,
    user_agent TEXT,
    request_id VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 系统配置表
CREATE TABLE system_configs (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value JSONB,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    updated_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 通知表
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type notification_type NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    read_at TIMESTAMP WITH TIME ZONE,
    action_url VARCHAR(500),
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 通知类型枚举
CREATE TYPE notification_type AS ENUM (
    'info', 'success', 'warning', 'error', 
    'data_sync', 'report_ready', 'invitation', 'security_alert'
);
```

### 2.3 索引优化策略

#### 2.3.1 主要索引设计

```sql
-- 用户表索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status) WHERE status != 'deleted';
CREATE INDEX idx_users_tenant_lookup ON users(id, email) WHERE status = 'active';

-- 租户用户关联索引
CREATE INDEX idx_tenant_users_lookup ON tenant_users(tenant_id, user_id, status);
CREATE INDEX idx_tenant_users_user ON tenant_users(user_id);

-- 数据源索引
CREATE INDEX idx_data_sources_tenant ON data_sources(tenant_id, status);
CREATE INDEX idx_data_sources_sync ON data_sources(next_sync_at) WHERE status = 'connected';

-- 报表索引
CREATE INDEX idx_reports_tenant ON reports(tenant_id, created_at DESC);
CREATE INDEX idx_reports_dashboard ON reports(dashboard_id) WHERE dashboard_id IS NOT NULL;

-- 审计日志索引
CREATE INDEX idx_audit_logs_tenant_time ON audit_logs(tenant_id, created_at DESC);
CREATE INDEX idx_audit_logs_user_time ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_logs_event ON audit_logs(event_type, created_at DESC);

-- 通知索引
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, read_at) WHERE read_at IS NULL;
CREATE INDEX idx_notifications_tenant_time ON notifications(tenant_id, created_at DESC);

-- 会话索引
CREATE INDEX idx_user_sessions_active ON user_sessions(user_id, is_active, last_activity_at);
CREATE INDEX idx_user_sessions_cleanup ON user_sessions(expires_at) WHERE is_active = false;

-- 刷新令牌索引
CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id, revoked_at);
CREATE INDEX idx_refresh_tokens_cleanup ON refresh_tokens(expires_at) WHERE revoked_at IS NULL;
```

#### 2.3.2 部分索引优化

```sql
-- 只索引活跃用户
CREATE INDEX idx_users_active ON users(created_at DESC) WHERE status = 'active';

-- 只索引未读通知
CREATE INDEX idx_notifications_unread ON notifications(user_id, created_at DESC) WHERE read_at IS NULL;

-- 只索引连接的数据源
CREATE INDEX idx_data_sources_connected ON data_sources(tenant_id) WHERE status = 'connected';

-- 只索引公开报表
CREATE INDEX idx_reports_public ON reports(created_at DESC) WHERE is_public = true;
```

### 2.4 数据约束和触发器

#### 2.4.1 数据约束

```sql
-- 邮箱格式约束
ALTER TABLE users ADD CONSTRAINT check_email_format 
    CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- 租户slug格式约束
ALTER TABLE tenants ADD CONSTRAINT check_slug_format 
    CHECK (slug ~* '^[a-z0-9][a-z0-9-]*[a-z0-9]$' AND length(slug) >= 3);

-- 密码强度约束(在应用层处理，数据库只存储hash)
ALTER TABLE users ADD CONSTRAINT check_password_hash_length 
    CHECK (length(password_hash) >= 60);

-- 用户限制约束
ALTER TABLE tenants ADD CONSTRAINT check_positive_limits 
    CHECK (max_users > 0 AND max_data_sources > 0 AND max_storage_gb > 0);
```

#### 2.4.2 自动更新触发器

```sql
-- 自动更新updated_at字段的触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 应用触发器到需要的表
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tenants_updated_at 
    BEFORE UPDATE ON tenants 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tenant_users_updated_at 
    BEFORE UPDATE ON tenant_users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_data_sources_updated_at 
    BEFORE UPDATE ON data_sources 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dashboards_updated_at 
    BEFORE UPDATE ON dashboards 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reports_updated_at 
    BEFORE UPDATE ON reports 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## 3. ClickHouse 分析数据库设计

### 3.1 事件追踪表设计

```sql
-- 用户行为事件表
CREATE TABLE user_events (
    event_time DateTime64(3),
    event_date Date DEFAULT toDate(event_time),
    tenant_id UInt32,
    user_id UInt32,
    session_id String,
    event_type String,
    event_name String,
    page_url String,
    referrer_url String,
    user_agent String,
    ip_address String,
    country_code FixedString(2),
    city String,
    device_type String,
    browser_name String,
    os_name String,
    properties Map(String, String),
    created_at DateTime64(3) DEFAULT now64(3)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (tenant_id, user_id, event_time)
TTL event_date + INTERVAL 2 YEAR;

-- 数据源使用统计表
CREATE TABLE data_source_usage (
    usage_time DateTime64(3),
    usage_date Date DEFAULT toDate(usage_time),
    tenant_id UInt32,
    data_source_id UInt32,
    user_id UInt32,
    operation_type String, -- 'query', 'sync', 'connect'
    query_duration_ms UInt32,
    records_processed UInt64,
    bytes_processed UInt64,
    status String, -- 'success', 'error'
    error_code String,
    created_at DateTime64(3) DEFAULT now64(3)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(usage_date)
ORDER BY (tenant_id, data_source_id, usage_time)
TTL usage_date + INTERVAL 1 YEAR;

-- 报表访问统计表
CREATE TABLE report_views (
    view_time DateTime64(3),
    view_date Date DEFAULT toDate(view_time),
    tenant_id UInt32,
    report_id UInt32,
    dashboard_id UInt32,
    user_id UInt32,
    session_id String,
    view_duration_ms UInt32,
    is_shared_access UInt8, -- 0: direct, 1: shared link
    share_token String,
    ip_address String,
    user_agent String,
    created_at DateTime64(3) DEFAULT now64(3)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(view_date)
ORDER BY (tenant_id, report_id, view_time)
TTL view_date + INTERVAL 1 YEAR;

-- API调用统计表
CREATE TABLE api_calls (
    call_time DateTime64(3),
    call_date Date DEFAULT toDate(call_time),
    tenant_id UInt32,
    user_id UInt32,
    endpoint String,
    method String,
    status_code UInt16,
    response_time_ms UInt32,
    request_size_bytes UInt64,
    response_size_bytes UInt64,
    ip_address String,
    user_agent String,
    api_key_id UInt32,
    rate_limit_remaining UInt32,
    created_at DateTime64(3) DEFAULT now64(3)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(call_date)
ORDER BY (tenant_id, endpoint, call_time)
TTL call_date + INTERVAL 6 MONTH;
```

### 3.2 业务指标聚合表

```sql
-- 每日租户使用统计
CREATE TABLE daily_tenant_stats (
    stats_date Date,
    tenant_id UInt32,
    active_users UInt32,
    total_queries UInt32,
    data_processed_gb Float64,
    reports_created UInt32,
    reports_viewed UInt32,
    api_calls UInt32,
    storage_used_gb Float64,
    created_at DateTime64(3) DEFAULT now64(3)
) ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(stats_date)
ORDER BY (tenant_id, stats_date);

-- 每小时系统性能指标
CREATE TABLE hourly_performance_stats (
    stats_hour DateTime,
    stats_date Date DEFAULT toDate(stats_hour),
    total_requests UInt64,
    successful_requests UInt64,
    failed_requests UInt64,
    avg_response_time_ms Float64,
    max_response_time_ms UInt32,
    active_connections UInt32,
    cpu_usage Float64,
    memory_usage Float64,
    disk_usage Float64,
    created_at DateTime64(3) DEFAULT now64(3)
) ENGINE = ReplacingMergeTree()
PARTITION BY toYYYYMM(stats_date)
ORDER BY (stats_hour);

-- 实时在线用户统计
CREATE TABLE realtime_user_activity (
    activity_time DateTime64(3),
    tenant_id UInt32,
    user_id UInt32,
    session_id String,
    page_path String,
    activity_type String, -- 'page_view', 'action', 'idle'
    metadata Map(String, String),
    created_at DateTime64(3) DEFAULT now64(3)
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(toDate(activity_time))
ORDER BY (tenant_id, user_id, activity_time)
TTL toDate(activity_time) + INTERVAL 7 DAY;
```

### 3.3 ClickHouse 优化配置

#### 3.3.1 表引擎选择

```sql
-- 事件日志表 - 大量插入，按时间查询
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (tenant_id, user_id, event_time)
TTL event_date + INTERVAL 2 YEAR

-- 聚合统计表 - 需要去重和聚合
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(stats_date)
ORDER BY (tenant_id, stats_date)

-- 配置表 - 需要替换更新
ENGINE = ReplacingMergeTree()
PARTITION BY toYYYYMM(updated_date)
ORDER BY (id, updated_at)
```

#### 3.3.2 物化视图设计

```sql
-- 实时活跃用户统计物化视图
CREATE MATERIALIZED VIEW mv_active_users_realtime
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(event_date)
ORDER BY (tenant_id, event_hour)
AS SELECT
    tenant_id,
    toStartOfHour(event_time) as event_hour,
    toDate(event_time) as event_date,
    uniqState(user_id) as active_users,
    countState() as total_events
FROM user_events
WHERE event_time >= now() - INTERVAL 1 DAY
GROUP BY tenant_id, event_hour, event_date;

-- 数据源使用趋势物化视图
CREATE MATERIALIZED VIEW mv_data_source_trends
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(usage_date)
ORDER BY (tenant_id, data_source_id, usage_hour)
AS SELECT
    tenant_id,
    data_source_id,
    toStartOfHour(usage_time) as usage_hour,
    usage_date,
    count() as usage_count,
    sum(query_duration_ms) as total_duration_ms,
    sum(records_processed) as total_records,
    sum(bytes_processed) as total_bytes
FROM data_source_usage
GROUP BY tenant_id, data_source_id, usage_hour, usage_date;
```

## 4. MongoDB 文档数据库设计

### 4.1 集合设计

#### 4.1.1 系统配置集合

```javascript
// tenant_configurations 集合
{
  "_id": ObjectId(),
  "tenant_id": 123,
  "config_type": "dashboard_theme",
  "config_data": {
    "primary_color": "#FF6B35",
    "secondary_color": "#F7931E",
    "background_color": "#FFFFFF",
    "font_family": "Inter, sans-serif",
    "custom_css": "...",
    "layout_settings": {
      "sidebar_position": "left",
      "header_height": 64,
      "footer_visible": true
    }
  },
  "version": 1,
  "is_active": true,
  "created_by": 456,
  "created_at": ISODate(),
  "updated_at": ISODate()
}

// integration_configs 集合
{
  "_id": ObjectId(),
  "tenant_id": 123,
  "integration_type": "salesforce",
  "config": {
    "api_version": "v52.0",
    "instance_url": "https://mycompany.salesforce.com",
    "client_id": "...",
    "client_secret_encrypted": "...",
    "refresh_token_encrypted": "...",
    "sandbox": false,
    "objects_to_sync": ["Account", "Contact", "Opportunity"],
    "sync_schedule": "0 */6 * * *", // Every 6 hours
    "field_mappings": {
      "Account": {
        "Name": "account_name",
        "Industry": "industry",
        "AnnualRevenue": "annual_revenue"
      }
    }
  },
  "status": "active",
  "last_sync": ISODate(),
  "sync_logs": [],
  "created_at": ISODate(),
  "updated_at": ISODate()
}
```

#### 4.1.2 数据模式和映射

```javascript
// data_schemas 集合
{
  "_id": ObjectId(),
  "data_source_id": 789,
  "tenant_id": 123,
  "schema_name": "sales_data",
  "schema_version": "1.2",
  "fields": [
    {
      "name": "customer_id",
      "type": "integer",
      "nullable": false,
      "primary_key": true,
      "description": "Unique customer identifier"
    },
    {
      "name": "order_date",
      "type": "datetime",
      "nullable": false,
      "format": "YYYY-MM-DD HH:mm:ss",
      "timezone": "UTC"
    },
    {
      "name": "amount",
      "type": "decimal",
      "precision": 10,
      "scale": 2,
      "nullable": false,
      "currency": "USD"
    }
  ],
  "relationships": [
    {
      "type": "belongs_to",
      "foreign_table": "customers",
      "foreign_key": "customer_id",
      "local_key": "customer_id"
    }
  ],
  "indexes": [
    {"fields": ["customer_id"], "type": "btree"},
    {"fields": ["order_date"], "type": "btree"}
  ],
  "statistics": {
    "row_count": 1500000,
    "last_analyzed": ISODate(),
    "size_bytes": 245760000
  },
  "created_at": ISODate(),
  "updated_at": ISODate()
}

// query_templates 集合
{
  "_id": ObjectId(),
  "tenant_id": 123,
  "template_name": "Monthly Sales Report",
  "category": "sales",
  "description": "Monthly sales performance by region",
  "sql_template": `
    SELECT 
      DATE_TRUNC('month', order_date) as month,
      region,
      COUNT(*) as order_count,
      SUM(amount) as total_revenue,
      AVG(amount) as avg_order_value
    FROM sales_data 
    WHERE order_date >= $start_date 
      AND order_date <= $end_date
      AND tenant_id = $tenant_id
    GROUP BY month, region
    ORDER BY month DESC, total_revenue DESC
  `,
  "parameters": [
    {
      "name": "start_date",
      "type": "date",
      "required": true,
      "default": "CURRENT_DATE - INTERVAL '30 days'"
    },
    {
      "name": "end_date",
      "type": "date",
      "required": true,
      "default": "CURRENT_DATE"
    },
    {
      "name": "tenant_id",
      "type": "integer",
      "required": true,
      "hidden": true
    }
  ],
  "tags": ["sales", "monthly", "region"],
  "usage_count": 245,
  "is_public": false,
  "created_by": 456,
  "created_at": ISODate(),
  "updated_at": ISODate()
}
```

### 4.2 索引策略

```javascript
// 为集合创建索引
db.tenant_configurations.createIndex(
  { "tenant_id": 1, "config_type": 1 }, 
  { unique: true }
);

db.integration_configs.createIndex(
  { "tenant_id": 1, "integration_type": 1 }
);

db.data_schemas.createIndex(
  { "data_source_id": 1 },
  { unique: true }
);

db.data_schemas.createIndex(
  { "tenant_id": 1, "schema_name": 1 }
);

db.query_templates.createIndex(
  { "tenant_id": 1, "category": 1, "tags": 1 }
);

// 全文搜索索引
db.query_templates.createIndex(
  { 
    "template_name": "text", 
    "description": "text", 
    "tags": "text" 
  },
  { 
    weights: { 
      "template_name": 10, 
      "description": 5, 
      "tags": 2 
    } 
  }
);
```

## 5. Redis 缓存架构设计

### 5.1 缓存键命名规范

```
# 用户会话缓存
session:{session_id} -> {user_data}
user_sessions:{user_id} -> Set{session_id1, session_id2, ...}

# API限流
rate_limit:api:{user_id}:{endpoint} -> {count}
rate_limit:tenant:{tenant_id} -> {usage_stats}

# 查询缓存
query_cache:{tenant_id}:{query_hash} -> {result_data}
schema_cache:{data_source_id} -> {schema_info}

# 实时统计
stats:realtime:{tenant_id}:active_users -> {count}
stats:daily:{tenant_id}:{date} -> {daily_stats}

# 通知队列
notifications:{user_id} -> List[{notification_data}]
email_queue -> List[{email_job}]

# 锁和信号量
lock:data_sync:{data_source_id} -> {lock_info}
semaphore:concurrent_queries:{tenant_id} -> {count}
```

### 5.2 缓存策略配置

```python
# Python Redis配置示例
REDIS_CACHE_CONFIG = {
    # 用户会话缓存 - 较短TTL
    'session': {
        'ttl': 3600,  # 1小时
        'max_connections': 20
    },
    
    # 查询缓存 - 中等TTL
    'query_cache': {
        'ttl': 1800,  # 30分钟
        'max_memory': '256mb',
        'eviction_policy': 'allkeys-lru'
    },
    
    # 配置缓存 - 长TTL
    'config_cache': {
        'ttl': 86400,  # 24小时
        'max_memory': '64mb'
    },
    
    # 实时统计 - 短TTL，高频更新
    'realtime_stats': {
        'ttl': 300,  # 5分钟
        'max_memory': '128mb'
    }
}
```

## 6. 数据迁移策略

### 6.1 现有数据迁移

#### 6.1.1 从Flask迁移到新架构

```sql
-- 迁移现有用户数据
INSERT INTO users (
    email, password_hash, created_at, updated_at
)
SELECT 
    email, 
    password_hash, 
    created_at, 
    updated_at
FROM old_users_table
WHERE email IS NOT NULL;

-- 迁移刷新令牌数据
INSERT INTO refresh_tokens (
    user_id, token_hash, expires_at, user_agent, ip_address, created_at
)
SELECT 
    u.id as user_id,
    rt.token_hash,
    rt.expires_at,
    rt.user_agent,
    rt.ip,
    rt.created_at
FROM old_refresh_tokens rt
JOIN users u ON u.email = rt.user_email;
```

#### 6.1.2 创建默认租户

```sql
-- 为现有用户创建默认租户
WITH tenant_creation AS (
    INSERT INTO tenants (name, slug, status, created_at)
    VALUES ('Default Tenant', 'default', 'active', NOW())
    RETURNING id as tenant_id
)
INSERT INTO tenant_users (tenant_id, user_id, role, status)
SELECT 
    tc.tenant_id,
    u.id as user_id,
    'owner'::tenant_role,
    'active'::invitation_status
FROM users u
CROSS JOIN tenant_creation tc
WHERE u.created_at < NOW();
```

### 6.2 数据同步和一致性

#### 6.2.1 双写策略

```python
# 在迁移期间实现双写
class DualWriteUserService:
    def create_user(self, user_data):
        # 写入新数据库
        new_user = self.new_db.create_user(user_data)
        
        try:
            # 写入旧数据库
            old_user = self.old_db.create_user(user_data)
        except Exception as e:
            # 补偿事务
            self.new_db.delete_user(new_user.id)
            raise e
        
        return new_user
```

#### 6.2.2 数据一致性检查

```sql
-- 检查数据一致性的脚本
WITH consistency_check AS (
    SELECT 
        'users' as table_name,
        COUNT(*) as new_count,
        (SELECT COUNT(*) FROM old_users) as old_count,
        COUNT(*) - (SELECT COUNT(*) FROM old_users) as difference
    FROM users
    WHERE deleted_at IS NULL
)
SELECT * FROM consistency_check
WHERE difference != 0;
```

## 7. 性能优化和监控

### 7.1 数据库性能监控

```sql
-- PostgreSQL性能监控查询
-- 慢查询监控
SELECT 
    query,
    calls,
    total_time / 1000.0 as total_time_seconds,
    mean_time / 1000.0 as mean_time_seconds,
    (100.0 * total_time / sum(total_time) OVER()) AS percentage
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 20;

-- 索引使用情况
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch,
    idx_scan
FROM pg_stat_user_indexes 
ORDER BY idx_scan DESC;

-- 表大小监控
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 7.2 ClickHouse性能优化

```sql
-- ClickHouse查询优化
-- 分区修剪检查
SELECT 
    table,
    partition,
    rows,
    bytes_on_disk,
    data_compressed_bytes,
    data_uncompressed_bytes
FROM system.parts 
WHERE table = 'user_events' 
ORDER BY partition DESC;

-- 合并性能监控
SELECT 
    table,
    elapsed,
    progress,
    is_mutation,
    total_size_bytes_compressed
FROM system.merges 
WHERE table LIKE '%events%';
```

### 7.3 缓存命中率监控

```python
# Redis监控脚本
def get_redis_stats():
    info = redis_client.info()
    return {
        'used_memory': info['used_memory'],
        'used_memory_human': info['used_memory_human'],
        'keyspace_hits': info['keyspace_hits'],
        'keyspace_misses': info['keyspace_misses'],
        'hit_rate': info['keyspace_hits'] / (info['keyspace_hits'] + info['keyspace_misses']),
        'connected_clients': info['connected_clients'],
        'total_commands_processed': info['total_commands_processed']
    }
```

这个数据库架构设计为您的SaaS数据分析平台提供了完整的数据存储解决方案，包括多租户支持、高性能分析、灵活配置和可扩展性。通过合理的数据库分层和优化策略，可以支持大规模的数据处理和分析需求。