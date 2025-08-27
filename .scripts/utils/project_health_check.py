#!/usr/bin/env python3
"""
项目健康检查工具
快速检查项目的整体健康状况
"""
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def check_git_status():
    """检查Git状态"""
    print("🔍 Git状态检查...")
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            changes = result.stdout.strip()
            if changes:
                print("⚠️ 有未提交的更改:")
                for line in changes.split('\n')[:5]:  # 只显示前5行
                    print(f"  {line}")
                if len(changes.split('\n')) > 5:
                    print(f"  ... 还有 {len(changes.split('\n')) - 5} 个文件")
            else:
                print("✅ 工作区干净")
        else:
            print("⚠️ 不是Git仓库或Git命令失败")
    except Exception as e:
        print(f"❌ Git检查失败: {e}")

def check_disk_space():
    """检查磁盘空间"""
    print("💾 磁盘空间检查...")
    try:
        import shutil
        total, used, free = shutil.disk_usage('.')
        
        # 转换为GB
        total_gb = total / (1024**3)
        used_gb = used / (1024**3)
        free_gb = free / (1024**3)
        usage_percent = (used / total) * 100
        
        print(f"  总空间: {total_gb:.1f} GB")
        print(f"  已使用: {used_gb:.1f} GB ({usage_percent:.1f}%)")
        print(f"  剩余空间: {free_gb:.1f} GB")
        
        if free_gb < 1:
            print("❌ 磁盘空间不足 (< 1GB)")
        elif free_gb < 5:
            print("⚠️ 磁盘空间较低 (< 5GB)")
        else:
            print("✅ 磁盘空间充足")
            
    except Exception as e:
        print(f"❌ 磁盘检查失败: {e}")

def check_project_size():
    """检查项目大小"""
    print("📁 项目大小检查...")
    try:
        def get_dir_size(path):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                # 跳过一些大的目录
                if any(skip in dirpath for skip in ['.git', 'node_modules', '__pycache__', '.venv']):
                    continue
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
            return total_size
        
        project_size = get_dir_size('.')
        size_mb = project_size / (1024**2)
        
        print(f"  项目大小: {size_mb:.1f} MB")
        
        if size_mb > 1000:
            print("⚠️ 项目较大，考虑清理不必要的文件")
        else:
            print("✅ 项目大小合理")
            
    except Exception as e:
        print(f"❌ 项目大小检查失败: {e}")

def check_python_environment():
    """检查Python环境"""
    print("🐍 Python环境检查...")
    
    # Python版本
    print(f"  Python版本: {sys.version.split()[0]}")
    
    # 虚拟环境
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 在虚拟环境中运行")
    else:
        print("⚠️ 未在虚拟环境中运行")
    
    # uv检查
    try:
        result = subprocess.run(['uv', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ uv版本: {result.stdout.strip()}")
        else:
            print("❌ uv不可用")
    except:
        print("❌ uv不可用")

def check_common_issues():
    """检查常见问题"""
    print("🔧 常见问题检查...")
    
    issues = []
    
    # 检查.env文件
    if Path('.env').exists():
        print("✅ 发现.env配置文件")
    else:
        issues.append("未发现.env配置文件")
    
    # 检查关键文件权限
    scripts = list(Path('.scripts').glob('**/*.sh')) if Path('.scripts').exists() else []
    executable_scripts = [s for s in scripts if os.access(s, os.X_OK)]
    
    if scripts:
        print(f"  发现 {len(scripts)} 个shell脚本")
        print(f"  其中 {len(executable_scripts)} 个可执行")
        if len(executable_scripts) < len(scripts):
            issues.append("部分脚本缺少执行权限")
    
    # 检查端口占用
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', 80))
            if result == 0:
                issues.append("端口80已被占用")
    except:
        pass
    
    if issues:
        print("⚠️ 发现问题:")
        for issue in issues:
            print(f"  • {issue}")
    else:
        print("✅ 未发现常见问题")

def generate_health_summary():
    """生成健康摘要"""
    print("\n" + "="*50)
    print("📊 健康检查摘要")
    print("="*50)
    
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"工作目录: {os.getcwd()}")
    
    # 项目基础信息
    essential_files = ['main.py', 'pyproject.toml', 'CLAUDE.md']
    existing_files = [f for f in essential_files if Path(f).exists()]
    
    print(f"\n核心文件: {len(existing_files)}/{len(essential_files)} 存在")
    for f in essential_files:
        status = "✅" if Path(f).exists() else "❌"
        print(f"  {status} {f}")
    
    print(f"\n💡 建议:")
    if len(existing_files) == len(essential_files):
        print("  • 项目结构完整，运行 ./devserver.sh 启动开发服务器")
        print("  • 运行验证脚本: uv run python .scripts/validate_analysis_feature.py")
    else:
        print("  • 项目文件不完整，请检查缺失的文件")
        print("  • 运行设置脚本: .scripts/setup/setup.sh")

def main():
    """主函数"""
    print("🚀 数据实验室项目健康检查")
    print("="*50)
    
    try:
        check_python_environment()
        print()
        
        check_git_status()
        print()
        
        check_disk_space()
        print()
        
        check_project_size()
        print()
        
        check_common_issues()
        
        generate_health_summary()
        
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️ 健康检查被用户中断")
        return False
    except Exception as e:
        print(f"❌ 健康检查发生错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)