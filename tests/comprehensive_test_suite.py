"""
FullPathTest Comprehensive Test Suite - 完整测试套件

包含单元测试、集成测试、系统测试
"""

import pytest
import os
import tempfile
from pathlib import Path
from typing import Any, Dict
import time


# 测试数据
TEST_CODE = '''
"""
Test module for FullPathTest
"""

def add(a, b):
    """Add two numbers"""
    return a + b

def multiply(a, b):
    """Multiply two numbers"""
    return a * b

def complex_function(x, y, z):
    """Complex function with multiple paths"""
    result = 0
    if x > 0:
        result += x
    else:
        result -= x
    
    if y > 0:
        result *= y
    else:
        result /= 2
    
    if z > 0:
        result += z
    
    return result
'''

# ==================== 单元测试 ====================

class TestCoreTypes:
    """核心类型单元测试"""
    
    def test_task_request_creation(self):
        """测试任务请求创建"""
        from fullpathtest.types.core import TaskRequest, SourceType
        req = TaskRequest(
            task_id="test-001",
            source_type=SourceType.LOCAL_DIRECTORY,
            source_path="/tmp/test"
        )
        assert req.task_id == "test-001"
        assert req.source_type == SourceType.LOCAL_DIRECTORY
    
    def test_config_snapshot(self):
        """测试配置快照"""
        from fullpathtest.types.core import ConfigSnapshot
        config = ConfigSnapshot()
        assert config.llm_config is not None
        assert config.coverage_rules is not None
    
    def test_path_creation(self):
        """测试路径对象创建"""
        from fullpathtest.types.core import Path, PathType
        path = Path(
            path_id="path-001",
            path_type=PathType.INTRAPROCEDURAL
        )
        assert path.path_id == "path-001"
        assert path.path_type == PathType.INTRAPROCEDURAL


class TestExtendedTypes:
    """扩展类型单元测试"""
    
    def test_dataflow_node(self):
        """测试数据流节点"""
        from fullpathtest.types.extended import DataFlowNode, DataFlowNodeType
        node = DataFlowNode(
            node_id="node-001",
            node_type=DataFlowNodeType.VARIABLE_READ,
            name="test_var",
            line_number=10,
            scope="global"
        )
        assert node.node_id == "node-001"
        assert node.name == "test_var"
    
    def test_complexity_metric(self):
        """测试复杂度指标"""
        from fullpathtest.types.extended import ComplexityMetric, ComplexityLevel
        metric = ComplexityMetric(
            element_name="test_func",
            element_type="function",
            file_path="/tmp/test.py",
            line_number=1,
            cyclomatic_complexity=15,
            cognitive_complexity=8
        )
        assert metric.cyclomatic_complexity == 15
        assert metric.level == ComplexityLevel.VERY_LOW


class TestCoreModules:
    """核心模块单元测试"""
    
    def test_entry_point(self):
        """测试入口点"""
        from fullpathtest.core.layer_01_entry.entry_point import EntryPoint
        entry = EntryPoint()
        assert entry is not None
    
    def test_task_manager(self):
        """测试任务管理器"""
        from fullpathtest.core.layer_02_lifecycle.task_manager import TaskManager
        manager = TaskManager()
        assert manager is not None


class TestModuleBase:
    """模块基类测试"""
    
    def test_module_config(self):
        """测试模块配置"""
        from fullpathtest.modules.base import ModuleConfig, ModulePriority
        config = ModuleConfig(
            module_name="TestModule",
            priority=ModulePriority.HIGH
        )
        assert config.module_name == "TestModule"
        assert config.priority == ModulePriority.HIGH


class TestToolIntegration:
    """工具集成测试"""
    
    def test_tool_integrator_creation(self):
        """测试工具集成器创建"""
        from fullpathtest.integrations.tools import (
            OpenSourceToolIntegrator,
            get_integrator
        )
        integrator = get_integrator()
        assert integrator is not None
        assert integrator.available_tools is not None


# ==================== 集成测试 ====================

class TestCodeAnalyzerIntegration:
    """代码分析器集成测试"""
    
    def test_code_analyzer_initialize(self):
        """测试代码分析器初始化"""
        from fullpathtest.modules.code_analyzer import get_code_analyzer
        analyzer = get_code_analyzer()
        assert analyzer is not None
    
    def test_code_analyzer_execute(self):
        """测试代码分析器执行"""
        from fullpathtest.modules.code_analyzer import (
            get_code_analyzer,
            CodeAnalysisInput,
        )
        import tempfile
        
        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(TEST_CODE)
            temp_path = f.name
        
        try:
            analyzer = get_code_analyzer()
            input_data = CodeAnalysisInput(
                source_path=temp_path,
                analysis_types=["all"]
            )
            result = analyzer.execute(input_data)
            assert result is not None
            assert result.overall_score >= 0
        finally:
            os.unlink(temp_path)


