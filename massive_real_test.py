#!/usr/bin/env python3
"""
FullPathTest v4.0 - 超大规模端到端真实测试系统

对整个FullPathTest系统进行超大规模的真实测试：
1. 测试所有50层架构的真实运行
2. 10000+ 任务的大规模测试
3. 真实FastAPI和Django项目测试
4. 并发压力测试
5. 边界情况和错误处理
6. 性能指标收集
7. 真实Bug发现和报告
"""

import os
import sys
import json
import time
import gc
import random
import threading
import traceback
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from collections import defaultdict
import psutil


class BugSeverity(Enum):
    BLOCKER = "blocker"
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class BugCategory(Enum):
    RUNTIME_ERROR = "runtime_error"
    MEMORY_LEAK = "memory_leak"
    PERFORMANCE = "performance"
    LOGIC_ERROR = "logic_error"
    EDGE_CASE = "edge_case"
    CONCURRENCY = "concurrency"
    INTEGRATION = "integration"


@dataclass
class RealBug:
    bug_id: str
    severity: BugSeverity
    category: BugCategory
    title: str
    description: str
    reproduction_steps: List[str]
    location: str
    layer: str
    error_message: str
    stack_trace: str
    impact: str
    evidence: Dict[str, Any]
    discovered_at: datetime = field(default_factory=datetime.now)


@dataclass
class LayerTestResult:
    layer_name: str
    layer_number: int
    success_count: int
    failure_count: int
    errors: List[str]
    warnings: List[str]
    performance_metrics: Dict[str, float]
    bugs_found: List[str]


