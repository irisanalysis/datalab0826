# AI数据分析平台 - 完整架构文档

## 项目概述

基于AI的智能数据分析平台，支持自然语言查询、自动化数据分析、机器学习建模和交互式可视化。采用现代化微服务架构，具备高性能分布式计算能力。

## 技术栈

### 前端技术栈
- **框架**: React 18 + TypeScript + Next.js 14
- **状态管理**: Zustand + React Query
- **UI组件**: shadcn/ui + Tailwind CSS
- **图表库**: Recharts + D3.js + Plotly.js
- **构建工具**: Vite + Turbo
- **开发工具**: ESLint + Prettier + Husky

### 后端技术栈
- **Web框架**: FastAPI + Uvicorn
- **异步任务**: Celery + Redis
- **分布式计算**: Ray + Dask
- **数据库**: PostgreSQL + Redis Cluster
- **存储**: MinIO (S3兼容)
- **消息队列**: Apache Kafka
- **搜索引擎**: Elasticsearch

### 数据科学栈
- **数据处理**: Pandas + Polars + Dask
- **机器学习**: Scikit-learn + XGBoost + LightGBM
- **深度学习**: PyTorch + Transformers
- **统计分析**: SciPy + Statsmodels
- **可视化**: Plotly + Matplotlib + Seaborn

### DevOps & 基础设施
- **容器化**: Docker + Docker Compose
- **编排**: Kubernetes + Helm
- **监控**: Prometheus + Grafana + Jaeger
- **日志**: ELK Stack (Elasticsearch + Logstash + Kibana)
- **CI/CD**: GitHub Actions + ArgoCD

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer                            │
│                   (Nginx/HAProxy)                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
┌─────────┐    ┌─────────┐    ┌─────────┐
│Frontend │    │Frontend │    │Frontend │
│ Node 1  │    │ Node 2  │    │ Node 3  │
└────┬────┘    └────┬────┘    └────┬────┘
     │              │              │
     └──────────────┼──────────────┘
                    │
┌─────────────────────────────────────────────────────────────┐
│                   API Gateway                               │
│                   (FastAPI)                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│   Data   │   │    AI    │   │ Compute  │
│ Service  │   │ Service  │   │ Service  │
└────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │
     └──────────────┼──────────────┘
                    │
┌─────────────────────────────────────────────────────────────┐
│               Computing Layer                               │
│        ┌─────────────┬─────────────┬─────────────┐         │
│        │ Ray Cluster │ Ray Cluster │ Ray Cluster │         │
│        │   Node 1    │   Node 2    │   Node 3    │         │
│        └─────────────┴─────────────┴─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────┐
│                   Storage Layer                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐ │
│  │ PostgreSQL  │ │    Redis    │ │   MinIO     │ │ Kafka  │ │
│  │  Cluster    │ │   Cluster   │ │  Storage    │ │Cluster │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 前端架构

### 目录结构

