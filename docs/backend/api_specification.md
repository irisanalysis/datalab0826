# SaaS数据分析平台API规范设计

## 1. API设计概览

### 1.1 API架构原则

- **RESTful设计**: 遵循REST架构风格和HTTP语义
- **版本控制**: 支持多版本并存和向后兼容
- **统一响应**: 标准化的响应格式和错误处理
- **安全优先**: 端到端的身份验证和授权
- **性能优化**: 缓存策略和分页机制
- **可观测性**: 完整的请求追踪和监控

### 1.2 API分层架构

```
┌─────────────────────────────────────────────────────────┐
│                    API Gateway                          │
├─────────────────────────────────────────────────────────┤
│  • Authentication & Authorization                       │
│  • Rate Limiting & Throttling                          │
│  • Request/Response Transformation                     │
│  • Monitoring & Logging                                │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                  Service Layer APIs                     │
├─────────────────────────────────────────────────────────┤
│  Auth API    │  Tenant API   │  Data API   │  Report API│
│  (v1, v2)    │  (v1)         │  (v1, v2)   │  (v1)      │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   Business Logic                        │
├─────────────────────────────────────────────────────────┤
│  • Domain Services                                      │
│  • Data Validation                                      │
│  • Business Rules                                       │
└─────────────────────────────────────────────────────────┘
```

## 2. API版本控制和路由规范

### 2.1 URL结构规范

```
https://api.yourplatform.com/{version}/{service}/{resource}
```

**示例路径结构**:
```
# 认证服务
/api/v1/auth/login
/api/v1/auth/refresh
/api/v2/auth/sso

# 租户管理
/api/v1/tenants
/api/v1/tenants/{tenant_id}/users
/api/v1/tenants/{tenant_id}/settings

# 数据源管理
/api/v1/data-sources
/api/v1/data-sources/{data_source_id}/sync
/api/v2/data-sources/{data_source_id}/schema

# 报表和仪表板
/api/v1/dashboards
/api/v1/dashboards/{dashboard_id}/reports
/api/v1/reports/{report_id}/data
```

### 2.2 HTTP方法规范

| 方法 | 用途 | 幂等性 | 安全性 |
|------|------|--------|--------|
| GET | 获取资源 | ✓ | ✓ |
| POST | 创建资源 | ✗ | ✗ |
| PUT | 完整更新资源 | ✓ | ✗ |
| PATCH | 部分更新资源 | ✗ | ✗ |
| DELETE | 删除资源 | ✓ | ✗ |

### 2.3 版本控制策略

#### URL版本控制
```yaml
# 版本在URL路径中
/api/v1/users
/api/v2/users

# 版本兼容性矩阵
versions:
  v1:
    status: "deprecated"
    sunset_date: "2024-12-31"
    supported_until: "2025-03-31"
  
  v2:
    status: "stable"
    introduced: "2024-01-01"
    breaking_changes:
      - "user.profile moved to user.personal_info"
      - "pagination format changed"
```

#### Header版本控制 (可选)
```http
# 请求头版本控制
API-Version: 2024-01-15
Accept: application/vnd.api.v2+json
```

## 3. 认证和授权API

### 3.1 认证API端点

#### 3.1.1 用户注册

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecureP@ssw0rd",
  "first_name": "John",
  "last_name": "Doe",
  "tenant_name": "Acme Corp",
  "tenant_slug": "acme-corp"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 123,
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "status": "pending",
      "email_verified": false,
      "created_at": "2024-01-15T10:30:00Z"
    },
    "tenant": {
      "id": 456,
      "uuid": "660e8400-e29b-41d4-a716-446655440001",
      "name": "Acme Corp",
      "slug": "acme-corp",
      "status": "trial",
      "plan_type": "free"
    }
  },
  "message": "Registration successful. Please check your email to verify your account.",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_abc123xyz"
}
```

#### 3.1.2 用户登录

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecureP@ssw0rd",
  "remember_me": true,
  "device_info": {
    "name": "Chrome on MacOS",
    "type": "desktop",
    "os": "macOS",
    "browser": "Chrome"
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "rt_550e8400e29b41d4a716446655440000",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": 123,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "avatar_url": "https://cdn.example.com/avatars/123.jpg",
      "tenants": [
        {
          "id": 456,
          "name": "Acme Corp",
          "slug": "acme-corp",
          "role": "owner",
          "permissions": ["*"]
        }
      ],
      "preferences": {
        "timezone": "America/New_York",
        "locale": "en-US",
        "theme": "light"
      }
    }
  },
  "message": "Login successful",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_def456uvw"
}
```

