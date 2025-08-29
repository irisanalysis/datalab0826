# .scripts - 数据实验室开发工具集

这个目录包含用于数据实验室项目的开发辅助工具集合，包括测试、验证、部署和维护项目的自动化脚本。

## 📁 目录结构

```
.scripts/
├── setup/                    # 环境设置和部署
│   ├── setup.sh             # 开发环境初始化
│   └── deploy_production.sh  # 生产环境部署
├── testing/                  # 测试和验证
│   ├── test_flask_app.py     # Flask应用测试
│   ├── test_api_endpoints.py # API端点测试
│   └── run_all_tests.sh      # 运行所有测试
├── auth-fixes/               # 认证相关设置
│   ├── setup_basic_auth.py   # 基础认证设置
│   └── jwt_auth_setup.py     # JWT认证设置
├── utils/                    # 实用工具
│   └── project_health_check.py # 项目健康检查
├── validate_analysis_feature.py # 核心功能验证
└── README.md                # 本文档
```

## 🚀 快速开始

### 1. 初始化开发环境

```bash
# 设置开发环境
chmod +x .scripts/setup/setup.sh
.scripts/setup/setup.sh
```

### 2. 验证项目功能

```bash
# 运行核心功能验证
uv run python .scripts/validate_analysis_feature.py
```

### 3. 运行测试套件

```bash
# 运行所有测试
chmod +x .scripts/testing/run_all_tests.sh
.scripts/testing/run_all_tests.sh
```

## 🔧 主要脚本功能

### 核心验证脚本

#### `validate_analysis_feature.py` - 全面功能验证

**用途**: 数据实验室的核心验证脚本，全面检查项目各项功能。

**功能**:
- ✅ 项目结构验证：检查所有必需文件是否存在
- 🔍 依赖环境验证：验证uv、Python依赖等
- 🌐 Flask应用验证：检查应用配置和代码
- 📄 HTML内容验证：验证前端文件完整性
- 🧪 功能测试：启动服务器进行实际测试
- 📊 生成详细报告：包含建议和错误修复指导

**使用方法**:
```bash
uv run python .scripts/validate_analysis_feature.py
```

**输出**: 
- 终端显示彩色状态信息
- 生成 `.scripts/validation_report.txt` 详细报告

### 环境设置脚本

#### `setup/setup.sh` - 开发环境初始化

**用途**: 一键设置完整的开发环境。

**功能**:
- 检查并使用uv创建虚拟环境
- 安装Python和Node.js依赖
- 创建必要的目录结构
- 设置脚本执行权限
- 提供启动指导

**使用方法**:
```bash
chmod +x .scripts/setup/setup.sh
.scripts/setup/setup.sh
```

#### `setup/deploy_production.sh` - 生产环境部署

**用途**: 生产环境部署脚本。

**功能**:
- 运行预部署验证
- 代码格式化
- 启动生产应用

**使用方法**:
```bash
chmod +x .scripts/setup/deploy_production.sh
.scripts/setup/deploy_production.sh
```

### 测试脚本

#### `testing/test_flask_app.py` - Flask应用测试

**用途**: 测试Flask应用的基本功能。

**功能**:
- 检查应用文件完整性
- 启动测试服务器
- 验证主页路由响应
- 检查HTML内容有效性

#### `testing/test_api_endpoints.py` - API端点测试

**用途**: 全面测试API接口的可用性和性能。

**功能**:
- 测试各种HTTP方法 (GET, POST, PUT, DELETE)
- 记录响应时间和状态码
- 生成API测试报告
- 支持自定义端点配置

#### `testing/run_all_tests.sh` - 综合测试套件

**用途**: 运行所有测试并生成综合报告。

**功能**:
- Flask应用基础测试
- API端点测试
- 代码质量检查
- 项目结构验证
- 依赖检查
- 生成时间戳报告

### 认证设置脚本

#### `auth-fixes/setup_basic_auth.py` - 基础认证设置

**用途**: 为Flask应用添加基础HTTP认证。

**功能**:
- 生成安全的环境配置文件
- 创建认证中间件示例
- 更新.gitignore防止敏感信息泄露
- 提供使用指导

#### `auth-fixes/jwt_auth_setup.py` - JWT认证设置

**用途**: 为Flask应用添加JWT (JSON Web Token) 认证。

**功能**:
- 创建完整的JWT认证模块
- 提供令牌生成和验证功能
- 创建使用示例和演示应用
- 支持用户认证和权限管理

