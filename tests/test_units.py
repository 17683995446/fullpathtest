"""
FullPathTest V4.0 单元测试

测试核心功能模块。
"""

import unittest
from pathlib import Path


class TestCoreTypes(unittest.TestCase):
    """测试核心类型"""
    
    def test_task_request_creation(self):
        """测试任务请求创建"""
        from fullpathtest.types.core import TaskRequest, SourceType
        
        request = TaskRequest(
            task_id="test-001",
            source_type=SourceType.LOCAL_DIRECTORY,
            source_path="/tmp/test"
        )
        
        self.assertEqual(request.task_id, "test-001")
        self.assertEqual(request.source_type, SourceType.LOCAL_DIRECTORY)
        self.assertEqual(request.source_path, "/tmp/test")
    
    def test_config_snapshot_creation(self):
        """测试配置快照创建"""
        from fullpathtest.types.core import ConfigSnapshot
        
        config = ConfigSnapshot()
        self.assertIsNotNone(config.llm_config)
        self.assertIsNotNone(config.coverage_rules)
        self.assertIsNotNone(config.cache_config)
    
    def test_source_type_enum(self):
        """测试源码类型枚举"""
        from fullpathtest.types.core import SourceType
        
        self.assertIsNotNone(SourceType.LOCAL_DIRECTORY)
        self.assertIsNotNone(SourceType.GIT_REPOSITORY)
        self.assertIsNotNone(SourceType.ARCHIVE_FILE)
        self.assertEqual(len(SourceType), 5)
    
    def test_llm_mode_enum(self):
        """测试LLM模式枚举"""
        from fullpathtest.types.core import LLMMode
        
        self.assertIsNotNone(LLMMode.LOCAL_ONLY)
        self.assertIsNotNone(LLMMode.CLOUD_ONLY)
        self.assertIsNotNone(LLMMode.HYBRID)
        self.assertIsNotNone(LLMMode.OFFLINE)


class TestExtendedTypes(unittest.TestCase):
    """测试扩展类型"""
    
    def test_dataflow_node_creation(self):
        """测试数据流节点创建"""
        from fullpathtest.types.extended import DataFlowNode, DataFlowNodeType
        
        node = DataFlowNode(
            node_id="node_001",
            node_type=DataFlowNodeType.VARIABLE_READ,
            name="x",
            line_number=10,
            scope="global"
        )
        
        self.assertEqual(node.name, "x")
        self.assertEqual(node.line_number, 10)
        self.assertFalse(node.is_parameter)
    
    def test_dependency_node_creation(self):
        """测试依赖节点创建"""
        from fullpathtest.types.extended import DependencyNode, DependencyScope
        
        node = DependencyNode(
            node_id="dep_001",
            name="module_a",
            node_type=DependencyScope.MODULE_LEVEL,
            file_path="/path/to/file.py"
        )
        
        self.assertEqual(node.name, "module_a")
        self.assertEqual(node.node_type, DependencyScope.MODULE_LEVEL)
    
    def test_complexity_metric(self):
        """测试复杂度指标"""
        from fullpathtest.types.extended import ComplexityMetric, ComplexityLevel
        
        metric = ComplexityMetric(
            element_name="calculate",
            element_type="function",
            file_path="/path/to/file.py",
            line_number=1,
            cyclomatic_complexity=15,
            cognitive_complexity=8
        )
        
        self.assertEqual(metric.cyclomatic_complexity, 15)
        self.assertEqual(metric.level, ComplexityLevel.VERY_LOW)
        self.assertFalse(metric.is_hotspot)
    
    def test_smell_instance(self):
        """测试代码异味实例"""
        from fullpathtest.types.extended import SmellInstance, SmellType, SmellSeverity
        
        smell = SmellInstance(
            smell_id="smell_001",
            smell_type=SmellType.LONG_METHOD,
            severity=SmellSeverity.MEDIUM
        )
        
        self.assertEqual(smell.smell_type, SmellType.LONG_METHOD)
        self.assertEqual(smell.severity, SmellSeverity.MEDIUM)
        self.assertEqual(len(smell.locations), 0)
    
    def test_coverage_target(self):
        """测试覆盖目标"""
        from fullpathtest.types.extended import CoverageTarget, TargetType, TargetPriority
        
        target = CoverageTarget(
            target_id="target_001",
            target_type=TargetType.FUNCTION,
            name="critical_function",
            file_path="/path/to/file.py",
            line_number=1,
            priority=TargetPriority.CRITICAL,
            risk_score=0.9
        )
        
        self.assertEqual(target.name, "critical_function")
        self.assertEqual(target.priority, TargetPriority.CRITICAL)
        self.assertEqual(target.risk_score, 0.9)


