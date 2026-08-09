#!/usr/bin/env python3
"""
FullPathTest v4.0 - 深度缺陷发现框架
专门设计用来发现系统缺陷的极端测试
"""

import os
import sys
import json
import time
import random
import string
import gc
import tracemalloc
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from datetime import datetime
from pathlib import Path


class DefectSeverity(Enum):
    """缺陷严重性"""
    BLOCKER = "blocker"      # 系统无法使用
    CRITICAL = "critical"    # 核心功能不可用
    HIGH = "high"          # 主要功能受影响
    MEDIUM = "medium"     # 次要功能受影响
    LOW = "low"         # 轻微问题


class DefectCategory(Enum):
    """缺陷类别"""
    MEMORY_LEAK = "memory_leak"
    PERFORMANCE_BUG = "performance_bug"
    LOGIC_ERROR = "logic_error"
    RACE_CONDITION = "race_condition"
    INPUT_VALIDATION = "input_validation"
    ERROR_HANDLING = "error_handling"
    CACHE_INVALIDATION = "cache_invalidation"
    TYPE_ERROR = "type_error"
    NONE_RETURN = "none_return"
    INFINITE_LOOP = "infinite_loop"


@dataclass
class Defect:
    """缺陷数据类"""
    defect_id: str
    severity: DefectSeverity
    category: DefectCategory
    title: str
    description: str
    reproduction: str
    location: str
    impact: str
    discovered_at: datetime
    stack_trace: Optional[str] = None
    fixed: bool = False
    fix_description: Optional[str] = None


