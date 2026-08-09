#!/usr/bin/env python3
"""
FullPathTest V16.0 - 超极端现实场景深度测试系统

目标：
1. 找到系统在真实运行时的BUG
2. 测试超极端的复杂场景
3. 超长时间运行稳定性测试
4. 随机混乱输入测试
5. 真实大型项目测试
"""

import sys
import time
import gc
import random
import traceback
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))


class ExtremeTestSystem:
    """超极端测试系统"""
    
    def __init__(self):
        self.passed_tests = 0
        self.total_tests = 0
        self.found_bugs = []
        self.start_time = time.time()
        self.test_logs = []
    
    def log(self, message: str, level: str = "INFO"):
        """详细日志"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_line = f"[{timestamp}] [{level}] {message}"
        print(log_line)
        self.test_logs.append(log_line)
    
    def record_bug(self, test_name: str, bug_desc: str, severity: str = "MEDIUM"):
        """记录发现的BUG"""
        bug = {
            "test_name": test_name,
            "description": bug_desc,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        }
        self.found_bugs.append(bug)
        self.log(f"🔴 BUG FOUND: {test_name} - {bug_desc} ({severity})", "BUG")
    
    def run_test(self, test_name: str, test_func) -> bool:
        """运行单个测试"""
        self.total_tests += 1
        self.log(f"🔍 Starting test: {test_name}")
        
        start = time.time()
        try:
            result = test_func()
            duration = time.time() - start
            
            if result:
                self.passed_tests += 1
                self.log(f"✅ PASS: {test_name} ({duration:.2f}s)", "PASS")
            else:
                self.log(f"❌ FAIL: {test_name} ({duration:.2f}s)", "FAIL")
            return result
        except Exception as e:
            duration = time.time() - start
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            self.record_bug(test_name, error_msg, "CRITICAL")
            self.log(f"💥 CRASH: {test_name} - {str(e)}", "ERROR")
            return False
    
    # ============ 1. 极端边界条件测试 ============
    def test_extreme_inputs(self) -> bool:
        """极端输入测试"""
        self.log("="*60, "TEST")
        self.log("TEST 1: 极端边界条件测试", "TEST")
        self.log("="*60, "TEST")
        
        from fullpathtest.main import FullPathTestSystem
        
        system = FullPathTestSystem()
        
        # 极端输入场景
        extreme_inputs = [
            # 空输入
            ("empty_string", ""),
            ("whitespace_only", "   \t\n\r  "),
            # 超长输入
            ("super_long_path", "/test/path/abcdefghijklmnopqrstuvwxyz/" * 50),
            # 特殊字符
            ("null_char", "/test\x00path"),
            ("weird_chars", "/test😀€ñçøæßpath"),
            ("control_chars", "/test\x01\x02\x03path"),
            # 极端相对路径
            ("parent_attack", "../../../../../etc/passwd"),
            ("dot_dot", "../../../../../"),
            # 单个字符
            ("single_slash", "/"),
            ("single_dot", "."),
            ("double_dot", ".."),
            # 空文件路径
            ("file_empty", ""),
            # 混合
            ("mixed_up", "/t\x00e../s t/\n path.."),
        ]
        
        passed = 0
        failed = 0
        
        for name, path in extreme_inputs:
            try:
                result = system.run_full_test(source_path=path)
                if "status" in result:
                    passed += 1
                    self.log(f"  ✅ {name}: status={result.get('status')}", "PASS")
                else:
                    failed += 1
                    self.record_bug(f"extreme_input_{name}", "Result missing 'status' key", "MEDIUM")
            except Exception as e:
                failed += 1
                self.record_bug(f"extreme_input_{name}", f"Exception: {str(e)}", "HIGH")
        
        self.log(f"  Summary: {passed}/{len(extreme_inputs)} passed")
        return failed == 0
    
    # ============ 2. 超长时间连续测试 ============
    def test_long_running_stability(self) -> bool:
        """超长时间运行稳定性测试"""
        self.log("="*60, "TEST")
        self.log("TEST 2: 超长时间连续运行稳定性测试 (100次)", "TEST")
        self.log("="*60, "TEST")
        
        from fullpathtest.main import FullPathTestSystem
        
        system = FullPathTestSystem()
        test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
        
        failures = 0
        durations = []
        
        for i in range(100):
            if i % 10 == 0:
                gc.collect()
                self.log(f"  Iteration {i+1}/100 (garbage collected)", "PROGRESS")
            
            start = time.time()
            try:
                result = system.run_full_test(source_path=test_path)
                duration = time.time() - start
                durations.append(duration)
                
                if result.get("status") != "success":
                    failures += 1
                    self.record_bug(f"long_run_{i}", f"Unexpected status: {result.get('status')}", "MEDIUM")
            except Exception as e:
                failures += 1
                self.record_bug(f"long_run_{i}", f"Crash: {str(e)}", "CRITICAL")
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        
        self.log(f"  Duration stats: min={min_duration:.3f}s, avg={avg_duration:.3f}s, max={max_duration:.3f}s")
        self.log(f"  Success: {100-failures}/100")
        
        return failures == 0
    
    # ============ 3. 超大规模并发测试 ============
    def test_massive_concurrency(self) -> bool:
        """超大规模并发测试"""
        self.log("="*60, "TEST")
        self.log("TEST 3: 超大规模并发测试 (20任务 × 5 worker)", "TEST")
        self.log("="*60, "TEST")
        
        from fullpathtest.main import FullPathTestSystem
        
        system = FullPathTestSystem()
        test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
        
        results = []
        
        def task_func(idx):
            try:
                result = system.run_full_test(source_path=test_path)
                return (idx, result.get("status") == "success")
            except Exception as e:
                self.record_bug(f"concurrency_{idx}", f"Concurrent crash: {str(e)}", "CRITICAL")
                return (idx, False)
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(task_func, i) for i in range(20)]
            
            for future in as_completed(futures):
                results.append(future.result())
        
        successful = sum(1 for _, success in results if success)
        self.log(f"  Concurrent test: {successful}/20 succeeded")
        
        return successful >= 18
    
    # ============ 4. 真实大型项目测试 ============
    def test_real_large_projects(self) -> bool:
        """真实大型项目测试"""
        self.log("="*60, "TEST")
        self.log("TEST 4: 真实大型项目测试", "TEST")
        self.log("="*60, "TEST")
        
        from fullpathtest.main import FullPathTestSystem
        
        system = FullPathTestSystem()
        
        projects = [
            ("FastAPI", "/workspace/cloned_fastapi_project/fastapi/__init__.py"),
            ("Django", "/workspace/django_project/django/__init__.py"),
        ]
        
        success = 0
        
        for name, path in projects:
            try:
                self.log(f"  Testing {name}...", "PROJECT")
                result = system.run_full_test(source_path=path)
                
                if result.get("status") == "success":
                    success += 1
                    self.log(f"  ✅ {name} - SUCCESS", "PASS")
                    
                    if "coverage_report" in result:
                        cov = result["coverage_report"]
                        self.log(f"     Coverage: {cov.statement_coverage:.1%}", "DETAIL")
                else:
                    self.record_bug(f"project_{name}", f"Failed with: {result.get('error')}", "HIGH")
                    self.log(f"  ❌ {name} - FAILED", "FAIL")
            except Exception as e:
                self.record_bug(f"project_{name}", f"Crash: {str(e)}", "CRITICAL")
        
        return success == len(projects)
    
    # ============ 5. 随机混乱输入测试 ============
    def test_chaotic_random_inputs(self) -> bool:
        """随机混乱输入测试"""
        self.log("="*60, "TEST")
        self.log("TEST 5: 随机混乱输入测试 (50次)", "TEST")
        self.log("="*60, "TEST")
        
        from fullpathtest.main import FullPathTestSystem
        
        system = FullPathTestSystem()
        
        # 生成混乱输入
        chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;':\",./<>?\t\n\r\x00"
        good_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
        
        input_types = [
            # 随机长度随机字符串
            lambda: "".join(random.choice(chars) for _ in range(random.randint(0, 200))),
            # 好路径 + 随机垃圾
            lambda: good_path + "".join(random.choice(chars) for _ in range(random.randint(0, 50))),
            # 随机垃圾 + 好路径
            lambda: "".join(random.choice(chars) for _ in range(random.randint(0, 50))) + good_path,
            # 混合路径片段
            lambda: "/".join(random.choice(["test", good_path, "\x00", "", "..", "../", "/"]) for _ in range(random.randint(1, 10))),
            # 空或点
            lambda: random.choice(["", ".", "..", "/", "///"]),
            # 极端重复
            lambda: random.choice(["/x", "x/", "/"]) * random.randint(1, 100),
        ]
        
        crashes = 0
        for i in range(50):
            try:
                input_generator = random.choice(input_types)
                test_input = input_generator()
                
                result = system.run_full_test(source_path=test_input)
                
                # 只要不崩溃就行
                if "status" in result:
                    if i % 10 == 0:
                        self.log(f"  Iteration {i+1}: status={result.get('status')}", "PROGRESS")
            except Exception as e:
                crashes += 1
                self.record_bug(f"chaos_{i}", f"Chaos crash: {str(e)}", "HIGH")
        
        self.log(f"  Chaotic test: {50 - crashes}/50 without crash")
        return crashes == 0
    
    # ============ 6. 复杂参数组合测试 ============
    def test_complex_param_combinations(self) -> bool:
        """复杂参数组合测试"""
        self.log("="*60, "TEST")
        self.log("TEST 6: 复杂参数组合测试", "TEST")
        self.log("="*60, "TEST")
        
        from fullpathtest.main import FullPathTestSystem
        from fullpathtest.types.core import LanguageType, LLMMode, SourceType
        
        system = FullPathTestSystem()
        test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
        
        # 各种参数组合
        param_combinations = [
            {"language": None},
            {"language": LanguageType.PYTHON},
            {"llm_mode": LLMMode.LOCAL_ONLY},
            {"llm_mode": LLMMode.CLOUD_ONLY},
            {"source_type": SourceType.LOCAL_DIRECTORY},
            {"user_command": "全面测试这个代码库"},
            {"requirements": ["高覆盖率", "无缺陷"]},
            # 组合
            {"language": LanguageType.PYTHON, "llm_mode": LLMMode.LOCAL_ONLY},
            {"user_command": "test", "requirements": ["coverage"]},
        ]
        
        success = 0
        for i, params in enumerate(param_combinations):
            try:
                result = system.run_full_test(source_path=test_path, **params)
                if result.get("status") == "success":
                    success += 1
                    self.log(f"  ✅ Combination {i}: SUCCESS", "PASS")
                else:
                    self.log(f"  ⚠️ Combination {i}: {result.get('status')}", "WARN")
            except Exception as e:
                self.record_bug(f"param_{i}", f"Param combination failed: {str(e)}", "MEDIUM")
        
        self.log(f"  Param combinations: {success}/{len(param_combinations)} success")
        return success >= len(param_combinations) * 0.7
    
    # ============ 运行所有测试 ============
    def run_all_extreme_tests(self) -> Dict[str, Any]:
        """运行所有极端测试"""
        self.log("\n" + "="*70, "MAIN")
        self.log("V16.0 - 超极端现实场景深度测试系统", "MAIN")
        self.log("="*70 + "\n", "MAIN")
        
        results = {}
        
        # 1. 极端输入测试
        results["extreme_inputs"] = self.run_test("极端边界条件", self.test_extreme_inputs)
        
        # 2. 超长时间测试
        results["long_running"] = self.run_test("超长时间稳定性", self.test_long_running_stability)
        
        # 3. 并发测试
        results["massive_concurrency"] = self.run_test("超大规模并发", self.test_massive_concurrency)
        
        # 4. 真实项目测试
        results["real_projects"] = self.run_test("真实大型项目", self.test_real_large_projects)
        
        # 5. 随机混乱测试
        results["chaos"] = self.run_test("随机混乱输入", self.test_chaotic_random_inputs)
        
        # 6. 复杂参数组合
        results["params"] = self.run_test("复杂参数组合", self.test_complex_param_combinations)
        
        # 最终总结
        self.print_final_summary(results)
        
        return results
    
    def print_final_summary(self, results: Dict[str, Any]):
        """打印最终总结"""
        self.log("\n" + "="*70, "SUMMARY")
        self.log("最终测试总结", "SUMMARY")
        self.log("="*70, "SUMMARY")
        
        total_time = time.time() - self.start_time
        pass_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        self.log(f"\n总耗时: {total_time:.2f}秒")
        self.log(f"测试数: {self.total_tests}")
        self.log(f"通过数: {self.passed_tests}")
        self.log(f"通过率: {pass_rate:.1f}%")
        self.log(f"发现BUG: {len(self.found_bugs)}")
        
        if self.found_bugs:
            self.log("\n发现的BUG:")
            for bug in self.found_bugs:
                self.log(f"  - {bug['test_name']}: {bug['description'][:100]}...")
        
        if pass_rate >= 90 and len(self.found_bugs) == 0:
            self.log("\n🎉 完美！系统在所有超极端测试中表现出色！", "FINAL_PASS")
        elif pass_rate >= 80:
            self.log("\n✅ 良好！系统基本稳定，但有改进空间", "FINAL_GOOD")
        else:
            self.log("\n⚠️ 需要改进！系统在极端条件下表现不佳", "FINAL_WARN")


def main():
    """主函数"""
    tester = ExtremeTestSystem()
    results = tester.run_all_extreme_tests()
    
    # 保存日志
    log_file = Path("/workspace/v16_test_log.txt")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("\n".join(tester.test_logs))
    print(f"\n📝 Log saved to: {log_file}")
    
    return 0 if len(tester.found_bugs) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
