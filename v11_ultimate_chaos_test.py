#!/usr/bin/env python3
"""
FullPathTest v11.0 - 慢工出细活 超大规模极端混乱测试
遵循慢工出细活：逐步扩大规模、混合多种混乱、超长时间运行
"""

import sys
import time
import gc
import random
import threading
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from collections import deque

sys.path.insert(0, str(Path(__file__).parent))

from fullpathtest.main import FullPathTestSystem


class UltimateChaosTestSystem:
    """超大规模极端混乱测试系统"""
    
    def __init__(self):
        self.results = []
        self.errors = []
        self.success_count = 0
        self.failure_count = 0
        self.start_time = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [{level}] {message}")
        
    def generate_extreme_chaos_input(self, index):
        """生成极端混乱的测试输入"""
        # 极端混乱的输入类型
        chaos_type = random.choice([
            'normal_fastapi',
            'normal_django',
            'empty',
            'blank',
            'nonexistent_random',
            'ultra_long_path',
            'special_chars',
            'unicode_cn',
            'unicode_jp',
            'relative_path',
            'parent_path',
            'mixed_case',
            'trailing_slash',
            'no_permission',
            'partial_path'
        ])
        
        test_path = self.test_path_fastapi
        
        if chaos_type == 'normal_fastapi':
            test_path = self.test_path_fastapi
        elif chaos_type == 'normal_django':
            test_path = self.test_path_django
        elif chaos_type == 'empty':
            test_path = ''
        elif chaos_type == 'blank':
            test_path = '   \t\n\r  '
        elif chaos_type == 'nonexistent_random':
            test_path = f"/nonexistent/path/to/project/{random.randint(1, 1000000)}"
        elif chaos_type == 'ultra_long_path':
            test_path = '/test/' * 500  # 超长路径
        elif chaos_type == 'special_chars':
            test_path = '/test/with spaces/\t/newlines/\r/\x00/💻/äéü/'
        elif chaos_type == 'unicode_cn':
            test_path = '/测试/路径/中文/项目/代码'
        elif chaos_type == 'unicode_jp':
            test_path = '/テスト/パス/日本語/プロジェクト'
        elif chaos_type == 'relative_path':
            test_path = './././././'
        elif chaos_type == 'parent_path':
            test_path = '../../../../../'
        elif chaos_type == 'mixed_case':
            test_path = '/TesT/PrOjEcT/CoDe'
        elif chaos_type == 'trailing_slash':
            test_path = self.test_path_fastapi + '/'
        elif chaos_type == 'no_permission':
            test_path = '/root/'
        elif chaos_type == 'partial_path':
            test_path = '/workspace/'
            
        return chaos_type, test_path
        
    def test_single_task_with_extreme_chaos(self, index):
        """单个极端混乱任务"""
        try:
            chaos_type, test_path = self.generate_extreme_chaos_input(index)
            
            # 随机添加额外压力
            if random.random() < 0.3:
                for _ in range(random.randint(10, 500)):
                    x = random.random() * 100
            
            system = FullPathTestSystem()
            result = system.run_full_test(source_path=test_path)
            
            status = result.get("status")
            
            if status == "success":
                return True, None, chaos_type, test_path
            else:
                error_msg = result.get("error", "Unknown")
                # 检查是否为预期错误
                if ("路径不能为空" in error_msg or "目录不存在" in error_msg or 
                    "无法访问" in error_msg):
                    return True, None, chaos_type, test_path
                else:
                    return False, error_msg, chaos_type, test_path
                    
        except Exception as e:
            return False, str(e), "exception", ""
        
    def phase1_small_scale_test(self):
        """阶段1：小规模测试（20个任务）"""
        self.log("=" * 70, "PHASE")
        self.log("阶段1：小规模测试（20个极端混乱任务）", "PHASE")
        self.log("=" * 70, "PHASE")
        
        self.start_time = time.time()
        local_success = 0
        local_failures = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for i in range(20):
                futures.append(executor.submit(self.test_single_task_with_extreme_chaos, i))
                
            for i, future in enumerate(as_completed(futures)):
                success, error, chaos_type, path = future.result()
                
                if success:
                    local_success += 1
                else:
                    local_failures.append((i, chaos_type, path, error))
                    
                if (i + 1) % 10 == 0:
                    self.log(f"进度: {i + 1}/20", "PROGRESS")
        
        elapsed = time.time() - self.start_time
        
        self.log(f"阶段1完成: {local_success}/20 成功处理，耗时 {elapsed:.2f}秒", "RESULT")
        
        if local_failures:
            self.log(f"发现 {len(local_failures)} 个问题:", "WARNING")
            for i, ct, path, err in local_failures:
                self.log(f"  任务{i} ({ct}): {err}", "WARNING")
        
        return len(local_failures) == 0
        
    def phase2_medium_scale_test(self):
        """阶段2：中等规模测试（100个任务）"""
        self.log("\n" + "=" * 70, "PHASE")
        self.log("阶段2：中等规模测试（100个极端混乱任务）", "PHASE")
        self.log("=" * 70, "PHASE")
        
        local_success = 0
        local_failures = []
        
        phase_start = time.time()
        
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = []
            for i in range(100):
                futures.append(executor.submit(self.test_single_task_with_extreme_chaos, i))
                
            for i, future in enumerate(as_completed(futures)):
                success, error, chaos_type, path = future.result()
                
                if success:
                    local_success += 1
                else:
                    local_failures.append((i, chaos_type, error))
                    
                if (i + 1) % 25 == 0:
                    self.log(f"进度: {i + 1}/100", "PROGRESS")
        
        elapsed = time.time() - phase_start
        
        self.log(f"阶段2完成: {local_success}/100 成功处理，耗时 {elapsed:.2f}秒", "RESULT")
        
        if local_failures:
            self.log(f"发现 {len(local_failures)} 个问题:", "WARNING")
            for i, ct, err in local_failures[:10]:
                self.log(f"  任务{i} ({ct}): {err}", "WARNING")
        
        return len(local_failures) == 0
        
    def phase3_long_duration_test(self):
        """阶段3：长时间运行测试（500个任务，持续运行）"""
        self.log("\n" + "=" * 70, "PHASE")
        self.log("阶段3：长时间运行测试（500个任务，持续运行）", "PHASE")
        self.log("=" * 70, "PHASE")
        
        local_success = 0
        local_failures = []
        
        phase_start = time.time()
        
        for i in range(500):
            success, error, chaos_type, path = self.test_single_task_with_extreme_chaos(i)
            
            if success:
                local_success += 1
            else:
                local_failures.append((i, chaos_type, error))
                
            if (i + 1) % 100 == 0:
                self.log(f"进度: {i + 1}/500", "PROGRESS")
                gc.collect()  # 定期GC
                time.sleep(0.1)  # 短暂休息
        
        elapsed = time.time() - phase_start
        
        self.log(f"阶段3完成: {local_success}/500 成功处理，耗时 {elapsed:.2f}秒", "RESULT")
        
        if local_failures:
            self.log(f"发现 {len(local_failures)} 个问题:", "WARNING")
            for i, ct, err in local_failures[:15]:
                self.log(f"  任务{i} ({ct}): {err}", "WARNING")
        
        return len(local_failures) == 0
        
    def run_all_tests(self):
        """运行所有测试"""
        self.log("\n" + "=" * 70, "MAIN")
        self.log("FullPathTest v11.0 - 超大规模极端混乱测试", "MAIN")
        self.log("=" * 70, "MAIN")
        
        self.log("\n📋 测试计划:", "INFO")
        self.log("  1. 小规模测试（20个）", "INFO")
        self.log("  2. 中等规模测试（100个）", "INFO")
        self.log("  3. 长时间运行测试（500个）", "INFO")
        
        phase_results = []
        all_passed = True
        
        # 阶段1
        self.log("\n" + "-" * 70)
        p1_ok = self.phase1_small_scale_test()
        phase_results.append(("阶段1", p1_ok))
        if not p1_ok:
            self.log("⚠️ 阶段1存在问题", "WARNING")
            all_passed = False
        else:
            self.log("✅ 阶段1通过", "PHASE_PASS")
        
        self.log("\n⏸️ 系统稳定中（5秒）...", "WAIT")
        time.sleep(5)
        gc.collect()
        
        if all_passed:
            # 阶段2
            self.log("\n" + "-" * 70)
            p2_ok = self.phase2_medium_scale_test()
            phase_results.append(("阶段2", p2_ok))
            if not p2_ok:
                self.log("⚠️ 阶段2存在问题", "WARNING")
                all_passed = False
            else:
                self.log("✅ 阶段2通过", "PHASE_PASS")
            
            self.log("\n⏸️ 系统稳定中（5秒）...", "WAIT")
            time.sleep(5)
            gc.collect()
        
        if all_passed:
            # 阶段3
            self.log("\n" + "-" * 70)
            p3_ok = self.phase3_long_duration_test()
            phase_results.append(("阶段3", p3_ok))
            if not p3_ok:
                self.log("⚠️ 阶段3存在问题", "WARNING")
                all_passed = False
            else:
                self.log("✅ 阶段3通过", "PHASE_PASS")
        
        # 总结
        self.log("\n" + "=" * 70, "FINAL")
        if all_passed:
            self.log("🎉 超大规模极端混乱测试全部通过！", "FINAL_PASS")
        else:
            self.log("⚠️ 部分测试阶段存在问题", "FINAL_WARN")
            for name, ok in phase_results:
                status = "✅ 通过" if ok else "❌ 有问题"
                self.log(f"  {name}: {status}", "FINAL")
        
        self.log("\n" + "=" * 70)
        return all_passed
        
    @property
    def test_path_fastapi(self):
        return "/workspace/cloned_fastapi_project/fastapi/__init__.py"
        
    @property
    def test_path_django(self):
        return "/workspace/django_project/django/__init__.py"


def main():
    try:
        tester = UltimateChaosTestSystem()
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断测试")
        return 130
    except Exception as e:
        print(f"\n\n❌ 测试系统异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