```
frontend/
├── public/
│   ├── sample-datasets/          # 示例数据集
│   ├── chart-templates/          # 图表模板
│   └── icons/
│
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── dashboard/           # 主仪表板
│   │   ├── datasets/            # 数据集管理
│   │   ├── analysis/            # 分析工作区
│   │   ├── visualizations/      # 可视化图表
│   │   ├── ai-chat/            # AI对话界面
│   │   └── api/                # API路由
│   │
│   ├── components/
│   │   ├── ui/                  # 基础UI组件 (shadcn/ui)
│   │   ├── charts/              # 图表组件库
│   │   │   ├── BarChart.tsx
│   │   │   ├── LineChart.tsx
│   │   │   ├── ScatterPlot.tsx
│   │   │   ├── HeatMap.tsx
│   │   │   ├── DistributionChart.tsx
│   │   │   └── StatisticalChart.tsx
│   │   ├── data/                # 数据相关组件
│   │   │   ├── DataTable.tsx
│   │   │   ├── DataUploader.tsx
│   │   │   ├── DataPreview.tsx
│   │   │   ├── ColumnMapper.tsx
│   │   │   └── DataValidator.tsx
│   │   ├── ai/                  # AI功能组件
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── QueryBuilder.tsx
│   │   │   ├── InsightPanel.tsx
│   │   │   ├── ModelSelector.tsx
│   │   │   └── PromptEditor.tsx
│   │   ├── analysis/            # 分析组件
│   │   │   ├── RegressionPanel.tsx
│   │   │   ├── ClusteringPanel.tsx
│   │   │   ├── CorrelationMatrix.tsx
│   │   │   ├── StatsSummary.tsx
│   │   │   └── MLPipeline.tsx
│   │   └── layout/              # 布局组件
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── Footer.tsx
│   │
│   ├── features/                # 功能模块
│   │   ├── datasets/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   └── types/
│   │   ├── ai-analysis/
│   │   │   ├── components/
│   │   │   ├── prompts/         # AI提示词模板
│   │   │   ├── parsers/         # 结果解析器
│   │   │   └── services/
│   │   ├── visualization/
│   │   │   ├── components/
│   │   │   ├── templates/       # 图表模板
│   │   │   ├── exporters/       # 导出功能
│   │   │   └── services/
│   │   ├── data-science/
│   │   │   ├── regression/
│   │   │   ├── clustering/
│   │   │   ├── statistics/
│   │   │   └── preprocessing/
│   │   └── collaboration/
│   │       ├── sharing/
│   │       ├── comments/
│   │       └── permissions/
│   │
│   ├── lib/
│   │   ├── ai/
│   │   │   ├── client.ts        # AI客户端
│   │   │   ├── prompts.ts       # 提示词管理
│   │   │   ├── parsers.ts       # 响应解析
│   │   │   └── cache.ts         # AI结果缓存
│   │   ├── data/
│   │   │   ├── processing.ts    # 数据处理
│   │   │   ├── validation.ts    # 数据验证
│   │   │   ├── transformers.ts  # 数据转换
│   │   │   ├── statistics.ts    # 统计计算
│   │   │   └── streaming.ts     # 流式数据处理
│   │   ├── charts/
│   │   │   ├── factory.ts       # 图表工厂
│   │   │   ├── themes.ts        # 图表主题
│   │   │   ├── exporters.ts     # 图表导出
│   │   │   └── interactions.ts  # 交互逻辑
│   │   ├── ml/
│   │   │   ├── regression.ts    # 回归分析
│   │   │   ├── clustering.ts    # 聚类分析
│   │   │   ├── correlation.ts   # 相关性分析
│   │   │   ├── preprocessing.ts # 数据预处理
│   │   │   └── evaluation.ts    # 模型评估
│   │   └── api/
│   │       ├── client.ts        # API客户端
│   │       ├── endpoints.ts     # API端点定义
│   │       └── websocket.ts     # WebSocket连接
│   │
│   ├── hooks/                   # 自定义Hooks
│   │   ├── useDataset.ts        # 数据集管理
│   │   ├── useAiChat.ts         # AI对话
│   │   ├── useVisualization.ts  # 图表生成
│   │   ├── useAnalysis.ts       # 数据分析
│   │   ├── useExport.ts         # 导出功能
│   │   └── useRealtime.ts       # 实时更新
│   │
│   ├── types/                   # TypeScript类型定义
│   │   ├── dataset.ts           # 数据集类型
│   │   ├── analysis.ts          # 分析结果类型
│   │   ├── chart.ts            # 图表配置类型
│   │   ├── ai.ts               # AI相关类型
│   │   ├── ml.ts               # 机器学习类型
│   │   └── api.ts              # API接口类型
│   │
│   ├── store/                   # 状态管理 (Zustand)
│   │   ├── datasetStore.ts      # 数据集状态
│   │   ├── analysisStore.ts     # 分析状态
│   │   ├── aiStore.ts           # AI对话状态
│   │   ├── visualizationStore.ts # 可视化状态
│   │   └── userStore.ts         # 用户状态
│   │
│   ├── context/                 # React Context
│   │   ├── ThemeContext.tsx     # 主题上下文
│   │   ├── DataContext.tsx      # 数据上下文
│   │   └── AuthContext.tsx      # 认证上下文
│   │
│   ├── styles/                  # 样式文件
│   │   ├── globals.css          # 全局样式
│   │   ├── tailwind.css         # Tailwind配置
│   │   └── components.css       # 组件样式
│   │
│   └── utils/                   # 工具函数
│       ├── dataHelpers.ts       # 数据处理工具
│       ├── chartHelpers.ts      # 图表工具
│       ├── mlHelpers.ts         # 机器学习工具
│       ├── exportHelpers.ts     # 导出工具
│       └── formatters.ts        # 格式化工具
│
├── package.json
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── .env.local
└── .env.example
```

