"""
FullPathTest 单元测试

测试核心功能模块。
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fullpathtest.types.core import (
    TaskRequest, TaskContext, ConfigSnapshot, SourceType, LLMMode,
    CoverageRules, TaskState, LanguageType, Path, PathSet, PathType
)
from fullpathtest.core.layer_01_entry.entry_point import EntryPoint
from fullpathtest.core.layer_02_lifecycle.task_manager import TaskManager
from fullpathtest.core.layer_03_config.config_loader import ConfigLoader
from fullpathtest.core.layer_04_nlp.parser import NLPCommandParser
from fullpathtest.core.layer_06_cache.cache_manager import MemoryCache, DiskCache, LLMCacheManager
from fullpathtest.core.layer_09_source_scanner.scanner import SourceScanner
from fullpathtest.core.layer_11_preprocess.preprocessor import CodePreprocessor
from fullpathtest.core.layer_17_lexer.lexer import Lexer
from fullpathtest.core.layer_22_cfg.cfg_builder import CFGBuilder
from fullpathtest.core.layer_26_path_enumerator.path_enumerator import PathEnumerator
from fullpathtest.core.layer_32_execution.test_case_generator import TestCaseGenerator
from fullpathtest.core.layer_39_coverage.coverage_calculator import CoverageCalculator
from fullpathtest.core.layer_41_report.report_generator import ReportGenerator


class TestTaskManager:
    """任务管理器测试"""
    
    def test_create_task(self):
        """测试创建任务"""
        request = TaskRequest(
            task_id="TEST-001",
            source_type=SourceType.LOCAL_DIRECTORY,
            source_path="/tmp/test"
        )
        
        config = ConfigSnapshot()
        manager = TaskManager()
        context = manager.create_task(request, config)
        
        assert context.task_id == "TEST-001"
        assert context.state == TaskState.INITIALIZING
        assert context.progress == 0.0
    
    def test_update_state(self):
        """测试更新状态"""
        request = TaskRequest(
            task_id="TEST-002",
            source_type=SourceType.LOCAL_DIRECTORY,
            source_path="/tmp/test"
        )
        
        config = ConfigSnapshot()
        manager = TaskManager()
        context = manager.create_task(request, config)
        
        success = manager.update_state("TEST-002", TaskState.PARSING, 50.0)
        assert success is True
        
        context = manager.get_task_context("TEST-002")
        assert context.state == TaskState.PARSING
        assert context.progress == 50.0
    
    def test_list_tasks(self):
        """测试列出任务"""
        manager = TaskManager()
        tasks = manager.list_tasks()
        assert isinstance(tasks, list)


class TestConfigLoader:
    """配置加载器测试"""
    
    def test_load_default_config(self):
        """测试加载默认配置"""
        loader = ConfigLoader()
        
        request = TaskRequest(
            task_id="TEST-003",
            source_type=SourceType.LOCAL_DIRECTORY,
            source_path="/tmp/test"
        )
        
        config = loader.load_config(request)
        
        assert config is not None
        assert isinstance(config, ConfigSnapshot)
        assert config.llm_config is not None


class TestNLPCommandParser:
    """NLP命令解析器测试"""
    
    def test_identify_intent_full_coverage(self):
        """测试识别全面测试意图"""
        parser = NLPCommandParser()
        
        intent = parser._identify_intent("请对所有模块进行完整覆盖测试")
        assert intent == 'full_coverage'
    
    def test_identify_intent_critical_path(self):
        """测试识别关键路径意图"""
        parser = NLPCommandParser()
        
        intent = parser._identify_intent("测试关键路径和核心功能")
        assert intent == 'critical_path'
    
    def test_extract_targets(self):
        """测试提取目标模块"""
        parser = NLPCommandParser()
        
        targets = parser._extract_targets("测试模块: auth, 测试: user, 文件: test.py")
        assert 'auth' in targets
        assert 'user' in targets


class TestMemoryCache:
    """内存缓存测试"""
    
    def test_set_and_get(self):
        """测试设置和获取"""
        cache = MemoryCache(max_size=10)
        
        cache.set("key1", {"data": "value1"})
        result = cache.get("key1")
        
        assert result is not None
        assert result["data"] == "value1"
    
    def test_cache_miss(self):
        """测试缓存未命中"""
        cache = MemoryCache(max_size=10)
        
        result = cache.get("nonexistent")
        assert result is None
    
    def test_eviction(self):
        """测试缓存淘汰"""
        cache = MemoryCache(max_size=3)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        cache.set("key4", "value4")
        
        assert cache.get("key1") is None
        assert cache.get("key4") is not None
    
    def test_get_stats(self):
        """测试获取统计"""
        cache = MemoryCache(max_size=10)
        
        cache.set("key1", "value1")
        cache.get("key1")
        cache.get("nonexistent")
        
        stats = cache.get_stats()
        
        assert 'hits' in stats
        assert 'misses' in stats
        assert stats['hits'] == 1
        assert stats['misses'] == 1


class TestSourceScanner:
    """源码扫描器测试"""
    
    def test_detect_language(self):
        """测试语言检测"""
        scanner = SourceScanner()
        
        assert scanner._detect_language(Path("test.py")) == LanguageType.PYTHON
        assert scanner._detect_language(Path("Main.java")) == LanguageType.JAVA
        assert scanner._detect_language(Path("main.go")) == LanguageType.GOLANG
        assert scanner._detect_language(Path("lib.rs")) == LanguageType.RUST
    
    def test_is_test_file(self):
        """测试测试文件识别"""
        scanner = SourceScanner()
        
        assert scanner._is_test_file(Path("test_auth.py")) is True
        assert scanner._is_test_file(Path("auth_test.py")) is True
        assert scanner._is_test_file(Path("tests/user.py")) is True
        assert scanner._is_test_file(Path("auth.py")) is False


class TestCodePreprocessor:
    """代码预处理器测试"""
    
    def test_remove_comments_python(self):
        """测试Python注释移除"""
        preprocessor = CodePreprocessor()
        
        code = '''
def hello():
    # This is a comment
    x = 1  # inline comment
    return x
'''
        
        result = preprocessor.preprocess(code, "test.py")
        
        assert "# This is a comment" not in result.normalized_content
        assert "# inline comment" not in result.normalized_content
    
    def test_normalize_whitespace(self):
        """测试空白字符标准化"""
        preprocessor = CodePreprocessor()
        
        code = "def   hello():    pass"
        
        result = preprocessor.preprocess(code, "test.py")
        
        assert "  " not in result.normalized_content


class TestLexer:
    """词法分析器测试"""
    
    def test_tokenize_simple(self):
        """测试简单词法分析"""
        lexer = Lexer(LanguageType.PYTHON)
        
        code = "def hello(): pass"
        tokens = lexer.tokenize_simple(code)
        
        assert len(tokens) > 0
        token_types = [t['type'] for t in tokens]
        assert 'KEYWORD' in token_types
        assert 'IDENTIFIER' in token_types
    
    def test_tokenize_numbers(self):
        """测试数字识别"""
        lexer = Lexer(LanguageType.PYTHON)
        
        code = "x = 42 y = 3.14"
        tokens = lexer.tokenize_simple(code)
        
        number_tokens = [t for t in tokens if t['type'] == 'NUMBER']
        assert len(number_tokens) >= 2


class TestCFGBuilder:
    """控制流图构建器测试"""
    
    def test_build_cfg(self):
        """测试CFG构建"""
        from fullpathtest.types.core import FunctionSlice
        
        function = FunctionSlice(
            name="test_func",
            file_path="test.py",
            start_line=1,
            end_line=10,
            parameters=[],
            return_type="int"
        )
        
        builder = CFGBuilder()
        cfg = builder.build(function)
        
        assert cfg is not None
        assert cfg.function_name == "test_func"
        assert cfg.entry_node is not None
        assert len(cfg.nodes) > 0
    
    def test_get_paths(self):
        """测试获取路径"""
        from fullpathtest.types.core import FunctionSlice
        
        function = FunctionSlice(
            name="simple_func",
            file_path="test.py",
            start_line=1,
            end_line=5,
            parameters=[]
        )
        
        builder = CFGBuilder()
        cfg = builder.build(function)
        paths = builder.get_paths(cfg)
        
        assert isinstance(paths, list)


class TestPathEnumerator:
    """路径枚举器测试"""
    
    def test_enumerate_paths(self):
        """测试路径枚举"""
        from fullpathtest.types.core import ControlFlowGraph, CFGNode
        
        cfg = ControlFlowGraph(
            function_name="test",
            file_path="test.py",
            nodes={
                "entry": CFGNode(node_id="entry", node_type="entry", successors=["node1"]),
                "node1": CFGNode(node_id="node1", node_type="statement", successors=["exit"]),
                "exit": CFGNode(node_id="exit", node_type="exit", predecessors=["node1"])
            },
            entry_node="entry",
            exit_nodes=["exit"]
        )
        
        enumerator = PathEnumerator(max_depth=10, max_paths=100)
        path_set = enumerator.enumerate_paths(cfg)
        
        assert path_set is not None
        assert isinstance(path_set, PathSet)


class TestTestCaseGenerator:
    """测试用例生成器测试"""
    
    def test_generate_from_path(self):
        """测试从路径生成测试用例"""
        from fullpathtest.types.core import Path, PathType
        
        path = Path(
            path_id="PATH-001",
            path_type=PathType.INTRAPROCEDURAL,
            node_sequence=["entry", "node1", "exit"]
        )
        
        generator = TestCaseGenerator()
        test_case = generator.generate_from_path(path)
        
        assert test_case is not None
        assert test_case.path_id == "PATH-001"
        assert len(test_case.inputs) > 0


class TestCoverageCalculator:
    """覆盖率计算器测试"""
    
    def test_calculate_percentage(self):
        """测试百分比计算"""
        calculator = CoverageCalculator()
        
        percentage = calculator._calculate_percentage(80, 100)
        assert percentage == 80.0
        
        percentage = calculator._calculate_percentage(0, 0)
        assert percentage == 0.0


class TestReportGenerator:
    """报告生成器测试"""
    
    def test_generate_text_report(self):
        """测试生成文本报告"""
        generator = ReportGenerator()
        
        data = {
            'task_id': 'TEST-001',
            'status': 'COMPLETED',
            'progress': 100.0
        }
        
        report = generator._generate_text_report(data, True, True)
        
        assert report is not None
        assert 'TEST-001' in report.content
        assert report.format_type == 'text'
    
    def test_generate_json_report(self):
        """测试生成JSON报告"""
        generator = ReportGenerator()
        
        data = {
            'task_id': 'TEST-002',
            'status': 'COMPLETED',
            'progress': 100.0
        }
        
        report = generator._generate_json_report(data, True, True)
        
        assert report is not None
        assert report.format_type == 'json'
        assert 'TEST-002' in report.content


class TestIntegration:
    """集成测试"""
    
    def test_full_pipeline(self):
        """测试完整流程"""
        request = TaskRequest(
            task_id="INTEGRATION-001",
            source_type=SourceType.LOCAL_DIRECTORY,
            source_path="/tmp/test"
        )
        
        entry = EntryPoint()
        
        try:
            context = entry.process_request(request)
            assert context.task_id == "INTEGRATION-001"
        except ValueError:
            pass
    
    def test_nlp_to_instruction(self):
        """测试NLP解析"""
        parser = NLPCommandParser()
        
        instruction = parser.parse(TaskContext(
            task_id="TEST",
            request=TaskRequest(
                task_id="TEST",
                source_type=SourceType.LOCAL_DIRECTORY,
                source_path="/tmp"
            ),
            config=ConfigSnapshot(),
            metadata={'user_command': '全面测试核心模块'}
        ))
        
        assert instruction is not None
        assert instruction.task_id == "TEST"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