### 实用工具

#### `utils/project_health_check.py` - 项目健康检查

**用途**: 快速诊断项目的整体健康状况。

**功能**:
- Git状态检查
- 磁盘空间检查
- Python环境验证
- 项目大小分析
- 常见问题诊断
- 生成健康摘要和建议

## 💡 使用场景和工作流

### 新项目启动工作流

```bash
# 1. 克隆项目后立即运行
.scripts/setup/setup.sh

# 2. 验证环境设置
uv run python .scripts/validate_analysis_feature.py

# 3. 开始开发
./devserver.sh
```

### 开发过程中的验证工作流

```bash
# 每日开发前的健康检查
uv run python .scripts/utils/project_health_check.py

# 功能开发后的验证
uv run python .scripts/validate_analysis_feature.py

# 提交代码前的全面测试
.scripts/testing/run_all_tests.sh
```

### 部署前验证工作流

```bash
# 1. 全面功能验证
uv run python .scripts/validate_analysis_feature.py

# 2. 运行完整测试套件
.scripts/testing/run_all_tests.sh

# 3. 部署到生产环境
.scripts/setup/deploy_production.sh
```

### 问题诊断工作流

```bash
# 1. 基础健康检查
uv run python .scripts/utils/project_health_check.py

# 2. 详细功能验证
uv run python .scripts/validate_analysis_feature.py

# 3. 特定问题测试
uv run python .scripts/testing/test_flask_app.py
uv run python .scripts/testing/test_api_endpoints.py
```

## 🛠️ 脚本扩展和定制

### 添加新的测试脚本

1. 在 `testing/` 目录创建新的测试脚本
2. 在 `run_all_tests.sh` 中添加调用
3. 更新本README文档

### 添加新的工具脚本

1. 在相应的子目录创建脚本
2. 确保脚本有适当的错误处理
3. 添加使用说明到本文档

### 环境变量配置

脚本支持以下环境变量：
- `PORT`: 应用端口 (默认: 80)
- `FLASK_ENV`: Flask环境 (开发/生产)
- `SECRET_KEY`: 应用密钥
- `DEBUG`: 调试模式开关

## 📊 报告和日志

### 生成的报告文件

- `.scripts/validation_report.txt` - 功能验证报告
- `.scripts/testing/api_test_report.txt` - API测试报告
- `.scripts/testing/results/test_results_YYYYMMDD_HHMMSS.txt` - 综合测试结果

### 查看报告

```bash
# 查看最新的验证报告
cat .scripts/validation_report.txt

# 查看最新的测试结果
ls -la .scripts/testing/results/
cat .scripts/testing/results/test_results_*.txt
```

## ⚡ 性能和最佳实践

### 脚本执行性能

- 大多数验证脚本在30秒内完成
- 功能测试需要启动临时服务器，可能需要1-2分钟
- 所有脚本支持Ctrl+C中断

### 最佳实践建议

1. **定期运行**: 每日开始工作前运行健康检查
2. **提交前验证**: 每次代码提交前运行完整验证
3. **部署前测试**: 生产部署前必须通过所有测试
4. **报告保存**: 重要的测试报告应该保存或提交到版本控制
5. **权限管理**: 确保脚本有适当的执行权限

### 故障排除

常见问题和解决方案：

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| uv命令不存在 | uv未安装 | 安装uv: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| 端口占用 | 其他进程占用端口 | 更改端口或停止占用进程 |
| 权限不足 | 脚本缺少执行权限 | `chmod +x .scripts/**/*.sh` |
| 依赖缺失 | Python包未安装 | 运行 `uv pip install -e .` |
| 测试超时 | 网络或系统负载问题 | 重试或检查系统资源 |

## 🔄 持续集成支持

这些脚本设计为支持CI/CD流水线：

```yaml
# GitHub Actions 示例
- name: Setup Environment
  run: .scripts/setup/setup.sh

- name: Run Tests
  run: .scripts/testing/run_all_tests.sh

- name: Validate Features
  run: uv run python .scripts/validate_analysis_feature.py
```

## 📞 获取帮助

如果在使用过程中遇到问题：

1. 查看脚本生成的错误报告
2. 运行健康检查脚本诊断问题
3. 检查本文档的故障排除部分
4. 查看具体脚本的内部注释和文档字符串

---

**创建时间**: 2024年开发
**维护**: 数据实验室开发团队
**版本**: 1.0.0