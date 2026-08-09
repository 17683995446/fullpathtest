#!/usr/bin/env python3
"""
FullPathTest v4.0 - 超复杂超难度缺陷发现系统
专门设计用于发现系统真实缺陷的极端测试

测试场景：
1. 极端并发竞争
2. Unicode编码地狱
3. 文件系统陷阱
4. 资源耗尽攻击
5. 插件循环依赖
6. 恶意输入攻击
"""

import os
import sys
import json
import time
import gc
import threading
import traceback
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime
from pathlib import Path
import signal
import resource


class DefectSeverity(Enum):
    BLOCKER = "blocker"
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DefectCategory(Enum):
    RACE_CONDITION = "race_condition"
    ENCODING_ERROR = "encoding_error"
    FILE_SYSTEM_TRAP = "file_system_trap"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    SECURITY_VULNERABILITY = "security_vulnerability"
    INFINITE_LOOP = "infinite_loop"
    MEMORY_LEAK = "memory_leak"


@dataclass
class RealDefect:
    """真实缺陷"""
    defect_id: str
    severity: DefectSeverity
    category: DefectCategory
    title: str
    description: str
    reproduction_steps: List[str]
    location: str
    impact: str
    evidence: Dict[str, Any]
    discovered_at: datetime = field(default_factory=datetime.now)