class TestCoreModules(unittest.TestCase):
    """测试核心模块"""
    
    def test_entry_point_import(self):
        """测试入口点导入"""
        try:
            from fullpathtest.core.layer_01_entry.entry_point import EntryPoint
            self.assertIsNotNone(EntryPoint)
        except ImportError as e:
            self.fail(f"Failed to import EntryPoint: {e}")
    
    def test_task_manager_import(self):
        """测试任务管理器导入"""
        try:
            from fullpathtest.core.layer_02_lifecycle.task_manager import TaskManager
            self.assertIsNotNone(TaskManager)
        except ImportError as e:
            self.fail(f"Failed to import TaskManager: {e}")
    
    def test_source_scanner_import(self):
        """测试源码扫描器导入"""
        try:
            from fullpathtest.core.layer_09_source_scanner.scanner import SourceScanner
            self.assertIsNotNone(SourceScanner)
        except ImportError as e:
            self.fail(f"Failed to import SourceScanner: {e}")
    
    def test_cfg_builder_import(self):
        """测试CFG构建器导入"""
        try:
            from fullpathtest.core.layer_22_cfg.cfg_builder import CFGBuilder
            self.assertIsNotNone(CFGBuilder)
        except ImportError as e:
            self.fail(f"Failed to import CFGBuilder: {e}")
    
    def test_path_enumerator_import(self):
        """测试路径枚举器导入"""
        try:
            from fullpathtest.core.layer_26_path_enumerator.path_enumerator import PathEnumerator
            self.assertIsNotNone(PathEnumerator)
        except ImportError as e:
            self.fail(f"Failed to import PathEnumerator: {e}")
    
    def test_report_generator_import(self):
        """测试报告生成器导入"""
        try:
            from fullpathtest.core.layer_41_report.report_generator import ReportGenerator
            self.assertIsNotNone(ReportGenerator)
        except ImportError as e:
            self.fail(f"Failed to import ReportGenerator: {e}")


class TestIntegration(unittest.TestCase):
    """测试集成"""
    
    def test_system_creation(self):
        """测试系统创建"""
        try:
            from fullpathtest import FullPathTestSystem
            
            system = FullPathTestSystem()
            self.assertIsNotNone(system)
        except Exception as e:
            self.fail(f"Failed to create system: {e}")
    
    def test_system_config(self):
        """测试系统配置"""
        try:
            from fullpathtest import SystemConfig
            
            config = SystemConfig(
                enable_logging=False,
                max_workers=2
            )
            self.assertFalse(config.enable_logging)
            self.assertEqual(config.max_workers, 2)
        except Exception as e:
            self.fail(f"Failed to create system config: {e}")
    
    def test_create_system_function(self):
        """测试创建系统函数"""
        try:
            from fullpathtest import create_system
            
            system = create_system()
            self.assertIsNotNone(system)
        except Exception as e:
            self.fail(f"Failed to create system with factory: {e}")


class TestDataStructures(unittest.TestCase):
    """测试数据结构"""
    
    def test_path_creation(self):
        """测试路径创建"""
        from fullpathtest.types.core import Path, PathType
        
        path = Path(
            path_id="path_001",
            path_type=PathType.INTRAPROCEDURAL
        )
        
        self.assertEqual(path.path_id, "path_001")
        self.assertEqual(path.path_type, PathType.INTRAPROCEDURAL)
        self.assertEqual(len(path.node_sequence), 0)
    
    def test_cfg_creation(self):
        """测试CFG创建"""
        from fullpathtest.types.core import ControlFlowGraph, CFGNode
        
        node1 = CFGNode(
            node_id="n1",
            node_type="entry"
        )
        
        cfg = ControlFlowGraph(
            function_name="test_func",
            file_path="/path/to/file.py",
            entry_node="n1"
        )
        cfg.nodes["n1"] = node1
        
        self.assertEqual(len(cfg.nodes), 1)
        self.assertEqual(cfg.entry_node, "n1")
    
    def test_function_slice_creation(self):
        """测试函数切片创建"""
        from fullpathtest.types.core import FunctionSlice
        
        func = FunctionSlice(
            name="test_function",
            file_path="/path/to/file.py",
            start_line=10,
            end_line=50,
            complexity=5
        )
        
        self.assertEqual(func.name, "test_function")
        self.assertEqual(func.start_line, 10)
        self.assertEqual(func.complexity, 5)


if __name__ == '__main__':
    unittest.main()