#### 3.1.3 令牌刷新

```http
POST /api/v1/auth/refresh
Authorization: Bearer {refresh_token}
Content-Type: application/json

{}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "rt_660e8400e29b41d4a716446655440001",
    "token_type": "Bearer",
    "expires_in": 3600
  },
  "message": "Token refreshed successfully",
  "timestamp": "2024-01-15T11:30:00Z",
  "request_id": "req_ghi789rst"
}
```

#### 3.1.4 单点登录 (SSO)

```http
POST /api/v2/auth/sso
Content-Type: application/json

{
  "provider": "google",
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjE2NzAyN...",
  "tenant_slug": "acme-corp"
}
```

### 3.2 权限控制API

#### 3.2.1 权限检查中间件

```python
# FastAPI权限检查装饰器
from functools import wraps
from fastapi import Depends, HTTPException, status

def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not has_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# 使用示例
@app.get("/api/v1/users")
@require_permission("read:users")
async def get_users(current_user: User = Depends(get_current_user)):
    return await user_service.get_users(current_user.tenant_id)
```

#### 3.2.2 角色和权限管理

```http
GET /api/v1/tenants/{tenant_id}/roles
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "roles": [
      {
        "id": 1,
        "name": "admin",
        "display_name": "Administrator",
        "description": "Full access to tenant resources",
        "permissions": [
          "users:read", "users:write", "users:delete",
          "data_sources:read", "data_sources:write",
          "reports:read", "reports:write", "reports:share"
        ],
        "user_count": 2,
        "is_system_role": true
      },
      {
        "id": 2,
        "name": "analyst",
        "display_name": "Data Analyst",
        "description": "Can create and view reports",
        "permissions": [
          "data_sources:read",
          "reports:read", "reports:write",
          "dashboards:read", "dashboards:write"
        ],
        "user_count": 5,
        "is_system_role": false
      }
    ]
  }
}
```

## 4. 租户管理API

### 4.1 租户CRUD操作

#### 4.1.1 获取租户信息

```http
GET /api/v1/tenants/{tenant_id}
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "tenant": {
      "id": 456,
      "uuid": "660e8400-e29b-41d4-a716-446655440001",
      "name": "Acme Corp",
      "slug": "acme-corp",
      "domain": "acme-corp.yourplatform.com",
      "description": "Leading provider of enterprise solutions",
      "logo_url": "https://cdn.example.com/logos/456.png",
      "status": "active",
      "plan_type": "professional",
      "trial_ends_at": null,
      "subscription_ends_at": "2024-12-31T23:59:59Z",
      "settings": {
        "timezone": "America/New_York",
        "date_format": "MM/DD/YYYY",
        "currency": "USD",
        "allow_public_sharing": true,
        "data_retention_days": 365,
        "sso_enabled": true,
        "sso_provider": "google"
      },
      "usage_stats": {
        "current_users": 25,
        "max_users": 100,
        "current_data_sources": 8,
        "max_data_sources": 50,
        "storage_used_gb": 15.7,
        "max_storage_gb": 500
      },
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  }
}
```

#### 4.1.2 更新租户设置

```http
PATCH /api/v1/tenants/{tenant_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Acme Corporation",
  "description": "Updated description",
  "settings": {
    "timezone": "America/Los_Angeles",
    "allow_public_sharing": false,
    "data_retention_days": 730
  }
}
```

### 4.2 租户用户管理

#### 4.2.1 获取租户用户列表

```http
GET /api/v1/tenants/{tenant_id}/users?page=1&limit=20&role=analyst&status=active
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 123,
        "email": "john.doe@acme.com",
        "first_name": "John",
        "last_name": "Doe",
        "avatar_url": "https://cdn.example.com/avatars/123.jpg",
        "role": "analyst",
        "permissions": ["data_sources:read", "reports:write"],
        "status": "active",
        "last_login_at": "2024-01-14T15:30:00Z",
        "joined_at": "2024-01-01T00:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 25,
      "pages": 2,
      "has_next": true,
      "has_prev": false
    },
    "filters_applied": {
      "role": "analyst",
      "status": "active"
    }
  }
}
```

