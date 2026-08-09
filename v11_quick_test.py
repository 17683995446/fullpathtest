#!/usr/bin/env python3
"""
FullPathTest v11.0 - 快速小规模测试
慢工出细活：先小规模测试，发现问题
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fullpathtest.main import FullPathTestSystem


def log(message):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def main():
    print("=" * 70)
    print("FullPathTest v11.0 - 快速小规模测试")
    print("=" * 70)
    
    test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
    errors = []
    
    # 测试1：单个任务
    print("\n[1/3] 单个任务测试")
    try:
        system = FullPathTestSystem()
        result = system.run_full_test(source_path=test_path)
        if result.get("status") == "success":
            print("  ✅ 单个任务成功")
        else:
            errors.append(f"单个任务失败: {result.get('error')}")
            print(f"  ❌ 失败: {result.get('error')}")
    except Exception as e:
        errors.append(f"单个任务异常: {e}")
        print(f"  ❌ 异常: {e}")
    
    # 测试2：5个任务（快速）
    print("\n[2/3] 快速5个任务测试")
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    success_count = 0
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for i in range(5):
            futures.append(executor.submit(lambda: _test_task(i, test_path)))
        
        for future in as_completed(futures):
            try:
                success, err = future.result()
                if success:
                    success_count += 1
            except Exception as e:
                errors.append(f"任务异常: {e}")
    
    print(f"  结果: {success_count}/5 成功")
    if success_count != 5:
        print("  ⚠️  部分任务失败")
    
    # 测试3：边界条件测试
    print("\n[3/3] 快速边界条件测试")
    test_cases = [
        ("空", ""),
        ("空白", "   "),
        ("不存在", "/nonexistent")
    ]
    
    bc_success = 0
    for name, path in test_cases:
        try:
            system = FullPathTestSystem()
            result = system.run_full_test(source_path=path)
            error_msg = result.get("error", "")
            if "路径不能为空" in error_msg or "目录不存在" in error_msg:
                print(f"  ✅ {name} 正确处理")
                bc_success += 1
            else:
                errors.append(f"{name} 处理异常")
        except Exception as e:
            errors.append(f"{name} 异常: {e}")
    
    # 总结
    print("\n" + "=" * 70)
    if len(errors) == 0:
        print("🎉 快速测试全部通过！")
        return 0
    else:
        print(f"⚠️  发现 {len(errors)} 个问题:")
        for i, err in enumerate(errors, 1):
            print(f"  {i}. {err}")
        return 1


def _test_task(index, test_path):
    try:
        system = FullPathTestSystem()
        result = system.run_full_test(source_path=test_path)
        if result.get("status") == "success":
            return True, None
        else:
            return False, result.get("error")
    except Exception as e:
        return False, str(e)


if __name__ == "__main__":
    sys.exit(main())
