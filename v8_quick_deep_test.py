#!/usr/bin/env python3
"""
FullPathTest v8.0 - 快速但深入的测试
慢工出细活：先深入测试发现问题，再修复
"""

import sys
import time
import traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from fullpathtest.main import FullPathTestSystem


def log(message):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def test_concurrent_issue():
    """测试并发问题 - 先小后大"""
    log("=" * 70)
    log("阶段1：并发测试 - 10个并发")
    log("=" * 70)
    
    test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
    concurrency = 10
    errors = []
    
    start = time.time()
    success_count = 0
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for i in range(concurrency):
            futures.append(executor.submit(lambda: _run_test(test_path)))
        
        for i, future in enumerate(as_completed(futures)):
            try:
                success, error = future.result()
                if success:
                    success_count += 1
                else:
                    errors.append(f"Task {i}: {error[:80]}")
                if (i + 1) % 5 == 0:
                    log(f"进度: {i + 1}/{concurrency}")
            except Exception as e:
                errors.append(f"Task {i}: {str(e)[:80]}")
    
    elapsed = time.time() - start
    log(f"\n结果: {success_count}/{concurrency} 成功, 耗时 {elapsed:.2f}秒")
    
    if errors:
        log(f"\n发现 {len(errors)} 个问题:")
        for i, error in enumerate(errors, 1):
            log(f"  {i}. {error}")
    
    return len(errors) == 0, errors


def _run_test(test_path):
    try:
        system = FullPathTestSystem()
        result = system.run_full_test(source_path=test_path)
        if result.get("status") == "success":
            return True, None
        else:
            return False, result.get("error", "Unknown")
    except Exception as e:
        return False, str(e)


def test_long_running():
    """测试长时间运行 - 20次连续"""
    log("\n" + "=" * 70)
    log("阶段2：长时运行 - 20次连续")
    log("=" * 70)
    
    test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
    iterations = 20
    errors = []
    
    start = time.time()
    success_count = 0
    task_times = []
    
    for i in range(iterations):
        task_start = time.time()
        try:
            system = FullPathTestSystem()
            result = system.run_full_test(source_path=test_path)
            
            task_time = time.time() - task_start
            task_times.append(task_time)
            
            if result.get("status") == "success":
                success_count += 1
            else:
                errors.append(f"Run {i}: {result.get('error', 'Unknown')[:80]}")
                
        except Exception as e:
            task_time = time.time() - task_start
            task_times.append(task_time)
            errors.append(f"Run {i}: Exception - {str(e)[:80]}")
        
        if (i + 1) % 10 == 0:
            log(f"进度: {i + 1}/{iterations}")
        
        if i < iterations - 1:
            time.sleep(0.1)
    
    elapsed = time.time() - start
    
    log(f"\n结果: {success_count}/{iterations} 成功, 耗时 {elapsed:.2f}秒")
    if task_times:
        log(f"平均耗时: {sum(task_times)/len(task_times):.3f}秒")
        log(f"最快: {min(task_times):.3f}秒, 最慢: {max(task_times):.3f}秒")
    
    if errors:
        log(f"\n发现 {len(errors)} 个问题:")
        for i, error in enumerate(errors, 1):
            log(f"  {i}. {error}")
    
    return len(errors) == 0, errors


def test_real_projects():
    """测试真实项目 - 各2次"""
    log("\n" + "=" * 70)
    log("阶段3：真实项目测试")
    log("=" * 70)
    
    projects = [
        ("FastAPI", "/workspace/cloned_fastapi_project/fastapi/__init__.py"),
        ("Django", "/workspace/django_project/django/__init__.py"),
    ]
    
    all_errors = []
    
    for name, path in projects:
        log(f"\n测试项目: {name}")
        
        for run in range(2):
            try:
                system = FullPathTestSystem()
                result = system.run_full_test(source_path=path)
                
                if result.get("status") == "success":
                    log(f"  运行 {run + 1}: ✅ 成功")
                else:
                    err_msg = f"{name} run {run + 1}: {result.get('error', 'Unknown')[:80]}"
                    log(f"  运行 {run + 1}: ❌ 失败 - {err_msg}")
                    all_errors.append(err_msg)
                    
            except Exception as e:
                err_msg = f"{name} run {run + 1}: Exception - {str(e)[:80]}"
                log(f"  运行 {run + 1}: ❌ 异常 - {err_msg}")
                all_errors.append(err_msg)
    
    return len(all_errors) == 0, all_errors


def main():
    print("\n" + "=" * 70)
    print("FullPathTest v8.0 - 慢工出细活 快速深入测试")
    print("=" * 70)
    
    all_errors = []
    
    # 测试1
    ok1, errors1 = test_concurrent_issue()
    all_errors.extend(errors1)
    
    # 测试2
    ok2, errors2 = test_long_running()
    all_errors.extend(errors2)
    
    # 测试3
    ok3, errors3 = test_real_projects()
    all_errors.extend(errors3)
    
    # 总结
    print("\n" + "=" * 70)
    if len(all_errors) == 0:
        print("🎉 所有测试通过！系统稳定！")
    else:
        print(f"⚠️  发现 {len(all_errors)} 个问题:")
        for i, error in enumerate(all_errors, 1):
            print(f"  {i}. {error}")
    print("=" * 70)
    
    return 0 if len(all_errors) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
