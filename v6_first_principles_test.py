#!/usr/bin/env python3
"""
FullPathTest v6.0 - 第一性原理深度测试系统
遵循第一性原理：从最基本的假设出发，发现系统最深层的缺陷

核心原则：
1. 边界条件测试（0, 1, -1, 空, 无限大）
2. 并发竞争条件
3. 资源极限压力
4. 异常路径处理
5. 数据一致性保证
"""

import os
import sys
import time
import gc
import threading
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))


class FirstPrinciplesTestSystem:
    """第一性原理测试系统"""

    def __init__(self):
        self.start_time = datetime.now()
        self.results: List[Dict[str, Any]] = []
        self.defects_found: List[Dict[str, Any]] = []
        self.test_counter = 0

    def log(self, message: str, level: str = "INFO"):
        """日志"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [{level:8}] {message}")

    def log_defect(self, defect: Dict[str, Any]):
        """记录发现的缺陷"""
        self.defects_found.append(defect)
        self.log(f"🔴🔴🔴 发现深层缺陷: {defect['title']}", "DEFECT")
        self.log(f"    严重性: {defect['severity']}", "DEFECT")
        self.log(f"    根本原因: {defect['root_cause']}", "DEFECT")

    def test_01_boundary_conditions(self):
        """测试1: 边界条件（第一性原理：0, 1, -1, 空, 极限）"""
        self.log("=" * 70)
        self.log("测试1: 边界条件测试", "TEST")
        self.log("=" * 70)

        from fullpathtest.main import FullPathTestSystem
        system = FullPathTestSystem()

        boundary_cases = [
            ("空字符串路径", ""),
            ("单个字符路径", "/a"),
            ("超长路径", "/" + "x" * 10000),
            ("特殊字符路径", "/test/with spaces/and\tspecial/chars"),
            ("Unicode路径", "/测试/路径/测试"),
            ("仅点路径", "./"),
            ("仅双点路径", "../"),
            ("符号链接路径", "/tmp"),  # 可能指向其他位置
            ("根路径", "/"),
            ("不存在的路径", "/this/path/does/not/exist/12345"),
        ]

        defects = []

        for name, path in boundary_cases:
            self.log(f"测试边界: {name}", "TEST")
            try:
                start = time.time()
                result = system.run_full_test(source_path=path)
                duration = time.time() - start

                if result.get('status') != 'success':
                    defects.append({
                        'name': name,
                        'path': path,
                        'error': result.get('error', 'unknown'),
                        'duration': duration
                    })
                    self.log(f"  ❌ 失败: {result.get('error', 'unknown')[:80]}", "FAIL")
                else:
                    self.log(f"  ✅ 成功 ({duration:.3f}s)", "PASS")

            except Exception as e:
                defects.append({
                    'name': name,
                    'path': path,
                    'error': str(e),
                    'traceback': traceback.format_exc()
                })
                self.log(f"  ❌ 异常: {str(e)[:80]}", "ERROR")

        if defects:
            self.log_defect({
                'id': 'FP001',
                'severity': 'HIGH',
                'category': '边界条件',
                'title': f'边界条件处理不完善 ({len(defects)}个失败)',
                'description': f'发现{len(defects)}个边界条件处理问题',
                'root_cause': '缺乏对极端输入的防御性编程',
                'examples': defects[:3],
                'fix_suggestion': '添加完整的边界检查和异常处理'
            })

    def test_02_concurrent_stress(self):
        """测试2: 并发压力测试（第一性原理：多线程同时访问共享资源）"""
        self.log("=" * 70)
        self.log("测试2: 并发压力测试", "TEST")
        self.log("=" * 70)

        from fullpathtest.main import FullPathTestSystem

        errors = []
        success_count = [0]

        def concurrent_task(task_id: int):
            """并发任务"""
            try:
                system = FullPathTestSystem()
                result = system.run_full_test(
                    source_path="/workspace/cloned_fastapi_project/fastapi/__init__.py"
                )

                if result.get('status') == 'success':
                    success_count[0] += 1
                else:
                    errors.append({
                        'task_id': task_id,
                        'error': result.get('error'),
                        'status': result.get('status')
                    })
            except Exception as e:
                errors.append({
                    'task_id': task_id,
                    'error': str(e),
                    'type': type(e).__name__
                })

        # 启动20个并发任务
        self.log("启动20个并发任务...", "TEST")
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(concurrent_task, i) for i in range(20)]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    errors.append({'type': 'future_error', 'error': str(e)})

        duration = time.time() - start_time

        self.log(f"并发测试完成: {success_count[0]}/20 成功", "RESULT")
        self.log(f"总耗时: {duration:.2f}s, 平均: {duration/20:.3f}s/任务", "RESULT")

        if errors:
            self.log_defect({
                'id': 'FP002',
                'severity': 'CRITICAL',
                'category': '并发安全',
                'title': f'并发环境下出现{len(errors)}个错误',
                'description': f'20个并发任务中有{len(errors)}个失败',
                'root_cause': '缺乏线程安全保护，共享资源竞争',
                'examples': errors[:3],
                'fix_suggestion': '添加线程锁、队列保护、资源隔离'
            })

    def test_03_memory_extremes(self):
        """测试3: 内存极限测试（第一性原理：资源耗尽）"""
        self.log("=" * 70)
        self.log("测试3: 内存极限测试", "TEST")
        self.log("=" * 70)

        from fullpathtest.main import FullPathTestSystem
        system = FullPathTestSystem()

        # 创建超大代码文件
        temp_dir = Path("/tmp/v6_extreme_tests")
        temp_dir.mkdir(exist_ok=True)

        extreme_cases = [
            ("100行重复代码", "def func(x): return x\n" * 100),
            ("10000行重复代码", "def func(x): return x\n" * 10000),
            ("超长单行代码", f"x = " + "1+" * 10000),
            ("超深嵌套", "def f(): " * 100 + "return 1" + ")" * 100),
        ]

        memory_errors = []

        for name, content in extreme_cases:
            self.log(f"测试内存极限: {name}", "TEST")
            test_file = temp_dir / f"extreme_{name.split()[0]}.py"

            try:
                test_file.write_text(content)
                file_size = test_file.stat().st_size

                self.log(f"  文件大小: {file_size:,} bytes", "INFO")

                start = time.time()
                result = system.run_full_test(source_path=str(test_file))
                duration = time.time() - start

                if result.get('status') != 'success':
                    memory_errors.append({
                        'name': name,
                        'size': file_size,
                        'error': result.get('error')
                    })
                    self.log(f"  ❌ 失败: {result.get('error', 'unknown')[:60]}", "FAIL")
                else:
                    self.log(f"  ✅ 成功 ({duration:.3f}s)", "PASS")

            except MemoryError as e:
                memory_errors.append({
                    'name': name,
                    'error': 'MemoryError',
                    'type': 'memory_limit'
                })
                self.log(f"  ⚠️  内存错误: MemoryError", "WARN")
            except Exception as e:
                memory_errors.append({
                    'name': name,
                    'error': str(e),
                    'type': type(e).__name__
                })
                self.log(f"  ❌ 异常: {str(e)[:60]}", "ERROR")
            finally:
                if test_file.exists():
                    test_file.unlink()

        if memory_errors:
            self.log_defect({
                'id': 'FP003',
                'severity': 'HIGH',
                'category': '资源管理',
                'title': f'内存极限处理不完善 ({len(memory_errors)}个问题)',
                'description': f'处理超大文件时出现{len(memory_errors)}个内存相关错误',
                'root_cause': '缺乏流式处理和内存限制保护',
                'examples': memory_errors[:3],
                'fix_suggestion': '实现流式处理、内存限制、分块处理'
            })

    def test_04_data_consistency(self):
        """测试4: 数据一致性测试（第一性原理：同一输入产生同一输出）"""
        self.log("=" * 70)
        self.log("测试4: 数据一致性测试", "TEST")
        self.log("=" * 70)

        from fullpathtest.main import FullPathTestSystem
        system = FullPathTestSystem()

        test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"

        # 连续运行3次相同的测试
        results = []
        for i in range(3):
            self.log(f"第{i+1}次运行...", "TEST")
            try:
                result = system.run_full_test(source_path=test_path)

                results.append({
                    'run': i + 1,
                    'status': result.get('status'),
                    'coverage': result.get('coverage_report', {}).get('statement_coverage'),
                    'defects': len(result.get('defect_report', {}).get('defects', []))
                })

                self.log(f"  覆盖率: {result.get('coverage_report', {}).get('statement_coverage', 0)*100:.1f}%", "INFO")

            except Exception as e:
                results.append({
                    'run': i + 1,
                    'error': str(e)
                })
                self.log(f"  ❌ 异常: {str(e)[:60]}", "ERROR")

        # 检查一致性
        if results:
            statuses = [r.get('status') for r in results if 'status' in r]
            coverages = [r.get('coverage') for r in results if 'coverage' in r]

            if len(set(statuses)) > 1:
                self.log_defect({
                    'id': 'FP004',
                    'severity': 'MEDIUM',
                    'category': '数据一致性',
                    'title': '同一输入产生不同结果',
                    'description': '相同代码多次测试产生不同的状态',
                    'root_cause': '缺乏确定性执行保证',
                    'examples': results,
                    'fix_suggestion': '使用固定的随机种子，确保可重现性'
                })

            if coverages and max(coverages) - min(coverages) > 0.01:
                self.log_defect({
                    'id': 'FP005',
                    'severity': 'LOW',
                    'category': '数据一致性',
                    'title': '覆盖率结果不一致',
                    'description': f'最大差异: {max(coverages) - min(coverages):.2%}',
                    'root_cause': '采样或统计的随机性',
                    'examples': coverages,
                    'fix_suggestion': '增加采样数量或使用固定种子'
                })

    def test_05_exception_handling(self):
        """测试5: 异常处理完整性（第一性原理：每个异常都应被捕获）"""
        self.log("=" * 70)
        self.log("测试5: 异常处理完整性测试", "TEST")
        self.log("=" * 70)

        from fullpathtest.main import FullPathTestSystem
        system = FullPathTestSystem()

        exception_cases = [
            ("损坏的Python文件", b"\x00\x01\x02import sys"),
            ("二进制文件伪装", b"\x89PNG\r\n\x1a\n" + b"x" * 100),
            ("路径遍历攻击", "/workspace/../../etc/passwd"),
            ("循环导入模拟", "/workspace/fullpathtest/main.py"),  # 可能触发循环依赖
            ("超深递归目录", "/workspace"),  # 大量文件
        ]

        unhandled_exceptions = []

        for name, case in exception_cases:
            self.log(f"测试异常处理: {name}", "TEST")

            try:
                if isinstance(case, bytes):
                    test_file = Path("/tmp/exception_test.py")
                    test_file.write_bytes(case)
                    path = str(test_file)
                else:
                    path = case

                result = system.run_full_test(source_path=path)

                if result.get('status') != 'success':
                    error = result.get('error', '')
                    if 'Traceback' in error or 'Exception' in error:
                        unhandled_exceptions.append({
                            'name': name,
                            'error': error[:200]
                        })
                        self.log(f"  ⚠️  未处理异常: {error[:80]}", "WARN")
                    else:
                        self.log(f"  ✅ 已处理: {error[:60]}", "PASS")

                if isinstance(case, bytes) and test_file.exists():
                    test_file.unlink()

            except Exception as e:
                unhandled_exceptions.append({
                    'name': name,
                    'error': str(e),
                    'traceback': traceback.format_exc()[:500]
                })
                self.log(f"  ❌ 未捕获异常: {str(e)[:60]}", "ERROR")

        if unhandled_exceptions:
            self.log_defect({
                'id': 'FP006',
                'severity': 'HIGH',
                'category': '异常处理',
                'title': f'存在{len(unhandled_exceptions)}个未处理异常',
                'description': '部分异常未被适当捕获和处理',
                'root_cause': '异常处理不完整或异常类型遗漏',
                'examples': unhandled_exceptions[:3],
                'fix_suggestion': '完善异常处理，增加更多异常类型捕获'
            })

    def test_06_integration_deep(self):
        """测试6: 深度集成测试（完整真实项目）"""
        self.log("=" * 70)
        self.log("测试6: 深度集成测试 - Django项目", "TEST")
        self.log("=" * 70)

        from fullpathtest.main import FullPathTestSystem
        system = FullPathTestSystem()

        self.log("测试Django完整项目...", "TEST")

        try:
            start = time.time()
            result = system.run_full_test(
                source_path="/workspace/django_project",
                user_command="全面深度测试Django框架"
            )
            duration = time.time() - start

            self.log(f"覆盖率: {result.get('coverage_report', {}).get('statement_coverage', 0)*100:.1f}%", "RESULT")
            self.log(f"缺陷数: {len(result.get('defect_report', {}).get('defects', []))}", "RESULT")
            self.log(f"耗时: {duration:.2f}s", "RESULT")

            if result.get('status') != 'success':
                self.log_defect({
                    'id': 'FP007',
                    'severity': 'HIGH',
                    'category': '集成测试',
                    'title': 'Django项目测试失败',
                    'description': f'大型真实项目测试失败: {result.get("error", "unknown")}',
                    'root_cause': '系统处理复杂项目的逻辑缺陷',
                    'examples': [result.get('error', '')],
                    'fix_suggestion': '优化项目结构处理逻辑'
                })

        except Exception as e:
            self.log(f"❌ 集成测试异常: {str(e)}", "ERROR")
            self.log_defect({
                'id': 'FP008',
                'severity': 'CRITICAL',
                'category': '集成测试',
                'title': '集成测试完全失败',
                'description': f'深度集成测试抛出未捕获异常: {str(e)}',
                'root_cause': '核心逻辑存在致命缺陷',
                'examples': [traceback.format_exc()[:500]],
                'fix_suggestion': '立即修复核心逻辑'
            })

    def run_all_tests(self):
        """运行所有第一性原理测试"""
        self.log("\n" + "=" * 70)
        self.log("FullPathTest v6.0 - 第一性原理深度测试系统")
        self.log("=" * 70)
        self.log("从最基本的假设出发，发现系统最深层的缺陷", "INFO")
        self.log("=" * 70)

        total_start = time.time()

        # 执行所有测试
        self.test_01_boundary_conditions()
        self.test_02_concurrent_stress()
        self.test_03_memory_extremes()
        self.test_04_data_consistency()
        self.test_05_exception_handling()
        self.test_06_integration_deep()

        total_duration = time.time() - total_start

        # 生成报告
        self.generate_report(total_duration)

    def generate_report(self, total_duration: float):
        """生成第一性原理分析报告"""
        self.log("\n" + "=" * 70)
        self.log("第一性原理分析报告", "REPORT")
        self.log("=" * 70)

        total_defects = len(self.defects_found)

        self.log(f"\n📊 总体统计:", "REPORT")
        self.log(f"   总缺陷数: {total_defects}", "REPORT")
        self.log(f"   总测试耗时: {total_duration:.2f}秒", "REPORT")

        # 按严重性分组
        severity_counts = {}
        for d in self.defects_found:
            sev = d.get('severity', 'UNKNOWN')
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        self.log(f"\n🔴 按严重性分类:", "REPORT")
        for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = severity_counts.get(sev, 0)
            if count > 0:
                self.log(f"   {sev}: {count}个", "REPORT")

        self.log(f"\n📝 缺陷摘要:", "REPORT")
        for i, defect in enumerate(self.defects_found, 1):
            self.log(f"   {i}. [{defect['id']}] {defect['title']}", "REPORT")
            self.log(f"      根本原因: {defect['root_cause']}", "REPORT")

        # 保存详细报告
        report_path = Path("/workspace/v6_first_principles_report.json")
        import json

        report = {
            'summary': {
                'total_defects': total_defects,
                'total_duration': total_duration,
                'timestamp': datetime.now().isoformat()
            },
            'defects': self.defects_found
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.log(f"\n✅ 详细报告已保存到: {report_path}", "REPORT")


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("FullPathTest v6.0 - 第一性原理深度测试系统")
    print("=" * 70)
    print("\n⚠️  注意：这将进行超深度、超复杂的第一性原理测试")
    print("⚠️  目的：从最基本的假设出发，发现系统最深层的缺陷\n")

    system = FirstPrinciplesTestSystem()
    system.run_all_tests()


if __name__ == "__main__":
    main()
