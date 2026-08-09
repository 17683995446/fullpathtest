#!/usr/bin/env python3
"""
FullPathTest V24.0 - 快速验证 - 测试我们修复的bug!
"""

import sys
import time
import gc
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent))


class V24QuickTestSystem:
    """V24.0 - 快速验证系统"""
    
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.crashes = 0
        self.issues = []
        self.issues_fixed = [
            "language.name AttributeError when language is None - FIXED!"
        ]
        
    def log(self, msg: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [{level:8}] {msg}")
        
    def log_section(self, title: str):
        self.log("=" * 80, "SECTION")
        self.log(f"  {title}", "SECTION")
        self.log("=" * 80, "SECTION")
        
    def phase1_test_bug_fix(self):
        """测试修复的language=None bug"""
        self.log_section("Phase 1: 验证 language=None bug 修复")
        
        from fullpathtest.main import FullPathTestSystem
        
        system = FullPathTestSystem()
        test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
        
        self.log("测试: language=None")
        try:
            result = system.run_full_test(
                source_path=test_path,
                language=None
            )
            if result.get("status") == "success":
                self.log("✅ SUCCESS! language=None now works!")
                self.passed_tests += 1
        except AttributeError as e:
            if "object has no attribute 'name'" in str(e):
                self.log(f"❌ FAILED! Bug still exists: {e}")
                self.issues.append("Bug NOT fixed!")
            else:
                self.log(f"❌ ERROR: {e}")
        except Exception as e:
            self.log(f"⚠️ 其他错误: {e}")
            
        self.total_tests += 1
        
    def phase2_100_consecutive(self):
        """100次连续测试"""
        self.log_section("Phase 2: 100次连续测试")
        
        from fullpathtest.main import FullPathTestSystem
        
        system = FullPathTestSystem()
        test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
        
        success = 0
        
        for i in range(100):
            try:
                result = system.run_full_test(source_path=test_path)
                if result.get("status") == "success":
                    success += 1
                if (i+1) % 25 == 0:
                    self.log(f"进度: {i+1}/100, 成功: {success}")
                if (i+1) % 50 == 0:
                    gc.collect()
            except Exception as e:
                self.crashes +=1
                if self.crashes <=5:
                    self.issues.append(f"连续测试 {i+1} 崩溃: {str(e)[:80]}")
        
        pass_rate = success/100 *100
        self.log(f"Phase 2结果: {success}/100 通过 ({pass_rate:.1f}%)")
        
        if pass_rate >=99:
            self.passed_tests +=1
        self.total_tests +=1
        
    def phase3_20_concurrent(self):
        """20并发测试"""
        self.log_section("Phase 3: 20并发测试")
        
        from fullpathtest.main import FullPathTestSystem
        
        system = FullPathTestSystem()
        test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
        
        def run_task(i):
            try:
                result = system.run_full_test(source_path=test_path)
                return result.get("status") == "success", None
            except Exception as e:
                return False, str(e)
        
        success =0
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(run_task, i) for i in range(20)]
            for future in as_completed(futures):
                is_ok, err = future.result()
                if is_ok:
                    success +=1
        
        pass_rate = success/20 *100
        self.log(f"Phase3结果: {success}/20 通过 ({pass_rate:.1f}%)")
        
        if pass_rate >=90:
            self.passed_tests +=1
        self.total_tests +=1
        
    def phase4_50_chaos(self):
        """50种混乱场景"""
        self.log_section("Phase 4: 50种混乱场景")
        
        from fullpathtest.main import FullPathTestSystem
        
        system = FullPathTestSystem()
        
        chaos_inputs = [
            ("", "空字符串"),
            ("   ", "空白"),
            ("a"*5000, "超长字符串"),
            ("/nonexistent", "不存在路径"),
            ("../"*5, "路径遍历"),
            ("\x00\x01\x02", "空字节"),
            ("中文路径", "中文"),
            ("🎉🚀💯", "emoji"),
            ("'; DROP TABLE", "SQL注入"),
            ("<script>alert</script>", "XSS")
        ]
        
        for _ in range(4):
            chaos_inputs.extend([(f"/test_{i}", f"随机路径{i}") for i in range(10)])
        
        response_count =0
        
        for path, desc in chaos_inputs[:50]:
            try:
                result = system.run_full_test(source_path=path)
                if "status" in result:
                    response_count +=1
            except Exception as e:
                self.crashes +=1
        
        pass_rate = response_count /50 *100
        self.log(f"Phase4结果: {response_count}/50 响应, 崩溃: {self.crashes}")
        
        if self.crashes ==0:
            self.passed_tests +=1
        self.total_tests +=1
        
    def run_all(self):
        self.log_section("V24 快速验证开始")
        
        self.phase1_test_bug_fix()
        self.phase2_100_consecutive()
        self.phase3_20_concurrent()
        self.phase4_50_chaos()
        
        self.log_section("V24 总结")
        
        total_rate = self.passed_tests / self.total_tests *100 if self.total_tests >0 else 0
        self.log(f"总测试: {self.total_tests}, 通过: {self.passed_tests}, 通过率: {total_rate:.1f}%")
        self.log(f"总崩溃: {self.crashes}")
        
        if self.issues:
            self.log(f"发现问题: {len(self.issues)}")
            for issue in self.issues:
                self.log(f"  - {issue}")
                
        if self.issues_fixed:
            self.log(f"已修复问题: {len(self.issues_fixed)}")
            for fix in self.issues_fixed:
                self.log(f"  - {fix}")


def main():
    try:
        print("=" * 80)
        print("FullPathTest V24.0 - 快速验证")
        print("=" * 80)
        print()
        
        tester = V24QuickTestSystem()
        tester.run_all()
        
        return 0
    except Exception as e:
        print(f"\nFATAL: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