#### 4.2.2 邀请用户加入租户

```http
POST /api/v1/tenants/{tenant_id}/invitations
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "email": "newuser@example.com",
  "role": "analyst",
  "message": "Welcome to our analytics team!",
  "expires_in_days": 7
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "invitation": {
      "id": 789,
      "email": "newuser@example.com",
      "role": "analyst",
      "status": "pending",
      "token": "inv_abc123def456",
      "expires_at": "2024-01-22T10:30:00Z",
      "invitation_url": "https://yourplatform.com/accept-invitation?token=inv_abc123def456",
      "invited_by": {
        "id": 123,
        "email": "john.doe@acme.com",
        "name": "John Doe"
      },
      "created_at": "2024-01-15T10:30:00Z"
    }
  },
  "message": "Invitation sent successfully"
}
```

## 5. 数据源管理API

### 5.1 数据源CRUD操作

#### 5.1.1 创建数据源连接

```http
POST /api/v1/data-sources
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Production Database",
  "description": "Main production PostgreSQL database",
  "type": "postgresql",
  "connection_config": {
    "host": "prod-db.example.com",
    "port": 5432,
    "database": "production",
    "ssl_mode": "require"
  },
  "credentials": {
    "username": "analytics_user",
    "password": "secure_password"
  },
  "sync_config": {
    "frequency": 3600,
    "sync_type": "incremental",
    "tables": ["orders", "customers", "products"],
    "incremental_column": "updated_at"
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "data_source": {
      "id": 101,
      "uuid": "770e8400-e29b-41d4-a716-446655440002",
      "name": "Production Database",
      "description": "Main production PostgreSQL database",
      "type": "postgresql",
      "status": "testing_connection",
      "connection_config": {
        "host": "prod-db.example.com",
        "port": 5432,
        "database": "production",
        "ssl_mode": "require"
      },
      "sync_config": {
        "frequency": 3600,
        "sync_type": "incremental",
        "tables": ["orders", "customers", "products"],
        "incremental_column": "updated_at",
        "next_sync_at": "2024-01-15T11:30:00Z"
      },
      "created_by": {
        "id": 123,
        "email": "john.doe@acme.com"
      },
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  },
  "message": "Data source created successfully. Connection test in progress."
}
```

#### 5.1.2 测试数据源连接

```http
POST /api/v1/data-sources/{data_source_id}/test-connection
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "connection_test": {
      "status": "success",
      "response_time_ms": 245,
      "database_version": "PostgreSQL 14.5",
      "accessible_tables": ["orders", "customers", "products", "payments"],
      "estimated_records": {
        "orders": 1500000,
        "customers": 250000,
        "products": 10000
      },
      "tested_at": "2024-01-15T10:35:00Z"
    }
  },
  "message": "Connection test successful"
}
```

#### 5.1.3 获取数据源模式

```http
GET /api/v2/data-sources/{data_source_id}/schema
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "schema": {
      "tables": [
        {
          "name": "orders",
          "type": "table",
          "columns": [
            {
              "name": "id",
              "type": "integer",
              "nullable": false,
              "primary_key": true,
              "description": "Order unique identifier"
            },
            {
              "name": "customer_id",
              "type": "integer",
              "nullable": false,
              "foreign_key": {
                "table": "customers",
                "column": "id"
              }
            },
            {
              "name": "order_date",
              "type": "timestamp",
              "nullable": false,
              "format": "YYYY-MM-DD HH:mm:ss"
            },
            {
              "name": "total_amount",
              "type": "decimal",
              "precision": 10,
              "scale": 2,
              "nullable": false
            }
          ],
          "indexes": [
            {
              "name": "idx_orders_customer_id",
              "columns": ["customer_id"],
              "type": "btree"
            },
            {
              "name": "idx_orders_order_date",
              "columns": ["order_date"],
              "type": "btree"
            }
          ],
          "row_count": 1500000,
          "size_bytes": 245760000,
          "last_analyzed": "2024-01-15T09:00:00Z"
        }
      ],
      "relationships": [
        {
          "type": "one_to_many",
          "from_table": "customers",
          "from_column": "id",
          "to_table": "orders",
          "to_column": "customer_id"
        }
      ]
    }
  }
}
```

### 5.2 数据同步API