## 后端架构

### 微服务架构设计

```
backend/
├── apps/                        # 微服务应用
│   ├── api_gateway/             # API网关服务
│   │   ├── main.py             # FastAPI应用入口
│   │   ├── middleware/
│   │   │   ├── auth.py         # 认证中间件
│   │   │   ├── cors.py         # CORS处理
│   │   │   ├── rate_limit.py   # 限流中间件
│   │   │   └── logging.py      # 日志中间件
│   │   ├── routers/
│   │   │   ├── datasets.py     # 数据集路由
│   │   │   ├── analysis.py     # 分析路由
│   │   │   ├── ai.py          # AI路由
│   │   │   └── visualizations.py # 可视化路由
│   │   ├── services/
│   │   │   └── proxy.py        # 服务代理
│   │   └── config.py           # 配置管理
│   │
│   ├── data_service/            # 数据管理服务
│   │   ├── main.py
│   │   ├── models/
│   │   │   ├── dataset.py      # 数据集模型
│   │   │   ├── schema.py       # 数据模式
│   │   │   └── metadata.py     # 元数据模型
│   │   ├── repositories/
│   │   │   ├── dataset_repo.py
│   │   │   └── metadata_repo.py
│   │   ├── services/
│   │   │   ├── upload_service.py    # 数据上传
│   │   │   ├── validation_service.py # 数据验证
│   │   │   ├── preprocessing_service.py # 预处理
│   │   │   └── export_service.py    # 数据导出
│   │   ├── schemas/
│   │   │   ├── dataset_schema.py
│   │   │   └── upload_schema.py
│   │   └── utils/
│   │       ├── file_handlers.py     # 文件处理
│   │       └── data_validators.py   # 数据验证
│   │
│   ├── ai_service/              # AI分析服务
│   │   ├── main.py
│   │   ├── llm/
│   │   │   ├── openai_client.py     # OpenAI客户端
│   │   │   ├── prompt_manager.py    # 提示词管理
│   │   │   ├── response_parser.py   # 响应解析
│   │   │   └── context_manager.py   # 上下文管理
│   │   ├── analysis/
│   │   │   ├── query_processor.py   # 查询处理
│   │   │   ├── insight_generator.py # 洞察生成
│   │   │   └── recommendation_engine.py # 推荐引擎
│   │   ├── models/
│   │   │   ├── chat_session.py     # 对话会话
│   │   │   └── analysis_request.py # 分析请求
│   │   └── prompts/                # 提示词模板
│   │       ├── data_analysis.txt
│   │       ├── visualization.txt
│   │       ├── statistical.txt
│   │       └── ml_modeling.txt
│   │
│   ├── compute_service/         # 分布式计算服务
│   │   ├── main.py
│   │   ├── ray_cluster/
│   │   │   ├── cluster_manager.py   # 集群管理
│   │   │   ├── resource_manager.py # 资源管理
│   │   │   └── task_scheduler.py   # 任务调度
│   │   ├── tasks/
│   │   │   ├── __init__.py
│   │   │   ├── regression.py       # 回归分析任务
│   │   │   ├── clustering.py       # 聚类分析任务
│   │   │   ├── statistics.py       # 统计分析任务
│   │   │   ├── preprocessing.py    # 数据预处理任务
│   │   │   └── visualization.py    # 可视化任务
│   │   ├── workers/
│   │   │   ├── data_worker.py      # 数据处理工作器
│   │   │   ├── ml_worker.py        # 机器学习工作器
│   │   │   └── viz_worker.py       # 可视化工作器
│   │   └── algorithms/
│   │       ├── supervised/
│   │       │   ├── linear_regression.py
│   │       │   ├── random_forest.py
│   │       │   └── neural_network.py
│   │       ├── unsupervised/
│   │       │   ├── kmeans.py
│   │       │   ├── dbscan.py
│   │       │   └── pca.py
│   │       └── statistical/
│   │           ├── descriptive.py
│   │           ├── hypothesis_testing.py
│   │           └── correlation.py
│   │
│   ├── visualization_service/    # 可视化服务
│   │   ├── main.py
│   │   ├── chart_generators/
│   │   │   ├── plotly_generator.py
│   │   │   ├── matplotlib_generator.py
│   │   │   └── d3_generator.py
│   │   ├── templates/
│   │   │   ├── business_dashboard.py
│   │   │   ├── scientific_plots.py
│   │   │   └── statistical_charts.py
│   │   ├── exporters/
│   │   │   ├── pdf_exporter.py
│   │   │   ├── png_exporter.py
│   │   │   └── svg_exporter.py
│   │   └── services/
│   │       ├── chart_service.py
│   │       └── template_service.py
│   │
│   ├── notification_service/     # 通知服务
│   │   ├── main.py
│   │   ├── websocket/
│   │   │   ├── connection_manager.py
│   │   │   └── event_handler.py
│   │   ├── email/
│   │   │   └── email_service.py
│   │   └── push/
│   │       └── push_service.py
│   │
│   └── user_service/            # 用户管理服务
│       ├── main.py
│       ├── auth/
│       │   ├── jwt_handler.py
│       │   └── oauth_handler.py
│       ├── models/
│       │   ├── user.py
│       │   └── session.py
│       └── services/
│           ├── auth_service.py
│           └── user_service.py
│
├── shared/                      # 共享模块
│   ├── database/
│   │   ├── models/              # SQLAlchemy模型
│   │   │   ├── base.py
│   │   │   ├── dataset.py
│   │   │   ├── analysis.py
│   │   │   ├── user.py
│   │   │   └── visualization.py
│   │   ├── migrations/          # Alembic迁移
│   │   ├── connections/
│   │   │   ├── postgres.py      # PostgreSQL连接
│   │   │   ├── redis.py         # Redis连接
│   │   │   └── minio.py         # MinIO连接
│   │   └── repositories/
│   │       ├── base_repo.py
│   │       └── dataset_repo.py
│   │
│   ├── cache/
│   │   ├── redis_manager.py     # Redis缓存管理
│   │   ├── strategies.py        # 缓存策略
│   │   └── decorators.py        # 缓存装饰器
│   │
│   ├── message_queue/
│   │   ├── kafka_producer.py    # Kafka生产者
│   │   ├── kafka_consumer.py    # Kafka消费者
│   │   └── event_schemas.py     # 事件模式
│   │
│   ├── storage/
│   │   ├── file_manager.py      # 文件管理
│   │   ├── s3_client.py         # S3客户端
│   │   └── backup_manager.py    # 备份管理
│   │
│   ├── security/
│   │   ├── encryption.py        # 加密工具
│   │   ├── jwt_utils.py         # JWT工具
│   │   └── rate_limiter.py      # 限流器
│   │
│   └── utils/
│       ├── logging.py           # 日志配置
│       ├── config.py            # 配置管理
│       ├── exceptions.py        # 异常处理
│       └── validators.py        # 数据验证
│
├── infrastructure/              # 基础设施配置
│   ├── docker/
│   │   ├── Dockerfile.api
│   │   ├── Dockerfile.compute
│   │   ├── Dockerfile.ai
│   │   └── Dockerfile.viz
│   │
│   ├── kubernetes/
│   │   ├── namespace.yaml
│   │   ├── deployments/
│   │   │   ├── api-gateway.yaml
│   │   │   ├── data-service.yaml
│   │   │   ├── ai-service.yaml
│   │   │   ├── compute-service.yaml
│   │   │   └── viz-service.yaml
│   │   ├── services/
│   │   │   ├── api-gateway-svc.yaml
│   │   │   └── internal-services.yaml
│   │   ├── ingress/
│   │   │   └── main-ingress.yaml
│   │   ├── configmaps/
│   │   │   └── app-config.yaml
│   │   └── secrets/
│   │       └── api-keys.yaml
│   │
│   ├── monitoring/
│   │   ├── prometheus/
│   │   │   ├── prometheus.yml
│   │   │   └── rules/
│   │   ├── grafana/
│   │   │   ├── dashboards/
│   │   │   └── datasources/
│   │   └── jaeger/
│   │       └── jaeger-config.yaml
│   │
│   ├── logging/
│   │   ├── elasticsearch/
│   │   │   └── es-config.yml
│   │   ├── logstash/
│   │   │   └── pipeline.conf
│   │   └── kibana/
│   │       └── kibana.yml
│   │
│   └── security/
│       ├── ssl/
│       ├── firewall/
│       └── policies/
│
├── scripts/                     # 部署和运维脚本
│   ├── deployment/
│   │   ├── deploy.sh
│   │   ├── rollback.sh
│   │   └── health_check.sh
│   ├── migration/
│   │   ├── migrate.py
│   │   └── seed_data.py
│   ├── monitoring/
│   │   ├── setup_monitoring.sh
│   │   └── alert_setup.py
│   └── backup/
│       ├── backup_db.sh
│       └── restore_db.sh
│
├── tests/                       # 测试套件
│   ├── unit/
│   ├── integration/
│   ├── performance/
│   └── e2e/
│
├── docs/                        # 文档
│   ├── api/                     # API文档
│   ├── deployment/              # 部署文档
│   ├── development/             # 开发文档
│   └── architecture/            # 架构文档
│
├── requirements/
│   ├── base.txt                 # 基础依赖
│   ├── development.txt          # 开发依赖
│   ├── production.txt           # 生产依赖
│   └── ml.txt                   # 机器学习依赖
│
├── docker-compose.yml           # 开发环境
├── docker-compose.prod.yml      # 生产环境
├── .env.example
└── README.md
```

