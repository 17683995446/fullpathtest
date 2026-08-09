#!/usr/bin/env python3
"""
FullPathTest v5.0 - 超深度真实测试系统
长时间特复杂且高难度的真实项目测试
目的：发现系统在真实运行时的bug
"""

import os
import sys
import json
import time
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))


class V5DeepTestSystem:
    """v5.0 深度真实测试系统"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.results: List[Dict[str, Any]] = []
        self.defects_found: List[Dict[str, Any]] = []
        self.test_counter = 0
        
    def log(self, message: str, level: str = "INFO"):
        """日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def log_result(self, test_name: str, status: str, **kwargs):
        """记录测试结果"""
        # 安全地处理可能不可JSON序列化的内容
        safe_kwargs = {}
        for key, value in kwargs.items():
            try:
                # 尝试检查是否可JSON序列化
                import json
                json.dumps(value)
                safe_kwargs[key] = value
            except (TypeError, OverflowError):
                # 转换为字符串表示
                safe_kwargs[key] = str(value)
        
        result = {
            'test_id': f"TEST_{self.test_counter:04d}",
            'name': test_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            **safe_kwargs
        }
        self.results.append(result)
        self.test_counter += 1

        if status == "FAILED" or status == "DEFECT_FOUND":
            self.defects_found.append(result)
            self.log(f"⚠️ {test_name}: {status}", "ERROR")
        elif status == "SUCCESS":
            self.log(f"✅ {test_name}: {status}")
            
    def test_fastapi_project_complete(self):
        """测试1: FastAPI 项目完整分析"""
        self.log("="*70)
        self.log("测试1: FastAPI 项目完整深度分析")
        self.log("="*70)
        
        try:
            from fullpathtest.main import FullPathTestSystem
            
            self.log("🚀 启动 FullPathTestSystem...")
            system = FullPathTestSystem()
            
            self.log("📂 开始测试 FastAPI 项目...")
            start = time.time()
            
            result = system.run_full_test(
                source_path="/workspace/cloned_fastapi_project",
                llm_mode="local_only",
                user_command="完整深度分析这个真实的FastAPI项目，发现所有问题"
            )
            
            duration = time.time() - start
            
            self.log(f"✅ FastAPI 测试完成，耗时: {duration:.2f}秒")
            self.log(f"📊 结果状态: {result.get('status', 'unknown')}")
            
            # 检查结果完整性
            if result.get('status') == 'success':
                coverage = result.get('coverage_report', {})
                self.log(f"📈 覆盖率: {coverage.get('statement_coverage', 0)*100:.1f}%")
                self.log_result("FastAPI完整分析", "SUCCESS", duration=duration, coverage=coverage)
            else:
                self.log_result("FastAPI完整分析", "DEFECT_FOUND", error=result.get('error'), result=result)
                
        except Exception as e:
            self.log(f"❌ FastAPI 测试异常: {e}")
            traceback.print_exc()
            self.log_result("FastAPI完整分析", "FAILED", error=str(e), traceback=traceback.format_exc())
            
    def test_django_project_complete(self):
        """测试2: Django 项目完整分析"""
        self.log("="*70)
        self.log("测试2: Django 项目完整深度分析")
        self.log("="*70)
        
        try:
            from fullpathtest.main import FullPathTestSystem
            
            self.log("🚀 再次启动 FullPathTestSystem...")
            system = FullPathTestSystem()
            
            self.log("📂 开始测试 Django 项目...")
            start = time.time()
            
            result = system.run_full_test(
                source_path="/workspace/django_project",
                llm_mode="local_only",
                user_command="深度分析Django项目，生成测试套件"
            )
            
            duration = time.time() - start
            
            self.log(f"✅ Django 测试完成，耗时: {duration:.2f}秒")
            self.log(f"📊 结果状态: {result.get('status', 'unknown')}")
            
            if result.get('status') == 'success':
                coverage = result.get('coverage_report', {})
                self.log(f"📈 覆盖率: {coverage.get('statement_coverage', 0)*100:.1f}%")
                self.log_result("Django完整分析", "SUCCESS", duration=duration, coverage=coverage)
            else:
                self.log_result("Django完整分析", "DEFECT_FOUND", error=result.get('error'), result=result)
                
        except Exception as e:
            self.log(f"❌ Django 测试异常: {e}")
            traceback.print_exc()
            self.log_result("Django完整分析", "FAILED", error=str(e), traceback=traceback.format_exc())
            
    def test_consecutive_tasks(self):
        """测试3: 连续执行多个任务"""
        self.log("="*70)
        self.log("测试3: 连续执行多个任务（资源泄漏测试）")
        self.log("="*70)
        
        try:
            from fullpathtest.main import FullPathTestSystem
            
            system = FullPathTestSystem()
            small_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
            
            all_success = True
            start = time.time()
            
            for i in range(5):  # 连续执行5次
                self.log(f"🔄 任务 {i+1}/5...")
                try:
                    result = system.run_full_test(
                        source_path=small_path,
                        llm_mode="local_only"
                    )
                    if result.get('status') != 'success':
                        all_success = False
                        self.log(f"⚠️  任务 {i+1} 状态: {result.get('status')}")
                except Exception as e:
                    all_success = False
                    self.log(f"❌ 任务 {i+1} 失败: {e}")
                    
            duration = time.time() - start
            
            if all_success:
                self.log(f"✅ 连续5次任务执行成功，总耗时: {duration:.2f}秒")
                self.log_result("连续任务测试", "SUCCESS", duration=duration, tasks=5)
            else:
                self.log_result("连续任务测试", "DEFECT_FOUND", duration=duration)
                
        except Exception as e:
            self.log(f"❌ 连续任务测试异常: {e}")
            traceback.print_exc()
            self.log_result("连续任务测试", "FAILED", error=str(e))
            
    def test_extreme_edge_cases(self):
        """测试4: 极端边界情况"""
        self.log("="*70)
        self.log("测试4: 极端边界情况测试")
        self.log("="*70)
        
        try:
            from fullpathtest.main import FullPathTestSystem
            system = FullPathTestSystem()
            
            # 创建临时极端测试文件
            temp_dir = Path("/tmp/v5_edge_cases")
            temp_dir.mkdir(exist_ok=True)
            
            # 测试1: 空文件
            self.log("测试4.1: 空文件")
            empty_file = temp_dir / "empty.py"
            empty_file.write_text("")
            try:
                result = system.run_full_test(source_path=str(empty_file))
                self.log_result("空文件测试", "SUCCESS")
            except Exception as e:
                self.log_result("空文件测试", "DEFECT_FOUND", error=str(e))
                
            # 测试2: 超大文件（1MB）
            self.log("测试4.2: 超大代码文件")
            large_file = temp_dir / "large.py"
            large_content = "# Test file\n" + "def func_{}(x): return x\n".format("0"*1000) * 100
            large_file.write_text(large_content)
            try:
                start = time.time()
                result = system.run_full_test(source_path=str(large_file))
                duration = time.time() - start
                self.log(f"✅ 超大文件处理耗时: {duration:.2f}秒")
                self.log_result("超大文件测试", "SUCCESS", duration=duration)
            except Exception as e:
                self.log_result("超大文件测试", "DEFECT_FOUND", error=str(e))
                
            # 清理
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
        except Exception as e:
            self.log(f"❌ 边界情况测试异常: {e}")
            traceback.print_exc()
            
    def run_all_tests(self):
        """运行所有深度测试"""
        self.log("\n" + "="*70)
        self.log("FullPathTest v5.0 - 超深度真实测试系统")
        self.log("="*70)
        
        total_start = time.time()
        
        # 执行所有测试
        self.test_fastapi_project_complete()
        self.test_django_project_complete()
        self.test_consecutive_tasks()
        self.test_extreme_edge_cases()
        
        total_duration = time.time() - total_start
        
        # 生成最终报告
        self.generate_final_report(total_duration)
        
    def generate_final_report(self, total_duration: float):
        """生成最终报告"""
        self.log("\n" + "="*70)
        self.log("v5.0 深度真实测试报告")
        self.log("="*70)

        total_tests = len(self.results)
        success_tests = sum(1 for r in self.results if r['status'] == "SUCCESS")
        defect_tests = sum(1 for r in self.results if r['status'] == "DEFECT_FOUND")
        failed_tests = sum(1 for r in self.results if r['status'] == "FAILED")

        self.log(f"\n📊 总体统计:")
        self.log(f"   总测试数: {total_tests}")
        self.log(f"   成功: {success_tests}")
        self.log(f"   发现缺陷: {defect_tests}")
        self.log(f"   失败: {failed_tests}")
        self.log(f"   总耗时: {total_duration:.2f}秒")

        # 保存详细报告（确保所有内容可序列化）
        def make_serializable(obj):
            """递归转换为可JSON序列化对象"""
            if isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            elif isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [make_serializable(item) for item in obj]
            else:
                return str(obj)
        
        report_path = Path("/workspace/v5_deep_test_report.json")
        report = {
            'summary': {
                'total_tests': total_tests,
                'success': success_tests,
                'defect_found': defect_tests,
                'failed': failed_tests,
                'total_duration_seconds': total_duration
            },
            'timestamp': datetime.now().isoformat(),
            'defects': make_serializable(self.defects_found),
            'all_results': make_serializable(self.results)
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.log(f"\n✅ 详细报告已保存到: {report_path}")

        return report


def main():
    """主函数"""
    print("\n" + "="*70)
    print("FullPathTest v5.0 - 超深度真实测试系统")
    print("="*70)
    print("\n⚠️ 注意：这将进行长时间特复杂的真实测试")
    print("⚠️ 目的：发现系统在真实运行时的bug\n")
    
    system = V5DeepTestSystem()
    report = system.run_all_tests()
    
    return report


if __name__ == "__main__":
    main()