#### 5.2.1 手动触发同步

```http
POST /api/v1/data-sources/{data_source_id}/sync
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "sync_type": "full",
  "tables": ["orders", "customers"],
  "priority": "high"
}
```

#### 5.2.2 获取同步状态

```http
GET /api/v1/data-sources/{data_source_id}/sync-status
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "current_sync": {
      "id": 1001,
      "status": "running",
      "sync_type": "incremental",
      "started_at": "2024-01-15T10:00:00Z",
      "progress": {
        "completed_tables": 2,
        "total_tables": 5,
        "current_table": "orders",
        "records_processed": 15000,
        "estimated_total": 50000,
        "percentage": 65
      },
      "estimated_completion": "2024-01-15T10:45:00Z"
    },
    "last_successful_sync": {
      "id": 1000,
      "completed_at": "2024-01-15T06:30:00Z",
      "records_processed": 47500,
      "duration_ms": 180000
    },
    "next_scheduled_sync": "2024-01-15T11:00:00Z"
  }
}
```

## 6. 报表和仪表板API

### 6.1 仪表板管理

#### 6.1.1 创建仪表板

```http
POST /api/v1/dashboards
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Sales Performance Dashboard",
  "description": "Overview of sales metrics and trends",
  "layout": {
    "type": "grid",
    "columns": 12,
    "rows": 8,
    "components": [
      {
        "id": "revenue_chart",
        "type": "chart",
        "position": { "x": 0, "y": 0, "w": 6, "h": 4 },
        "report_id": 201
      },
      {
        "id": "top_products",
        "type": "table",
        "position": { "x": 6, "y": 0, "w": 6, "h": 4 },
        "report_id": 202
      }
    ]
  },
  "settings": {
    "theme": "light",
    "auto_refresh": true,
    "refresh_interval": 300,
    "public_access": false
  }
}
```

#### 6.1.2 获取仪表板数据

```http
GET /api/v1/dashboards/{dashboard_id}
Authorization: Bearer {access_token}
```

### 6.2 报表管理

#### 6.2.1 创建报表

```http
POST /api/v1/reports
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Monthly Revenue Trend",
  "description": "Revenue trends by month for the current year",
  "type": "chart_line",
  "data_source_id": 101,
  "config": {
    "query": {
      "sql": "SELECT DATE_TRUNC('month', order_date) as month, SUM(total_amount) as revenue FROM orders WHERE order_date >= CURRENT_DATE - INTERVAL '12 months' GROUP BY month ORDER BY month",
      "parameters": []
    },
    "visualization": {
      "x_axis": "month",
      "y_axis": "revenue",
      "chart_type": "line",
      "colors": ["#FF6B35"],
      "show_grid": true,
      "show_legend": false
    },
    "refresh_frequency": 3600
  }
}
```

#### 6.2.2 获取报表数据

```http
GET /api/v1/reports/{report_id}/data
Authorization: Bearer {access_token}
Query Parameters:
  - start_date: 2024-01-01
  - end_date: 2024-01-31
  - cache: true
```

**响应**:
```json
{
  "success": true,
  "data": {
    "report_data": {
      "columns": [
        {
          "name": "month",
          "type": "date",
          "display_name": "Month"
        },
        {
          "name": "revenue",
          "type": "decimal",
          "display_name": "Revenue",
          "format": "currency"
        }
      ],
      "rows": [
        {
          "month": "2024-01-01",
          "revenue": 125000.00
        },
        {
          "month": "2024-02-01",
          "revenue": 142000.00
        }
      ],
      "metadata": {
        "row_count": 12,
        "query_duration_ms": 234,
        "cached": true,
        "cache_expires_at": "2024-01-15T11:30:00Z",
        "generated_at": "2024-01-15T10:30:00Z"
      }
    },
    "visualization_config": {
      "chart_type": "line",
      "x_axis": "month",
      "y_axis": "revenue",
      "colors": ["#FF6B35"]
    }
  }
}
```

## 7. 集成和Webhook API

### 7.1 第三方集成管理

#### 7.1.1 创建集成配置