## 数据流架构

### 1. 用户查询流程
```
User Query → Frontend → API Gateway → AI Service → Query Processing → 
Compute Service → Ray Cluster → Analysis Results → Visualization Service → 
Chart Generation → Frontend Display
```

### 2. 数据处理流程
```
Data Upload → Data Service → Validation → Storage (MinIO) → 
Metadata (PostgreSQL) → Cache (Redis) → Preprocessing → 
Analysis Ready → Notification
```

### 3. 实时分析流程
```
Streaming Data → Kafka → Data Service → Ray Streaming → 
Real-time Analysis → WebSocket → Frontend Updates
```

## 核心技术特性

### 高性能计算
- **Ray集群**: 分布式计算框架，支持自动扩缩容
- **Dask**: 大数据并行处理
- **Celery**: 异步任务队列，处理长时间运行的分析任务
- **连接池**: 数据库连接池优化

### 缓存策略
- **多级缓存**: Redis + 应用级内存缓存
- **智能失效**: 基于数据变更的缓存失效
- **预计算**: 常用分析结果预计算
- **CDN**: 静态资源和图表缓存

### 数据存储
- **主存储**: PostgreSQL (元数据、用户数据、分析结果)
- **文件存储**: MinIO/S3 (原始数据集、生成的图表)
- **时序数据**: InfluxDB (性能监控数据)
- **搜索**: Elasticsearch (全文搜索、日志分析)

