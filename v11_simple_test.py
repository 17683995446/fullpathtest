#!/usr/bin/env python3
"""
FullPathTest v11.0 - 简化测试
慢工出细活：直接测试主要边界条件
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fullpathtest.main import FullPathTestSystem


def main():
    print("=" * 70)
    print("简化测试：边界条件检查")
    print("=" * 70)
    
    # 测试1：含空字符的路径（使用原始字符串）
    print("\n测试1：含空字符的路径")
    try:
        system = FullPathTestSystem()
        # 直接构造含空字符的字符串
        test_path = "/test" + chr(0) + "path"
        result = system.run_full_test(source_path=test_path)
        print(f"  结果：状态={result.get('status')}, 错误={result.get('error')}")
    except Exception as e:
        print(f"  异常：{e}")
    
    # 测试2：空字符串
    print("\n测试2：空字符串")
    try:
        system = FullPathTestSystem()
        result = system.run_full_test(source_path="")
        print(f"  结果：状态={result.get('status')}, 错误={result.get('error')}")
    except Exception as e:
        print(f"  异常：{e}")
    
    # 测试3：正常路径
    print("\n测试3：正常路径")
    try:
        system = FullPathTestSystem()
        result = system.run_full_test(source_path="/workspace/cloned_fastapi_project/fastapi/__init__.py")
        print(f"  结果：状态={result.get('status')}")
    except Exception as e:
        print(f"  异常：{e}")
    
    print("\n" + "=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
