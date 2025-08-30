#!/usr/bin/env python3
"""
Backend Quality Assessment Tool
Migrated and adapted from root run_quality_assessment.py
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Any, List

class BackendQualityAssessment:
    """Backend Quality Assessment Tool"""
    
    def __init__(self):
        self.backend_root = Path(__file__).parent.parent  # backend directory
        self.project_root = self.backend_root.parent      # project root
        self.results = {}
        
    def check_backend_structure(self):
        """Check backend directory structure"""
        print("📁 Checking backend structure...")
        
        required_structure = {
            "apps/": "Microservice applications",
            "apps/api_gateway/": "API Gateway service",
            "apps/data_service/": "Data management service", 
            "apps/legacy_flask/": "Legacy Flask compatibility",
            "shared/": "Shared modules",
            "shared/database/": "Database models and connections",
            "shared/utils/": "Utility functions",
            "scripts/": "Database and maintenance scripts",
            "tests/": "Test suites",
            "requirements.txt": "Python dependencies",
            "pyproject.toml": "Project configuration",
            ".env.example": "Environment template"
        }
        
        missing_items = []
        existing_items = []
        
        for item_path, description in required_structure.items():
            full_path = self.backend_root / item_path
            if full_path.exists():
                existing_items.append((item_path, description))
                print(f"  ✅ {item_path} - {description}")
            else:
                missing_items.append((item_path, description))
                print(f"  ❌ {item_path} - {description}")
        
        score = len(existing_items) / len(required_structure) * 100
        self.results["backend_structure"] = {
            "existing": len(existing_items),
            "missing": len(missing_items),
            "score": score
        }
        
        print(f"Backend Structure Score: {score:.1f}%")
        
    def check_python_code_quality(self):
        """Check Python code quality with basic analysis"""
        print("🐍 Checking Python code quality...")
        
        python_files = list(self.backend_root.glob("**/*.py"))
        
        issues = {
            "syntax_errors": [],
            "import_errors": [],
            "style_warnings": []
        }
        
        for py_file in python_files:
            try:
                # Basic syntax check
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()
                    compile(source, str(py_file), 'exec')
                    
                # Check for common issues
                if 'import *' in source:
                    issues["style_warnings"].append(f"{py_file}: Wildcard import detected")
                
                if 'print(' in source and 'debug' not in str(py_file).lower():
                    issues["style_warnings"].append(f"{py_file}: Print statement in non-debug code")
                    
            except SyntaxError as e:
                issues["syntax_errors"].append(f"{py_file}: {str(e)}")
            except Exception as e:
                issues["import_errors"].append(f"{py_file}: {str(e)}")
        
        total_issues = sum(len(issue_list) for issue_list in issues.values())
        quality_score = max(0, 100 - (total_issues * 5))  # Deduct 5 points per issue
        
        self.results["code_quality"] = {
            "files_checked": len(python_files),
            "issues": issues,
            "total_issues": total_issues,
            "score": quality_score
        }
        
        print(f"  Python files checked: {len(python_files)}")
        print(f"  Total issues found: {total_issues}")
        print(f"Code Quality Score: {quality_score:.1f}%")
        
    def check_dependencies(self):
        """Check dependency management"""
        print("📦 Checking dependencies...")
        
        issues = []
        score = 100
        
        # Check requirements.txt
        req_file = self.backend_root / "requirements.txt"
        if req_file.exists():
            print("  ✅ requirements.txt exists")
            try:
                with open(req_file) as f:
                    deps = f.readlines()
                    print(f"  ✅ {len(deps)} dependencies listed")
            except Exception as e:
                issues.append(f"requirements.txt read error: {str(e)}")
                score -= 20
        else:
            issues.append("requirements.txt missing")
            score -= 30
        
        # Check pyproject.toml
        pyproject_file = self.backend_root / "pyproject.toml"
        if pyproject_file.exists():
            print("  ✅ pyproject.toml exists")
        else:
            issues.append("pyproject.toml missing")
            score -= 20
        
        # Check for virtual environment indicators
        if (self.backend_root / "venv").exists() or (self.backend_root / ".venv").exists():
            print("  ✅ Virtual environment detected")
        else:
            print("  ⚠️  No virtual environment detected")
            score -= 10
        
        self.results["dependencies"] = {
            "issues": issues,
            "score": max(0, score)
        }
        
        print(f"Dependencies Score: {max(0, score):.1f}%")
        
    def check_security_basics(self):
        """Check basic security practices"""
        print("🔒 Checking security basics...")
        
        issues = []
        score = 100
        
        # Check for .env.example
        env_example = self.backend_root / ".env.example"
        if env_example.exists():
            print("  ✅ .env.example exists")
        else:
            issues.append(".env.example missing")
            score -= 20
        
        # Check for hardcoded secrets in code
        python_files = list(self.backend_root.glob("**/*.py"))
        secret_patterns = ['password', 'secret', 'key', 'token']
        
        hardcoded_secrets = []
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    for pattern in secret_patterns:
                        if f'{pattern} = "' in content or f"{pattern} = '" in content:
                            hardcoded_secrets.append(f"{py_file}: Potential hardcoded {pattern}")
            except:
                continue
        
        if hardcoded_secrets:
            print(f"  ⚠️  {len(hardcoded_secrets)} potential hardcoded secrets found")
            score -= len(hardcoded_secrets) * 10
            issues.extend(hardcoded_secrets[:5])  # Show first 5
        else:
            print("  ✅ No obvious hardcoded secrets detected")
        
        self.results["security"] = {
            "issues": issues,
            "hardcoded_secrets": len(hardcoded_secrets),
            "score": max(0, score)
        }
        
        print(f"Security Score: {max(0, score):.1f}%")
        
    def check_testing_setup(self):
        """Check testing configuration"""
        print("🧪 Checking testing setup...")
        
        score = 0
        
        # Check for tests directory
        tests_dir = self.backend_root / "tests"
        if tests_dir.exists():
            print("  ✅ tests/ directory exists")
            score += 30
            
            # Check for different test types
            if (tests_dir / "unit").exists():
                print("  ✅ unit tests directory exists")
                score += 20
            if (tests_dir / "integration").exists():
                print("  ✅ integration tests directory exists")
                score += 20
            
            # Count test files
            test_files = list(tests_dir.glob("**/test_*.py"))
            if test_files:
                print(f"  ✅ {len(test_files)} test files found")
                score += min(30, len(test_files) * 5)
            else:
                print("  ⚠️  No test files found")
        else:
            print("  ❌ tests/ directory missing")
        
        # Check for pytest configuration
        if (self.project_root / "pytest.ini").exists():
            print("  ✅ pytest.ini configuration exists")
            score += 10
        
        self.results["testing"] = {
            "tests_dir_exists": tests_dir.exists(),
            "test_files_count": len(list(tests_dir.glob("**/test_*.py"))) if tests_dir.exists() else 0,
            "score": min(100, score)
        }
        
        print(f"Testing Score: {min(100, score):.1f}%")
        
    def run_basic_import_tests(self):
        """Test basic imports of backend modules"""
        print("🔍 Testing backend module imports...")
        
        import_results = {
            "successful": [],
            "failed": []
        }
        
        # Test critical imports
        test_imports = [
            "apps.legacy_flask.main",
            "shared.utils.security",
            "shared.utils.config", 
            "shared.data_connectors",
        ]
        
        original_path = sys.path[:]
        sys.path.insert(0, str(self.backend_root))
        
        try:
            for module_name in test_imports:
                try:
                    __import__(module_name)
                    import_results["successful"].append(module_name)
                    print(f"  ✅ {module_name}")
                except Exception as e:
                    import_results["failed"].append((module_name, str(e)))
                    print(f"  ❌ {module_name}: {str(e)}")
        finally:
            sys.path[:] = original_path
        
        success_rate = len(import_results["successful"]) / len(test_imports) * 100
        
        self.results["imports"] = {
            "successful": import_results["successful"],
            "failed": import_results["failed"],
            "success_rate": success_rate
        }
        
        print(f"Import Success Rate: {success_rate:.1f}%")
        
    def generate_report(self):
        """Generate final quality assessment report"""
        print("\n" + "=" * 60)
        print("📊 BACKEND QUALITY ASSESSMENT REPORT")
        print("=" * 60)
        
        total_score = 0
        category_count = 0
        
        for category, data in self.results.items():
            if "score" in data:
                score = data["score"]
                total_score += score
                category_count += 1
                
                # Color coding
                if score >= 80:
                    status = "🟢 GOOD"
                elif score >= 60:
                    status = "🟡 NEEDS IMPROVEMENT"
                else:
                    status = "🔴 CRITICAL"
                
                print(f"{category.upper().replace('_', ' ')}: {score:.1f}% {status}")
        
        if category_count > 0:
            overall_score = total_score / category_count
            
            print(f"\nOVERALL SCORE: {overall_score:.1f}%")
            
            if overall_score >= 80:
                print("🎉 Excellent! Backend quality is high.")
            elif overall_score >= 60:
                print("👍 Good! Some areas need attention.")
            else:
                print("⚠️  Backend needs significant improvements.")
        
        # Save detailed results
        report_file = self.backend_root / "quality_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\nDetailed report saved to: {report_file}")
        
    def run_assessment(self):
        """Run complete quality assessment"""
        print("🔍 AI Data Platform Backend Quality Assessment")
        print("=" * 60)
        print(f"Backend directory: {self.backend_root}")
        print(f"Assessment time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            self.check_backend_structure()
            print()
            
            self.check_python_code_quality() 
            print()
            
            self.check_dependencies()
            print()
            
            self.check_security_basics()
            print()
            
            self.check_testing_setup()
            print()
            
            self.run_basic_import_tests()
            print()
            
            self.generate_report()
            
        except Exception as e:
            print(f"❌ Assessment failed: {str(e)}")
            return False
        
        return True

def main():
    """Main function"""
    assessment = BackendQualityAssessment()
    success = assessment.run_assessment()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()