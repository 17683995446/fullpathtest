#!/usr/bin/env python3
"""
FullPathTest v11.0 - 阶段1小规模测试
慢工出细活：先执行20个任务的小规模测试
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from v11_ultimate_chaos_test import UltimateChaosTestSystem


def main():
    print("=" * 70)
    print("FullPathTest v11.0 - 阶段1小规模测试")
    print("=" * 70)
    
    try:
        tester = UltimateChaosTestSystem()
        success = tester.phase1_small_scale_test()
        
        print("\n" + "=" * 70)
        if success:
            print("🎉 阶段1小规模测试全部通过！")
            return 0
        else:
            print("⚠️  阶段1存在问题")
            return 1
    except Exception as e:
        print(f"\n❌ 测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