### 安全性
- **认证**: JWT + OAuth 2.0
- **授权**: RBAC权限控制
- **数据加密**: 传输加密(TLS) + 存储加密
- **API安全**: 限流、防SQL注入、XSS防护

## 部署配置

### 开发环境 (Docker Compose)

```yaml
version: '3.8'

services:
  # 前端服务
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    
  # API网关
  api-gateway:
    build: 
      context: ./backend
      dockerfile: infrastructure/docker/Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://user:pass@postgres:5432/dataplatform
      - AI_SERVICE_URL=http://ai-service:8002
      - COMPUTE_SERVICE_URL=http://compute-service:8003
    depends_on:
      - redis
      - postgres
      - ai-service
      - compute-service
      
  # AI服务
  ai-service:
    build:
      context: ./backend
      dockerfile: infrastructure/docker/Dockerfile.ai
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    replicas: 2
    
  # 计算服务
  compute-service:
    build:
      context: ./backend
      dockerfile: infrastructure/docker/Dockerfile.compute
    environment:
      - RAY_ADDRESS=ray://ray-head:10001
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - ray-head
      - redis
    replicas: 2
    
  # Ray集群头节点
  ray-head:
    image: rayproject/ray:2.8.0-py310
    command: >
      ray start --head 
      --port=6379 
      --dashboard-host=0.0.0.0 
      --dashboard-port=8265
      --redis-port=6380
    ports:
      - "8265:8265"  # Ray Dashboard
      - "10001:10001" # Ray Client
    volumes:
      - ./backend:/app
      - ray_data:/tmp/ray
    environment:
      - RAY_DISABLE_IMPORT_WARNING=1
      
  # Ray工作节点
  ray-worker:
    image: rayproject/ray:2.8.0-py310
    command: ray start --address=ray-head:6379
    volumes:
      - ./backend:/app
      - ray_data:/tmp/ray
    depends_on:
      - ray-head
    deploy:
      replicas: 3
      
  # 数据服务
  data-service:
    build:
      context: ./backend
      dockerfile: infrastructure/docker/Dockerfile.api
    command: uvicorn apps.data_service.main:app --host 0.0.0.0 --port 8001
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/dataplatform
      - MINIO_URL=http://minio:9000
      - MINIO_ACCESS_KEY=minioadmin
      - MINIO_SECRET_KEY=minioadmin
    depends_on:
      - postgres
      - minio
    
  # 可视化服务
  viz-service:
    build:
      context: ./backend
      dockerfile: infrastructure/docker/Dockerfile.viz
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      
  # Celery工作节点
  celery-worker:
    build:
      context: ./backend
      dockerfile: infrastructure/docker/Dockerfile.compute
    command: celery -A shared.tasks worker --loglevel=info --concurrency=4
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
      - DATABASE_URL=postgresql://user:pass@postgres:5432/dataplatform
    depends_on:
      - redis
      - postgres
    deploy:
      replicas: 3
      
  # Celery监控
  celery-flower:
    build:
      context: ./backend
      dockerfile: infrastructure/docker/Dockerfile.compute
    command: celery -A shared.tasks flower --port=5555
    ports:
      - "5555:5555"
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - redis

  # 数据库
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: dataplatform
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/shared/database/init.sql:/docker-entrypoint-initdb.d/init.sql
    
  # Redis集群
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    
  # MinIO对象存储
  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"
    
  # Kafka
  kafka:
    image: confluentinc/cp-kafka:latest
    ports:
      - "9092:9092"
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    depends_on:
      - zookeeper
      
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    
  # Elasticsearch
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    ports:
      - "9200:9200"
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
      
  # Kibana
  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  postgres_data:
  redis_data:
  minio_data:
  elasticsearch_data:
  ray_data:

networks:
  default:
    driver: bridge
```

