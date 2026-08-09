#!/usr/bin/env python3
"""
FullPathTest v6.0 - 快速缺陷扫描
快速发现系统最关键的缺陷
"""

import sys
import time
import traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent))

from fullpathtest.main import FullPathTestSystem

def quick_test(name, path):
    """快速测试"""
    print(f"\n[测试] {name}")
    try:
        system = FullPathTestSystem()
        result = system.run_full_test(source_path=path)
        print(f"  状态: {result.get('status', 'unknown')}")
        return result.get('status') == 'success'
    except Exception as e:
        print(f"  ❌ 异常: {str(e)[:100]}")
        return False

def main():
    print("=" * 70)
    print("FullPathTest v6.0 - 快速缺陷扫描")
    print("=" * 70)

    defects = []

    # 测试1: 边界条件
    print("\n[阶段1] 边界条件测试")
    if not quick_test("空路径", ""):
        defects.append("空路径处理失败")
    if not quick_test("单个字符", "/a"):
        defects.append("单字符路径失败")
    if not quick_test("不存在路径", "/nonexistent/path/12345"):
        defects.append("不存在路径处理失败")

    # 测试2: 真实项目
    print("\n[阶段2] 真实项目测试")
    quick_test("FastAPI", "/workspace/cloned_fastapi_project/fastapi/__init__.py")
    quick_test("Django", "/workspace/django_project/django/__init__.py")

    # 测试3: 并发
    print("\n[阶段3] 并发测试")
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(quick_test, f"并发{i}", "/workspace/cloned_fastapi_project/fastapi/__init__.py") for i in range(5)]
        for f in as_completed(futures):
            try:
                f.result()
            except:
                pass

    # 总结
    print("\n" + "=" * 70)
    print("缺陷总结:")
    for i, d in enumerate(defects, 1):
        print(f"  {i}. {d}")
    print("=" * 70)

if __name__ == "__main__":
    main()