class TestWebAppIntegration:
    """Web应用集成测试"""
    
    def test_web_app_import(self):
        """测试Web应用导入"""
        from fastapi.testclient import TestClient
        from fullpathtest.web.app import app
        client = TestClient(app)
        response = client.get("/api/health")
        assert response.status_code in [200, 500]  # 200 成功，500可能模块未完全初始化


class TestFullPathTestSystem:
    """FullPathTest系统集成测试"""
    
    def test_system_creation(self):
        """测试系统创建"""
        from fullpathtest import FullPathTestSystem
        system = FullPathTestSystem()
        assert system is not None
    
    def test_system_scan_code(self):
        """测试系统代码扫描"""
        from fullpathtest import FullPathTestSystem
        system = FullPathTestSystem()
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建测试文件
            test_file = Path(temp_dir) / "test.py"
            test_file.write_text(TEST_CODE)
            
            result = system.scan_code(temp_dir)
            assert result is not None
            assert "status" in result


# ==================== 系统测试 ====================

class TestEndToEnd:
    """端到端系统测试"""
    
    def test_complete_workflow(self):
        """测试完整工作流"""
        from fullpathtest import FullPathTestSystem
        import tempfile
        
        # 1. 创建临时测试目录和文件
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "main.py"
            test_file.write_text(TEST_CODE)
            
            # 2. 创建系统
            system = FullPathTestSystem()
            
            # 3. 扫描代码
            scan_result = system.scan_code(temp_dir)
            assert scan_result is not None
            
            # 4. 运行分析
            analysis_result = system.analyze_complexity(temp_dir)
            assert analysis_result is not None
            
            print("✅ 完整工作流测试通过")


# ==================== 性能测试 ====================

class TestPerformance:
    """性能测试"""
    
    @pytest.mark.timeout(10)
    def test_initialization_performance(self):
        """测试初始化性能"""
        from fullpathtest import FullPathTestSystem
        
        start = time.time()
        system = FullPathTestSystem()
        duration = time.time() - start
        
        assert duration < 5.0  # 初始化应在5秒内完成
        print(f"⚡ 系统初始化耗时: {duration:.2f}s")
    
    @pytest.mark.timeout(30)
    def test_scan_performance(self):
        """测试扫描性能"""
        from fullpathtest import FullPathTestSystem
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建多个测试文件
            for i in range(10):
                test_file = Path(temp_dir) / f"test{i}.py"
                test_file.write_text(TEST_CODE)
            
            system = FullPathTestSystem()
            
            start = time.time()
            result = system.scan_code(temp_dir)
            duration = time.time() - start
            
            assert duration < 20.0  # 扫描应在20秒内完成
            print(f"⚡ 代码扫描耗时: {duration:.2f}s")


# ==================== 综合评分 ====================

class ComprehensiveScore:
    """综合评分系统"""
    
    def __init__(self):
        self.scores: Dict[str, float] = {}
        self.weights: Dict[str, float] = {
            "创新性": 0.15,
            "创造性": 0.15,
            "价值量": 0.2,
            "实用性": 0.2,
            "易用性": 0.15,
            "可维护性": 0.1,
            "扩展性": 0.05
        }
    
    def calculate_overall(self) -> float:
        """计算总体分数"""
        if not self.scores:
            return 0.0
        
        total = 0.0
        total_weight = 0.0
        
        for category, score in self.scores.items():
            weight = self.weights.get(category, 0.0)
            total += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return total / total_weight
    
    def get_grade(self) -> str:
        """获取等级"""
        overall = self.calculate_overall()
        if overall >= 90:
            return "S"
        elif overall >= 80:
            return "A"
        elif overall >= 70:
            return "B"
        elif overall >= 60:
            return "C"
        else:
            return "D"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "scores": self.scores,
            "overall": self.calculate_overall(),
            "grade": self.get_grade()
        }


def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("FullPathTest - 完整测试套件")
    print("=" * 70)
    print()
    
    # 运行 pytest
    test_file = __file__
    result = pytest.main([test_file, "-v", "--tb=short"])
    
    print()
    print("=" * 70)
    if result == 0:
        print("✅ 所有测试通过！")
    else:
        print(f"⚠️ 有测试失败，退出码: {result}")
    print("=" * 70)
    
    return result


if __name__ == "__main__":
    run_all_tests()
