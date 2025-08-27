#!/bin/bash
set -e

# 全面测试执行脚本
echo "🧪 开始运行所有测试..."

# 创建测试结果目录
mkdir -p .scripts/testing/results

# 测试结果收集
RESULTS_FILE=".scripts/testing/results/test_results_$(date +%Y%m%d_%H%M%S).txt"
echo "📊 测试结果将保存到: $RESULTS_FILE"

# 记录测试开始时间
echo "测试开始时间: $(date)" >> "$RESULTS_FILE"
echo "=================" >> "$RESULTS_FILE"

# 1. Flask应用测试
echo "🔍 1. Flask应用基础测试"
if uv run python .scripts/testing/test_flask_app.py >> "$RESULTS_FILE" 2>&1; then
    echo "✅ Flask应用测试通过"
else
    echo "❌ Flask应用测试失败"
fi

# 2. API端点测试
echo "🔍 2. API端点测试"
if uv run python .scripts/testing/test_api_endpoints.py >> "$RESULTS_FILE" 2>&1; then
    echo "✅ API端点测试通过"
else
    echo "❌ API端点测试失败"
fi

# 3. 代码质量检查
echo "🔍 3. 代码质量检查"
echo "代码质量检查结果:" >> "$RESULTS_FILE"
if uv run autopep8 --diff --recursive . >> "$RESULTS_FILE" 2>&1; then
    echo "✅ 代码格式检查通过"
else
    echo "⚠️ 代码格式需要调整"
fi

# 4. 项目结构验证
echo "🔍 4. 项目结构验证"
echo "项目结构验证:" >> "$RESULTS_FILE"
{
    echo "检查必要文件:"
    [ -f "main.py" ] && echo "✅ main.py 存在" || echo "❌ main.py 缺失"
    [ -f "src/index.html" ] && echo "✅ src/index.html 存在" || echo "❌ src/index.html 缺失"
    [ -f "pyproject.toml" ] && echo "✅ pyproject.toml 存在" || echo "❌ pyproject.toml 缺失"
    [ -f "devserver.sh" ] && echo "✅ devserver.sh 存在" || echo "❌ devserver.sh 缺失"
    [ -f "CLAUDE.md" ] && echo "✅ CLAUDE.md 存在" || echo "❌ CLAUDE.md 缺失"
} >> "$RESULTS_FILE"

# 5. 依赖检查
echo "🔍 5. 依赖检查"
echo "依赖检查结果:" >> "$RESULTS_FILE"
if uv pip list >> "$RESULTS_FILE" 2>&1; then
    echo "✅ 依赖列表获取成功"
else
    echo "❌ 依赖检查失败"
fi

# 记录测试结束时间
echo "=================" >> "$RESULTS_FILE"
echo "测试结束时间: $(date)" >> "$RESULTS_FILE"

# 显示测试摘要
echo ""
echo "📋 测试完成摘要:"
echo "=================="
tail -20 "$RESULTS_FILE"

echo ""
echo "📄 完整测试结果请查看: $RESULTS_FILE"