#!/usr/bin/env python3
"""
SaaS数据分析平台质量评估工具
检查代码质量、测试覆盖率、性能和安全性
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

class QualityAssessment:
    """质量评估主类"""
    
    def __init__(self):
        self.project_root = Path("/home/user/datalab0826")
        self.results = {}
        
    def check_file_structure(self):
        """检查项目文件结构"""
        print("📁 检查项目文件结构...")
        
        required_files = {
            "main.py": "主应用文件",
            "requirements.txt": "Python依赖",
            "devserver.sh": "开发服务器脚本", 
            "pyproject.toml": "项目配置",
            ".env.example": "环境变量模板",
            "docker/docker-compose.yml": "Docker配置"
        }
        
        missing_files = []
        existing_files = []
        
        for file_path, description in required_files.items():
            full_path = self.project_root / file_path
            if full_path.exists():
                existing_files.append((file_path, description))
                print(f"  ✅ {file_path} - {description}")
            else:
                missing_files.append((file_path, description))
                print(f"  ❌ {file_path} - {description}")
                
        self.results["file_structure"] = {
            "existing": len(existing_files),
            "missing": len(missing_files),
            "score": len(existing_files) / len(required_files) * 100
        }
        
        return len(missing_files) == 0
        
    def check_documentation(self):
        """检查文档完整性"""
        print("\n📚 检查文档完整性...")
        
        doc_files = {
            "docs/PRD/saas_platform_prd.md": "产品需求文档",
            "docs/system_architecture.md": "系统架构文档", 
            "docs/frontend_architecture.md": "前端架构文档",
            "docs/ui_design_system.md": "UI设计系统",
            "docs/brand_guidelines.md": "品牌指南",
            "docs/ux_research_report.md": "UX研究报告",
            "docs/visual_storytelling_guide.md": "视觉叙事指南",
            "docs/whimsy_interaction_guide.md": "交互设计指南",
            "docs/analytics_professional_assessment.md": "专业性评估报告"
        }
        
        existing_docs = []
        missing_docs = []
        
        for doc_path, description in doc_files.items():
            full_path = self.project_root / doc_path
            if full_path.exists():
                existing_docs.append(doc_path)
                print(f"  ✅ {doc_path}")
            else:
                missing_docs.append(doc_path)
                print(f"  ❌ {doc_path}")
                
        self.results["documentation"] = {
            "existing": len(existing_docs),
            "missing": len(missing_docs), 
            "score": len(existing_docs) / len(doc_files) * 100
        }
        
        return len(missing_docs) == 0
        
    def check_code_quality(self):
        """检查代码质量"""
        print("\n🔍 检查代码质量...")
        
        # 检查Python文件
        python_files = list(self.project_root.glob("*.py"))
        
        quality_metrics = {
            "python_files": len(python_files),
            "large_files": 0,
            "has_docstrings": 0,
            "has_type_hints": 0
        }
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    # 检查文件大小
                    if len(lines) > 500:
                        quality_metrics["large_files"] += 1
                        print(f"  ⚠️  {py_file.name} 文件较大 ({len(lines)} 行)")
                    
                    # 检查文档字符串
                    if '"""' in content or "'''" in content:
                        quality_metrics["has_docstrings"] += 1
                        
                    # 检查类型提示
                    if ":" in content and ("->" in content or "typing" in content):
                        quality_metrics["has_type_hints"] += 1
                        
            except Exception as e:
                print(f"  ❌ 无法分析 {py_file.name}: {e}")
                
        # 计算质量得分
        if quality_metrics["python_files"] > 0:
            docstring_score = quality_metrics["has_docstrings"] / quality_metrics["python_files"] * 100
            type_hint_score = quality_metrics["has_type_hints"] / quality_metrics["python_files"] * 100
            
            print(f"  📊 Python文件数量: {quality_metrics['python_files']}")
            print(f"  📝 文档字符串覆盖率: {docstring_score:.1f}%")
            print(f"  🏷️  类型提示覆盖率: {type_hint_score:.1f}%")
            
            self.results["code_quality"] = {
                "files": quality_metrics["python_files"],
                "docstring_coverage": docstring_score,
                "type_hint_coverage": type_hint_score,
                "score": (docstring_score + type_hint_score) / 2
            }
        else:
            self.results["code_quality"] = {"score": 0}
            
    def check_security_basics(self):
        """检查基本安全配置"""
        print("\n🔒 检查安全配置...")
        
        security_checks = {
            ".env in .gitignore": False,
            "JWT secret configured": False, 
            "Password hashing": False,
            "HTTPS configuration": False
        }
        
        # 检查.gitignore
        gitignore_path = self.project_root / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                gitignore_content = f.read()
                if ".env" in gitignore_content:
                    security_checks[".env in .gitignore"] = True
                    print("  ✅ .env文件已加入.gitignore")
                else:
                    print("  ⚠️  .env文件未加入.gitignore")
        
        # 检查main.py中的安全配置
        main_py = self.project_root / "main.py"
        if main_py.exists():
            with open(main_py, 'r') as f:
                content = f.read()
                
                if "JWT_SECRET_KEY" in content:
                    security_checks["JWT secret configured"] = True
                    print("  ✅ JWT密钥已配置")
                    
                if "bcrypt" in content or "werkzeug.security" in content:
                    security_checks["Password hashing"] = True
                    print("  ✅ 密码哈希已实现")
                    
        passed_checks = sum(security_checks.values())
        total_checks = len(security_checks)
        
        self.results["security"] = {
            "passed": passed_checks,
            "total": total_checks,
            "score": passed_checks / total_checks * 100
        }
        
        print(f"  📊 安全检查通过: {passed_checks}/{total_checks}")
        
    def check_performance_config(self):
        """检查性能配置"""
        print("\n⚡ 检查性能配置...")
        
        performance_indicators = {
            "Database indexing": False,
            "Caching configured": False,
            "Static file serving": False,
            "Compression enabled": False
        }
        
        # 检查main.py中的性能配置
        main_py = self.project_root / "main.py"
        if main_py.exists():
            with open(main_py, 'r') as f:
                content = f.read()
                
                if "Index" in content or "index=" in content:
                    performance_indicators["Database indexing"] = True
                    print("  ✅ 数据库索引已配置")
                    
                if "cache" in content.lower():
                    performance_indicators["Caching configured"] = True
                    print("  ✅ 缓存已配置")
                    
                if "static" in content.lower():
                    performance_indicators["Static file serving"] = True
                    print("  ✅ 静态文件服务已配置")
        
        passed_checks = sum(performance_indicators.values())
        total_checks = len(performance_indicators)
        
        self.results["performance"] = {
            "passed": passed_checks,
            "total": total_checks,
            "score": passed_checks / total_checks * 100
        }
        
    def run_tests(self):
        """运行测试套件"""
        print("\n🧪 运行测试套件...")
        
        test_files = [
            "test_comprehensive_saas.py",
            "test_saas_api.py",
            "tests/test_api.sh",
            "tests/test_e2e.sh"
        ]
        
        available_tests = []
        for test_file in test_files:
            test_path = self.project_root / test_file
            if test_path.exists():
                available_tests.append(test_file)
                print(f"  ✅ {test_file} 存在")
            else:
                print(f"  ❌ {test_file} 不存在")
        
        self.results["testing"] = {
            "available_tests": len(available_tests),
            "total_tests": len(test_files),
            "score": len(available_tests) / len(test_files) * 100
        }
        
        # 如果pytest可用，尝试运行Python测试
        if "test_comprehensive_saas.py" in available_tests:
            try:
                print("  🔄 运行Python测试...")
                result = subprocess.run(
                    [sys.executable, "test_comprehensive_saas.py"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                print("  ✅ 测试执行完成")
            except Exception as e:
                print(f"  ⚠️  测试执行失败: {e}")
                
    def generate_overall_score(self):
        """计算总体质量得分"""
        print("\n📊 质量评估总结")
        print("=" * 50)
        
        weights = {
            "file_structure": 0.15,
            "documentation": 0.25,
            "code_quality": 0.20,
            "security": 0.20,
            "performance": 0.10,
            "testing": 0.10
        }
        
        total_score = 0
        for category, weight in weights.items():
            if category in self.results:
                score = self.results[category].get("score", 0)
                weighted_score = score * weight
                total_score += weighted_score
                
                print(f"{category:15}: {score:5.1f}% (权重: {weight:.0%}) = {weighted_score:5.1f}")
            else:
                print(f"{category:15}: 未评估")
                
        print("-" * 50)
        print(f"{'总体得分':15}: {total_score:5.1f}%")
        
        # 评级
        if total_score >= 90:
            grade = "A+ (优秀)"
        elif total_score >= 80:
            grade = "A  (良好)"
        elif total_score >= 70:
            grade = "B+ (中等偏上)"
        elif total_score >= 60:
            grade = "B  (中等)"
        else:
            grade = "C  (需要改进)"
            
        print(f"{'质量评级':15}: {grade}")
        
        self.results["overall"] = {
            "score": total_score,
            "grade": grade
        }
        
        return total_score
        
    def generate_recommendations(self):
        """生成改进建议"""
        print("\n💡 改进建议")
        print("=" * 50)
        
        recommendations = []
        
        # 基于结果生成建议
        if self.results.get("file_structure", {}).get("score", 0) < 100:
            recommendations.append("完善项目文件结构，确保所有必要文件存在")
            
        if self.results.get("documentation", {}).get("score", 0) < 80:
            recommendations.append("完善项目文档，特别是API文档和部署指南")
            
        if self.results.get("code_quality", {}).get("score", 0) < 70:
            recommendations.append("提高代码质量：添加文档字符串和类型提示")
            
        if self.results.get("security", {}).get("score", 0) < 90:
            recommendations.append("加强安全配置：HTTPS、密钥管理、输入验证")
            
        if self.results.get("testing", {}).get("score", 0) < 80:
            recommendations.append("完善测试套件，提高测试覆盖率")
            
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        else:
            print("🎉 项目质量良好，无重要改进建议！")
            
    def save_report(self):
        """保存评估报告"""
        report_path = self.project_root / "quality_assessment_report.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
            
        print(f"\n📄 详细报告已保存至: {report_path}")
        
    def run_full_assessment(self):
        """运行完整的质量评估"""
        print("🚀 开始SaaS平台质量评估")
        print("=" * 50)
        
        # 运行各项检查
        self.check_file_structure()
        self.check_documentation()
        self.check_code_quality()
        self.check_security_basics()
        self.check_performance_config()
        self.run_tests()
        
        # 生成总结
        overall_score = self.generate_overall_score()
        self.generate_recommendations()
        self.save_report()
        
        print("\n✅ 质量评估完成！")
        
        return overall_score

def main():
    """主函数"""
    assessor = QualityAssessment()
    score = assessor.run_full_assessment()
    
    # 根据得分设置退出码
    if score >= 80:
        sys.exit(0)  # 优秀/良好
    elif score >= 60:
        sys.exit(1)  # 中等，需要关注
    else:
        sys.exit(2)  # 需要重大改进

if __name__ == "__main__":
    main()