#!/usr/bin/env python3
"""
FullPathTest v7.0 - 深度真实测试
慢工出细活：逐步深入测试，不急于求成
"""

import sys
import time
import traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from fullpathtest.main import FullPathTestSystem


def log(message, level="INFO"):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def test_single_task(test_path, task_id):
    """单个任务测试"""
    try:
        system = FullPathTestSystem()
        result = system.run_full_test(source_path=test_path)
        return result.get("status") == "success"
    except Exception as e:
        return False


def phase_1_concurrent_test():
    """阶段1：轻量级并发测试（5个并发）"""
    log("=" * 70, "PHASE")
    log("阶段1：轻量级并发测试（5个并发）", "PHASE")
    log("=" * 70, "PHASE")
    
    test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
    concurrency = 5
    
    start_time = time.time()
    success_count = 0
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(test_single_task, test_path, f"P1-T{i}"): i
            for i in range(concurrency)
        }
        
        for future in as_completed(futures):
            if future.result():
                success_count += 1
    
    elapsed = time.time() - start_time
    
    log(f"并发测试完成: {success_count}/{concurrency} 成功", "RESULT")
    log(f"总耗时: {elapsed:.2f}秒", "RESULT")
    log(f"平均: {elapsed/concurrency:.3f}秒/任务", "RESULT")
    
    return success_count == concurrency


def phase_2_slow_pressure_test():
    """阶段2：慢速压力测试（10次连续）"""
    log("\n" + "=" * 70, "PHASE")
    log("阶段2：慢速压力测试（10次连续）", "PHASE")
    log("=" * 70, "PHASE")
    
    test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
    iterations = 10
    
    start_time = time.time()
    success_count = 0
    task_times = []
    
    for i in range(iterations):
        task_start = time.time()
        success = test_single_task(test_path, f"P2-T{i}")
        task_time = time.time() - task_start
        
        task_times.append(task_time)
        if success:
            success_count += 1
        
        if i < iterations - 1:
            time.sleep(0.1)
        
        if (i + 1) % 5 == 0:
            log(f"完成 {i + 1}/{iterations} 次...", "PROGRESS")
    
    elapsed = time.time() - start_time
    
    log(f"慢速压力测试完成: {success_count}/{iterations} 成功", "RESULT")
    log(f"总耗时: {elapsed:.2f}秒", "RESULT")
    log(f"平均: {elapsed/iterations:.3f}秒/任务", "RESULT")
    if task_times:
        log(f"最快: {min(task_times):.3f}秒, 最慢: {max(task_times):.3f}秒", "RESULT")
    
    return success_count == iterations


def phase_3_real_project_test():
    """阶段3：真实项目测试"""
    log("\n" + "=" * 70, "PHASE")
    log("阶段3：真实项目测试", "PHASE")
    log("=" * 70, "PHASE")
    
    projects = [
        ("FastAPI", "/workspace/cloned_fastapi_project/fastapi/__init__.py"),
        ("Django", "/workspace/django_project/django/__init__.py"),
    ]
    
    results = []
    for name, path in projects:
        log(f"\n测试项目: {name}", "TEST")
        try:
            system = FullPathTestSystem()
            result = system.run_full_test(source_path=path)
            
            status = result.get("status")
            if status == "success":
                coverage = result.get("coverage_report").statement_coverage * 100
                defect_count = len(result.get("defect_report").defects)
                log(f"  ✅ 成功: 覆盖率 {coverage:.1f}%, 缺陷 {defect_count}", "PASS")
                results.append((name, True))
            else:
                log(f"  ❌ 失败: {result.get('error', 'Unknown')[:80]}", "FAIL")
                results.append((name, False))
                
        except Exception as e:
            log(f"  ❌ 异常: {str(e)[:80]}", "ERROR")
            results.append((name, False))
    
    success_count = sum(1 for _, success in results if success)
    log(f"\n真实项目测试: {success_count}/{len(projects)} 通过", "RESULT")
    
    return success_count == len(projects)


def main():
    print("\n" + "=" * 70)
    print("FullPathTest v7.0 - 慢工出细活 深度真实测试")
    print("=" * 70)
    
    print("\n📋 测试计划:")
    print("  1. 轻量级并发测试（5个并发）")
    print("  2. 慢速压力测试（10次连续）")
    print("  3. 真实项目测试")
    
    all_passed = True
    
    # 阶段1
    print("\n" + "-" * 70)
    if phase_1_concurrent_test():
        print("✅ 阶段1通过")
    else:
        print("❌ 阶段1失败")
        all_passed = False
    
    # 阶段2
    print("\n" + "-" * 70)
    if phase_2_slow_pressure_test():
        print("✅ 阶段2通过")
    else:
        print("❌ 阶段2失败")
        all_passed = False
    
    # 阶段3
    print("\n" + "-" * 70)
    if phase_3_real_project_test():
        print("✅ 阶段3通过")
    else:
        print("❌ 阶段3失败")
        all_passed = False
    
    # 总结
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 深度测试全部通过！系统健壮性良好！")
    else:
        print("⚠️  部分测试未通过，需要继续优化")
    print("=" * 70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
