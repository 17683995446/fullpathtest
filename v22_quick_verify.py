#!/usr/bin/env python3
"""
FullPathTest V22.0 - 极端测试快速验证版（100次+10并发+30种混乱）
"""

import sys
import time
import gc
import random
import traceback
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent))

class V22QuickVerify:
    """V22快速验证"""
    
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.discovered_issues = []
        self.start_time = None
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_line = f"[{timestamp}] [{level:8}] {message}"
        print(log_line)
    
    def record_issue(self, issue: str, severity: str = "MEDIUM"):
        self.discovered_issues.append({
            "issue": issue,
            "severity": severity
        })
        self.log(f"⚠️  ISSUE: [{severity}] {issue}", "ISSUE")
    
    def run(self):
        """运行快速验证"""
        self.start_time = time.time()
        self.log("=" * 100, "SECTION")
        self.log("V22.0 极端测试快速验证", "SECTION")
        self.log("=" * 100, "SECTION")
        
        from fullpathtest.main import FullPathTestSystem
        system = FullPathTestSystem()
        test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
        
        # Phase 1: 100次连续测试
        self.log("\n[Phase 1] 100次连续测试", "INFO")
        success1 = 0
        for i in range(100):
            try:
                result = system.run_full_test(source_path=test_path)
                if result.get("status") == "success":
                    success1 += 1
            except Exception as e:
                if i < 5:
                    self.record_issue(f"第{i}次崩溃: {e}", "HIGH")
            
            if (i + 1) % 25 == 0:
                self.log(f"  进度: {i+1}/100, 成功: {success1}", "INFO")
        
        pass_rate1 = success1 / 100 * 100
        self.log(f"Phase 1 结果: {success1}/100 成功 ({pass_rate1:.1f}%)", 
                 "PASS" if pass_rate1 >= 99 else "FAIL")
        if pass_rate1 >= 99:
            self.passed_tests += 1
        self.total_tests += 1
        
        # Phase 2: 10并发测试
        self.log("\n[Phase 2] 10并发测试", "INFO")
        success2 = 0
        
        def task(i):
            try:
                r = system.run_full_test(source_path=test_path)
                return r.get("status") == "success"
            except:
                return False
        
        with ThreadPoolExecutor(max_workers=10) as ex:
            results = [f.result() for f in as_completed([ex.submit(task, i) for i in range(10)])]
        success2 = sum(results)
        
        pass_rate2 = success2 / 10 * 100
        self.log(f"Phase 2 结果: {success2}/10 成功 ({pass_rate2:.1f}%)",
                 "PASS" if pass_rate2 >= 90 else "FAIL")
        if pass_rate2 >= 90:
            self.passed_tests += 1
        self.total_tests += 1
        
        # Phase 3: 30种混乱输入
        self.log("\n[Phase 3] 30种混乱输入测试", "INFO")
        from fullpathtest.types.core import SourceType
        
        chaos_inputs = [
            ("", SourceType.LOCAL_DIRECTORY),
            ("   ", SourceType.LOCAL_DIRECTORY),
            ("a" * 5000, SourceType.LOCAL_DIRECTORY),
            ("/nonexistent", SourceType.LOCAL_DIRECTORY),
            ("../" * 10, SourceType.LOCAL_DIRECTORY),
            ("\x00\x01\x02", SourceType.LOCAL_DIRECTORY),
            ("中文测试", SourceType.LOCAL_DIRECTORY),
            ("🎉🚀💯" * 20, SourceType.LOCAL_DIRECTORY),
            ("'; DROP TABLE", SourceType.LOCAL_DIRECTORY),
            ("<script>", SourceType.LOCAL_DIRECTORY),
        ] + [(f"/test{i}", SourceType.LOCAL_DIRECTORY) for i in range(20)]
        
        crashes = 0
        for idx, (path, src_type) in enumerate(chaos_inputs, 1):
            try:
                result = system.run_full_test(source_path=path, source_type=src_type)
                if "status" not in result:
                    crashes += 1
            except:
                crashes += 1
                if crashes <= 3:
                    self.record_issue(f"混乱测试#{idx}崩溃", "CRITICAL")
        
        pass_rate3 = (len(chaos_inputs) - crashes) / len(chaos_inputs) * 100
        self.log(f"Phase 3 结果: {len(chaos_inputs)-crashes}/{len(chaos_inputs)} 成功 ({pass_rate3:.1f}%)",
                 "PASS" if pass_rate3 >= 95 else "FAIL")
        if crashes == 0:
            self.passed_tests += 1
        self.total_tests += 1
        
        # 总结
        total_duration = time.time() - self.start_time
        
        self.log("\n" + "=" * 100, "SUMMARY")
        self.log("V22.0 快速验证总结", "SUMMARY")
        self.log("=" * 100, "SUMMARY")
        self.log(f"总测试数: {self.total_tests}", "SUMMARY")
        self.log(f"通过数: {self.passed_tests}", "SUMMARY")
        self.log(f"通过率: {self.passed_tests/self.total_tests*100:.1f}%", "SUMMARY")
        self.log(f"总耗时: {total_duration:.2f}秒 ({total_duration/60:.2f}分钟)", "SUMMARY")
        self.log(f"发现问题数: {len(self.discovered_issues)}", "SUMMARY")


def main():
    try:
        V22QuickVerify().run()
        return 0
    except Exception as e:
        print(f"\nFATAL: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
