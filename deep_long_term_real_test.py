#!/usr/bin/env python3
"""
FullPathTest v4.0 - 深度长时真实测试系统
设计用于：
1. 长时间真实项目测试（10000+任务）
2. 大规模并发压力测试
3. 边缘极限情况持续测试
4. 系统稳定性和可靠性验证
"""

import os
import sys
import json
import time
import gc
import threading
import traceback
import random
import multiprocessing
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import psutil


class DefectSeverity(Enum):
    BLOCKER = "blocker"
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DefectCategory(Enum):
    STABILITY = "stability"
    PERFORMANCE = "performance"
    MEMORY_LEAK = "memory_leak"
    RACE_CONDITION = "race_condition"
    EDGE_CASE = "edge_case"
    SCALABILITY = "scalability"
    FILE_SYSTEM = "file_system"
    INTEGRATION = "integration"


@dataclass
class DeepDefect:
    """深度缺陷"""
    defect_id: str
    severity: DefectSeverity
    category: DefectCategory
    title: str
    description: str
    reproduction_steps: List[str]
    location: str
    impact: str
    evidence: Dict[str, Any]
    discovered_at: datetime = field(default_factory=datetime.now)
    discovered_during: str = ""


@dataclass
class TestResult:
    """测试结果"""
    test_name: str
    success: bool
    duration: float
    memory_before: float
    memory_after: float
    cpu_before: float
    cpu_after: float
    errors: List[str]
    metrics: Dict[str, Any]


