#!/usr/bin/env python3
"""
FullPathTest V4.0 使用示例

展示如何使用 FullPathTest 系统进行全路径测试。
"""

import sys
from pathlib import Path


def example_1_basic_usage():
    """示例1：基本使用"""
    print("=" * 70)
    print("示例1：基本使用")
    print("=" * 70)
    
    try:
        from fullpathtest import FullPathTestSystem, SourceType, LanguageType, LLMMode
        from fullpathtest.types.core import TaskRequest
        
        print("\n1. 创建系统实例...")
        system = FullPathTestSystem()
        print("   ✅ 系统创建成功")
        
        print("\n2. 创建任务请求...")
        request = TaskRequest(
            task_id="demo-001",
            source_type=SourceType.LOCAL_DIRECTORY,
            source_path="/path/to/your/code"
        )
        print(f"   ✅ 任务请求创建: {request.task_id}")
        
        print("\n3. 运行完整测试...")
        result = system.run_full_test(
            source_path="/path/to/your/code",
            language=LanguageType.PYTHON
        )
        print(f"   ✅ 测试完成: {result['status']}")
        print(f"   - 执行层数: {result['metrics']['executed_layers']}/50")
        
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print()


def example_2_scan_code():
    """示例2：代码扫描"""
    print("=" * 70)
    print("示例2：代码扫描")
    print("=" * 70)
    
    try:
        from fullpathtest import FullPathTestSystem
        
        print("\n1. 创建系统...")
        system = FullPathTestSystem()
        
        print("\n2. 扫描代码目录...")
        result = system.scan_code("./fullpathtest")
        print(f"   ✅ 扫描完成")
        print(f"   - 发现文件: {result['files_found']}")
        print(f"   - 总行数: {result['total_lines']}")
        
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print()


def example_3_complexity_analysis():
    """示例3：复杂度分析"""
    print("=" * 70)
    print("示例3：复杂度分析")
    print("=" * 70)
    
    try:
        from fullpathtest import FullPathTestSystem
        
        print("\n1. 创建系统...")
        system = FullPathTestSystem()
        
        print("\n2. 分析代码复杂度...")
        result = system.analyze_complexity("./fullpathtest")
        print(f"   ✅ 分析完成")
        print(f"   - 平均复杂度: {result['average_complexity']:.2f}")
        print(f"   - 最大复杂度: {result['max_complexity']}")
        print(f"   - 热点数量: {result['hotspots']}")
        
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print()


def example_4_code_smell_detection():
    """示例4：代码异味检测"""
    print("=" * 70)
    print("示例4：代码异味检测")
    print("=" * 70)
    
    try:
        from fullpathtest import FullPathTestSystem
        
        print("\n1. 创建系统...")
        system = FullPathTestSystem()
        
        print("\n2. 检测代码异味...")
        result = system.detect_code_smells("./fullpathtest")
        print(f"   ✅ 检测完成")
        print(f"   - 总异味数: {result['total_smells']}")
        
        if result['by_severity']:
            print("   - 按严重程度:")
            for severity, count in result['by_severity'].items():
                print(f"     · {severity}: {count}")
        
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print()


def example_5_type_system():
    """示例5：类型系统"""
    print("=" * 70)
    print("示例5：类型系统")
    print("=" * 70)
    
    try:
        from fullpathtest.types.core import (
            TaskRequest, TaskContext, ConfigSnapshot,
            SourceType, LLMMode, LanguageType, RiskLevel, PathType
        )
        
        print("\n1. 使用核心类型...")
        request = TaskRequest(
            task_id="demo-002",
            source_type=SourceType.LOCAL_DIRECTORY,
            source_path="/tmp/demo"
        )
        print(f"   ✅ 任务请求: {request.task_id}")
        
        print("\n2. 使用配置快照...")
        config = ConfigSnapshot()
        print(f"   ✅ 配置快照创建成功")
        
        print("\n3. 使用枚举类型...")
        print(f"   - 语言: {[lang.name for lang in list(LanguageType)[:5]]}...")
        print(f"   - 风险: {[risk.name for risk in list(RiskLevel)]}")
        print(f"   - 路径: {[path.name for path in list(PathType)]}")
        
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print()


