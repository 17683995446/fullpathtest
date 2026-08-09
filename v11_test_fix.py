#!/usr/bin/env python3
"""
FullPathTest v11.0 - 精确测试特殊字符检查
慢工出细活：验证我们的检查能够捕获所有危险字符
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fullpathtest.core.layer_09_source_scanner.scanner import SourceScanner
from fullpathtest.types.core import TaskContext, TaskRequest, ConfigSnapshot, SourceType, LanguageType, CoverageRules, LLMMode


def test_special_chars():
    """测试特殊字符检查"""
    print("=" * 70)
    print("精确测试：特殊字符检查")
    print("=" * 70)
    
    scanner = SourceScanner()
    
    # 创建一个测试context
    request = TaskRequest(
        task_id="test",
        source_type=SourceType.LOCAL_DIRECTORY,
        source_path="/test",
        language=LanguageType.PYTHON,
        llm_mode=LLMMode.LOCAL_ONLY,
        coverage_rules=CoverageRules()
    )
    context = TaskContext(request, ConfigSnapshot())
    
    test_cases = [
        ("含空字符的路径", "/test\x00path", "应该捕获空字符"),
        ("含换行的路径", "/test\npath", "应该捕获换行符"),
        ("含回车的路径", "/test\rpath", "应该捕获回车符"),
        ("含0x01字符的路径", "/test\x01path", "应该捕获0x01"),
        ("正常路径", "/workspace/cloned_fastapi_project", "应该通过"),
    ]
    
    all_passed = True
    
    for name, path, description in test_cases:
        try:
            scanner._scan_directory(path, context)
            # 如果没有抛出异常，检查是否应该通过
            if "正常" in name:
                print(f"\n✅ {name}: 通过 - {description}")
            else:
                print(f"\n❌ {name}: 应该捕获非法字符但没有捕获！")
                all_passed = False
        except ValueError as e:
            if "正常" in name:
                print(f"\n❌ {name}: 正常路径不应该抛出异常 - {e}")
                all_passed = False
            else:
                print(f"\n✅ {name}: 正确捕获 - {e}")
        except Exception as e:
            print(f"\n❌ {name}: 意外异常 - {e}")
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️  部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(test_special_chars())
