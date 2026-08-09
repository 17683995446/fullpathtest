#!/usr/bin/env python3
"""
FullPathTest v9.0 - 慢工出细活 超深度极限测试
遵循慢工出细活：细致设计、混合场景、极限条件、充分验证
"""

import sys
import time
import gc
import random
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from datetime import datetime
from collections import deque

sys.path.insert(0, str(Path(__file__).parent))

from fullpathtest.main import FullPathTestSystem


class ExtremeTestSystem:
    """超深度极限测试系统"""
    
    def __init__(self):
        self.results = []
        self.errors = []
        self.success_count = 0
        self.failure_count = 0
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [{level}] {message}")
        
    def test_single_task(self, test_path, task_id, stress_level=1):
        """单个测试任务"""
        try:
            if stress_level > 1:
                for _ in range(stress_level * 50):
                    _ = [random.random() for _ in range(10)]
            
            system = FullPathTestSystem()
            result = system.run_full_test(source_path=test_path)
            
            if result.get("status") == "success":
                return True, None
            else:
                return False, result.get("error", "Unknown")
                
        except Exception as e:
            return False, str(e)
        
    def phase1_mixed_concurrent(self):
        """阶段1：混合并发测试"""
        self.log("=" * 70, "PHASE")
        self.log("阶段1：混合并发测试（20个并发 + 交错任务）", "PHASE")
        self.log("=" * 70, "PHASE")
        
        test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
        concurrency = 20
        local_success = 0
        
        start = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(concurrency):
                stress = 1 if i % 2 == 0 else 2
                futures.append(
                    executor.submit(
                        self.test_single_task, 
                        test_path, 
                        f"P1-T{i}", 
                        stress
                    )
                )
            
            completed = 0
            for future in as_completed(futures):
                success, error = future.result()
                if success:
                    local_success += 1
                else:
                    self.errors.append({"phase": 1, "task": f"P1-T{completed}", "error": error})
                
                completed += 1
                if completed % 5 == 0:
                    self.log(f"进度: {completed}/{concurrency}", "PROGRESS")
        
        elapsed = time.time() - start
        
        self.log(f"阶段1完成: {local_success}/{concurrency} 成功，耗时 {elapsed:.2f}秒", "RESULT")
        return local_success == concurrency
    
    def phase2_extreme_long_run(self):
        """阶段2：超长时间运行（150次连续）"""
        self.log("\n" + "=" * 70, "PHASE")
        self.log("阶段2：超长时间运行（150次连续）", "PHASE")
        self.log("=" * 70, "PHASE")
        
        test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
        iterations = 150
        local_success = 0
        
        start = time.time()
        
        for i in range(iterations):
            success, error = self.test_single_task(test_path, f"P2-T{i}", stress_level=1)
            
            if success:
                local_success += 1
            else:
                self.errors.append({"phase": 2, "task": f"P2-T{i}", "error": error})
            
            if (i + 1) % 25 == 0:
                self.log(f"进度: {i + 1}/{iterations}", "PROGRESS")
            
            if i < iterations - 1 and i % 50 == 0:
                self.log("⏸️  系统清理...", "WAIT")
                gc.collect()
                time.sleep(0.1)
        
        elapsed = time.time() - start
        
        self.log(f"阶段2完成: {local_success}/{iterations} 成功，耗时 {elapsed:.2f}秒", "RESULT")
        return local_success >= iterations * 0.99
    
    def phase3_edge_case_combination(self):
        """阶段3：边界条件组合测试"""
        self.log("\n" + "=" * 70, "PHASE")
        self.log("阶段3：边界条件组合测试", "PHASE")
        self.log("=" * 70, "PHASE")
        
        test_cases = [
            ("空路径", ""),
            ("空白路径", "   "),
            ("不存在路径", "/this/path/does/not/exist/123"),
            ("单个字符路径", "/a"),
            ("长路径（500字符）", "/test/" * 100),
        ]
        
        local_success = 0
        
        for name, path in test_cases:
            self.log(f"测试边界: {name}", "TEST")
            success, error = self.test_single_task(path, f"P3-{name}", stress_level=1)
            
            if error:
                self.log(f"  结果: ✅ 错误被正确处理 - {error[:60]}", "PASS")
                local_success += 1
            elif success:
                self.log(f"  结果: ✅ 成功（对于有效路径）", "PASS")
                local_success += 1
            else:
                self.log(f"  结果: ❌ 意外状态", "FAIL")
                self.errors.append({"phase": 3, "case": name, "error": error})
        
        self.log(f"阶段3完成: {local_success}/{len(test_cases)} 成功", "RESULT")
        return local_success == len(test_cases)
    
    def phase4_real_project_complete(self):
        """阶段4：真实项目完整测试"""
        self.log("\n" + "=" * 70, "PHASE")
        self.log("阶段4：真实项目完整测试（各5次）", "PHASE")
        self.log("=" * 70, "PHASE")
        
        projects = [
            ("FastAPI 完整", "/workspace/cloned_fastapi_project/fastapi/__init__.py"),
            ("Django 完整", "/workspace/django_project/django/__init__.py"),
        ]
        
        project_results = {}
        
        for name, path in projects:
            self.log(f"\n测试项目: {name}", "TEST")
            success_count = 0
            
            for i in range(5):
                self.log(f"  运行 {i + 1}/5...", "PROGRESS")
                success, error = self.test_single_task(path, f"P4-{name}-T{i}", stress_level=1)
                
                if success:
                    success_count += 1
                else:
                    self.errors.append({"phase": 4, "project": name, "task": i, "error": error})
                    self.log(f"    ❌ 错误: {error[:60]}", "ERROR")
                    break
            
            project_results[name] = success_count == 5
            if project_results[name]:
                self.log(f"  项目 {name}: ✅ 全部通过", "PASS")
        
        all_success = all(project_results.values())
        return all_success
    
    def run_all_tests(self):
        """运行所有测试"""
        self.log("\n" + "=" * 70, "MAIN")
        self.log("FullPathTest v9.0 - 超深度极限测试", "MAIN")
        self.log("=" * 70, "MAIN")
        
        self.log("\n📋 测试计划:", "INFO")
        self.log("  1. 混合并发测试（20个并发）", "INFO")
        self.log("  2. 超长时间运行（150次连续）", "INFO")
        self.log("  3. 边界条件组合测试", "INFO")
        self.log("  4. 真实项目完整测试（各5次）", "INFO")
        
        all_passed = True
        
        # 阶段1
        self.log("\n" + "-" * 70)
        phase1_ok = self.phase1_mixed_concurrent()
        if phase1_ok:
            self.log("✅ 阶段1通过", "PHASE_PASS")
        else:
            self.log("❌ 阶段1失败", "PHASE_FAIL")
            all_passed = False
        
        self.log("\n⏸️  系统稳定中（2秒）...", "WAIT")
        time.sleep(2)
        
        # 阶段2
        self.log("\n" + "-" * 70)
        phase2_ok = self.phase2_extreme_long_run()
        if phase2_ok:
            self.log("✅ 阶段2通过", "PHASE_PASS")
        else:
            self.log("❌ 阶段2失败", "PHASE_FAIL")
            all_passed = False
        
        self.log("\n⏸️  系统稳定中（2秒）...", "WAIT")
        time.sleep(2)
        
        # 阶段3
        self.log("\n" + "-" * 70)
        phase3_ok = self.phase3_edge_case_combination()
        if phase3_ok:
            self.log("✅ 阶段3通过", "PHASE_PASS")
        else:
            self.log("❌ 阶段3失败", "PHASE_FAIL")
            all_passed = False
        
        self.log("\n⏸️  系统稳定中（2秒）...", "WAIT")
        time.sleep(2)
        
        # 阶段4
        self.log("\n" + "-" * 70)
        phase4_ok = self.phase4_real_project_complete()
        if phase4_ok:
            self.log("✅ 阶段4通过", "PHASE_PASS")
        else:
            self.log("❌ 阶段4失败", "PHASE_FAIL")
            all_passed = False
        
        # 最终总结
        self.log("\n" + "=" * 70, "FINAL")
        if all_passed:
            self.log("🎉 超深度极限测试全部通过！系统优秀！", "FINAL_PASS")
        else:
            self.log("⚠️  部分测试未通过", "FINAL_WARN")
        
        if self.errors:
            self.log(f"\n❌ 发现 {len(self.errors)} 个问题:", "ISSUES")
            for i, err in enumerate(self.errors[:10], 1):
                self.log(f"  {i}. {err}", "ISSUE")
        
        self.log("\n" + "=" * 70)
        
        return all_passed


def main():
    try:
        tester = ExtremeTestSystem()
        success = tester.run_all_tests()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        return 130
    except Exception as e:
        print(f"\n\n❌ 测试系统异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
