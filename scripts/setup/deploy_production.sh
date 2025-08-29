#!/bin/bash
set -e

# 生产环境部署脚本
echo "🚀 开始生产环境部署..."

# 检查环境变量
if [ -z "$PORT" ]; then
    export PORT=80
    echo "⚠️ 未设置PORT环境变量，使用默认端口: $PORT"
fi

# 运行预部署验证
echo "🔍 运行预部署验证..."
if [ -f ".scripts/validate_analysis_feature.py" ]; then
    uv run python .scripts/validate_analysis_feature.py
fi

# 格式化代码
echo "🎨 格式化代码..."
uv run autopep8 --in-place --recursive . || echo "⚠️ 代码格式化失败，继续部署"

# 启动应用
echo "🌟 启动生产应用..."
echo "应用将在端口 $PORT 上运行"
exec uv run python main.py