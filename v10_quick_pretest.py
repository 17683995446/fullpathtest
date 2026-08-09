#!/usr/bin/env python3
"""
FullPathTest v10.0 - 极端混乱预测试
慢工出细活：先小规模测试发现问题，再大规模测试
"""

import sys
import time
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fullpathtest.main import FullPathTestSystem


def log(message):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def test_quick_chaos():
    """快速混乱测试"""
    print("=" * 70)
    print("FullPathTest v10.0 - 极端混乱预测试")
    print("=" * 70)
    
    test_path_fastapi = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
    errors = []
    
    # 测试1：单个任务
    print("\n[1/4] 单个任务测试")
    try:
        system = FullPathTestSystem()
        result = system.run_full_test(source_path=test_path_fastapi)
        if result.get("status") == "success":
            print("  ✅ 单个任务成功")
        else:
            errors.append(f"单个任务失败: {result.get('error')}")
            print(f"  ❌ 失败: {result.get('error')}")
    except Exception as e:
        errors.append(f"单个任务异常: {e}")
        print(f"  ❌ 异常: {e}")
    
    # 测试2：快速混乱输入
    print("\n[2/4] 混乱输入测试")
    chaos_inputs = [
        ("空", ""),
        ("空白", "   "),
        ("不存在", "/nonexistent/path"),
        ("单个字符", "/a"),
        ("长路径", "/test/"*100),
    ]
    
    chaos_success = 0
    for name, path in chaos_inputs:
        try:
            system = FullPathTestSystem()
            result = system.run_full_test(source_path=path)
            error = result.get("error", "Unknown")
            if "路径不能为空" in error or "目录不存在" in error:
                print(f"  ✅ {name}: 错误被正确处理")
                chaos_success += 1
            elif result.get("status") == "success":
                print(f"  ⚠️  {name}: 意外成功 (可能有问题)")
                chaos_success += 1
            else:
                print(f"  ❌ {name}: 未处理的错误: {error[:50]}")
                errors.append(f"{name}: {error}")
        except Exception as e:
            print(f"  ❌ {name}: 异常: {e}")
            errors.append(f"{name}: EXCEPTION - {e}")
    
    # 测试3：混合序列
    print("\n[3/4] 混合序列测试")
    mixed_sequence = [
        test_path_fastapi, "", test_path_fastapi, "/nonexistent", test_path_fastapi
    ]
    sequence_success = 0
    for i, path in enumerate(mixed_sequence):
        try:
            system = FullPathTestSystem()
            result = system.run_full_test(source_path=path)
            if result.get("status") == "success":
                print(f"  运行 {i+1}: ✅ 成功")
                sequence_success += 1
            else:
                error = result.get("error", "Unknown")
                if "路径不能为空" in error or "目录不存在" in error:
                    print(f"  运行 {i+1}: ✅ 正确处理")
                    sequence_success += 1
                else:
                    print(f"  运行 {i+1}: ❌ 失败")
                    errors.append(f"seq{i+1}: {error}")
        except Exception as e:
            print(f"  运行 {i+1}: ❌ 异常")
            errors.append(f"seq{i+1}: {e}")
    
    # 测试4：简单并发
    print("\n[4/4] 简单并发测试（5个任务")
    from concurrent.futures import ThreadPoolExecutor, as_completed
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for i in range(5):
            if i % 2 == 0:
                path = test_path_fastapi
            else:
                path = ""
            futures.append(executor.submit(lambda p=path, idx=i: test_task(p, idx)))
        
        concurrent_success = 0
        for i, future in enumerate(as_completed(futures)):
            try:
                success, msg = future.result()
                if success:
                    concurrent_success += 1
                    print(f"  任务 {i+1}: ✅ {msg}")
                else:
                    print(f"  任务 {i+1}: ❌ {msg}")
            except Exception as e:
                print(f"  任务 {i+1}: ❌ 异常: {e}")
                errors.append(f"concurrent{i+1}: EXCEPTION - {e}")
    
    # 总结
    print("\n" + "=" * 70)
    if len(errors) == 0:
        print("🎉 所有预测试通过！")
        return 0
    else:
        print(f"⚠️  发现 {len(errors)} 个问题:")
        for i, err in enumerate(errors[:10], 1):
            print(f"  {i}. {err}")
        return 1


def test_task(path, idx):
    """单个测试任务"""
    try:
        system = FullPathTestSystem()
        result = system.run_full_test(source_path=path)
        if result.get("status") == "success":
            return True, "成功"
        else:
            error = result.get("error", "Unknown")
            if "路径不能为空" in error or "目录不存在" in error:
                return True, "错误被正确处理"
            else:
                return False, f"失败: {error}"
    except Exception as e:
        return False, f"异常: {e}"


if __name__ == "__main__":
    sys.exit(test_quick_chaos())