class DeepLongTermRealTest:
    """深度长时真实测试器"""
    
    def __init__(self):
        self.defects: List[DeepDefect] = []
        self.test_results: List[TestResult] = []
        self.start_time = time.time()
        self.memory_baseline = self.get_memory_usage()
        self.process = psutil.Process()
        
    def get_memory_usage(self) -> float:
        """获取内存使用（MB）"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def get_cpu_usage(self) -> float:
        """获取CPU使用"""
        return psutil.cpu_percent(interval=0.1)
    
    def log_defect(self, defect: DeepDefect):
        """记录缺陷"""
        self.defects.append(defect)
        print(f"\n🔴🔴🔴 发现深度真实缺陷 🔴🔴🔴")
        print(f"ID: {defect.defect_id}")
        print(f"严重性: {defect.severity.value}")
        print(f"类别: {defect.category.value}")
        print(f"标题: {defect.title}")
        print(f"发现阶段: {defect.discovered_during}")
        print(f"位置: {defect.location}")
    
    def test_01_long_term_fastapi_analysis(self):
        """测试1: 长时间FastAPI项目分析（10000+任务）"""
        print("\n" + "="*80)
        print("测试1: 长时间FastAPI项目持续分析")
        print("="*80)
        
        project_dir = Path("/workspace/cloned_fastapi_project")
        if not project_dir.exists():
            print("❌ FastAPI项目不存在，跳过")
            return
        
        try:
            from fullpathtest import analyze_code, ProjectConfig
            from fullpathtest.modules.real_code_analyzer import RealCodeAnalyzer
            
            print(f"📂 项目目录: {project_dir}")
            
            # 收集所有Python文件
            py_files = list(project_dir.rglob("*.py"))
            print(f"📄 找到 {len(py_files)} 个Python文件")
            
            # 长时循环测试 - 分析10000次
            iterations = 10000
            success_count = 0
            error_count = 0
            memory_samples = []
            duration_samples = []
            errors = []
            
            print(f"🚀 开始 {iterations} 次迭代分析...")
            
            memory_before = self.get_memory_usage()
            cpu_before = self.get_cpu_usage()
            start_iter = time.time()
            
            for i in range(iterations):
                if i % 1000 == 0:
                    current_memory = self.get_memory_usage()
                    memory_samples.append(current_memory)
                    print(f"  进度: {i}/{iterations} ({i/iterations*100:.1f}%) - 内存: {current_memory:.2f}MB")
                
                try:
                    # 随机选择文件
                    file_path = random.choice(py_files)
                    try:
                        code = file_path.read_text(encoding='utf-8')
                        
                        # 执行分析
                        result = analyze_code(code, str(file_path))
                        
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        if len(errors) < 50:
                            errors.append(f"{file_path}: {e}")
                
                except Exception as e:
                    error_count += 1
                    if len(errors) < 50:
                        errors.append(f"Iteration {i}: {e}")
            
            end_iter = time.time()
            memory_after = self.get_memory_usage()
            cpu_after = self.get_cpu_usage()
            total_duration = end_iter - start_iter
            
            # 分析结果
            print(f"\n📊 分析完成:")
            print(f"  成功: {success_count}/{iterations}")
            print(f"  失败: {error_count}/{iterations}")
            print(f"  总耗时: {total_duration:.2f}秒")
            print(f"  内存变化: {memory_before:.2f}MB -> {memory_after:.2f}MB")
            print(f"  内存增长: {memory_after - memory_before:.2f}MB")
            
            # 检查内存泄漏
            memory_growth = memory_after - self.memory_baseline
            if memory_growth > 50:  # 超过50MB视为泄漏
                self.log_defect(DeepDefect(
                    defect_id="DEEP_001",
                    severity=DefectSeverity.HIGH,
                    category=DefectCategory.MEMORY_LEAK,
                    title=f"长时间分析导致内存泄漏（增长 {memory_growth:.2f}MB）",
                    description=f"{iterations}次迭代后内存增长 {memory_growth:.2f}MB，可能存在内存泄漏",
                    reproduction_steps=[
                        f"对FastAPI项目执行 {iterations} 次迭代分析",
                        "监控内存使用变化"
                    ],
                    location="fullpathtest - 主分析模块",
                    impact="长时间运行导致内存耗尽",
                    evidence={
                        'memory_samples': memory_samples,
                        'memory_before': memory_before,
                        'memory_after': memory_after,
                        'memory_growth': memory_growth,
                        'iterations': iterations
                    },
                    discovered_during="long_term_fastapi_analysis"
                ))
            
            # 检查错误率
            if error_count > iterations * 0.1:
                self.log_defect(DeepDefect(
                    defect_id="DEEP_002",
                    severity=DefectSeverity.HIGH,
                    category=DefectCategory.STABILITY,
                    title=f"分析错误率过高 ({error_count/iterations*100:.1f}%)",
                    description=f"{iterations}次迭代中有 {error_count} 次失败",
                    reproduction_steps=["执行大量文件分析"],
                    location="fullpathtest - 分析流程",
                    impact="大规模分析不稳定",
                    evidence={'error_rate': error_count/iterations, 'errors': errors[:20]},
                    discovered_during="long_term_fastapi_analysis"
                ))
            
            # 记录结果
            self.test_results.append(TestResult(
                test_name="long_term_fastapi_analysis",
                success=error_count == 0,
                duration=total_duration,
                memory_before=memory_before,
                memory_after=memory_after,
                cpu_before=cpu_before,
                cpu_after=cpu_after,
                errors=errors,
                metrics={'iterations': iterations, 'success_count': success_count, 'error_count': error_count}
            ))
            
        except Exception as e:
            print(f"❌ FastAPI长时测试失败: {e}")
            traceback.print_exc()
    
    def test_02_massive_concurrent_analysis(self):
        """测试2: 大规模并发分析（100+并发）"""
        print("\n" + "="*80)
        print("测试2: 大规模并发压力测试")
        print("="*80)
        
        project_dir = Path("/workspace/cloned_fastapi_project")
        if not project_dir.exists():
            print("❌ FastAPI项目不存在，跳过")
            return
        
        try:
            from fullpathtest import analyze_code
            
            py_files = list(project_dir.rglob("*.py"))[:100]  # 取前100个文件
            if not py_files:
                print("❌ 没有找到Python文件")
                return
            
            print(f"📄 测试文件数: {len(py_files)}")
            
            # 测试不同并发级别
            concurrency_levels = [10, 30, 50, 100]
            errors = []
            
            for concurrency in concurrency_levels:
                print(f"\n🔄 测试并发度: {concurrency}")
                
                memory_before = self.get_memory_usage()
                start_time = time.time()
                success = 0
                failed = 0
                thread_errors = []
                
                def analyze_task(file_path):
                    try:
                        code = file_path.read_text(encoding='utf-8', errors='ignore')
                        analyze_code(code, str(file_path))
                        return True
                    except Exception as e:
                        return str(e)
                
                with ThreadPoolExecutor(max_workers=concurrency) as executor:
                    futures = {executor.submit(analyze_task, f): f for f in py_files}
                    for future in as_completed(futures):
                        result = future.result()
                        if result is True:
                            success += 1
                        else:
                            failed += 1
                            if len(thread_errors) < 20:
                                thread_errors.append(result)
                
                duration = time.time() - start_time
                memory_after = self.get_memory_usage()
                
                print(f"  成功: {success}, 失败: {failed}")
                print(f"  耗时: {duration:.2f}秒")
                print(f"  内存: {memory_before:.2f}MB -> {memory_after:.2f}MB")
                
                if failed > 0 and len(thread_errors) > 0:
                    errors.append({
                        'concurrency': concurrency,
                        'failed': failed,
                        'errors': thread_errors
                    })
            
            if len(errors) > 0:
                self.log_defect(DeepDefect(
                    defect_id="DEEP_003",
                    severity=DefectSeverity.HIGH,
                    category=DefectCategory.SCALABILITY,
                    title=f"并发分析在高负载下出现 {len(errors)} 次失败",
                    description="并发级别提高时错误率上升",
                    reproduction_steps=["使用不同并发级别测试"],
                    location="fullpathtest - 并发处理",
                    impact="高并发场景下不稳定",
                    evidence={'concurrency_errors': errors},
                    discovered_during="massive_concurrent_analysis"
                ))
            
            self.test_results.append(TestResult(
                test_name="massive_concurrent_analysis",
                success=len(errors) == 0,
                duration=0,
                memory_before=0,
                memory_after=0,
                cpu_before=0,
                cpu_after=0,
                errors=[str(e) for e in errors],
                metrics={}
            ))
            
        except Exception as e:
            print(f"❌ 并发测试失败: {e}")
            traceback.print_exc()
    
    def test_03_django_large_scale_test(self):
        """测试3: Django项目大规模测试"""
        print("\n" + "="*80)
        print("测试3: Django项目大规模测试")
        print("="*80)
        
        project_dir = Path("/workspace/django_project")
        if not project_dir.exists():
            print("❌ Django项目不存在，跳过")
            return
        
        try:
            from fullpathtest import ProjectConfig, analyze_project
            
            print(f"📂 项目目录: {project_dir}")
            
            memory_before = self.get_memory_usage()
            cpu_before = self.get_cpu_usage()
            start_time = time.time()
            
            # 整个项目分析
            errors = []
            try:
                config = ProjectConfig(
                    project_path=str(project_dir),
                    include_patterns=["*.py"],
                    exclude_patterns=["*.pyc", "__pycache__", "*.git"],
                    max_depth=20
                )
                
                print("🚀 开始完整Django项目分析...")
                result = analyze_project(str(project_dir))
                print(f"  ✅ 分析完成")
                
            except Exception as e:
                errors.append(str(e))
                print(f"  ❌ 分析失败: {e}")
                traceback.print_exc()
            
            end_time = time.time()
            memory_after = self.get_memory_usage()
            cpu_after = self.get_cpu_usage()
            duration = end_time - start_time
            
            print(f"\n📊 Django项目分析:")
            print(f"  耗时: {duration:.2f}秒")
            print(f"  内存: {memory_before:.2f}MB -> {memory_after:.2f}MB")
            
            if len(errors) > 0:
                self.log_defect(DeepDefect(
                    defect_id="DEEP_004",
                    severity=DefectSeverity.CRITICAL,
                    category=DefectCategory.INTEGRATION,
                    title="Django项目大规模分析失败",
                    description=f"完整Django项目分析失败: {errors[0]}",
                    reproduction_steps=["分析整个Django项目"],
                    location="fullpathtest - 项目分析",
                    impact="无法分析大型项目",
                    evidence={'errors': errors},
                    discovered_during="django_large_scale_test"
                ))
            
            self.test_results.append(TestResult(
                test_name="django_large_scale_test",
                success=len(errors) == 0,
                duration=duration,
                memory_before=memory_before,
                memory_after=memory_after,
                cpu_before=cpu_before,
                cpu_after=cpu_after,
                errors=errors,
                metrics={}
            ))
            
        except Exception as e:
            print(f"❌ Django测试失败: {e}")
            traceback.print_exc()
    
    def test_04_edge_case_stress_test(self):
        """测试4: 极端边缘情况压力测试"""
        print("\n" + "="*80)
        print("测试4: 极端边缘情况压力测试")
        print("="*80)
        
        try:
            from fullpathtest import analyze_code
            
            edge_cases = [
                ("empty_file", ""),
                ("single_char", "x"),
                ("huge_file", "x = " + "'y'" * 100000),
                ("deep_nesting", "if True:\n" * 1000 + "    pass"),
                ("weird_chars", "def 你好_世界_🎯_🚀(): pass"),
                ("binary_data", "\x00\x01\x02\x03\x04\x05"),
                ("very_long_line", "x = " + "1" * 10000),
            ]
            
            errors = []
            
            for name, code in edge_cases:
                print(f"\n🔄 测试: {name}")
                try:
                    start = time.time()
                    analyze_code(code, f"edge_{name}.py")
                    dur = time.time() - start
                    print(f"  ✅ 成功, 耗时: {dur:.4f}秒")
                except Exception as e:
                    errors.append((name, str(e)))
                    print(f"  ❌ 失败: {e}")
            
            if len(errors) > 0:
                self.log_defect(DeepDefect(
                    defect_id="DEEP_005",
                    severity=DefectSeverity.MEDIUM,
                    category=DefectCategory.EDGE_CASE,
                    title=f"边缘情况处理失败 ({len(errors)}个)",
                    description=f"以下边缘情况处理失败: {[e[0] for e in errors]}",
                    reproduction_steps=["测试各种极端边缘情况"],
                    location="fullpathtest - 代码分析",
                    impact="特殊输入可能导致失败",
                    evidence={'edge_errors': errors},
                    discovered_during="edge_case_stress_test"
                ))
            
            self.test_results.append(TestResult(
                test_name="edge_case_stress_test",
                success=len(errors) == 0,
                duration=0,
                memory_before=0,
                memory_after=0,
                cpu_before=0,
                cpu_after=0,
                errors=[f"{n}: {e}" for n, e in errors],
                metrics={}
            ))
            
        except Exception as e:
            print(f"❌ 边缘情况测试失败: {e}")
            traceback.print_exc()
    
    def run_all_deep_tests(self):
        """运行所有深度测试"""
        print("\n" + "="*80)
        print("FullPathTest v4.0 - 深度长时真实测试系统")
        print("="*80)
        print(f"开始时间: {datetime.now().isoformat()}")
        print(f"基线内存: {self.memory_baseline:.2f}MB")
        
        self.test_01_long_term_fastapi_analysis()
        self.test_02_massive_concurrent_analysis()
        self.test_03_django_large_scale_test()
        self.test_04_edge_case_stress_test()
        
        # 生成最终报告
        self.generate_final_report()
        
        return self.defects
    
    def generate_final_report(self):
        """生成最终报告"""
        print("\n" + "="*80)
        print("深度长时真实测试 - 最终报告")
        print("="*80)
        
        total_defects = len(self.defects)
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.success)
        
        print(f"\n📊 总体统计:")
        print(f"  总测试数: {total_tests}")
        print(f"  成功测试: {successful_tests}/{total_tests}")
        print(f"  发现缺陷: {total_defects}")
        
        if total_defects == 0:
            print("\n🎉 太棒了！深度长时测试中未发现任何缺陷！")
            print("系统在真实场景下表现完美！")
        else:
            print(f"\n🔴 发现 {total_defects} 个真实缺陷:")
            
            # 按严重性分组
            severity_groups = {}
            for d in self.defects:
                sev = d.severity
                if sev not in severity_groups:
                    severity_groups[sev] = []
                severity_groups[sev].append(d)
            
            for sev in [DefectSeverity.BLOCKER, DefectSeverity.CRITICAL,
                       DefectSeverity.HIGH, DefectSeverity.MEDIUM, DefectSeverity.LOW]:
                if sev in severity_groups:
                    print(f"\n{sev.value.upper()} ({len(severity_groups[sev])}个):")
                    for d in severity_groups[sev]:
                        print(f"  - {d.title} [{d.defect_id}]")
        
        # 保存详细报告
        report = {
            'summary': {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'total_defects': total_defects,
                'duration': time.time() - self.start_time,
                'baseline_memory_mb': self.memory_baseline
            },
            'defects': [
                {
                    'id': d.defect_id,
                    'severity': d.severity.value,
                    'category': d.category.value,
                    'title': d.title,
                    'description': d.description,
                    'discovered_during': d.discovered_during,
                    'location': d.location,
                    'impact': d.impact,
                    'evidence': d.evidence
                }
                for d in self.defects
            ],
            'test_results': [
                {
                    'name': r.test_name,
                    'success': r.success,
                    'duration': r.duration,
                    'errors': r.errors
                }
                for r in self.test_results
            ]
        }
        
        with open('/workspace/deep_long_term_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ 详细报告已保存到: /workspace/deep_long_term_test_report.json")


def main():
    """主函数"""
    tester = DeepLongTermRealTest()
    defects = tester.run_all_deep_tests()
    
    return defects


if __name__ == "__main__":
    main()
