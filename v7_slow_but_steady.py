#!/usr/bin/env python3
"""
FullPathTest v7.0 - 慢工出细活深度测试
遵循慢工出细活原理：不追求速度，追求彻底
"""

import sys
import time
import threading
import traceback
import gc
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from fullpathtest.main import FullPathTestSystem

class SlowButSteadyTester:
    """慢工出细活的测试器"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.results = []
        self.errors = []
        self.success_count = 0
        self.failure_count = 0
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [{level}] {message}")
        
    def single_test(self, task_id, test_path):
        """单个测试任务（细致）"""
        try:
            self.log(f"开始任务 {task_id}", "TASK")
            
            system = FullPathTestSystem()
            
            # 慢工出细活：详细记录每个阶段
            phase_start = time.time()
            result = system.run_full_test(
                source_path=test_path,
                llm_mode="LOCAL_ONLY"
            )
            
            phase_time = time.time() - phase_start
            
            status = result.get('status', 'unknown')
            
            if status == 'success':
                self.success_count += 1
                self.log(f"任务 {task_id} 成功 (耗时: {phase_time:.2f}s)", "SUCCESS")
                return True
            else:
                self.failure_count += 1
                error_msg = result.get('error', '未知错误')
                self.log(f"任务 {task_id} 失败: {error_msg}", "ERROR")
                self.errors.append({
                    'task_id': task_id,
                    'error': error_msg
                })
                return False
                
        except Exception as e:
            self.failure_count += 1
            self.log(f"任务 {task_id} 异常: {str(e)}", "EXCEPTION")
            traceback.print_exc()
            self.errors.append({
                'task_id': task_id,
                'exception': str(e),
                'traceback': traceback.format_exc()
            })
            return False
            
    def phase_one_concurrency(self):
        """第一阶段：100并发任务"""
        self.log("=" * 70, "PHASE")
        self.log("第一阶段：100并发任务", "PHASE")
        self.log("=" * 70, "PHASE")
        
        test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
        concurrency = 100
        
        self.log(f"启动 {concurrency} 个并发任务...", "INFO")
        phase_start = time.time()
        
        # 慢工出细活：用线程池控制
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            for i in range(concurrency):
                futures.append(executor.submit(self.single_test, f"P1-T{i}", test_path))
            
            # 逐个收集结果
            completed = 0
            for future in as_completed(futures):
                try:
                    future.result()
                    completed += 1
                    if completed % 10 == 0:
                        self.log(f"已完成 {completed}/{concurrency} 任务...", "PROGRESS")
                except Exception as e:
                    self.log(f"任务失败: {e}", "ERROR")
        
        phase_time = time.time() - phase_start
        
        self.log(f"\n第一阶段结束（耗时: {phase_time:.2f}s）", "PHASE_END")
        self.log(f"成功: {self.success_count}, 失败: {self.failure_count}", "SUMMARY")
        
        return phase_time
        
    def phase_two_slow_pressure(self):
        """第二阶段：缓慢压力测试"""
        self.log("=" * 70, "PHASE")
        self.log("第二阶段：缓慢压力测试", "PHASE")
        self.log("=" * 70, "PHASE")
        
        test_path = "/workspace/django_project/django/__init__.py"
        iterations = 50
        
        self.log(f"启动 {iterations} 次连续任务...", "INFO")
        phase_start = time.time()
        
        for i in range(iterations):
            self.single_test(f"P2-T{i}", test_path)
            
            # 慢工出细活：每次间隔0.5秒
            if i < iterations - 1:
                time.sleep(0.5)
            
            if (i + 1) % 10 == 0:
                self.log(f"已完成 {i + 1}/{iterations} 任务...", "PROGRESS")
        
        phase_time = time.time() - phase_start
        
        self.log(f"\n第二阶段结束（耗时: {phase_time:.2f}s）", "PHASE_END")
        self.log(f"成功: {self.success_count}, 失败: {self.failure_count}", "SUMMARY")
        
        return phase_time
        
    def phase_three_boundary_stress(self):
        """第三阶段：边界条件压力测试"""
        self.log("=" * 70, "PHASE")
        self.log("第三阶段：边界条件压力测试", "PHASE")
        self.log("=" * 70, "PHASE")
        
        boundary_tests = [
            ("空", ""),
            ("不存在", "/nonexistent/path"),
            ("单字符", "/a"),
        ]
        
        for name, test_path in boundary_tests:
            self.log(f"测试边界: {name}", "TEST")
            try:
                self.single_test(f"P3-{name}", test_path)
            except Exception as e:
                self.log(f"边界测试 {name} 异常: {e}", "ERROR")
        
        self.log(f"第三阶段结束", "PHASE_END")
        
    def run_all(self):
        """运行所有测试"""
        self.log("\n" + "=" * 70, "MAIN")
        self.log("FullPathTest v7.0 - 慢工出细活深度测试", "MAIN")
        self.log("=" * 70, "MAIN")
        
        total_start = time.time()
        
        try:
            # 第一阶段：并发
            self.phase_one_concurrency()
            
            # 慢工出细活：间隔一下，让系统稳定
            self.log("等待系统稳定（3秒）...", "WAIT")
            time.sleep(3)
            
            # 第二阶段：缓慢压力
            self.phase_two_slow_pressure()
            
            # 再等一下
            self.log("再次等待系统稳定（2秒）...", "WAIT")
            time.sleep(2)
            
            # 第三阶段：边界测试
            self.phase_three_boundary_stress()
            
        except Exception as e:
            self.log(f"全局异常: {e}", "CRITICAL")
            traceback.print_exc()
            
        total_time = time.time() - total_start
        
        # 生成报告
        self.generate_report(total_time)
        
    def generate_report(self, total_time):
        """生成慢工出细活报告"""
        self.log("\n" + "=" * 70, "REPORT")
        self.log("慢工出细活 - 深度测试报告", "REPORT")
        self.log("=" * 70, "REPORT")
        
        self.log(f"\n📊 总体统计:", "REPORT")
        self.log(f"   总耗时: {total_time:.2f}秒", "REPORT")
        self.log(f"   成功任务: {self.success_count}", "REPORT")
        self.log(f"   失败任务: {self.failure_count}", "REPORT")
        
        if self.errors:
            self.log(f"\n❌ 发现 {len(self.errors)} 个错误:", "REPORT")
            for i, err in enumerate(self.errors[:10], 1):
                task_id = err.get('task_id', 'unknown')
                if 'exception' in err:
                    self.log(f"   {i}. [{task_id}] {err['exception'][:80]}", "REPORT")
                else:
                    self.log(f"   {i}. [{task_id}] {err['error'][:80]}", "REPORT")
            
            if len(self.errors) > 10:
                self.log(f"   ... 还有 {len(self.errors) - 10} 个错误", "REPORT")
        
        # 保存报告
        report_path = Path("/workspace/v7_slow_but_steady_report.json")
        import json
        
        report = {
            'total_time': total_time,
            'success': self.success_count,
            'failures': self.failure_count,
            'errors': self.errors,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log(f"\n✅ 详细报告已保存到: {report_path}", "REPORT")

def main():
    print("\n" + "=" * 70)
    print("FullPathTest v7.0 - 慢工出细活深度测试")
    print("=" * 70)
    print("\n⚠️  此测试将会缓慢但彻底地运行")
    print("⚠️  遵循原则：不追求速度，追求彻底")
    print("=" * 70 + "\n")
    
    try:
        tester = SlowButSteadyTester()
        tester.run_all()
        
        print("\n✅ 慢工出细活测试完成！")
        print("📁 查看 /workspace/v7_slow_but_steady_report.json 获取详细报告")
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 主程序异常: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