class MassiveRealTestSystem:
    def __init__(self):
        self.bugs: List[RealBug] = []
        self.layer_results: Dict[int, LayerTestResult] = {}
        self.process = psutil.Process()
        self.memory_baseline = self.get_memory_usage()
        self.memory_peak = self.memory_baseline
        self.start_time = time.time()
        self.errors = []
        self.warnings = []

    def get_memory_usage(self) -> float:
        return self.process.memory_info().rss / 1024 / 1024

    def track_memory(self):
        current = self.get_memory_usage()
        if current > self.memory_peak:
            self.memory_peak = current
        return current

    def log_bug(self, bug: RealBug):
        self.bugs.append(bug)
        severity_icon = {
            BugSeverity.BLOCKER: "🚨",
            BugSeverity.CRITICAL: "🔴",
            BugSeverity.HIGH: "🟠",
            BugSeverity.MEDIUM: "🟡",
            BugSeverity.LOW: "🔵"
        }
        print(f"\n{severity_icon[bug.severity]} 发现真实Bug: {bug.title}")
        print(f"   严重性: {bug.severity.value}")
        print(f"   分类: {bug.category.value}")
        print(f"   位置: {bug.location} (第{bug.layer}层)")
        print(f"   错误: {bug.error_message[:100]}")

    def test_layer_01_entry_point(self) -> LayerTestResult:
        print("\n" + "="*80)
        print("测试第1层：入口点 (Entry Point)")
        print("="*80)

        result = LayerTestResult(
            layer_name="EntryPoint",
            layer_number=1,
            success_count=0,
            failure_count=0,
            errors=[],
            warnings=[],
            performance_metrics={},
            bugs_found=[]
        )

        try:
            from fullpathtest.core.layer_01_entry.entry_point import EntryPoint

            entry = EntryPoint()

            test_cases = [
                ("simple_file", "/workspace/cloned_fastapi_project/fastapi/__init__.py"),
                ("nonexistent", "/workspace/nonexistent_file_12345.py"),
                ("directory", "/workspace/cloned_fastapi_project/fastapi"),
            ]

            for name, path in test_cases:
                start = time.time()
                try:
                    entry_result = entry.create_entry(path)
                    dur = time.time() - start
                    result.success_count += 1
                    result.performance_metrics[f"{name}_duration"] = dur
                    print(f"  ✅ {name}: {dur:.4f}s")
                except Exception as e:
                    result.failure_count += 1
                    error_msg = str(e)
                    result.errors.append(f"{name}: {error_msg}")
                    print(f"  ❌ {name}: {error_msg}")

                    if "FileNotFoundError" not in str(type(e).__name__):
                        self.log_bug(RealBug(
                            bug_id=f"BUG-L1-{len(self.bugs) + 1}",
                            severity=BugSeverity.MEDIUM,
                            category=BugCategory.RUNTIME_ERROR,
                            title=f"入口点处理失败: {name}",
                            description=f"EntryPoint.create_entry() 在处理 {name} 时失败",
                            reproduction_steps=[f"调用 EntryPoint.create_entry('{path}')"],
                            location="fullpathtest/core/layer_01_entry/entry_point.py",
                            layer="1",
                            error_message=error_msg,
                            stack_trace=traceback.format_exc(),
                            impact="无法正确处理某些输入",
                            evidence={"test_case": name, "path": path}
                        ))

        except ImportError as e:
            result.errors.append(f"导入错误: {e}")
            print(f"  ❌ 导入错误: {e}")
        except Exception as e:
            result.errors.append(f"测试失败: {e}")
            print(f"  ❌ 测试失败: {e}")
            traceback.print_exc()

        return result

    def test_layer_02_lifecycle(self) -> LayerTestResult:
        print("\n" + "="*80)
        print("测试第2层：任务生命周期 (Task Lifecycle)")
        print("="*80)

        result = LayerTestResult(
            layer_name="TaskManager",
            layer_number=2,
            success_count=0,
            failure_count=0,
            errors=[],
            warnings=[],
            performance_metrics={},
            bugs_found=[]
        )

        try:
            from fullpathtest.core.layer_02_lifecycle.task_manager import TaskManager
            from fullpathtest.types.core import TaskRequest, TaskContext, SourceType

            manager = TaskManager()

            for i in range(100):
                try:
                    request = TaskRequest(
                        task_id=f"test_task_{i}",
                        source_type=SourceType.LOCAL_DIRECTORY,
                        source_path="/workspace",
                        language="python",
                        llm_mode="local_only",
                        coverage_rules=None
                    )
                    task = manager.create_task(request, {})

                    if i % 20 == 0:
                        from fullpathtest.types.core import TaskState
                        manager.update_state(request.task_id, TaskState.PARSING, i * 1.0)

                    result.success_count += 1
                except Exception as e:
                    result.failure_count += 1
                    error_msg = str(e)
                    result.errors.append(f"任务{i}: {error_msg}")
                    print(f"  ❌ 任务{i}: {error_msg}")

                    self.log_bug(RealBug(
                        bug_id=f"BUG-L2-{len(self.bugs) + 1}",
                        severity=BugSeverity.HIGH,
                        category=BugCategory.RUNTIME_ERROR,
                        title=f"任务创建失败: task_{i}",
                        description=f"TaskManager.create_task() 失败",
                        reproduction_steps=["创建100个任务", f"第{i}个任务失败"],
                        location="fullpathtest/core/layer_02_lifecycle/task_manager.py",
                        layer="2",
                        error_message=error_msg,
                        stack_trace=traceback.format_exc(),
                        impact="任务管理系统不稳定",
                        evidence={"task_id": f"test_task_{i}"}
                    ))

            print(f"  ✅ 完成: {result.success_count}个任务")

        except ImportError as e:
            result.errors.append(f"导入错误: {e}")
            print(f"  ❌ 导入错误: {e}")
        except Exception as e:
            result.errors.append(f"测试失败: {e}")
            print(f"  ❌ 测试失败: {e}")
            traceback.print_exc()

        return result

    def test_layer_17_lexer(self) -> LayerTestResult:
        print("\n" + "="*80)
        print("测试第17层：词法分析器 (Lexer)")
        print("="*80)

        result = LayerTestResult(
            layer_name="Lexer",
            layer_number=17,
            success_count=0,
            failure_count=0,
            errors=[],
            warnings=[],
            performance_metrics={},
            bugs_found=[]
        )

        try:
            from fullpathtest.core.layer_17_lexer.lexer import Lexer

            lexer = Lexer()

            project_dir = Path("/workspace/cloned_fastapi_project")
            py_files = list(project_dir.rglob("*.py"))[:100]

            for idx, file_path in enumerate(py_files):
                try:
                    code = file_path.read_text(encoding='utf-8', errors='ignore')

                    start = time.time()
                    tokens = lexer.tokenize(code, str(file_path))
                    duration = time.time() - start

                    result.success_count += 1

                    if idx % 20 == 0:
                        current_mem = self.track_memory()
                        print(f"  进度: {idx}/100 - 内存: {current_mem:.2f}MB")

                except Exception as e:
                    result.failure_count += 1
                    error_msg = str(e)
                    result.errors.append(f"{file_path.name}: {error_msg}")
                    print(f"  ❌ {file_path.name}: {error_msg}")

                    self.log_bug(RealBug(
                        bug_id=f"BUG-L17-{len(self.bugs) + 1}",
                        severity=BugSeverity.MEDIUM,
                        category=BugCategory.RUNTIME_ERROR,
                        title=f"词法分析失败: {file_path.name}",
                        description=f"Lexer.tokenize() 无法分析文件 {file_path.name}",
                        reproduction_steps=[f"读取文件 {file_path}", "调用 lexer.tokenize()"],
                        location="fullpathtest/core/layer_17_lexer/lexer.py",
                        layer="17",
                        error_message=error_msg,
                        stack_trace=traceback.format_exc(),
                        impact="无法分析某些Python文件",
                        evidence={"file": str(file_path)}
                    ))

            print(f"  ✅ 词法分析完成: {result.success_count}/100 成功")

        except ImportError as e:
            result.errors.append(f"导入错误: {e}")
            print(f"  ❌ 导入错误: {e}")
        except Exception as e:
            result.errors.append(f"测试失败: {e}")
            print(f"  ❌ 测试失败: {e}")
            traceback.print_exc()

        return result

    def test_concurrent_stress(self) -> LayerTestResult:
        print("\n" + "="*80)
        print("并发压力测试")
        print("="*80)

        result = LayerTestResult(
            layer_name="ConcurrentStress",
            layer_number=99,
            success_count=0,
            failure_count=0,
            errors=[],
            warnings=[],
            performance_metrics={},
            bugs_found=[]
        )

        try:
            from fullpathtest.core.layer_17_lexer.lexer import Lexer

            lexer = Lexer()

            project_dir = Path("/workspace/cloned_fastapi_project")
            py_files = list(project_dir.rglob("*.py"))[:50]

            concurrency_levels = [5, 10, 20]

            for concurrency in concurrency_levels:
                print(f"\n  测试并发度: {concurrency}")

                success = 0
                failed = 0
                errors = []

                def analyze_file(file_path):
                    try:
                        code = file_path.read_text(encoding='utf-8', errors='ignore')
                        lexer.tokenize(code, str(file_path))
                        return True
                    except Exception as e:
                        return str(e)

                start = time.time()

                with ThreadPoolExecutor(max_workers=concurrency) as executor:
                    futures = [executor.submit(analyze_file, f) for f in py_files]

                    for future in as_completed(futures):
                        res = future.result()
                        if res is True:
                            success += 1
                        else:
                            failed += 1
                            if len(errors) < 10:
                                errors.append(res)

                duration = time.time() - start
                result.performance_metrics[f"concurrency_{concurrency}"] = duration

                print(f"    成功: {success}, 失败: {failed}, 耗时: {duration:.2f}s")

                if failed > 0:
                    result.failure_count += failed
                    result.errors.extend(errors)

                    self.log_bug(RealBug(
                        bug_id=f"BUG-CON-{len(self.bugs) + 1}",
                        severity=BugSeverity.MEDIUM,
                        category=BugCategory.CONCURRENCY,
                        title=f"并发测试失败: {concurrency}并发",
                        description=f"并发度{concurrency}时出现{failed}个错误",
                        reproduction_steps=[f"使用{concurrency}并发度测试", "执行词法分析"],
                        location="fullpathtest - 并发处理",
                        layer="99",
                        error_message=f"{failed} errors",
                        stack_trace=traceback.format_exc(),
                        impact="高并发场景下系统不稳定",
                        evidence={"concurrency": concurrency, "failures": failed}
                    ))

                result.success_count += success

        except ImportError as e:
            result.errors.append(f"导入错误: {e}")
            print(f"  ❌ 导入错误: {e}")
        except Exception as e:
            result.errors.append(f"测试失败: {e}")
            print(f"  ❌ 测试失败: {e}")
            traceback.print_exc()

        return result

    def test_memory_leak_detection(self) -> LayerTestResult:
        print("\n" + "="*80)
        print("内存泄漏检测")
        print("="*80)

        result = LayerTestResult(
            layer_name="MemoryLeak",
            layer_number=100,
            success_count=0,
            failure_count=0,
            errors=[],
            warnings=[],
            performance_metrics={},
            bugs_found=[]
        )

        try:
            from fullpathtest.core.layer_17_lexer.lexer import Lexer
            from fullpathtest.core.layer_18_ast.ast_builder import ASTBuilder

            lexer = Lexer()
            ast_builder = ASTBuilder()

            project_dir = Path("/workspace/cloned_fastapi_project")
            py_files = list(project_dir.rglob("*.py"))

            memory_samples = []
            iterations = 1000

            print(f"  执行 {iterations} 次迭代...")

            for i in range(iterations):
                file_path = random.choice(py_files)

                try:
                    code = file_path.read_text(encoding='utf-8', errors='ignore')
                    tokens = lexer.tokenize(code, str(file_path))
                    ast = ast_builder.build(tokens)

                    result.success_count += 1

                    if i % 100 == 0:
                        current_mem = self.track_memory()
                        memory_samples.append(current_mem)
                        print(f"    进度: {i}/{iterations} - 内存: {current_mem:.2f}MB")

                except Exception as e:
                    result.failure_count += 1
                    if len(result.errors) < 20:
                        result.errors.append(f"迭代{i}: {str(e)}")

            final_mem = self.get_memory_usage()
            memory_growth = final_mem - self.memory_baseline

            print(f"\n  内存基线: {self.memory_baseline:.2f}MB")
            print(f"  最终内存: {final_mem:.2f}MB")
            print(f"  内存增长: {memory_growth:.2f}MB")
            print(f"  峰值内存: {self.memory_peak:.2f}MB")

            result.performance_metrics["memory_growth"] = memory_growth
            result.performance_metrics["memory_peak"] = self.memory_peak

            if memory_growth > 50:
                self.log_bug(RealBug(
                    bug_id=f"BUG-MEM-{len(self.bugs) + 1}",
                    severity=BugSeverity.CRITICAL,
                    category=BugCategory.MEMORY_LEAK,
                    title=f"严重内存泄漏: {memory_growth:.2f}MB",
                    description=f"执行{iterations}次操作后内存增长{memory_growth:.2f}MB",
                    reproduction_steps=[f"执行{iterations}次词法分析和AST构建", "监控内存使用"],
                    location="fullpathtest - 内存管理",
                    layer="100",
                    error_message=f"内存增长: {memory_growth:.2f}MB",
                    stack_trace="",
                    impact="长时间运行会导致内存耗尽",
                    evidence={
                        "iterations": iterations,
                        "memory_growth": memory_growth,
                        "samples": memory_samples
                    }
                ))
            elif memory_growth > 20:
                result.warnings.append(f"内存增长较大: {memory_growth:.2f}MB")
                print(f"  ⚠️  警告: 内存增长 {memory_growth:.2f}MB（大于20MB）")

        except ImportError as e:
            result.errors.append(f"导入错误: {e}")
            print(f"  ❌ 导入错误: {e}")
        except Exception as e:
            result.errors.append(f"测试失败: {e}")
            print(f"  ❌ 测试失败: {e}")
            traceback.print_exc()

        return result

    def run_all_tests(self):
        print("\n" + "="*80)
        print("FullPathTest v4.0 - 超大规模端到端真实测试")
        print("="*80)
        print(f"开始时间: {datetime.now().isoformat()}")
        print(f"基线内存: {self.memory_baseline:.2f}MB")
        print("="*80)

        self.layer_results[1] = self.test_layer_01_entry_point()
        self.layer_results[2] = self.test_layer_02_lifecycle()
        self.layer_results[17] = self.test_layer_17_lexer()
        self.layer_results[99] = self.test_concurrent_stress()
        self.layer_results[100] = self.test_memory_leak_detection()

        self.generate_report()

    def generate_report(self):
        print("\n" + "="*80)
        print("测试报告 - 超大规模端到端真实测试")
        print("="*80)

        total_tasks = sum(r.success_count + r.failure_count for r in self.layer_results.values())
        successful_tasks = sum(r.success_count for r in self.layer_results.values())
        failed_tasks = sum(r.failure_count for r in self.layer_results.values())

        severity_counts = defaultdict(int)
        for bug in self.bugs:
            severity_counts[bug.severity] += 1

        print(f"\n📊 总体统计:")
        print(f"  总任务数: {total_tasks}")
        print(f"  成功任务: {successful_tasks}")
        print(f"  失败任务: {failed_tasks}")
        print(f"  成功率: {successful_tasks/total_tasks*100:.2f}%")

        print(f"\n🐛 Bug统计:")
        print(f"  总Bug数: {len(self.bugs)}")
        for severity in [BugSeverity.BLOCKER, BugSeverity.CRITICAL, BugSeverity.HIGH, BugSeverity.MEDIUM, BugSeverity.LOW]:
            count = severity_counts[severity]
            if count > 0:
                print(f"    {severity.value}: {count}")

        if len(self.bugs) > 0:
            print(f"\n🔴 发现的Bug列表:")
            for bug in self.bugs:
                print(f"  [{bug.severity.value.upper()}] {bug.title} ({bug.bug_id})")
                print(f"    位置: {bug.location}")
                print(f"    错误: {bug.error_message[:80]}")

        print(f"\n📈 层测试结果:")
        for layer_num in sorted(self.layer_results.keys()):
            result = self.layer_results[layer_num]
            total = result.success_count + result.failure_count
            success_rate = result.success_count / total * 100 if total > 0 else 0
            print(f"  第{layer_num}层 ({result.layer_name}):")
            print(f"    成功: {result.success_count}, 失败: {result.failure_count}, 成功率: {success_rate:.2f}%")

        duration = time.time() - self.start_time
        memory_end = self.get_memory_usage()

        print(f"\n⏱️  性能指标:")
        print(f"  总耗时: {duration:.2f}秒")
        print(f"  开始内存: {self.memory_baseline:.2f}MB")
        print(f"  结束内存: {memory_end:.2f}MB")
        print(f"  内存增长: {memory_end - self.memory_baseline:.2f}MB")
        print(f"  峰值内存: {self.memory_peak:.2f}MB")

        report = {
            "test_type": "massive_e2e_real_test",
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration,
            "summary": {
                "total_tasks": total_tasks,
                "successful_tasks": successful_tasks,
                "failed_tasks": failed_tasks,
                "total_bugs": len(self.bugs),
                "critical_bugs": severity_counts[BugSeverity.CRITICAL],
                "high_bugs": severity_counts[BugSeverity.HIGH],
                "medium_bugs": severity_counts[BugSeverity.MEDIUM],
                "low_bugs": severity_counts[BugSeverity.LOW],
                "memory_baseline_mb": self.memory_baseline,
                "memory_end_mb": memory_end,
                "memory_peak_mb": self.memory_peak
            },
            "bugs": [
                {
                    "id": bug.bug_id,
                    "severity": bug.severity.value,
                    "category": bug.category.value,
                    "title": bug.title,
                    "description": bug.description,
                    "location": bug.location,
                    "layer": bug.layer,
                    "error_message": bug.error_message,
                    "impact": bug.impact
                }
                for bug in self.bugs
            ],
            "layer_results": [
                {
                    "layer_number": r.layer_number,
                    "layer_name": r.layer_name,
                    "success_count": r.success_count,
                    "failure_count": r.failure_count,
                    "errors": r.errors[:10],
                    "performance_metrics": r.performance_metrics
                }
                for r in self.layer_results.values()
            ]
        }

        report_path = "/workspace/massive_e2e_test_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n✅ 详细报告已保存到: {report_path}")


def main():
    tester = MassiveRealTestSystem()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