### 生产环境 (Kubernetes)

#### Namespace配置
```yaml
# infrastructure/kubernetes/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-data-platform
  labels:
    name: ai-data-platform
```

#### API Gateway部署
```yaml
# infrastructure/kubernetes/deployments/api-gateway.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: ai-data-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: dataplatform/api-gateway:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway-service
  namespace: ai-data-platform
spec:
  selector:
    app: api-gateway
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

#### Ray集群部署
```yaml
# infrastructure/kubernetes/deployments/ray-cluster.yaml
apiVersion: ray.io/v1alpha1
kind: RayCluster
metadata:
  name: ray-cluster
  namespace: ai-data-platform
spec:
  rayVersion: '2.8.0'
  headGroupSpec:
    replicas: 1
    rayStartParams:
      dashboard-host: '0.0.0.0'
      port: '6379'
      redis-port: '6380'
    template:
      spec:
        containers:
        - name: ray-head
          image: rayproject/ray:2.8.0-py310
          ports:
          - containerPort: 6379
          - containerPort: 8265
          - containerPort: 10001
          resources:
            requests:
              cpu: 1000m
              memory: 2Gi
            limits:
              cpu: 2000m
              memory: 4Gi
          volumeMounts:
          - mountPath: /tmp/ray
            name: ray-logs
        volumes:
        - name: ray-logs
          emptyDir: {}
  workerGroupSpecs:
  - replicas: 4
    minReplicas: 2
    maxReplicas: 10
    groupName: worker-group
    rayStartParams:
      redis-address: ray-cluster-head-svc:6379
    template:
      spec:
        containers:
        - name: ray-worker
          image: rayproject/ray:2.8.0-py310
          resources:
            requests:
              cpu: 1000m
              memory: 2Gi
            limits:
              cpu: 2000m
              memory: 4Gi
          volumeMounts:
          - mountPath: /tmp/ray
            name: ray-logs
        volumes:
        - name: ray-logs
          emptyDir: {}
