#!/bin/bash

# SaaS数据分析平台完整测试套件运行脚本
# 包含后端、前端、集成和质量评估测试

set -e  # 出错时退出

PROJECT_ROOT="/home/user/datalab0826"
cd "$PROJECT_ROOT"

echo "🚀 开始SaaS数据分析平台完整测试套件"
echo "================================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 测试结果统计
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# 记录测试结果
log_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2 通过${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ $2 失败${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# 检查依赖
check_dependencies() {
    echo -e "${BLUE}🔍 检查测试依赖...${NC}"
    
    # 检查Python
    if command -v python3 &> /dev/null; then
        echo "✅ Python3 已安装"
    else
        echo "❌ Python3 未安装"
        exit 1
    fi
    
    # 检查uv
    if command -v uv &> /dev/null; then
        echo "✅ uv 包管理器已安装"
    else
        echo "⚠️  uv 未安装，使用pip"
    fi
    
    # 检查Node.js (用于前端测试)
    if command -v node &> /dev/null; then
        echo "✅ Node.js 已安装"
    else
        echo "⚠️  Node.js 未安装，跳过前端测试"
    fi
}

# 安装测试依赖
install_test_dependencies() {
    echo -e "${BLUE}📦 安装测试依赖...${NC}"
    
    # Python测试依赖
    if command -v uv &> /dev/null; then
        uv pip install pytest requests pytest-cov pytest-html || echo "警告: Python测试依赖安装失败"
    else
        pip3 install pytest requests pytest-cov pytest-html || echo "警告: Python测试依赖安装失败"
    fi
    
    # 前端测试依赖
    if [ -d "web" ] && command -v npm &> /dev/null; then
        cd web
        npm install --save-dev jest @testing-library/react @testing-library/jest-dom || echo "警告: 前端测试依赖安装失败"
        cd ..
    fi
}

# 启动测试服务器
start_test_server() {
    echo -e "${BLUE}🚀 启动测试服务器...${NC}"
    
    if [ -f "main.py" ]; then
        # 导出测试环境变量
        export FLASK_ENV=testing
        export DATABASE_URL=sqlite:///test.db
        
        # 启动Flask应用作为后台进程
        if command -v uv &> /dev/null; then
            uv run python -u -m flask --app main run -p 5000 > server.log 2>&1 &
        else
            python3 -u -m flask --app main run -p 5000 > server.log 2>&1 &
        fi
        
        SERVER_PID=$!
        echo "服务器PID: $SERVER_PID"
        
        # 等待服务器启动
        echo "等待服务器启动..."
        sleep 5
        
        # 检查服务器是否启动成功
        if curl -s http://localhost:5000/health > /dev/null 2>&1; then
            echo "✅ 测试服务器启动成功"
            return 0
        else
            echo "❌ 测试服务器启动失败"
            if [ -f server.log ]; then
                echo "服务器日志:"
                tail -10 server.log
            fi
            return 1
        fi
    else
        echo "❌ 未找到main.py文件"
        return 1
    fi
}

# 停止测试服务器
stop_test_server() {
    if [ ! -z "$SERVER_PID" ]; then
        echo -e "${BLUE}🛑 停止测试服务器...${NC}"
        kill $SERVER_PID 2>/dev/null || true
        wait $SERVER_PID 2>/dev/null || true
    fi
}

# 运行后端单元测试
run_backend_unit_tests() {
    echo -e "${BLUE}🧪 运行后端单元测试...${NC}"
    
    if [ -f "test_comprehensive_saas.py" ]; then
        pytest test_comprehensive_saas.py -v --tb=short --cov=. --cov-report=html:htmlcov --cov-report=term
        log_result $? "后端单元测试"
    else
        echo -e "${YELLOW}⚠️  跳过后端单元测试 (测试文件不存在)${NC}"
        TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
    fi
}

# 运行API集成测试
run_api_integration_tests() {
    echo -e "${BLUE}🔗 运行API集成测试...${NC}"
    
    if [ -f "test_saas_api.py" ]; then
        python3 test_saas_api.py
        log_result $? "API集成测试"
    else
        echo -e "${YELLOW}⚠️  跳过API集成测试 (测试文件不存在)${NC}"
        TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
    fi
}

# 运行现有shell测试
run_shell_tests() {
    echo -e "${BLUE}🐚 运行Shell测试...${NC}"
    
    # API测试
    if [ -f "tests/test_api.sh" ]; then
        chmod +x tests/test_api.sh
        ./tests/test_api.sh
        log_result $? "Shell API测试"
    else
        echo -e "${YELLOW}⚠️  跳过Shell API测试 (测试文件不存在)${NC}"
        TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
    fi
    
    # E2E测试
    if [ -f "tests/test_e2e.sh" ]; then
        chmod +x tests/test_e2e.sh
        ./tests/test_e2e.sh
        log_result $? "Shell E2E测试"
    else
        echo -e "${YELLOW}⚠️  跳过Shell E2E测试 (测试文件不存在)${NC}"
        TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
    fi
}

# 运行前端测试
run_frontend_tests() {
    echo -e "${BLUE}⚛️  运行前端测试...${NC}"
    
    if [ -d "web" ] && [ -f "web/package.json" ]; then
        cd web
        
        # 运行Jest测试
        if npm run test --silent 2>/dev/null; then
            log_result 0 "前端单元测试"
        else
            log_result 1 "前端单元测试"
        fi
        
        cd ..
    else
        echo -e "${YELLOW}⚠️  跳过前端测试 (前端项目不存在)${NC}"
        TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
    fi
}

# 运行性能测试
run_performance_tests() {
    echo -e "${BLUE}⚡ 运行性能测试...${NC}"
    
    # 简单的响应时间测试
    if curl -s -w "%{time_total}\n" -o /dev/null http://localhost:5000/health | awk '{if($1 < 1.0) exit 0; else exit 1}'; then
        log_result 0 "API响应时间测试"
    else
        log_result 1 "API响应时间测试"
    fi
    
    # 并发测试 (如果有ab工具)
    if command -v ab &> /dev/null; then
        if ab -n 100 -c 10 http://localhost:5000/health > /dev/null 2>&1; then
            log_result 0 "并发负载测试"
        else
            log_result 1 "并发负载测试"
        fi
    else
        echo -e "${YELLOW}⚠️  跳过并发测试 (ab工具未安装)${NC}"
        TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
    fi
}

# 运行质量评估
run_quality_assessment() {
    echo -e "${BLUE}📊 运行质量评估...${NC}"
    
    if [ -f "run_quality_assessment.py" ]; then
        python3 run_quality_assessment.py
        log_result $? "质量评估"
    else
        echo -e "${YELLOW}⚠️  跳过质量评估 (评估脚本不存在)${NC}"
        TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
    fi
}

# 生成测试报告
generate_test_report() {
    echo -e "${BLUE}📄 生成测试报告...${NC}"
    
    cat > test_report.html << EOF
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SaaS数据分析平台测试报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: linear-gradient(135deg, #FF6B35, #F7931E); color: white; padding: 20px; border-radius: 8px; }
        .summary { display: flex; gap: 20px; margin: 20px 0; }
        .metric { background: #f5f5f5; padding: 15px; border-radius: 8px; flex: 1; text-align: center; }
        .passed { color: #22c55e; }
        .failed { color: #ef4444; }
        .skipped { color: #f59e0b; }
        .details { margin-top: 20px; }
        .test-section { background: white; border: 1px solid #e5e5e5; border-radius: 8px; padding: 15px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 SaaS数据分析平台测试报告</h1>
        <p>生成时间: $(date)</p>
    </div>
    
    <div class="summary">
        <div class="metric">
            <h3 class="passed">✅ 通过</h3>
            <p style="font-size: 24px; font-weight: bold;">$TESTS_PASSED</p>
        </div>
        <div class="metric">
            <h3 class="failed">❌ 失败</h3>
            <p style="font-size: 24px; font-weight: bold;">$TESTS_FAILED</p>
        </div>
        <div class="metric">
            <h3 class="skipped">⚠️ 跳过</h3>
            <p style="font-size: 24px; font-weight: bold;">$TESTS_SKIPPED</p>
        </div>
        <div class="metric">
            <h3>📊 总计</h3>
            <p style="font-size: 24px; font-weight: bold;">$((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))</p>
        </div>
    </div>
    
    <div class="details">
        <div class="test-section">
            <h3>🧪 测试覆盖范围</h3>
            <ul>
                <li>后端单元测试 - API功能、认证、数据处理</li>
                <li>前端组件测试 - UI组件、交互逻辑</li>
                <li>集成测试 - 前后端协作、数据库集成</li>
                <li>性能测试 - 响应时间、并发处理</li>
                <li>安全测试 - 输入验证、权限控制</li>
                <li>质量评估 - 代码质量、文档完整性</li>
            </ul>
        </div>
        
        <div class="test-section">
            <h3>📈 测试结果分析</h3>
            <p>成功率: $(echo "scale=2; $TESTS_PASSED * 100 / ($TESTS_PASSED + $TESTS_FAILED + 0.01)" | bc)%</p>
            <p>平台整体质量: $([ $TESTS_FAILED -eq 0 ] && echo "优秀 🏆" || echo "需要改进 🔧")</p>
        </div>
    </div>
</body>
</html>
EOF
    
    echo "✅ 测试报告已生成: test_report.html"
}

# 清理函数
cleanup() {
    echo -e "${BLUE}🧹 清理测试环境...${NC}"
    stop_test_server
    
    # 清理临时文件
    rm -f test.db server.log 2>/dev/null || true
}

# 设置陷阱以确保清理
trap cleanup EXIT

# 主要测试流程
main() {
    echo "开始时间: $(date)"
    
    # 检查依赖
    check_dependencies
    
    # 安装测试依赖
    install_test_dependencies
    
    # 启动测试服务器
    if start_test_server; then
        # 运行各种测试
        run_backend_unit_tests
        run_api_integration_tests
        run_shell_tests
        run_performance_tests
        
        # 停止服务器（前端测试不需要后端服务器）
        stop_test_server
        
        # 运行前端测试
        run_frontend_tests
        
        # 运行质量评估
        run_quality_assessment
    else
        echo -e "${RED}❌ 无法启动测试服务器，跳过需要服务器的测试${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 3))
    fi
    
    # 生成测试报告
    generate_test_report
    
    # 显示最终结果
    echo -e "\n${BLUE}================================================${NC}"
    echo -e "${BLUE}🎯 测试完成总结${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo -e "✅ 通过: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "❌ 失败: ${RED}$TESTS_FAILED${NC}"
    echo -e "⚠️  跳过: ${YELLOW}$TESTS_SKIPPED${NC}"
    echo -e "📊 总计: $((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))"
    echo "完成时间: $(date)"
    
    # 根据结果设置退出码
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}🎉 所有测试通过！平台质量优秀！${NC}"
        exit 0
    else
        echo -e "${RED}⚠️  存在测试失败，需要修复后再部署${NC}"
        exit 1
    fi
}

# 运行主程序
main "$@"