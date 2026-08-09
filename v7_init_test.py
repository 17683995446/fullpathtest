#!/usr/bin/env python3
"""
FullPathTest v7.0 - 初始化细致测试
慢工出细活：先小规模发现问题，再逐步扩大
"""

import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fullpathtest.main import FullPathTestSystem


def log(message, level="INFO"):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def test_single_task():
    """细致测试单个任务"""
    log("=" * 70)
    log("细致测试：单个任务")
    log("=" * 70)
    
    test_path = "/workspace/cloned_fastapi_project/fastapi/__init__.py"
    
    try:
        start = time.time()
        system = FullPathTestSystem()
        result = system.run_full_test(
            source_path=test_path,
            llm_mode="LOCAL_ONLY"
        )
        
        elapsed = time.time() - start
        
        status = result.get("status", "unknown")
        log(f"状态: {status}", "RESULT")
        
        if status == "success":
            coverage_report = result.get("coverage_report")
            statement_coverage = coverage_report.statement_coverage if coverage_report else 0
            log(f"覆盖率: {statement_coverage * 100:.1f}%", "RESULT")
            
            defect_report = result.get("defect_report")
            defect_count = len(defect_report.defects) if defect_report else 0
            log(f"缺陷数: {defect_count}", "RESULT")
            
            log(f"耗时: {elapsed:.2f}秒", "RESULT")
            return True
        else:
            log(f"错误: {result.get('error', 'unknown')}", "ERROR")
            return False
            
    except Exception as e:
        log(f"异常: {str(e)}", "EXCEPTION")
        traceback.print_exc()
        return False


def test_error_handling():
    """细致测试错误处理"""
    log("\n" + "=" * 70)
    log("细致测试：错误处理")
    log("=" * 70)
    
    test_cases = [
        ("空路径", ""),
        ("不存在路径", "/this/path/does/not/exist"),
        ("单字符路径", "/a"),
    ]
    
    success_count = 0
    total = 0
    
    for name, path in test_cases:
        total += 1
        try:
            log(f"测试: {name}", "TEST")
            system = FullPathTestSystem()
            result = system.run_full_test(source_path=path)
            
            status = result.get("status", "unknown")
            
            if status != "success":
                log(f"  ✅ 正确处理: {result.get('error', 'unknown')[:80]}", "PASS")
                success_count += 1
            else:
                log(f"  ❌ 意外成功", "FAIL")
                
        except Exception as e:
            log(f"  ✅ 正确捕获异常: {str(e)[:80]}", "PASS")
            success_count += 1
    
    log(f"\n错误处理测试结果: {success_count}/{total} 通过", "SUMMARY")
    return success_count == total


def main():
    print("\n" + "=" * 70)
    print("FullPathTest v7.0 - 慢工出细活 初始化测试")
    print("=" * 70)
    
    print("\n📋 测试计划:")
    print("  1. 单个任务正常运行")
    print("  2. 错误处理验证")
    
    all_passed = True
    
    # 测试1: 单个任务
    print("\n" + "-" * 70)
    if test_single_task():
        print("✅ 单个任务测试通过")
    else:
        print("❌ 单个任务测试失败")
        all_passed = False
    
    # 测试2: 错误处理
    print("\n" + "-" * 70)
    if test_error_handling():
        print("✅ 错误处理测试通过")
    else:
        print("❌ 错误处理测试有问题")
        all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ 初始化测试全部通过！")
        print("可以开始深度测试...")
    else:
        print("⚠️  发现问题，先修复再继续！")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