```http
POST /api/v1/integrations
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Salesforce Integration",
  "type": "salesforce",
  "config": {
    "instance_url": "https://mycompany.salesforce.com",
    "api_version": "v52.0",
    "client_id": "3MVG9...",
    "client_secret": "1234567890...",
    "username": "integration@mycompany.com",
    "objects_to_sync": [
      "Account",
      "Contact", 
      "Opportunity"
    ],
    "sync_schedule": "0 */6 * * *",
    "field_mappings": {
      "Account": {
        "Name": "account_name",
        "Industry": "industry",
        "AnnualRevenue": "annual_revenue"
      }
    }
  },
  "settings": {
    "auto_sync": true,
    "notification_on_error": true,
    "data_retention_days": 365
  }
}
```

#### 7.1.2 获取集成状态

```http
GET /api/v1/integrations/{integration_id}/status
Authorization: Bearer {access_token}
```

### 7.2 Webhook管理

#### 7.2.1 创建Webhook

```http
POST /api/v1/webhooks
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Data Sync Notifications",
  "url": "https://myapp.com/webhooks/data-sync",
  "events": [
    "data_source.sync_completed",
    "data_source.sync_failed",
    "report.generated"
  ],
  "secret": "webhook_secret_key",
  "active": true,
  "retry_policy": {
    "max_retries": 3,
    "retry_delay_ms": 5000,
    "exponential_backoff": true
  }
}
```

#### 7.2.2 Webhook事件格式

```json
{
  "id": "evt_abc123def456",
  "type": "data_source.sync_completed",
  "created_at": "2024-01-15T10:30:00Z",
  "data": {
    "data_source_id": 101,
    "sync_id": 1001,
    "tenant_id": 456,
    "status": "completed",
    "records_processed": 50000,
    "duration_ms": 180000,
    "tables_synced": ["orders", "customers", "products"]
  },
  "webhook": {
    "id": 301,
    "attempt": 1,
    "max_attempts": 3
  }
}
```

## 8. 统一响应格式和错误处理

### 8.1 成功响应格式

```json
{
  "success": true,
  "data": {
    // 响应数据
  },
  "message": "Optional success message",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_abc123xyz",
  "meta": {
    // 可选元数据，如分页信息
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "pages": 5
    }
  }
}
```

### 8.2 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "code": "INVALID_FORMAT",
        "message": "Invalid email format"
      },
      {
        "field": "password",
        "code": "TOO_SHORT",
        "message": "Password must be at least 8 characters long"
      }
    ]
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_def456uvw",
  "debug_info": {
    "trace_id": "trace_ghi789rst",
    "span_id": "span_jkl012mno"
  }
}
```

### 8.3 HTTP状态码规范

| 状态码 | 含义 | 使用场景 |
|--------|------|----------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 204 | No Content | 删除成功，无返回内容 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证或认证失败 |
| 403 | Forbidden | 已认证但无权限 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突（如邮箱已存在） |
| 422 | Unprocessable Entity | 请求格式正确但验证失败 |
| 429 | Too Many Requests | 超过速率限制 |
| 500 | Internal Server Error | 服务器内部错误 |
| 503 | Service Unavailable | 服务暂不可用 |

### 8.4 错误代码规范

```python
# 错误代码枚举
class ErrorCode(str, Enum):
    # 认证相关
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    ACCOUNT_DISABLED = "ACCOUNT_DISABLED"
    
    # 验证相关
    VALIDATION_ERROR = "VALIDATION_ERROR"
    REQUIRED_FIELD_MISSING = "REQUIRED_FIELD_MISSING"
    INVALID_FORMAT = "INVALID_FORMAT"
    VALUE_TOO_LONG = "VALUE_TOO_LONG"
    VALUE_TOO_SHORT = "VALUE_TOO_SHORT"
    
    # 资源相关
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    RESOURCE_LIMIT_EXCEEDED = "RESOURCE_LIMIT_EXCEEDED"
    
    # 权限相关
    PERMISSION_DENIED = "PERMISSION_DENIED"
    TENANT_ACCESS_DENIED = "TENANT_ACCESS_DENIED"
    
    # 业务逻辑相关
    DATA_SOURCE_CONNECTION_FAILED = "DATA_SOURCE_CONNECTION_FAILED"
    SYNC_IN_PROGRESS = "SYNC_IN_PROGRESS"
    QUERY_TIMEOUT = "QUERY_TIMEOUT"
    
    # 系统相关
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
```

## 9. API安全和限流

### 9.1 认证机制

#### JWT Token格式
```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "key_id_123"
  },
  "payload": {
    "sub": "user_123",
    "iss": "https://api.yourplatform.com",
    "aud": "yourplatform-api",
    "exp": 1642247400,
    "iat": 1642243800,
    "tenant_id": "456",
    "roles": ["admin"],
    "permissions": ["users:read", "reports:write"],
    "session_id": "sess_789"
  }
}
```

### 9.2 限流策略

```yaml
# 限流配置
rate_limits:
  # 用户级限流
  user_level:
    requests_per_minute: 60
    requests_per_hour: 1000
    requests_per_day: 10000
  
  # 租户级限流
  tenant_level:
    requests_per_minute: 300
    requests_per_hour: 10000
    burst_limit: 100
  
  # 端点特定限流
  endpoints:
    "/api/v1/auth/login":
      requests_per_minute: 5
      block_duration: 300  # 5 minutes
    
    "/api/v1/reports/{id}/data":
      requests_per_minute: 30
      concurrent_limit: 5
    
    "/api/v1/data-sources/{id}/sync":
      requests_per_hour: 10
      cooldown_period: 300
