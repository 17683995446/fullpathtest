#!/usr/bin/env python3
"""
FullPathTest v12.0 - 完整详细日志测试运行
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from v12_detailed_logging_test import DetailedLoggingTest


def main():
    print("=" * 80)
    print("FullPathTest v12.0 - 完整详细日志极端混乱测试")
    print("=" * 80)
    
    try:
        tester = DetailedLoggingTest()
        success = tester.run_all_tests()
        
        print("\n" + "=" * 80)
        if success:
            print("🎉 所有测试通过！系统表现优秀！")
            return 0
        else:
            print("⚠️ 部分测试发现问题！")
            return 1
            
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
