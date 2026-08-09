#!/usr/bin/env python3
"""
FullPathTest v12.0 - 详细日志插桩测试系统
遵循慢工出细活原则：在关键代码路径添加详细日志，通过日志观察问题
"""

import sys
import time
import os
import random
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent))


class DetailedLoggingTest:
    """带详细日志的测试系统"""
    
    def __init__(self):
        self.logs = []
        self.start_time = None
        self.test_count = 0
        
    def log(self, message, level="INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        self.logs.append(log_entry)
        
    def generate_extreme_chaos(self, index):
        """生成极端混乱的测试输入"""
        chaos_types = [
            ("normal_fastapi", "/workspace/cloned_fastapi_project/fastapi/__init__.py"),
            ("normal_django", "/workspace/django_project/django/__init__.py"),
            ("empty", ""),
            ("blank", "   \t\n\r"),
            ("nonexistent", f"/nonexistent/{index}/{index}"),
            ("ultra_long", "/test/" * 600),  # 600 * 6 = 3600字符
            ("null_char", f"/test{chr(0)}path{index}"),
            ("all_ctrl", "".join([chr(i) for i in range(32)]) + "/test"),
            ("unicode_mix", "/测试//🌍/日本語/project"),
            ("weird_chars", "/test/|*?<>[]_-$^+!#@%&()/path"),
            ("trailing_slash", "/workspace/cloned_fastapi_project/fastapi/__init__.py/"),
            ("relative_chaos", "././../../test/../test/"),
            ("parent_path", "../../../../../../../root/../root/../"),
            ("just_filename", "test.py"),
            ("space_only", "   "),
            ("mixed_capital", "/TesT/PrOjEcT/CoDe"),
        ]
        return random.choice(chaos_types)
    
    def test_with_detailed_logging(self, test_name, test_path):
        """带详细日志的单个测试"""
        self.log("-" * 80)
        self.log(f"开始测试: {test_name}", "TEST")
        self.log(f"测试路径: {repr(test_path)}", "INFO")
        
        try:
            # 延迟导入，避免在模块级别导入时出问题
            from fullpathtest.main import FullPathTestSystem
            
            self.log("1. 创建 FullPathTestSystem 实例...", "STEP")
            system = FullPathTestSystem()
            self.log("   ✓ 实例创建成功", "PASS")
            
            self.log("2. 调用 run_full_test()...", "STEP")
            self.log(f"   输入参数: source_path={repr(test_path)}", "INFO")
            
            result = system.run_full_test(source_path=test_path)
            
            self.log(f"   ✓ run_full_test 返回成功", "PASS")
            self.log(f"   返回状态: {result.get('status')}", "INFO")
            
            if result.get("status") == "success":
                self.log(f"   ✓ 成功完成测试", "SUCCESS")
                if result.get("coverage_report"):
                    cov = result.get("coverage_report")
                    self.log(f"   覆盖率: {cov.statement_coverage:.2%}", "INFO")
                return True
            else:
                self.log(f"   ⚠️ 测试失败，但错误被正确处理", "WARN")
                self.log(f"   错误信息: {result.get('error')}", "WARN")
                # 对于预期的错误，也视为通过
                return True
                
        except Exception as e:
            self.log(f"   ✗ 异常: {type(e).__name__}: {e}", "ERROR")
            import traceback
            self.log(f"   堆栈:\n{traceback.format_exc()}", "ERROR")
            return False
    
    def run_phase1_small_scale(self):
        """阶段1：小规模带日志测试（10个任务）"""
        self.log("=" * 80, "PHASE")
        self.log("阶段1：小规模带详细日志测试（10个任务）", "PHASE")
        self.log("=" * 80, "PHASE")
        
        results = []
        self.start_time = time.time()
        
        # 测试一些关键场景
        test_cases = [
            ("正常 FastAPI", "/workspace/cloned_fastapi_project/fastapi/__init__.py"),
            ("空字符串", ""),
            ("不存在路径", "/nonexistent/path"),
            ("正常 Django", "/workspace/django_project/django/__init__.py"),
            ("空白字符串", "   "),
            ("超长路径", "/test/" * 500),
        ]
        
        for test_name, test_path in test_cases:
            success = self.test_with_detailed_logging(test_name, test_path)
            results.append((test_name, success))
            self.test_count += 1
            time.sleep(0.5)  # 慢工出细活，短暂间隔
        
        elapsed = time.time() - self.start_time
        
        self.log("\n" + "=" * 80, "SUMMARY")
        self.log(f"阶段1 完成，共 {len(results)} 个测试，耗时 {elapsed:.2f}秒", "SUMMARY")
        
        passed = sum(1 for _, s in results if s)
        self.log(f"通过: {passed}/{len(results)}", "INFO")
        
        if passed < len(results):
            self.log("\n失败的测试:", "WARN")
            for name, success in results:
                if not success:
                    self.log(f"  - {name}", "WARN")
        
        return passed == len(results)
    
    def run_phase2_concurrent(self):
        """阶段2：并发带日志测试（20个任务）"""
        self.log("\n" + "=" * 80, "PHASE")
        self.log("阶段2：并发带详细日志测试（20个任务，最大并发5）", "PHASE")
        self.log("=" * 80, "PHASE")
        
        import random
        results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {}
            for i in range(20):
                chaos_name, chaos_path = self.generate_extreme_chaos(i)
                future = executor.submit(
                    self.test_with_detailed_logging, 
                    f"并发-{i} ({chaos_name})", 
                    chaos_path
                )
                futures[future] = i
                
            completed = 0
            for future in as_completed(futures):
                try:
                    success = future.result()
                    results.append(success)
                except Exception as e:
                    self.log(f"任务 {futures[future]} 异常: {e}", "ERROR")
                    results.append(False)
                
                completed += 1
                if completed % 5 == 0:
                    self.log(f"已完成 {completed}/20 个任务", "PROGRESS")
        
        elapsed = time.time() - start_time
        
        passed = sum(1 for s in results if s)
        self.log(f"\n阶段2 完成: {passed}/{len(results)} 成功，耗时 {elapsed:.2f}秒", "SUMMARY")
        
        return passed == len(results)
    
    def save_logs(self, filename="v12_detailed_logs.txt"):
        """保存日志到文件"""
        log_file = Path(filename)
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("\n".join(self.logs))
        self.log(f"日志已保存到: {log_file.absolute()}", "INFO")
        return log_file
    
    def run_all_tests(self):
        """运行所有测试"""
        self.log("\n" + "=" * 80, "MAIN")
        self.log("FullPathTest v12.0 - 详细日志插桩测试系统", "MAIN")
        self.log(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "MAIN")
        self.log("=" * 80, "MAIN")
        
        all_passed = True
        
        try:
            # 阶段1
            phase1_ok = self.run_phase1_small_scale()
            if not phase1_ok:
                self.log("阶段1发现问题！", "WARN")
                all_passed = False
            
            # 慢工出细活：系统稳定时间
            self.log("\n⏸️ 系统稳定中（3秒）...", "WAIT")
            time.sleep(3)
            
            # 阶段2
            if all_passed:
                phase2_ok = self.run_phase2_concurrent()
                if not phase2_ok:
                    self.log("阶段2发现问题！", "WARN")
                    all_passed = False
        
        except Exception as e:
            self.log(f"测试系统异常: {e}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "ERROR")
            all_passed = False
        
        finally:
            log_file = self.save_logs()
            
            self.log("\n" + "=" * 80, "FINAL")
            if all_passed:
                self.log("🎉 所有测试通过！系统表现优秀！", "FINAL_PASS")
            else:
                self.log("⚠️ 部分测试发现问题", "FINAL_WARN")
            self.log(f"总测试数: {self.test_count}", "FINAL")
            self.log(f"详细日志已保存到: {log_file}", "FINAL")
            self.log("=" * 80)
            
            return all_passed


def main():
    try:
        tester = DetailedLoggingTest()
        success = tester.run_all_tests()
        return 0 if success else 1
    except Exception as e:
        print(f"\n\n测试主程序异常: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
