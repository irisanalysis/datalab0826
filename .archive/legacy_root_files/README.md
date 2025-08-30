# Legacy Root Files Archive

## Overview
这些文件是在项目架构重构过程中从根目录迁移的遗留文件。它们已经被移动到backend目录中的相应位置，并且根目录中的依赖关系已被修复。

## Archived Files

### Core Application Files
- **main.py** - 原始的Flask应用文件，已迁移到 `backend/apps/legacy_flask/main.py`
- **data_connectors.py** - 数据源连接器，已迁移到 `backend/shared/data_connectors/connectors.py`

### Database Management Scripts
- **init_saas_database.py** - 原始的数据库初始化脚本，存在格式问题
- **init_saas_database_fixed.py** - 修复后的数据库初始化脚本
- **migrate_database.py** - 数据库迁移脚本，已更新导入路径使用backend模块

## Migration Status
✅ 所有文件已成功迁移到backend架构
✅ 导入依赖关系已修复
✅ 功能完整性已验证
✅ 兼容性脚本已创建 (`init_database_compatible.py`)

## Current Working Scripts
项目现在使用以下脚本：
- `init_database_compatible.py` - 兼容性数据库初始化脚本（推荐使用）
- `backend/apps/legacy_flask/main.py` - Flask应用
- `backend/shared/data_connectors/connectors.py` - 数据连接器

## Archive Date
2024-08-30 08:45:00 UTC

## Notes
- 这些文件仅作为历史参考保留
- 不应直接使用这些归档文件运行应用程序
- 如需使用相关功能，请使用backend目录中的对应文件