```

#### 数据库部署 (PostgreSQL with HA)
```yaml
# infrastructure/kubernetes/deployments/postgres-ha.yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: postgres-cluster
  namespace: ai-data-platform
spec:
  instances: 3
  
  postgresql:
    parameters:
      max_connections: "200"
      shared_buffers: "256MB"
      effective_cache_size: "1GB"
      work_mem: "4MB"
      
  bootstrap:
    initdb:
      database: dataplatform
      owner: app_user
      secret:
        name: postgres-credentials
        
  storage:
    size: 100Gi
    storageClass: fast-ssd
    
  resources:
    requests:
      memory: "1Gi"
      cpu: "500m"
    limits:
      memory: "2Gi"
      cpu: "1000m"
      
  monitoring:
    enabled: true
```

## 监控与日志

### Prometheus监控配置
```yaml
# infrastructure/monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'api-gateway'
    static_configs:
      - targets: ['api-gateway-service:8000']
    metrics_path: /metrics
    scrape_interval: 10s
    
  - job_name: 'ray-cluster'
    static_configs:
      - targets: ['ray-cluster-head-svc:8265']
    metrics_path: /api/metrics
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### Grafana Dashboard配置
```json
{
  "dashboard": {
    "title": "AI Data Platform Overview",
    "panels": [
      {
        "title": "API Gateway Requests",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Ray Cluster Resource Usage",
        "type": "graph", 
        "targets": [
          {
            "expr": "ray_cluster_cpu_usage",
            "legendFormat": "CPU Usage"
          },
          {
            "expr": "ray_cluster_memory_usage",
            "legendFormat": "Memory Usage"
          }
        ]
      },
      {
        "title": "Analysis Tasks Status",
        "type": "stat",
        "targets": [
          {
            "expr": "celery_tasks_total{state=\"SUCCESS\"}",
            "legendFormat": "Completed"
          },
          {
            "expr": "celery_tasks_total{state=\"PENDING\"}",
            "legendFormat": "Pending"
          }
        ]
      }
    ]
  }
}
```

## 开发指南

### 环境设置

1. **克隆项目**
```bash
git clone https://github.com/your-org/ai-data-platform.git
cd ai-data-platform
```

2. **前端开发环境**
```bash
cd frontend
npm install
npm run dev
```

3. **后端开发环境**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

pip install -r requirements/development.txt
```

4. **启动开发环境**
```bash
# 启动所有服务
docker-compose up -d

# 或单独启动服务
docker-compose up -d postgres redis minio
python -m apps.api_gateway.main
```

### 开发工作流

1. **功能开发**
   - 创建功能分支: `git checkout -b feature/new-analysis-type`
   - 编写测试用例
   - 实现功能
   - 运行测试: `pytest tests/`
   - 提交代码: `git commit -m "feat: add new analysis type"`

2. **代码质量检查**
```bash
# Python代码检查
black backend/
flake8 backend/
mypy backend/

# JavaScript代码检查
cd frontend
npm run lint
npm run type-check
```

3. **测试**
```bash
# 后端测试
pytest backend/tests/ -v --cov=backend

# 前端测试
cd frontend
npm test
npm run e2e
```

### API文档

API文档自动生成，访问: `http://localhost:8000/docs`

#### 核心API端点

**数据集管理**
- `POST /api/v1/datasets/upload` - 上传数据集
- `GET /api/v1/datasets/{id}` - 获取数据集信息
- `DELETE /api/v1/datasets/{id}` - 删除数据集

**AI分析**
- `POST /api/v1/analysis/query` - AI自然语言查询
- `GET /api/v1/analysis/{id}/status` - 获取分析状态
- `GET /api/v1/analysis/{id}/results` - 获取分析结果

