#!/usr/bin/env python3
"""
FullPathTest v8.0 - 慢工出细活 深度压力测试系统
遵循慢工出细活：细致设计、逐步深入、充分验证
"""

import sys
import time
import traceback
import gc
import random
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from collections import defaultdict, deque

sys.path.insert(0, str(Path(__file__).parent))

from fullpathtest.main import FullPathTestSystem


class SlowButSteadyTester:
    """慢工出细活的深度压力测试器"""
    
    def __init__(self):
        self.results = []
        self.errors = []
        self.success_count = 0
        self.failure_count = 0
        self.task_times = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [{level}] {message}")
        
    def single_task(self, task_id, test_path, stress_level=1):
        """单个测试任务（带压力）"""
        start_time = time.time()
        try:
            # 模拟工作压力
            if stress_level > 1:
                for i in range(stress_level * 100):
                    _ = [x * x for x in range(100)]
            
            system = FullPathTestSystem()
            result = system.run_full_test(source_path=test_path)
            
            elapsed = time.time() - start_time
            self.task_times.append(elapsed)
            
            status = result.get("status")
            if status == "success":
                self.success_count += 1
                return True
            else:
                self.failure_count += 1
                self.errors.append({
                    "task_id": task_id,
                    "error": result.get("error", "Unknown"),
                    "type": "api_error"
                })
                return False
                
        except Exception as e:
            elapsed = time.time() - start_time
            self.task_times.append(elapsed)
            self.failure_count += 1
            self.errors.append({
                "task_id": task_id,
                "error": str(e),
                "type": "exception",
                "traceback": traceback.format_exc()
            })
            return False
    
    def phase_1_medium_concurrent(self):
        """阶段1：中等并发测试（20个并发）"""
        self.log("=" * 70, "PHASE")
        self.log("阶段1：中等并发测试（20个并发）", "PHASE")
        self.log("=" * 70, "PHASE")
        
        test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
        concurrency = 20
        
        start_time = time.time()
        local_success = 0
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {}
            for i in range(concurrency):
                future = executor.submit(
                    self.single_task, 
                    f"P1-T{i}", 
                    test_path, 
                    stress_level=1
                )
                futures[future] = i
            
            completed = 0
            for future in as_completed(futures):
                try:
                    if future.result():
                        local_success += 1
                    completed += 1
                    if completed % 5 == 0:
                        self.log(f"进度: {completed}/{concurrency}", "PROGRESS")
                except Exception as e:
                    self.log(f"任务异常: {str(e)[:60]}", "ERROR")
        
        elapsed = time.time() - start_time
        
        self.log(f"\n阶段1完成:", "RESULT")
        self.log(f"  成功: {local_success}/{concurrency}", "RESULT")
        self.log(f"  总耗时: {elapsed:.2f}秒", "RESULT")
        if self.task_times:
            self.log(f"  平均: {sum(self.task_times)/len(self.task_times):.3f}秒/任务", "RESULT")
            self.log(f"  最快: {min(self.task_times):.3f}秒", "RESULT")
            self.log(f"  最慢: {max(self.task_times):.3f}秒", "RESULT")
        
        return local_success == concurrency
    
    def phase_2_high_concurrent(self):
        """阶段2：高并发测试（50个并发）"""
        self.log("\n" + "=" * 70, "PHASE")
        self.log("阶段2：高并发测试（50个并发）", "PHASE")
        self.log("=" * 70, "PHASE")
        
        test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
        concurrency = 50
        
        start_time = time.time()
        local_success = 0
        phase_task_times = []
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {}
            for i in range(concurrency):
                future = executor.submit(
                    self.single_task, 
                    f"P2-T{i}", 
                    test_path, 
                    stress_level=1
                )
                futures[future] = i
            
            completed = 0
            for future in as_completed(futures):
                try:
                    if future.result():
                        local_success += 1
                    completed += 1
                    if completed % 10 == 0:
                        self.log(f"进度: {completed}/{concurrency}", "PROGRESS")
                except Exception as e:
                    self.log(f"任务异常: {str(e)[:60]}", "ERROR")
        
        elapsed = time.time() - start_time
        
        self.log(f"\n阶段2完成:", "RESULT")
        self.log(f"  成功: {local_success}/{concurrency}", "RESULT")
        self.log(f"  总耗时: {elapsed:.2f}秒", "RESULT")
        
        return local_success >= concurrency * 0.95  # 允许5%失败率
    
    def phase_3_long_running(self):
        """阶段3：长时间运行测试（100次连续，间隔0.5秒）"""
        self.log("\n" + "=" * 70, "PHASE")
        self.log("阶段3：长时间运行测试（100次连续）", "PHASE")
        self.log("=" * 70, "PHASE")
        
        test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
        iterations = 100
        
        start_time = time.time()
        local_success = 0
        memory_samples = []
        
        for i in range(iterations):
            task_start = time.time()
            success = self.single_task(f"P3-T{i}", test_path, stress_level=2)
            task_time = time.time() - task_start
            
            if success:
                local_success += 1
            
            if (i + 1) % 20 == 0:
                self.log(f"进度: {i + 1}/{iterations}", "PROGRESS")
            
            # 间隔时间
            if i < iterations - 1:
                time.sleep(0.2)
        
        elapsed = time.time() - start_time
        
        self.log(f"\n阶段3完成:", "RESULT")
        self.log(f"  成功: {local_success}/{iterations}", "RESULT")
        self.log(f"  总耗时: {elapsed:.2f}秒", "RESULT")
        
        return local_success >= iterations * 0.99  # 99%成功率要求
    
    def phase_4_real_projects(self):
        """阶段4：真实项目测试（更深入）"""
        self.log("\n" + "=" * 70, "PHASE")
        self.log("阶段4：真实项目深度测试", "PHASE")
        self.log("=" * 70, "PHASE")
        
        projects = [
            ("FastAPI 完整", "/workspace/cloned_fastapi_project/fastapi/__init__.py"),
            ("Django 完整", "/workspace/django_project/django/__init__.py"),
        ]
        
        results = []
        
        for name, path in projects:
            self.log(f"\n测试项目: {name}", "TEST")
            
            try:
                # 每个项目测试3次，确保稳定性
                project_success = 0
                for i in range(3):
                    system = FullPathTestSystem()
                    result = system.run_full_test(source_path=path)
                    
                    if result.get("status") == "success":
                        project_success += 1
                        coverage = result.get("coverage_report").statement_coverage * 100
                        defect_count = len(result.get("defect_report").defects)
                        self.log(f"  运行 {i+1}: ✅ 成功, 覆盖率 {coverage:.1f}%, 缺陷 {defect_count}", "PASS")
                    else:
                        self.log(f"  运行 {i+1}: ❌ 失败 - {result.get('error', 'Unknown')[:60]}", "FAIL")
                
                if project_success == 3:
                    self.log(f"  项目 {name}: ✅ 全部通过", "RESULT")
                    results.append((name, True))
                else:
                    self.log(f"  项目 {name}: ⚠️ {project_success}/3 通过", "WARN")
                    results.append((name, False))
                    
            except Exception as e:
                self.log(f"  项目 {name}: ❌ 异常 - {str(e)[:60]}", "ERROR")
                results.append((name, False))
        
        success_count = sum(1 for _, success in results if success)
        self.log(f"\n真实项目测试: {success_count}/{len(projects)} 通过", "RESULT")
        
        return success_count == len(projects)
    
    def run_all_phases(self):
        """运行所有测试阶段"""
        self.log("\n" + "=" * 70, "MAIN")
        self.log("FullPathTest v8.0 - 慢工出细活 深度压力测试", "MAIN")
        self.log("=" * 70, "MAIN")
        
        self.log("\n📋 测试计划:")
        self.log("  1. 中等并发测试（20并发）")
        self.log("  2. 高并发测试（50并发）")
        self.log("  3. 长时间运行测试（100次连续）")
        self.log("  4. 真实项目深度测试")
        
        phase_results = []
        
        # 阶段1
        self.log("\n" + "-" * 70)
        if self.phase_1_medium_concurrent():
            self.log("✅ 阶段1通过", "PHASE_PASS")
            phase_results.append(True)
        else:
            self.log("❌ 阶段1失败", "PHASE_FAIL")
            phase_results.append(False)
        
        # 慢工出细活：阶段间稳定时间
        self.log("\n⏸️  系统稳定中（3秒）...", "WAIT")
        time.sleep(3)
        
        # 阶段2
        self.log("\n" + "-" * 70)
        if self.phase_2_high_concurrent():
            self.log("✅ 阶段2通过", "PHASE_PASS")
            phase_results.append(True)
        else:
            self.log("❌ 阶段2失败", "PHASE_FAIL")
            phase_results.append(False)
        
        self.log("\n⏸️  系统稳定中（3秒）...", "WAIT")
        time.sleep(3)
        
        # 阶段3
        self.log("\n" + "-" * 70)
        if self.phase_3_long_running():
            self.log("✅ 阶段3通过", "PHASE_PASS")
            phase_results.append(True)
        else:
            self.log("❌ 阶段3失败", "PHASE_FAIL")
            phase_results.append(False)
        
        self.log("\n⏸️  系统稳定中（2秒）...", "WAIT")
        time.sleep(2)
        
        # 阶段4
        self.log("\n" + "-" * 70)
        if self.phase_4_real_projects():
            self.log("✅ 阶段4通过", "PHASE_PASS")
            phase_results.append(True)
        else:
            self.log("❌ 阶段4失败", "PHASE_FAIL")
            phase_results.append(False)
        
        # 总结
        self.log("\n" + "=" * 70, "FINAL")
        all_passed = all(phase_results)
        
        if all_passed:
            self.log("🎉 深度压力测试全部通过！系统健壮性优秀！", "FINAL_PASS")
        else:
            self.log(f"⚠️  部分阶段未通过: {sum(phase_results)}/{len(phase_results)} 通过", "FINAL_WARN")
        
        if self.errors:
            self.log(f"\n❌ 发现 {len(self.errors)} 个问题:", "ISSUES")
            for i, error in enumerate(self.errors[:10], 1):
                self.log(f"  {i}. [{error.get('task_id')}] {error.get('error', 'Unknown')[:60]}", "ISSUE")
        
        self.log("\n" + "=" * 70)
        
        return all_passed


def main():
    """主函数"""
    try:
        tester = SlowButSteadyTester()
        success = tester.run_all_phases()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断测试")
        return 130
    except Exception as e:
        print(f"\n\n❌ 测试系统异常: {str(e)}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
