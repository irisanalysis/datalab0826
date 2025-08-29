#!/usr/bin/env python3
"""
数据实验室功能验证脚本
全面验证Flask应用的各项功能和配置
"""
import os
import sys
import subprocess
import requests
import time
from pathlib import Path
from typing import Dict, List, Tuple
import json
from datetime import datetime

class DataLabValidator:
    def __init__(self):
        self.test_results = []
        self.errors = []
        self.warnings = []
        self.project_root = Path.cwd()
    
    def log_result(self, test_name: str, passed: bool, message: str = "", 
                  error: str = "", warning: str = ""):
        """记录测试结果"""
        result = {
            'test': test_name,
            'passed': passed,
            'message': message,
            'error': error,
            'warning': warning,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if error:
            self.errors.append(f"{test_name}: {error}")
        if warning:
            self.warnings.append(f"{test_name}: {warning}")
    
    def print_status(self, message: str, status: str = "info"):
        """打印状态消息"""
        symbols = {"info": "🔍", "success": "✅", "error": "❌", "warning": "⚠️"}
        print(f"{symbols.get(status, '🔍')} {message}")
    
    def validate_project_structure(self) -> bool:
        """验证项目结构"""
        self.print_status("验证项目结构...")
        
        required_files = [
            'main.py',
            'src/index.html',
            'pyproject.toml',
            'devserver.sh',
            'CLAUDE.md'
        ]
        
        optional_files = [
            'README.md',
            '.env',
            '.gitignore',
            'requirements.txt'
        ]
        
        all_passed = True
        
        for file_path in required_files:
            file_obj = self.project_root / file_path
            if file_obj.exists():
                self.log_result(f"文件检查: {file_path}", True, f"文件存在")
                self.print_status(f"必需文件 {file_path} 存在", "success")
            else:
                self.log_result(f"文件检查: {file_path}", False, error=f"必需文件缺失")
                self.print_status(f"必需文件 {file_path} 缺失", "error")
                all_passed = False
        
        for file_path in optional_files:
            file_obj = self.project_root / file_path
            if file_obj.exists():
                self.print_status(f"可选文件 {file_path} 存在", "success")
            else:
                self.log_result(f"可选文件检查: {file_path}", True, 
                              warning=f"可选文件不存在，可以考虑创建")
        
        return all_passed
    
    def validate_dependencies(self) -> bool:
        """验证依赖和环境"""
        self.print_status("验证依赖和环境...")
        
        # 检查uv是否可用
        try:
            result = subprocess.run(['uv', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_result("uv版本检查", True, f"uv可用: {result.stdout.strip()}")
                self.print_status(f"uv可用: {result.stdout.strip()}", "success")
            else:
                self.log_result("uv版本检查", False, error="uv不可用")
                self.print_status("uv不可用", "error")
                return False
        except Exception as e:
            self.log_result("uv版本检查", False, error=f"检查uv时出错: {e}")
            self.print_status(f"检查uv时出错: {e}", "error")
            return False
        
        # 检查Python依赖
        try:
            result = subprocess.run(['uv', 'pip', 'list'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                dependencies = result.stdout
                self.log_result("依赖列表", True, f"成功获取依赖列表")
                self.print_status("Python依赖检查通过", "success")
                
                # 检查Flask是否安装
                if 'flask' in dependencies.lower():
                    self.print_status("Flask已安装", "success")
                else:
                    self.log_result("Flask检查", False, 
                                  warning="Flask可能未安装，请检查依赖配置")
                    self.print_status("Flask可能未安装", "warning")
            else:
                self.log_result("依赖检查", False, error="无法获取依赖列表")
                self.print_status("依赖检查失败", "error")
                return False
                
        except Exception as e:
            self.log_result("依赖检查", False, error=f"依赖检查出错: {e}")
            self.print_status(f"依赖检查出错: {e}", "error")
            return False
        
        return True
    
    def validate_flask_app(self) -> bool:
        """验证Flask应用"""
        self.print_status("验证Flask应用...")
        
        # 检查main.py内容
        main_py = self.project_root / 'main.py'
        try:
            with open(main_py, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'from flask import Flask' in content:
                self.log_result("Flask导入检查", True, "Flask已正确导入")
                self.print_status("Flask已正确导入", "success")
            else:
                self.log_result("Flask导入检查", False, warning="未发现Flask导入")
                self.print_status("未发现Flask导入", "warning")
            
            if 'app = Flask(__name__)' in content:
                self.log_result("Flask实例检查", True, "Flask实例已创建")
                self.print_status("Flask实例已创建", "success")
            else:
                self.log_result("Flask实例检查", False, warning="未发现Flask实例创建")
                self.print_status("未发现Flask实例创建", "warning")
                
        except Exception as e:
            self.log_result("Flask应用检查", False, error=f"读取main.py失败: {e}")
            self.print_status(f"读取main.py失败: {e}", "error")
            return False
        
        return True
    
    def validate_html_content(self) -> bool:
        """验证HTML内容"""
        self.print_status("验证HTML内容...")
        
        html_file = self.project_root / 'src' / 'index.html'
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '<html' in content.lower():
                self.log_result("HTML结构检查", True, "发现HTML标签")
                self.print_status("HTML结构正常", "success")
            else:
                self.log_result("HTML结构检查", False, warning="未发现HTML标签")
                self.print_status("HTML结构可能有问题", "warning")
            
            if '<title>' in content.lower():
                self.print_status("包含页面标题", "success")
            else:
                self.log_result("页面标题检查", True, warning="未发现页面标题")
                self.print_status("建议添加页面标题", "warning")
            
            # 检查文件大小
            size = len(content)
            self.log_result("HTML大小检查", True, f"HTML文件大小: {size} 字符")
            self.print_status(f"HTML文件大小: {size} 字符", "success")
            
        except Exception as e:
            self.log_result("HTML内容检查", False, error=f"读取HTML文件失败: {e}")
            self.print_status(f"读取HTML文件失败: {e}", "error")
            return False
        
        return True
    
    def validate_scripts_directory(self) -> bool:
        """验证脚本目录"""
        self.print_status("验证.scripts目录...")
        
        scripts_dir = self.project_root / '.scripts'
        if not scripts_dir.exists():
            self.log_result("脚本目录检查", False, warning="scripts目录不存在")
            self.print_status("scripts目录不存在，建议运行设置脚本", "warning")
            return True  # 不影响核心功能
        
        subdirs = ['setup', 'testing', 'auth-fixes', 'utils']
        for subdir in subdirs:
            subdir_path = scripts_dir / subdir
            if subdir_path.exists():
                self.print_status(f"脚本子目录 {subdir} 存在", "success")
            else:
                self.log_result(f"脚本子目录检查: {subdir}", True, 
                              warning=f"子目录 {subdir} 不存在")
        
        return True
    
    def run_functional_test(self) -> bool:
        """运行功能测试"""
        self.print_status("运行功能测试...")
        
        test_port = "8889"
        env = os.environ.copy()
        env['PORT'] = test_port
        
        try:
            # 启动Flask应用
            self.print_status(f"启动测试服务器，端口: {test_port}")
            process = subprocess.Popen(
                ['uv', 'run', 'python', 'main.py'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 等待服务启动
            time.sleep(4)
            
            # 测试主页
            try:
                response = requests.get(f'http://localhost:{test_port}/', timeout=10)
                if response.status_code == 200:
                    self.log_result("主页访问测试", True, 
                                  f"状态码: {response.status_code}, "
                                  f"响应长度: {len(response.text)}")
                    self.print_status("主页访问测试通过", "success")
                    return True
                else:
                    self.log_result("主页访问测试", False, 
                                  error=f"状态码异常: {response.status_code}")
                    self.print_status(f"主页访问异常，状态码: {response.status_code}", "error")
                    return False
                    
            except requests.RequestException as e:
                self.log_result("主页访问测试", False, error=f"请求失败: {e}")
                self.print_status(f"主页访问失败: {e}", "error")
                return False
            
        except Exception as e:
            self.log_result("功能测试", False, error=f"启动服务器失败: {e}")
            self.print_status(f"启动服务器失败: {e}", "error")
            return False
        finally:
            # 清理：停止服务器
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
    
    def generate_report(self) -> str:
        """生成验证报告"""
        passed = sum(1 for r in self.test_results if r['passed'])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        report = f"""
📊 数据实验室验证报告
{'=' * 50}
测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
总测试项: {total}
通过项目: {passed}
失败项目: {total - passed}
成功率: {success_rate:.1f}%

🔍 详细结果:
{'-' * 30}
"""
        
        for result in self.test_results:
            status_symbol = "✅" if result['passed'] else "❌"
            report += f"{status_symbol} {result['test']}"
            if result['message']:
                report += f" - {result['message']}"
            if result['error']:
                report += f" [错误: {result['error']}]"
            if result['warning']:
                report += f" [警告: {result['warning']}]"
            report += "\n"
        
        if self.errors:
            report += f"\n❌ 错误汇总 ({len(self.errors)}项):\n"
            for error in self.errors:
                report += f"  • {error}\n"
        
        if self.warnings:
            report += f"\n⚠️ 警告汇总 ({len(self.warnings)}项):\n"
            for warning in self.warnings:
                report += f"  • {warning}\n"
        
        # 建议
        report += f"\n💡 建议:\n"
        if self.errors:
            report += "  • 优先解决错误项目，确保核心功能正常\n"
        if self.warnings:
            report += "  • 考虑处理警告项目，提升项目完整性\n"
        
        if success_rate >= 90:
            report += "  • 项目状态良好，可以正常使用\n"
        elif success_rate >= 70:
            report += "  • 项目基本可用，建议修复部分问题\n"
        else:
            report += "  • 项目存在较多问题，建议全面检查\n"
        
        report += f"\n🚀 启动应用:\n"
        report += f"  开发模式: ./devserver.sh\n"
        report += f"  生产模式: uv run python main.py\n"
        
        return report
    
    def run_all_validations(self) -> bool:
        """运行所有验证"""
        self.print_status("开始全面验证数据实验室功能...", "info")
        print("=" * 50)
        
        validations = [
            ("项目结构验证", self.validate_project_structure),
            ("依赖环境验证", self.validate_dependencies),
            ("Flask应用验证", self.validate_flask_app),
            ("HTML内容验证", self.validate_html_content),
            ("脚本目录验证", self.validate_scripts_directory),
            ("功能测试", self.run_functional_test)
        ]
        
        overall_success = True
        for name, validation_func in validations:
            try:
                success = validation_func()
                if not success:
                    overall_success = False
            except Exception as e:
                self.log_result(name, False, error=f"验证过程异常: {e}")
                self.print_status(f"{name} 验证异常: {e}", "error")
                overall_success = False
            
            print()  # 空行分隔
        
        return overall_success

def main():
    """主函数"""
    validator = DataLabValidator()
    
    try:
        # 运行验证
        overall_success = validator.run_all_validations()
        
        # 生成报告
        report = validator.generate_report()
        print(report)
        
        # 保存报告
        report_file = Path(".scripts/validation_report.txt")
        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"\n📄 验证报告已保存到: {report_file}")
        
        return overall_success
        
    except KeyboardInterrupt:
        print("\n⚠️ 验证被用户中断")
        return False
    except Exception as e:
        print(f"❌ 验证过程发生错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)