```

### 9.3 API密钥管理

#### 创建API密钥
```http
POST /api/v1/api-keys
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Production API Key",
  "description": "API key for production integrations",
  "permissions": [
    "data_sources:read",
    "reports:read",
    "webhooks:write"
  ],
  "expires_at": "2024-12-31T23:59:59Z",
  "allowed_ips": [
    "192.168.1.0/24",
    "10.0.0.100"
  ]
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "api_key": {
      "id": 501,
      "name": "Production API Key",
      "key": "sk_live_[REDACTED]",
      "key_prefix": "sk_live_[REDACTED]",
      "permissions": ["data_sources:read", "reports:read"],
      "expires_at": "2024-12-31T23:59:59Z",
      "created_at": "2024-01-15T10:30:00Z",
      "last_used_at": null
    }
  },
  "message": "API key created successfully. Please save the key as it will not be shown again."
}
```

## 10. 分页和过滤

### 10.1 分页参数

```http
GET /api/v1/users?page=2&limit=25&sort=created_at&order=desc
```

**分页响应**:
```json
{
  "success": true,
  "data": {
    "users": [...],
    "pagination": {
      "page": 2,
      "limit": 25,
      "total": 150,
      "pages": 6,
      "has_next": true,
      "has_prev": true,
      "next_page": 3,
      "prev_page": 1
    }
  }
}
```

### 10.2 过滤和搜索

```http
GET /api/v1/reports?
  search=revenue&
  type=chart_line&
  created_after=2024-01-01&
  created_before=2024-01-31&
  tags=sales,monthly&
  is_public=true&
  sort=updated_at&
  order=desc
```

**过滤参数规范**:
- `search`: 全文搜索
- `{field}`: 精确匹配
- `{field}_like`: 模糊匹配
- `{field}_in`: 多值匹配
- `{field}_gt`, `{field}_gte`: 大于/大于等于
- `{field}_lt`, `{field}_lte`: 小于/小于等于
- `{field}_between`: 范围查询

## 11. 缓存策略

### 11.1 HTTP缓存头

```http
# 静态资源缓存
Cache-Control: public, max-age=31536000, immutable

# API响应缓存
Cache-Control: private, max-age=300
ETag: "a1b2c3d4e5f6"
Last-Modified: Mon, 15 Jan 2024 10:30:00 GMT

# 动态内容禁用缓存
Cache-Control: no-cache, no-store, must-revalidate
```

### 11.2 缓存策略配置

```python
# FastAPI缓存装饰器
from functools import wraps
import hashlib
import json

def cache_response(ttl: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"api_cache:{func.__name__}:{hash_args(*args, **kwargs)}"
            
            # 尝试从缓存获取
            cached_result = await redis.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            await redis.setex(cache_key, ttl, json.dumps(result))
            
            return result
        return wrapper
    return decorator

# 使用示例
@app.get("/api/v1/reports/{report_id}/data")
@cache_response(ttl=300)  # 缓存5分钟
async def get_report_data(report_id: int):
    return await report_service.get_data(report_id)
```

这个API规范设计为您的SaaS数据分析平台提供了完整的接口标准，包括认证授权、资源管理、数据处理、安全控制和性能优化。通过遵循这些规范，可以确保API的一致性、可维护性和可扩展性。