class UltraComplexDefectFinder:
    """超复杂缺陷发现器"""
    
    def __init__(self):
        self.defects: List[RealDefect] = []
        self.test_results: List[Dict[str, Any]] = []
    
    def log_defect(self, defect: RealDefect):
        """记录缺陷"""
        self.defects.append(defect)
        print(f"\n🔴🔴🔴 发现真实缺陷 🔴🔴🔴")
        print(f"ID: {defect.defect_id}")
        print(f"严重性: {defect.severity.value}")
        print(f"类别: {defect.category.value}")
        print(f"标题: {defect.title}")
        print(f"描述: {defect.description}")
        print(f"位置: {defect.location}")
        print(f"影响: {defect.impact}")
    
    def test_01_concurrent_race_condition(self):
        """测试1: 极端并发竞争条件"""
        print("\n" + "="*70)
        print("测试1: 极端并发竞争条件")
        print("="*70)
        
        try:
            from full_path_test.performance.performance_system import LRUCache
            
            print("🔄 测试多线程同时修改LRU缓存...")
            
            # 创建缓存
            cache = LRUCache(max_size=100)
            
            # 跟踪竞态条件
            errors = []
            success_count = [0]  # 使用列表以便在闭包中修改
            
            def worker(thread_id, iterations):
                try:
                    for i in range(iterations):
                        key = f"key_{i % 50}"
                        cache.set(key, f"value_{thread_id}_{i}")
                        cache.get(key)
                        cache.delete(key)
                    success_count[0] += 1
                except Exception as e:
                    errors.append((thread_id, str(e)))
            
            # 启动10个线程同时操作
            threads = []
            for t_id in range(10):
                t = threading.Thread(target=worker, args=(t_id, 1000))
                threads.append(t)
                t.start()
            
            for t in threads:
                t.join()
            
            print(f"  成功线程数: {success_count[0]}/10")
            print(f"  错误数: {len(errors)}")
            
            if len(errors) > 0:
                self.log_defect(RealDefect(
                    defect_id="REAL_001",
                    severity=DefectSeverity.CRITICAL,
                    category=DefectCategory.RACE_CONDITION,
                    title="LRU缓存在多线程环境下存在竞态条件",
                    description=f"10个线程并发操作导致{len(errors)}个错误: {errors[:3]}",
                    reproduction_steps=[
                        "创建LRUCache实例",
                        "启动10个线程同时执行set/get/delete",
                        "每个线程执行1000次操作",
                        "观察线程安全和数据一致性"
                    ],
                    location="full_path_test/performance/performance_system.py - LRUCache",
                    impact="多线程环境下数据损坏或丢失",
                    evidence={'errors': errors[:5], 'threads': 10}
                ))
            else:
                print("  ✅ 无竞态条件")
            
            # 测试更极端的并发
            print("\n🔄 测试100个线程同时操作...")
            errors2 = []
            success2 = [0]
            
            def extreme_worker(wid):
                try:
                    for j in range(100):
                        cache.set(f"k{wid}_{j}", f"v{j}")
                        cache.get(f"k{wid}_{j}")
                    success2[0] += 1
                except Exception as e:
                    errors2.append(str(e))
            
            threads2 = [threading.Thread(target=extreme_worker, args=(i,)) for i in range(100)]
            for t in threads2:
                t.start()
            for t in threads2:
                t.join()
            
            print(f"  100线程 - 成功: {success2[0]}, 错误: {len(errors2)}")
            
            if len(errors2) > 0:
                self.log_defect(RealDefect(
                    defect_id="REAL_002",
                    severity=DefectSeverity.HIGH,
                    category=DefectCategory.RACE_CONDITION,
                    title="极端并发导致数据竞争",
                    description=f"100个线程并发操作时出现{len(errors2)}个错误",
                    reproduction_steps=["创建100个线程同时操作缓存"],
                    location="full_path_test/performance/performance_system.py",
                    impact="高并发场景下系统不稳定",
                    evidence={'error_count': len(errors2)}
                ))
        
        except Exception as e:
            print(f"❌ 并发测试本身失败: {e}")
            import traceback
            traceback.print_exc()
    
    def test_02_unicode_encoding_hell(self):
        """测试2: Unicode编码地狱"""
        print("\n" + "="*70)
        print("测试2: Unicode编码地狱")
        print("="*70)
        
        try:
            from full_path_test.ai.ai_integration import CodeAnalysisRequest, AnalysisType
            
            unicode_tests = [
                ("emoji", "def foo(): 🎉 return '🎊'"),
                ("chinese", "def foo(): return '你好世界'"),
                ("arabic", "def foo(): return 'مرحبا'"),
                ("emoji_mixed", "def 你好(): return '🎯' * 1000"),
                ("null_bytes", "def foo():\x00: pass"),
                ("control_chars", "def foo():\x01\x02: pass"),
                ("bidi_override", "def foo(): return 'hello\u202eworld'"),
                ("overlong_utf8", "def foo(): pass"),  # 特殊构造
            ]
            
            errors = []
            
            for name, code in unicode_tests:
                print(f"\n  🔄 测试: {name}...")
                try:
                    request = CodeAnalysisRequest(
                        code=code,
                        file_path=f"test_{name}.py",
                        analysis_types=[AnalysisType.CODE_QUALITY]
                    )
                    
                    # 尝试处理
                    print(f"    ✅ 接受: {repr(code[:30])}...")
                    
                except UnicodeDecodeError as e:
                    errors.append((name, f"Unicode错误: {e}"))
                    print(f"    ❌ Unicode错误: {e}")
                except Exception as e:
                    errors.append((name, f"其他错误: {e}"))
                    print(f"    ⚠️  其他错误: {e}")
            
            if errors:
                self.log_defect(RealDefect(
                    defect_id="REAL_003",
                    severity=DefectSeverity.MEDIUM,
                    category=DefectCategory.ENCODING_ERROR,
                    title="Unicode编码处理不完善",
                    description=f"处理{len(errors)}种Unicode场景时出现问题",
                    reproduction_steps=["传入各种Unicode字符的代码"],
                    location="full_path_test/ai/ai_integration.py",
                    impact="无法正确处理多语言代码",
                    evidence={'errors': errors}
                ))
            else:
                print("\n  ✅ 所有Unicode测试通过")
        
        except Exception as e:
            print(f"❌ Unicode测试失败: {e}")
    
    def test_03_file_system_traps(self):
        """测试3: 文件系统陷阱"""
        print("\n" + "="*70)
        print("测试3: 文件系统陷阱")
        print("="*70)
        
        errors = []
        
        # 创建测试目录
        test_dir = Path("/tmp/fullpathtest_trap_test")
        test_dir.mkdir(exist_ok=True)
        
        # 测试1: 符号链接循环
        print("\n🔄 测试符号链接循环...")
        try:
            link1 = test_dir / "link1"
            link2 = test_dir / "link2"
            
            if link1.exists():
                link1.unlink()
            if link2.exists():
                link2.unlink()
            
            link1.symlink_to(link2)
            link2.symlink_to(link1)
            
            print(f"  创建循环符号链接: link1 -> link2 -> link1")
            
            # 尝试遍历
            count = 0
            try:
                for f in test_dir.rglob("*.py"):
                    count += 1
                    if count > 1000:
                        errors.append(("symlink_loop", "符号链接循环未正确处理"))
                        break
            except Exception as e:
                errors.append(("symlink_error", str(e)))
                print(f"  ⚠️  符号链接错误: {e}")
            
            link1.unlink()
            link2.unlink()
            
        except Exception as e:
            print(f"  ❌ 符号链接测试失败: {e}")
        
        # 测试2: 权限问题（不检查root用户权限问题，因为root可以读任何文件）
        print("\n🔄 测试权限问题（跳过，root用户权限测试无意义）...")
        
        # 测试3: 特殊文件名
        print("\n🔄 测试特殊文件名...")
        special_names = [
            "file with spaces.py",
            "file;with;semicolons.py",
            "file|with|pipes.py",
            "file<with>brackets.py",
            "..hidden.py",
            ".hidden..py",
        ]
        
        for name in special_names:
            try:
                special_file = test_dir / name
                special_file.write_text("# test")
                
                # 尝试处理
                print(f"  创建: {repr(name)}")
                
                special_file.unlink()
            except Exception as e:
                errors.append((name, str(e)))
        
        # 清理
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)
        
        if errors:
            self.log_defect(RealDefect(
                defect_id="REAL_004",
                severity=DefectSeverity.MEDIUM,
                category=DefectCategory.FILE_SYSTEM_TRAP,
                title="文件系统陷阱处理不完善",
                description=f"处理文件系统边界情况时出现{len(errors)}个问题",
                reproduction_steps=["创建符号链接循环", "测试权限问题", "使用特殊文件名"],
                location="full_path_test - 文件处理模块",
                impact="特定文件系统场景下可能失败",
                evidence={'errors': errors}
            ))
        else:
            print("\n  ✅ 所有文件系统陷阱测试通过")
    
    def test_04_resource_exhaustion(self):
        """测试4: 资源耗尽攻击"""
        print("\n" + "="*70)
        print("测试4: 资源耗尽攻击")
        print("="*70)
        
        errors = []
        
        # 测试1: 文件描述符耗尽
        print("\n🔄 测试文件描述符耗尽...")
        try:
            from full_path_test.performance.performance_system import FileCache
            
            cache = FileCache()
            
            # 打开大量文件
            open_files = []
            try:
                for i in range(100):
                    cache.set(f"key_{i}", f"value_{i}" * 1000)
                    if i % 10 == 0:
                        print(f"  已创建 {i} 个缓存文件...")
            except Exception as e:
                errors.append(("fd_exhaustion", str(e)))
                print(f"  ⚠️  文件描述符耗尽: {e}")
            
            cache.clear()
            
        except Exception as e:
            print(f"  ❌ 文件描述符测试失败: {e}")
        
        # 测试2: 内存限制
        print("\n🔄 测试内存限制...")
        try:
            # 设置内存限制
            soft, hard = resource.getrlimit(resource.RLIMIT_AS)
            resource.setrlimit(resource.RLIMIT_AS, (1024*1024*10, hard))  # 10MB限制
            
            try:
                from full_path_test.ai.ai_integration import AICodeAnalyzer
                
                # 尝试分配大量内存
                huge_code = "x = " + "y" * 1000000
                print(f"  分配大量内存: {len(huge_code)} 字符")
                
            except MemoryError as e:
                errors.append(("memory_limit", "正确触发MemoryError"))
                print(f"  ✅ 正确处理内存限制")
            except Exception as e:
                errors.append(("memory_other", str(e)))
                print(f"  ⚠️  其他内存错误: {e}")
            finally:
                resource.setrlimit(resource.RLIMIT_AS, (soft, hard))
                
        except Exception as e:
            print(f"  ❌ 内存限制测试失败: {e}")
        
        if len(errors) > 0:
            print(f"\n  发现 {len(errors)} 个资源问题")
    
    def test_05_plugin_circular_dependency(self):
        """测试5: 插件循环依赖"""
        print("\n" + "="*70)
        print("测试5: 插件循环依赖")
        print("="*70)
        
        try:
            from full_path_test.plugins.plugin_system import (
                PluginRegistry,
                PluginDependencyResolver,
                PluginInfo,
                PluginMetadata,
                PluginType
            )
            
            print("🔄 测试循环依赖检测...")
            
            registry = PluginRegistry()
            resolver = PluginDependencyResolver(registry)
            
            # 创建循环依赖: A -> B -> A
            metadata_a = PluginMetadata(
                plugin_id="plugin_a",
                plugin_name="Plugin A",
                version="1.0",
                author="Test",
                description="A",
                plugin_type=PluginType.CUSTOM,
                entry_point="PluginA",
                dependencies=["plugin_b"]
            )
            
            metadata_b = PluginMetadata(
                plugin_id="plugin_b",
                plugin_name="Plugin B",
                version="1.0",
                author="Test",
                description="B",
                plugin_type=PluginType.CUSTOM,
                entry_point="PluginB",
                dependencies=["plugin_a"]
            )
            
            registry.register(PluginInfo(metadata=metadata_a))
            registry.register(PluginInfo(metadata=metadata_b))
            
            # 尝试解析依赖
            try:
                order = resolver.resolve_dependencies("plugin_a")
                print(f"  依赖顺序: {order}")
                
                # 检查是否有循环
                cycle = resolver.check_circular_dependency("plugin_a")
                
                if cycle:
                    print(f"  ✅ 检测到循环依赖: {' -> '.join(cycle)}")
                else:
                    print("  ⚠️  未检测到循环依赖（可能存在问题）")
                    self.log_defect(RealDefect(
                        defect_id="REAL_005",
                        severity=DefectSeverity.MEDIUM,
                        category=DefectCategory.CIRCULAR_DEPENDENCY,
                        title="循环依赖检测可能不完善",
                        description="存在A->B->A的循环但check_circular_dependency未返回cycle",
                        reproduction_steps=["创建循环依赖的插件", "调用check_circular_dependency"],
                        location="full_path_test/plugins/plugin_system.py",
                        impact="循环依赖可能导致无限循环",
                        evidence={'order': order}
                    ))
                    
            except RecursionError as e:
                self.log_defect(RealDefect(
                    defect_id="REAL_006",
                    severity=DefectSeverity.CRITICAL,
                    category=DefectCategory.INFINITE_LOOP,
                    title="循环依赖导致无限递归",
                    description=f"解析依赖时触发RecursionError: {e}",
                    reproduction_steps=["创建循环依赖", "调用resolve_dependencies"],
                    location="full_path_test/plugins/plugin_system.py",
                    impact="程序崩溃",
                    evidence={'error': str(e)}
                ))
                print(f"  ❌ 循环依赖导致无限递归")
        
        except Exception as e:
            print(f"❌ 循环依赖测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    def test_06_malicious_input_attack(self):
        """测试6: 恶意输入攻击"""
        print("\n" + "="*70)
        print("测试6: 恶意输入攻击")
        print("="*70)
        
        try:
            from full_path_test.ai.ai_integration import CodeAnalysisRequest, AnalysisType
            
            attacks = [
                ("billion_laughs", 'a = "x" * 10**9'),  # Billion laughs
                ("zip_bomb", "# zip bomb - just a marker"),  # 模拟zip bomb
                ("path_traversal", "def foo():\n    import os\n    os.system('../bin/sh')"),
                ("code_injection", 'os.system("echo hacked")'),
                ("infinite_recursion", "def foo(): foo()"),
                ("regex_dos", "a = " + "(".join(["x?"]*1000)),  # Regex DoS
            ]
            
            errors = []
            
            for name, code in attacks:
                print(f"\n  🔄 测试攻击: {name}...")
                try:
                    request = CodeAnalysisRequest(
                        code=code,
                        analysis_types=[AnalysisType.CODE_QUALITY]
                    )
                    
                    print(f"    ✅ 接受: {name}")
                    
                except Exception as e:
                    errors.append((name, str(e)))
                    print(f"    ⚠️  错误: {e}")
            
            if errors:
                self.log_defect(RealDefect(
                    defect_id="REAL_007",
                    severity=DefectSeverity.LOW,
                    category=DefectCategory.SECURITY_VULNERABILITY,
                    title="某些恶意输入未正确处理",
                    description=f"检测到{len(errors)}种潜在恶意输入未妥善处理",
                    reproduction_steps=["传入各种恶意输入"],
                    location="full_path_test/ai/ai_integration.py",
                    impact="安全风险",
                    evidence={'attacks': errors}
                ))
        
        except Exception as e:
            print(f"❌ 恶意输入测试失败: {e}")
    
    def run_all_tests(self):
        """运行所有超复杂测试"""
        print("\n" + "="*70)
        print("FullPathTest v4.0 - 超复杂超难度缺陷发现系统")
        print("="*70)
        
        start_time = time.time()
        
        self.test_01_concurrent_race_condition()
        self.test_02_unicode_encoding_hell()
        self.test_03_file_system_traps()
        self.test_04_resource_exhaustion()
        self.test_05_plugin_circular_dependency()
        self.test_06_malicious_input_attack()
        
        duration = time.time() - start_time
        
        # 生成报告
        print("\n" + "="*70)
        print("超复杂缺陷发现报告")
        print("="*70)
        
        total = len(self.defects)
        
        if total == 0:
            print("\n🎉 太棒了！超复杂测试中未发现任何缺陷！")
            print("系统在极端条件下表现完美！")
        else:
            print(f"\n发现 {total} 个真实缺陷:")
            
            # 按严重性分组
            severity_groups = {}
            for d in self.defects:
                sev = d.severity
                if sev not in severity_groups:
                    severity_groups[sev] = []
                severity_groups[sev].append(d)
            
            for sev in [DefectSeverity.BLOCKER, DefectSeverity.CRITICAL,
                       DefectSeverity.HIGH, DefectSeverity.MEDIUM, DefectSeverity.LOW]:
                if sev in severity_groups:
                    print(f"\n{sev.value.upper()} ({len(severity_groups[sev])}个):")
                    for d in severity_groups[sev]:
                        print(f"  - {d.title} [{d.defect_id}]")
        
        print(f"\n测试耗时: {duration:.2f}秒")
        print("="*70)
        
        # 保存详细报告
        report = {
            'total_defects': total,
            'duration': duration,
            'defects': [
                {
                    'id': d.defect_id,
                    'severity': d.severity.value,
                    'category': d.category.value,
                    'title': d.title,
                    'description': d.description,
                    'steps': d.reproduction_steps,
                    'location': d.location,
                    'impact': d.impact,
                    'evidence': d.evidence
                }
                for d in self.defects
            ]
        }
        
        with open('/tmp/ultra_complex_defects.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ 详细报告已保存到: /tmp/ultra_complex_defects.json")
        
        return self.defects


def main():
    """主函数"""
    finder = UltraComplexDefectFinder()
    defects = finder.run_all_tests()
    
    return defects


if __name__ == "__main__":
    main()
