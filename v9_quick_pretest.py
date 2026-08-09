#!/usr/bin/env python3
"""
FullPathTest v9.0 - 预测试脚本
慢工出细活：先小规模测试发现问题，再大规模测试
"""

import sys
import time
import gc
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent))

from fullpathtest.main import FullPathTestSystem


def log(message):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def test_single_task(test_path, task_id=""):
    """单个测试任务"""
    try:
        system = FullPathTestSystem()
        result = system.run_full_test(source_path=test_path)
        if result.get("status") == "success":
            return True, None
        else:
            return False, result.get("error", "Unknown")
    except Exception as e:
        return False, str(e)


def pre_test():
    """预测试"""
    print("=" * 70)
    print("FullPathTest v9.0 - 预测试")
    print("=" * 70)
    
    errors = []
    
    # 1. 基础功能测试
    print("\n[1/3] 基础功能测试")
    success, error = test_single_task("/workspace/cloned_fastapi_project/fastapi/__init__.py")
    if success:
        print("  ✅ 基础功能正常")
    else:
        errors.append(f"基础功能失败: {error}")
        print(f"  ❌ 错误: {error[:60]}")
    
    # 2. 简单并发测试（5个）
    print("\n[2/3] 简单并发测试（5个）")
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for i in range(5):
            futures.append(
                executor.submit(
                    test_single_task,
                    "/workspace/cloned_fastapi_project/fastapi/__init__.py",
                    f"concurrent-{i}"
                )
            )
        
        concurrent_success = 0
        for i, future in enumerate(as_completed(futures)):
            success, error = future.result()
            if success:
                concurrent_success += 1
            else:
                errors.append(f"并发任务 {i} 失败: {error}")
        
        print(f"  成功: {concurrent_success}/5")
    
    # 3. 边界条件测试
    print("\n[3/3] 边界条件测试")
    test_cases = [
        ("空路径", ""),
        ("空白路径", "   "),
        ("不存在路径", "/does/not/exist/123"),
    ]
    for name, path in test_cases:
        success, error = test_single_task(path, name)
        if error:
            print(f"  ✅ {name}: 错误被正确处理")
        else:
            print(f"  ⚠️  {name}: 结果需要检查")
    
    # 总结
    print("\n" + "=" * 70)
    if len(errors) == 0:
        print("✅ 预测试通过")
        return 0
    else:
        print(f"⚠️  发现 {len(errors)} 个问题:")
        for i, err in enumerate(errors, 1):
            print(f"  {i}. {err}")
        return 1


if __name__ == "__main__":
    sys.exit(pre_test())
