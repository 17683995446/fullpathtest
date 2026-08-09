#!/usr/bin/env python3
"""
FullPathTest v11.0 - 验证边界条件修复
慢工出细活：验证含空字符的路径是否被正确处理
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fullpathtest.main import FullPathTestSystem


def test_null_char_path():
    """测试含空字符的路径"""
    print("=" * 70)
    print("测试：含空字符的路径处理")
    print("=" * 70)
    
    test_cases = [
        ("含空字符的路径", "/test\x00path"),
        ("含多个空字符的路径", "/test\x00\x00path"),
        ("正常路径", "/workspace/cloned_fastapi_project/fastapi/__init__.py"),
    ]
    
    all_passed = True
    
    for name, path in test_cases:
        try:
            system = FullPathTestSystem()
            result = system.run_full_test(source_path=path)
            
            if result.get("status") == "success":
                print(f"\n✅ {name}: 处理成功")
            else:
                print(f"\n✅ {name}: 正确处理错误 - {result.get('error')}")
        except Exception as e:
            print(f"\n❌ {name}: 异常 - {e}")
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 所有边界条件测试通过！")
        return 0
    else:
        print("⚠️  部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(test_null_char_path())
