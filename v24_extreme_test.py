#!/usr/bin/env python3
"""
FullPathTest V24.0 - 超详细日志+极端测试
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


class V24ExtremeTestSystem:
    """V24.0 - 极端测试系统"""
    
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.crashes = 0
        self.issues_found = []
        self.issues_fixed = [
            "language.name AttributeError when language is None - FIXED in V24"
        ]
        self.test_results = []
        
    def log(self, msg: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [{level:8}] {msg}")
        
    def log_section(self, title: str):
        self.log("=" * 100, "SECTION")
        self.log(f"  {title}", "SECTION")
        self.log("=" * 100, "SECTION")
        
    def phase1_long_duration_test(self):
        """500次超长时连续测试"""
        self.log_section("Phase 1: 500次超长时连续测试")
        
        from fullpathtest.main import FullPathTestSystem
        from fullpathtest.types.core import SourceType, LanguageType
        
        system = FullPathTestSystem()
        test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
        
        success_count = 0
        start_time = time.time()
        
        for i in range(500):
            try:
                self.log(f"[连续测试 {i+1}/500")
                
                result = system.run_full_test(
                    source_path=test_path,
                    language=random.choice([None, LanguageType.PYTHON]),
                    user_command=random.choice([None, "全面测试"]) if random.random() > 0.5 else None
                )
                
                if result.get("status") == "success":
                    success_count += 1
                
                if (i+1) % 50 == 0:
                    gc.collect()
                    elapsed = time.time() - start_time
                    avg_per = elapsed / (i+1)
                    self.log(f"进度: {i+1}/500, 成功: {success_count}, 耗时: {elapsed:.1f}s, 平均: {avg_per:.3f}s/次")
                
            except Exception as e:
                self.crashes += 1
                self.log(f"CRASH #{i+1}: {e")
                if self.crashes <= 10:
                    self.issues_found.append(f"连续测试 {i+1} 崩溃: {str(e)[:100]}")
        
        pass_rate = success_count / 500 * 100
        total_time = time.time() - start_time
        
        self.log(f"Phase1 结果: {success_count}/500 成功 ({pass_rate:.1f}%), 耗时: {total_time:.1f}s ({total_time/60:.1f}min)")
        
        if pass_rate >= 99.0:
            self.passed_tests += 1
        self.total_tests += 1
        
        return pass_rate
        
    def phase2_concurrent_stress_test(self):
        """30并发极端测试"""
        self.log_section("Phase 2: 30并发极端测试")
        
        from fullpathtest.main import FullPathTestSystem
        
        system = FullPathTestSystem()
        test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
        
        def concurrent_success = 0
        start_time = time.time()
        
        def run_concurrent(i):
            try:
                result = system.run_full_test(source_path=test_path)
                return result.get("status") == "success", None
            except Exception as e:
                    return False, str(e)
        
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = [executor.submit(run_concurrent, i) for i in range(30)]
            completed = 0
            for future in as_completed(futures):
                completed +=1
                is_ok, err = future.result()
                if is_ok:
                    concurrent_success += 1
                if err:
                    self.crashes +=1
                
                if completed %10 ==0:
                    self.log(f"并发进度: {completed}/30")
        
        pass_rate = concurrent_success /30 *100
        total_time = time.time() - start_time
        
        self.log(f"Phase2 结果: {concurrent_success}/30 成功 ({pass_rate:.1f}%), 耗时: {total_time:.2f}s")
        
        if pass_rate >=95:
            self.passed_tests +=1
        self.total_tests +=1
        
        return pass_rate
        
    def phase3_chaos_test(self):
        """100种混乱场景测试"""
        self.log_section("Phase 3: 100种混乱场景测试")
        
        from fullpathtest.main import FullPathTestSystem
        from fullpathtest.types.core import SourceType, LanguageType, LLMMode
        
        system = FullPathTestSystem()
        
        chaos_inputs = []
        
        for i in range(100):
            t = i % 20
            if t == 0: chaos_inputs.append(("", SourceType.LOCAL_DIRECTORY, "空字符串"))
            elif t == 1: chaos_inputs.append(("   ", SourceType.LOCAL_DIRECTORY, "空白字符串"))
            elif t == 2: chaos_inputs.append(("a"*10000, SourceType.LOCAL_DIRECTORY, "超长字符串"))
            elif t == 3: chaos_inputs.append(("/nonexistent", SourceType.LOCAL_DIRECTORY, "不存在路径"))
            elif t == 4: chaos_inputs.append(("../"*10, SourceType.LOCAL_DIRECTORY, "路径遍历"))
            elif t == 5: chaos_inputs.append(("\x00\x01\x02", SourceType.LOCAL_DIRECTORY, "空字节"))
            elif t == 6: chaos_inputs.append(("中文测试路径", SourceType.LOCAL_DIRECTORY, "中文路径"))
            elif t == 7: chaos_inputs.append(("🎉🚀💯"*10, SourceType.LOCAL_DIRECTORY, "emoji"))
            elif t == 8: chaos_inputs.append(("'; DROP TABLE users", SourceType.LOCAL_DIRECTORY, "SQL注入"))
            elif t == 9: chaos_inputs.append(("<script>alert('xss')</script>", SourceType.LOCAL_DIRECTORY, "XSS"))
            elif t ==10: 
                path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
                lang = random.choice([None, LanguageType.PYTHON])
                chaos_inputs.append((path, SourceType.LOCAL_DIRECTORY, f"正常+{lang}"))
            else:
                random_path = f"/test_{random.randint(1, 10000)}"
                chaos_inputs.append((random_path, SourceType.LOCAL_DIRECTORY, f"随机路径{i}"))
        
        chaos_success =0
        chaos_errors =0
        
        for idx, (path, source_type, desc) in enumerate(chaos_inputs,1):
            try:
                result = system.run_full_test(
                    source_path=path,
                    source_type=source_type
                )
                if "status" in result:
                    chaos_success +=1
                else:
                    chaos_errors +=1
                    
            except Exception as e:
                self.crashes +=1
                if self.crashes <=10:
                    self.issues_found.append(f"混乱测试#{idx}({desc})崩溃: {str(e)[:80]}")
        
        pass_rate = chaos_success /100 *100
        
        self.log(f"Phase3 结果: {chaos_success}/100 响应, {chaos_errors} 错误, {self.crashes} 崩溃")
        
        if self.crashes ==0:
            self.passed_tests +=1
        self.total_tests +=1
        
        return pass_rate
        
    def run_all(self):
        """运行所有V24极端测试"""
        self.log_section("FullPathTest V24.0 - 极端测试开始")
        
        self.phase1_long_duration_test()
        self.phase2_concurrent_stress_test()
        self.phase3_chaos_test()
        
        self.log_section("V24 总结")
        
        self.log(f"总测试: {self.total_tests}")
        self.log(f"通过: {self.passed_tests}")
        
        pass_rate = self.passed_tests / self.total_tests *100 if self.total_tests >0 else 0
        self.log(f"通过率: {pass_rate:.1f}%")
        self.log(f"总崩溃数: {self.crashes}")
        
        if self.issues_found:
            self.log(f"\n发现问题数: {len(self.issues_found)}")
            for issue in self.issues_found[:10]:
                self.log(f"  - {issue}")
                
        self.log(f"\n已修复问题: {len(self.issues_fixed)}")
        for fix in self.issues_fixed:
            self.log(f"  - {fix}")
        
        self.save_log()
        
    def save_log(self):
        log_content = f"V24 TEST LOG\n"
        log_content += f"Date: {datetime.now().isoformat()}\n"
        log_content += f"Tests: {self.total_tests}\n"
        log_content += f"Passed: {self.passed_tests}\n"
        log_content += f"Crashes: {self.crashes}\n"
        with open("/workspace/v24_test_log.txt", "w") as f:
            f.write(log_content)
        self.log(f"日志已保存到 /workspace/v24_test_log.txt")


def main():
    try:
        print("=" * 100)
        print("FullPathTest V24.0 - 极端测试系统")
        print("=" * 100)
        print()
        
        tester = V24ExtremeTestSystem()
        tester.run_all()
        
        return 0
    except Exception as e:
        print(f"\nFATAL: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