def example_6_extended_types():
    """示例6：扩展类型"""
    print("=" * 70)
    print("示例6：扩展类型（第21-31层）")
    print("=" * 70)
    
    try:
        from fullpathtest.types.extended import (
            DataFlowGraph, DataFlowNode, DataFlowNodeType,
            DependencyGraph, DependencyNode, DependencyType,
            ComplexityReport, ComplexityMetric, ComplexityLevel,
            CodeSmellReport, SmellInstance, SmellType,
            TestabilityReport, TestabilityIssue, TestabilityLevel,
            CoverageTarget, CoverageTargetSet, TargetPriority
        )
        
        print("\n1. 数据流图类型...")
        node = DataFlowNode(
            node_id="node_001",
            node_type=DataFlowNodeType.VARIABLE_READ,
            name="x",
            line_number=10,
            scope="global"
        )
        print(f"   ✅ 节点: {node.name}")
        
        print("\n2. 依赖图类型...")
        dep_node = DependencyNode(
            node_id="dep_001",
            name="module_a",
            node_type="module_level",
            file_path="/path/to/file.py"
        )
        print(f"   ✅ 依赖节点: {dep_node.name}")
        
        print("\n3. 复杂度类型...")
        metric = ComplexityMetric(
            element_name="calculate",
            element_type="function",
            file_path="/path/to/file.py",
            line_number=1,
            cyclomatic_complexity=15,
            cognitive_complexity=8
        )
        print(f"   ✅ 复杂度: {metric.cyclomatic_complexity} ({metric.level.name})")
        
        print("\n4. 代码异味类型...")
        smell = SmellInstance(
            smell_id="smell_001",
            smell_type=SmellType.LONG_METHOD,
            severity="medium"
        )
        print(f"   ✅ 异味类型: {smell.smell_type.name}")
        
        print("\n5. 可测试性类型...")
        issue = TestabilityIssue(
            issue_id="issue_001",
            issue_type="hard_to_initialize",
            severity="high",
            element_name="setup",
            element_type="function",
            file_path="/path/to/file.py",
            line_number=1,
            description="初始化复杂",
            impact="难以测试"
        )
        print(f"   ✅ 问题类型: {issue.issue_type}")
        
        print("\n6. 覆盖目标类型...")
        target = CoverageTarget(
            target_id="target_001",
            target_type="function",
            name="critical_function",
            file_path="/path/to/file.py",
            line_number=1,
            priority=TargetPriority.CRITICAL,
            risk_score=0.9
        )
        print(f"   ✅ 目标优先级: {target.priority.name}")
        
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print()


def example_7_core_modules():
    """示例7：核心模块"""
    print("=" * 70)
    print("示例7：核心模块")
    print("=" * 70)
    
    try:
        from fullpathtest.core.layer_01_entry.entry_point import EntryPoint
        from fullpathtest.core.layer_02_lifecycle.task_manager import TaskManager
        from fullpathtest.core.layer_09_source_scanner.scanner import SourceScanner
        from fullpathtest.core.layer_22_cfg.cfg_builder import CFGBuilder
        from fullpathtest.core.layer_26_path_enumerator.path_enumerator import PathEnumerator
        from fullpathtest.core.layer_41_report.report_generator import ReportGenerator
        
        print("\n1. 入口点模块...")
        entry = EntryPoint()
        print(f"   ✅ EntryPoint 可用")
        
        print("\n2. 任务管理器...")
        manager = TaskManager()
        print(f"   ✅ TaskManager 可用")
        
        print("\n3. 源码扫描器...")
        scanner = SourceScanner()
        print(f"   ✅ SourceScanner 可用")
        
        print("\n4. CFG构建器...")
        cfg_builder = CFGBuilder()
        print(f"   ✅ CFGBuilder 可用")
        
        print("\n5. 路径枚举器...")
        enumerator = PathEnumerator()
        print(f"   ✅ PathEnumerator 可用")
        
        print("\n6. 报告生成器...")
        reporter = ReportGenerator()
        print(f"   ✅ ReportGenerator 可用")
        
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print()


def main():
    """运行所有示例"""
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "FullPathTest V4.0 使用示例" + " " * 23 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    examples = [
        ("基本使用", example_1_basic_usage),
        ("代码扫描", example_2_scan_code),
        ("复杂度分析", example_3_complexity_analysis),
        ("代码异味检测", example_4_code_smell_detection),
        ("类型系统", example_5_type_system),
        ("扩展类型", example_6_extended_types),
        ("核心模块", example_7_core_modules),
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        try:
            func()
        except Exception as e:
            print(f"\n❌ 示例{i}执行失败: {e}\n")
    
    print()
    print("=" * 70)
    print("所有示例执行完成！")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
