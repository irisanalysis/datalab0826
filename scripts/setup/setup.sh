#!/bin/bash
set -e

# 数据实验室开发环境初始化脚本
echo "🚀 初始化数据实验室开发环境..."

# 检查 uv 是否已安装
if ! command -v uv &> /dev/null; then
    echo "❌ uv 未安装，请先安装 uv"
    echo "安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 创建Python虚拟环境
echo "📦 创建Python虚拟环境..."
uv venv

# 激活虚拟环境并安装依赖
echo "🔧 安装Python依赖..."
uv pip install -e .

# 检查是否需要Node.js依赖（如果存在package.json）
if [ -f "package.json" ]; then
    echo "📋 发现Node.js依赖，安装中..."
    if command -v npm &> /dev/null; then
        npm install
    elif command -v yarn &> /dev/null; then
        yarn install
    else
        echo "⚠️ 未找到npm或yarn，跳过Node.js依赖安装"
    fi
fi

# 创建必要的目录
echo "📁 创建必要目录..."
mkdir -p logs data temp

# 设置权限
chmod +x .scripts/**/*.sh 2>/dev/null || true

echo "✅ 开发环境初始化完成！"
echo ""
echo "🎯 启动应用:"
echo "  开发模式: ./devserver.sh"
echo "  生产模式: uv run python main.py"
echo ""
echo "🛠️ 其他脚本:"
echo "  验证功能: uv run python .scripts/validate_analysis_feature.py"
echo "  运行测试: .scripts/testing/run_all_tests.sh"