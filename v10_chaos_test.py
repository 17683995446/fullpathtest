#!/usr/bin/env python3
"""
FullPathTest v10.0 - 慢工出细活 极端混乱测试系统
遵循慢工出细活：极端场景、混乱输入、高并发、长时运行、充分验证
"""

import sys
import time
import gc
import random
import threading
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from datetime import datetime
from collections import deque

sys.path.insert(0, str(Path(__file__).parent))

from fullpathtest.main import FullPathTestSystem


class ChaosTestSystem:
    """极端混乱测试系统"""
    
    def __init__(self):
        self.results = []
        self.errors = []
        self.success_count = 0
        self.failure_count = 0
        self.test_path_fastapi = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
        self.test_path_django = "/workspace/django_project/django/__init__.py"
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [{level}] {message}")
        
    def generate_chaos_input(self, i):
        """生成混乱测试输入"""
        chaos_types = [
            ("normal", self.test_path_fastapi),
            ("empty", ""),
            ("blank", "   "),
            ("nonexistent", f"/nonexistent/path/{i}"),
            ("long", "/test/" * 200),
            ("special", "/test/with spaces/\t/newlines/"),
            ("unicode", "/测试/路径/测试"),
            ("dots", "./././"),
            ("double_dots", "../../../"),
        ]
        return random.choice(chaos_types)
        
    def test_chaos_task(self, i):
        """单个混乱测试任务"""
        try:
            # 随机选择测试路径
            chaos_type, path = self.generate_chaos_input(i)
            
            # 随机添加额外混乱
            if random.random() < 0.2:
                stress = 1
                for _ in range(random.randint(0, 100)):
                    _ = [x*x for x in range(10)]
            else:
                stress = 1
                
            system = FullPathTestSystem()
            result = system.run_full_test(source_path=path)
            
            status = result.get("status")
            if status == "success":
                return True, None, f"chaos:{chaos_type}"
            else:
                return False, result.get("error", "Unknown"), f"chaos:{chaos_type}"
                
        except Exception as e:
            return False, str(e), "exception"
        
    def phase1_chaos_concurrent(self):
        """阶段1：混乱并发测试（30个）"""
        self.log("=" * 70, "PHASE")
        self.log("阶段1：混乱并发测试（30个并发，混合正常和混乱输入）", "PHASE")
        self.log("=" * 70, "PHASE")
        
        concurrency = 30
        local_success = 0
        local_failures = []
        
        start = time.time()
        
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = []
            for i in range(concurrency):
                futures.append(executor.submit(self.test_chaos_task, i))
                
            completed = 0
            for future in as_completed(futures):
                success, error, tag = future.result()
                if success:
                    local_success += 1
                else:
                    if "路径不能为空" in str(error) or "目录不存在" in str(error):
                        # 这是预期的错误
                        local_success += 1
                    else:
                        local_failures.append(f"{tag}: {error}")
                        
                completed += 1
                if completed % 10 == 0:
                    self.log(f"进度: {completed}/{concurrency}", "PROGRESS")
        
        elapsed = time.time() - start
        
        self.log(f"阶段1完成: {local_success}/{concurrency} 成功处理，耗时 {elapsed:.2f}秒", "RESULT")
        if local_failures:
            self.log(f"  注意: {len(local_failures)} 个非预期失败", "WARN")
            for fail in local_failures[:5]:
                self.log(f"    {fail}", "WARN")
        
        return len(local_failures) == 0
        
    def phase2_extreme_long_run(self):
        """阶段2：超长时间运行（200次连续，混合混乱输入）"""
        self.log("\n" + "=" * 70, "PHASE")
        self.log("阶段2：超长时间运行（200次连续，混合正常和混乱输入）", "PHASE")
        self.log("=" * 70, "PHASE")
        
        iterations = 200
        local_success = 0
        local_failures = []
        
        start = time.time()
        
        for i in range(iterations):
            success, error, tag = self.test_chaos_task(i)
            
            if success:
                local_success += 1
            else:
                if "路径不能为空" in str(error) or "目录不存在" in str(error):
                    # 预期错误
                    local_success += 1
                else:
                    local_failures.append(f"{i}:{tag}: {error}")
            
            if (i + 1) % 50 == 0:
                self.log(f"进度: {i + 1}/{iterations}", "PROGRESS")
            
            if i < iterations - 1 and i % 100 == 0:
                self.log("⏸️  系统清理...", "WAIT")
                gc.collect()
                time.sleep(0.1)
        
        elapsed = time.time() - start
        
        self.log(f"阶段2完成: {local_success}/{iterations} 成功处理，耗时 {elapsed:.2f}秒", "RESULT")
        if local_failures:
            self.log(f"  注意: {len(local_failures)} 个非预期失败", "WARN")
            for fail in local_failures[:5]:
                self.log(f"    {fail}", "WARN")
        
        return len(local_failures) == 0
        
    def phase3_chaos_sequence(self):
        """阶段3：混乱序列测试（快速切换不同输入）"""
        self.log("\n" + "=" * 70, "PHASE")
        self.log("阶段3：混乱序列测试（快速切换不同输入）", "PHASE")
        self.log("=" * 70, "PHASE")
        
        chaos_sequence = [
            self.test_path_fastapi,
            "",
            self.test_path_fastapi,
            "   ",
            self.test_path_fastapi,
            "/nonexistent",
            self.test_path_fastapi,
            "/test/"*100,
            self.test_path_fastapi,
            "/测试/路径",
        ]
        
        local_success = 0
        local_failures = []
        
        for i, path in enumerate(chaos_sequence):
            try:
                system = FullPathTestSystem()
                result = system.run_full_test(source_path=path)
                
                if result.get("status") == "success":
                    local_success += 1
                else:
                    error = result.get("error", "Unknown")
                    if "路径不能为空" in error or "目录不存在" in error:
                        local_success += 1
                    else:
                        local_failures.append(f"seq{i}: {error}")
                    
            except Exception as e:
                local_failures.append(f"seq{i}: EXCEPTION - {str(e)}")
        
        self.log(f"阶段3完成: {local_success}/{len(chaos_sequence)} 成功处理", "RESULT")
        if local_failures:
            self.log(f"  注意: {len(local_failures)} 个问题", "WARN")
            for fail in local_failures:
                self.log(f"    {fail}", "WARN")
        
        return len(local_failures) == 0
        
    def phase4_real_projects_chaos(self):
        """阶段4：真实项目+混乱测试（混合正常/混乱输入）"""
        self.log("\n" + "=" * 70, "PHASE")
        self.log("阶段4：真实项目+混乱测试（混合正常/混乱输入）", "PHASE")
        self.log("=" * 70, "PHASE")
        
        test_sets = [
            ("FastAPI", self.test_path_fastapi),
            ("Django", self.test_path_django),
        ]
        
        all_success = True
        for name, good_path in test_sets:
            self.log(f"测试项目: {name}", "TEST")
            
            # 混合测试序列
            test_paths = [good_path, "", good_path, "/nonexistent", good_path]
            local_failures = []
            
            for i, path in enumerate(test_paths):
                try:
                    system = FullPathTestSystem()
                    result = system.run_full_test(source_path=path)
                    
                    if result.get("status") == "success":
                        self.log(f"  运行 {i+1}: ✅ 成功", "PASS")
                    else:
                        error = result.get("error", "Unknown")
                        if "路径不能为空" in error or "目录不存在" in error:
                            self.log(f"  运行 {i+1}: ✅ 正确处理错误 - {error[:60]}", "PASS")
                        else:
                            self.log(f"  运行 {i+1}: ❌ 失败 - {error}", "FAIL")
                            local_failures.append(f"{name}:{i}")
                            all_success = False
                            
                except Exception as e:
                    self.log(f"  运行 {i+1}: ❌ 异常 - {str(e)}", "ERROR")
                    local_failures.append(f"{name}:{i}")
                    all_success = False
        
        return all_success
        
    def run_all_tests(self):
        """运行所有测试"""
        self.log("\n" + "=" * 70, "MAIN")
        self.log("FullPathTest v10.0 - 极端混乱测试系统", "MAIN")
        self.log("=" * 70, "MAIN")
        
        self.log("\n📋 测试计划:", "INFO")
        self.log("  1. 混乱并发测试（30个并发）", "INFO")
        self.log("  2. 超长时间运行（200次连续）", "INFO")
        self.log("  3. 混乱序列测试（快速切换）", "INFO")
        self.log("  4. 真实项目+混乱测试", "INFO")
        
        phase_results = []
        
        # 阶段1
        self.log("\n" + "-" * 70)
        p1_ok = self.phase1_chaos_concurrent()
        phase_results.append(("阶段1", p1_ok))
        if p1_ok:
            self.log("✅ 阶段1通过", "PHASE_PASS")
        else:
            self.log("⚠️ 阶段1有问题", "PHASE_WARN")
        
        self.log("\n⏸️  系统稳定中（2秒）...", "WAIT")
        time.sleep(2)
        
        # 阶段2
        self.log("\n" + "-" * 70)
        p2_ok = self.phase2_extreme_long_run()
        phase_results.append(("阶段2", p2_ok))
        if p2_ok:
            self.log("✅ 阶段2通过", "PHASE_PASS")
        else:
            self.log("⚠️ 阶段2有问题", "PHASE_WARN")
        
        self.log("\n⏸️  系统稳定中（2秒）...", "WAIT")
        time.sleep(2)
        
        # 阶段3
        self.log("\n" + "-" * 70)
        p3_ok = self.phase3_chaos_sequence()
        phase_results.append(("阶段3", p3_ok))
        if p3_ok:
            self.log("✅ 阶段3通过", "PHASE_PASS")
        else:
            self.log("⚠️ 阶段3有问题", "PHASE_WARN")
        
        self.log("\n⏸️  系统稳定中（2秒）...", "WAIT")
        time.sleep(2)
        
        # 阶段4
        self.log("\n" + "-" * 70)
        p4_ok = self.phase4_real_projects_chaos()
        phase_results.append(("阶段4", p4_ok))
        if p4_ok:
            self.log("✅ 阶段4通过", "PHASE_PASS")
        else:
            self.log("⚠️ 阶段4有问题", "PHASE_WARN")
        
        # 总结
        self.log("\n" + "=" * 70, "FINAL")
        all_ok = all(ok for _, ok in phase_results)
        
        if all_ok:
            self.log("🎉 极端混乱测试全部通过！系统超级健壮！", "FINAL_PASS")
        else:
            self.log("⚠️ 部分测试阶段有问题", "FINAL_WARN")
            for name, ok in phase_results:
                status = "✅ 通过" if ok else "❌ 有问题"
                self.log(f"  {name}: {status}", "FINAL")
        
        self.log("\n" + "=" * 70)
        
        return all_ok


def main():
    try:
        tester = ChaosTestSystem()
        success = tester.run_all_tests()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
        return 130
    except Exception as e:
        print(f"\n\n❌ 测试系统异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