**可视化**
- `POST /api/v1/visualizations/generate` - 生成图表
- `GET /api/v1/visualizations/{id}` - 获取图表配置
- `POST /api/v1/visualizations/{id}/export` - 导出图表

## 性能优化

### 1. 前端优化
- **代码分割**: 使用Next.js动态导入
- **图片优化**: Next.js Image组件 + WebP格式
- **缓存策略**: SWR数据缓存 + Service Worker
- **Bundle优化**: Tree shaking + 压缩

### 2. 后端优化
- **数据库优化**: 索引优化 + 查询优化
- **缓存层**: Redis缓存 + 应用级缓存
- **连接池**: 数据库连接池配置
- **异步处理**: FastAPI异步视图 + Celery任务队列

### 3. 分布式计算优化
- **资源调度**: Ray自动扩缩容
- **任务分片**: 大数据集分片处理
- **内存管理**: Ray对象存储优化
- **网络优化**: 数据本地性优化

## 安全最佳实践

### 1. 认证与授权
```python
# JWT Token验证
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return await get_user_by_id(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 2. 数据保护
- **传输加密**: 全站HTTPS + TLS 1.3
- **存储加密**: 数据库透明加密 + MinIO加密
- **敏感数据**: 密钥管理系统(Vault)
- **数据脱敏**: 个人信息自动脱敏

### 3. API安全
```python
# 限流中间件
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@app.post("/api/v1/analysis/query")
@limiter.limit("10/minute")
async def ai_query(request: Request, query: AIQueryRequest):
    # 处理AI查询
    pass
```

## 扩展性设计

### 1. 水平扩展
- **无状态设计**: 所有服务无状态，支持水平扩展
- **数据库分片**: 按租户或数据集分片
- **CDN集成**: 静态资源全球分发
- **多区域部署**: 跨区域容灾

### 2. 插件架构
```python
# 分析算法插件接口
class AnalysisPlugin:
    name: str
    version: str
    
    def validate_input(self, data: DataFrame) -> bool:
        pass
        
    def execute(self, data: DataFrame, params: dict) -> dict:
        pass
        
    def get_visualization_config(self) -> dict:
        pass
```

### 3. 第三方集成
- **数据源集成**: Snowflake, BigQuery, Databricks
- **AI模型集成**: OpenAI, Anthropic, Azure OpenAI
- **可视化集成**: Tableau, Power BI, Observable

## 故障恢复

### 1. 高可用部署
- **多实例部署**: 每个服务至少3个实例
- **健康检查**: Kubernetes liveness/readiness probe
- **自动故障转移**: 数据库主从切换
- **断路器**: 服务间调用断路器模式

### 2. 数据备份
```bash
# 自动备份脚本
#!/bin/bash
# 数据库备份
pg_dump dataplatform | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# MinIO数据备份  
mc mirror minio/datasets s3://backup-bucket/datasets

# 配置备份
kubectl get configmaps,secrets -o yaml > k8s_config_backup.yaml
```

### 3. 监控告警
```yaml
# 告警规则
groups:
- name: platform.rules
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      
  - alert: RayClusterDown
    expr: up{job="ray-cluster"} == 0
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Ray cluster is down"
```

## 贡献指南

### 1. 开发规范
- **代码风格**: 遵循PEP8 (Python) 和 Airbnb (JavaScript) 规范
- **提交规范**: 使用Conventional Commits格式
- **分支策略**: Git Flow工作流
- **代码审查**: 所有PR必须经过代码审查

### 2. 提交流程
1. Fork项目
2. 创建功能分支
3. 编写测试
4. 确保测试通过
5. 提交PR
6. 通过代码审查
7. 合并到主分支

### 3. 发版流程
```bash
# 版本发布
git checkout main
git pull origin main
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0

# 自动部署到生产环境
# (通过GitHub Actions或Jenkins)
```

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- **项目负责人**: your-email@example.com
- **技术支持**: support@example.com  
- **问题反馈**: https://github.com/your-org/ai-data-platform/issues

---

**版本**: v1.0.0  
**最后更新**: 2025年8月