class DeepDefectDiscoverer:
    """深度缺陷发现器"""
    
    def __init__(self):
        self.defects: List[Defect] = []
        self.test_cases: List[Dict[str, Any]] = []
    
    def log_defect(self, defect: Defect):
        """记录发现的缺陷"""
        self.defects.append(defect)
        print(f"🔴 发现缺陷: {defect.severity.value} - {defect.title}")
        print(f"   描述: {defect.description}")
        print(f"   位置: {defect.location}")
    
    def test_input_validation(self):
        """测试1: 输入验证缺陷"""
        print("\n" + "="*60)
        print("测试1: 输入验证缺陷")
        print("="*60)
        
        try:
            from full_path_test.ai.ai_integration import (
                CodeAnalysisRequest,
                AnalysisType,
                LLMConfiguration
            )
            
            # 测试极端输入
            print("🔄 测试极端输入...")
            
            # 1. 极大输入
            print("  1. 测试极大输入...")
            try:
                huge_code = "def foo():\n" * 10000 + "    pass"
                request = CodeAnalysisRequest(
                    code=huge_code,
                    analysis_types=[AnalysisType.CODE_QUALITY]
                )
                print("    ✅ 接受大输入")
            except Exception as e:
                if isinstance(e, MemoryError):
                    self.log_defect(Defect(
                        defect_id="DEFECT_001",
                        severity=DefectSeverity.CRITICAL,
                        category=DefectCategory.INPUT_VALIDATION,
                        title="大输入导致内存耗尽",
                        description="处理超大代码输入时发生内存溢出",
                        reproduction="创建包含10000行重复内容的代码请求",
                        location="full_path_test/ai/ai_integration.py - CodeAnalysisRequest",
                        impact="拒绝服务攻击风险"
                    ))
            
            # 2. 空输入
            print("  2. 测试空输入...")
            try:
                request = CodeAnalysisRequest(
                    code="",
                    analysis_types=[AnalysisType.CODE_QUALITY]
                )
                print("    ✅ 接受空输入")
            except Exception as e:
                self.log_defect(Defect(
                    defect_id="DEFECT_002",
                    severity=DefectSeverity.MEDIUM,
                    category=DefectCategory.INPUT_VALIDATION,
                    title="空输入未正确处理",
                    description=f"空输入导致异常: {str(e)}",
                    reproduction="传入空代码字符串",
                    location="full_path_test/ai/ai_integration.py",
                    impact="用户体验"
                ))
            
            # 3. 特殊字符输入
            print("  3. 测试特殊字符输入...")
            try:
                special_code = "def foo(): \x00\x01\x02\x03\x04"
                request = CodeAnalysisRequest(
                    code=special_code,
                    analysis_types=[AnalysisType.CODE_QUALITY]
                )
                print("    ✅ 接受特殊字符")
            except Exception as e:
                self.log_defect(Defect(
                    defect_id="DEFECT_003",
                    severity=DefectSeverity.MEDIUM,
                    category=DefectCategory.INPUT_VALIDATION,
                    title="特殊字符输入处理错误",
                    description=f"特殊字符导致异常: {str(e)}",
                    reproduction="传入包含不可打印字符的代码",
                    location="full_path_test/ai/ai_integration.py",
                    impact="边界情况"
                ))
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    def test_memory_leaks(self):
        """测试2: 内存泄漏"""
        print("\n" + "="*60)
        print("测试2: 内存泄漏")
        print("="*60)
        
        try:
            from full_path_test.ai.ai_integration import (
                create_ai_analyzer,
                CodeAnalysisRequest,
                AnalysisType
            )
            from full_path_test.performance.performance_system import LRUCache
            
            # 1. 测试缓存内存泄漏
            print("🔄 测试缓存内存泄漏...")
            tracemalloc.start()
            
            snapshot1 = tracemalloc.take_snapshot()
            cache = LRUCache(max_size=100)
            
            # 大量操作
            for i in range(10000):
                cache.set(f"key_{i}", f"value_{i}" * 100)
            
            snapshot2 = tracemalloc.take_snapshot()
            
            top_stats = snapshot2.compare_to(snapshot1, 'lineno')
            memory_growth = 0
            
            for stat in top_stats[:10]:
                if "LRUCache" in str(stat.traceback):
                    memory_growth += stat.size
            
            memory_growth_mb = memory_growth / 1024 / 1024
            
            print(f"  内存增长: {memory_growth_mb:.2f} MB")
            
            if memory_growth_mb > 50:  # 如果超过50MB
                self.log_defect(Defect(
                    defect_id="DEFECT_004",
                    severity=DefectSeverity.HIGH,
                    category=DefectCategory.MEMORY_LEAK,
                    title="LRUCache存在内存泄漏",
                    description=f"10000次缓存操作导致内存增长{memory_growth_mb:.2f}MB",
                    reproduction="多次缓存操作，观察内存增长",
                    location="full_path_test/performance/performance_system.py - LRUCache",
                    impact="长时间运行时内存耗尽"
                ))
            else:
                print("  ✅ 缓存内存使用正常")
            
            # 2. 测试AI分析器内存泄漏
            print("\n🔄 测试AI分析器内存泄漏...")
            initial_snapshot = tracemalloc.take_snapshot()
            
            analyzer = create_ai_analyzer()
            
            for i in range(100):
                try:
                    request = CodeAnalysisRequest(
                        code=f"def foo{i}(): return {i}",
                        analysis_types=[AnalysisType.CODE_QUALITY]
                    )
                    analyzer.analyze_code(request)
                except:
                    pass
            
            gc.collect()
            final_snapshot = tracemalloc.take_snapshot()
            
            top_stats = final_snapshot.compare_to(initial_snapshot, 'lineno')
            
            ai_memory_growth = 0
            for stat in top_stats[:10]:
                if "ai_integration" in str(stat.traceback):
                    ai_memory_growth += stat.size
            
            ai_memory_mb = ai_memory_growth / 1024 / 1024
            print(f"  AI模块内存增长: {ai_memory_mb:.2f} MB")
            
            if ai_memory_mb > 100:  # 如果超过100MB
                self.log_defect(Defect(
                    defect_id="DEFECT_005",
                    severity=DefectSeverity.HIGH,
                    category=DefectCategory.MEMORY_LEAK,
                    title="AI分析器存在内存泄漏",
                    description=f"100次分析操作导致内存增长{ai_memory_mb:.2f}MB",
                    reproduction="循环调用analyze_code",
                    location="full_path_test/ai/ai_integration.py - AICodeAnalyzer",
                    impact="持续使用时内存耗尽"
                ))
            else:
                print("  ✅ AI分析器内存使用正常")
            
            tracemalloc.stop()
            
        except Exception as e:
            print(f"❌ 内存泄漏测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    def test_error_handling(self):
        """测试3: 错误处理缺陷"""
        print("\n" + "="*60)
        print("测试3: 错误处理")
        print("="*60)
        
        try:
            from full_path_test.ai.ai_integration import (
                create_ai_analyzer,
                CodeAnalysisRequest,
                AnalysisType,
                LLMConfiguration,
                LLMProvider
            )
            
            # 1. 测试无效provider
            print("🔄 测试无效provider...")
            try:
                config = LLMConfiguration(
                    provider="invalid_provider",
                    model="test"
                )
                print("    ℹ️  创建配置成功")
            except Exception as e:
                print(f"    ❌ 无效provider处理: {e}")
            
            # 2. 测试无效模型
            print("\n🔄 测试无效模型...")
            try:
                from full_path_test.ai.ai_integration import MockLLMClient
                
                config = LLMConfiguration(
                    provider=LLMProvider.MOCK,
                    model="nonexistent_model"
                )
                client = MockLLMClient(config)
                
                result = client.generate("test code")
                print("    ✅ 无效模型优雅处理")
            except Exception as e:
                self.log_defect(Defect(
                    defect_id="DEFECT_006",
                    severity=DefectSeverity.MEDIUM,
                    category=DefectCategory.ERROR_HANDLING,
                    title="无效模型处理不当",
                    description=f"无效模型导致未捕获异常: {str(e)}",
                    reproduction="使用不存在的模型名称",
                    location="full_path_test/ai/ai_integration.py",
                    impact="程序崩溃"
                ))
            
            # 3. 测试网络错误
            print("\n🔄 测试网络错误...")
            try:
                from full_path_test.ai.ai_integration import OllamaLLMClient
                
                # 测试无效API端点
                config = LLMConfiguration(
                    provider=LLMProvider.OLLAMA,
                    model="llama2",
                    api_base="http://127.0.0.1:9999",  # 无效端口
                    timeout=1
                )
                
                try:
                    client = OllamaLLMClient(config)
                    result = client.generate("test", "test")
                    print(f"    ℹ️  结果: {result[:50]}...")
                except Exception as e:
                    print(f"    ⚠️  网络错误被捕获: {type(e).__name__}")
            
            except ImportError as e:
                print(f"    ℹ️  Ollama客户端不可用")
        
        except Exception as e:
            print(f"❌ 错误处理测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    def test_performance_regressions(self):
        """测试4: 性能回归"""
        print("\n" + "="*60)
        print("测试4: 性能回归")
        print("="*60)
        
        try:
            from full_path_test.performance.performance_system import (
                LRUCache,
                benchmark
            )
            
            # 1. 基准性能
            print("🔄 基准性能测试...")
            
            cache = LRUCache(max_size=1000)
            
            def cache_operations():
                for i in range(1000):
                    cache.set(f"key_{i}", f"value_{i}")
                    cache.get(f"key_{i}")
            
            result = benchmark(cache_operations, iterations=100)
            
            print(f"  迭代次数: {result['iterations']}")
            print(f"  平均耗时: {result['avg']:.6f}秒")
            print(f"  吞吐量: {result['throughput']:.1f}/秒")
            
            avg_time = result['avg']
            if avg_time > 0.01:  # 如果单次超过10ms
                self.log_defect(Defect(
                    defect_id="DEFECT_007",
                    severity=DefectSeverity.MEDIUM,
                    category=DefectCategory.PERFORMANCE_BUG,
                    title="缓存性能低于预期",
                    description=f"单次缓存操作平均耗时{avg_time*1000:.2f}ms，超过预期10ms",
                    reproduction="运行缓存操作基准测试",
                    location="full_path_test/performance/performance_system.py",
                    impact="整体性能下降"
                ))
            else:
                print("  ✅ 缓存性能良好")
        
        except Exception as e:
            print(f"❌ 性能测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    def test_type_safety(self):
        """测试5: 类型安全缺陷"""
        print("\n" + "="*60)
        print("测试5: 类型安全")
        print("="*60)
        
        try:
            from full_path_test.ai.ai_integration import (
                CodeAnalysisRequest,
                AnalysisType
            )
            
            # 测试1: 传入错误类型
            print("🔄 测试错误类型传入...")
            type_errors = []
            
            try:
                # 应该是字符串，但传入数字
                request = CodeAnalysisRequest(
                    code=12345,
                    analysis_types=[AnalysisType.CODE_QUALITY]
                )
                print("  ⚠️  接受了数字类型代码")
                type_errors.append("code接受非字符串类型")
            except Exception as e:
                print("  ✅ 拒绝了非字符串类型")
            
            # 检查结果
            if type_errors:
                self.log_defect(Defect(
                    defect_id="DEFECT_008",
                    severity=DefectSeverity.LOW,
                    category=DefectCategory.TYPE_ERROR,
                    title="类型验证不足",
                    description=f"接受了错误的类型: {', '.join(type_errors)}",
                    reproduction="传入非字符串类型参数",
                    location="full_path_test/ai/ai_integration.py",
                    impact="潜在运行时错误"
                ))
            else:
                print("  ✅ 类型检查良好")
        
        except Exception as e:
            print(f"❌ 类型安全测试失败: {e}")
    
    def test_fuzzing(self):
        """测试6: Fuzzing测试"""
        print("\n" + "="*60)
        print("测试6: Fuzzing测试")
        print("="*60)
        
        try:
            from full_path_test.ai.ai_integration import (
                CodeAnalysisRequest,
                AnalysisType,
                LLMConfiguration,
                MockLLMClient
            )
            
            config = LLMConfiguration(provider=LLMProvider.MOCK)
            client = MockLLMClient(config)
            
            # 生成随机输入
            print("🔄 执行100次Fuzzing...")
            found_crashes = 0
            
            for i in range(100):
                # 随机字符串
                random_code = ''.join(random.choice(string.printable) 
                                     for _ in range(random.randint(1, 1000)))
                
                try:
                    # 尝试各种随机输入
                    request = CodeAnalysisRequest(
                        code=random_code,
                        analysis_types=[AnalysisType.CODE_QUALITY]
                    )
                    
                    result = client.generate(random_code, "test")
                    
                except Exception as e:
                    found_crashes += 1
                    print(f"  ❌ 第{i+1}次Fuzzing崩溃: {type(e).__name__}")
            
            if found_crashes > 0:
                self.log_defect(Defect(
                    defect_id="DEFECT_009",
                    severity=DefectSeverity.CRITICAL,
                    category=DefectCategory.INPUT_VALIDATION,
                    title="Fuzzing发现崩溃",
                    description=f"100次随机Fuzzing中有{found_crashes}次导致崩溃",
                    reproduction="运行Fuzzing测试",
                    location="full_path_test/ai/ai_integration.py",
                    impact="拒绝服务攻击风险"
                ))
            else:
                print("  ✅ Fuzzing测试通过，无崩溃")
        
        except Exception as e:
            print(f"❌ Fuzzing测试失败: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    print("\n" + "="*80)
    print("FullPathTest v4.0 - 深度缺陷发现框架")
    print("专门为发现系统缺陷而设计的极端测试")
    print("="*80)
    
    discoverer = DeepDefectDiscoverer()
    
    # 运行所有测试
    discoverer.test_input_validation()
    discoverer.test_memory_leaks()
    discoverer.test_error_handling()
    discoverer.test_performance_regressions()
    discoverer.test_type_safety()
    discoverer.test_fuzzing()
    
    # 生成报告
    print("\n" + "="*80)
    print("缺陷发现报告")
    print("="*80)
    
    total_defects = len(discoverer.defects)
    
    if total_defects == 0:
        print("\n🎉 太棒了！没有发现任何缺陷！")
        return
    
    # 按严重程度统计
    severity_counts = {}
    for defect in discoverer.defects:
        severity = defect.severity
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    print(f"\n📊 发现的缺陷总数: {total_defects}")
    for severity, count in severity_counts.items():
        icon = {
            DefectSeverity.BLOCKER: "🔴",
            DefectSeverity.CRITICAL: "🔴",
            DefectSeverity.HIGH: "🟠",
            DefectSeverity.MEDIUM: "🟡",
            DefectSeverity.LOW: "🟢"
        }.get(severity, "⚪")
        print(f"  {icon} {severity.value}: {count}")
    
    # 详细列表
    print(f"\n📝 缺陷详情:")
    for i, defect in enumerate(discoverer.defects, 1):
        icon = {
            DefectSeverity.BLOCKER: "🔴",
            DefectSeverity.CRITICAL: "🔴",
            DefectSeverity.HIGH: "🟠",
            DefectSeverity.MEDIUM: "🟡",
            DefectSeverity.LOW: "🟢"
        }.get(defect.severity, "⚪")
        
        print(f"\n{i}. {icon} [{defect.severity.value.upper()}] {defect.title}")
        print(f"   ID: {defect.defect_id}")
        print(f"   类别: {defect.category.value}")
        print(f"   描述: {defect.description}")
        print(f"   位置: {defect.location}")
        print(f"   复现步骤: {defect.reproduction}")
        print(f"   影响: {defect.impact}")
    
    # 保存报告
    report_data = {
        'total_defects': total_defects,
        'severity_distribution': {
            severity.value: count
            for severity, count in severity_counts.items()
        },
        'defects': [
            {
                'defect_id': d.defect_id,
                'severity': d.severity.value,
                'category': d.category.value,
                'title': d.title,
                'description': d.description,
                'location': d.location,
                'reproduction': d.reproduction,
                'impact': d.impact,
                'discovered_at': d.discovered_at.isoformat()
            }
            for d in discoverer.defects
        ]
    }
    
    with open('/workspace/deep_defect_report.json', 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 报告已保存到: /workspace/deep_defect_report.json")
    
    # 总结
    print("\n" + "="*80)
    print("测试完成总结")
    print("="*80)
    
    if DefectSeverity.BLOCKER in severity_counts or DefectSeverity.CRITICAL in severity_counts:
        print(f"⚠️  警告: 发现了严重缺陷！需要立即修复！")
    elif DefectSeverity.HIGH in severity_counts:
        print(f"⚠️  注意: 发现了高优先级缺陷")
    elif total_defects > 0:
        print(f"✅ 整体良好: 发现了{total_defects}个中低优先级缺陷")
    else:
        print(f"🎉 完美！没有发现任何缺陷！")
    
    print("\n" + "="*80)
    print("测试完成")
    print("="*80 + "\n")
    
    return discoverer


if __name__ == "__main__":
    discoverer = main()
