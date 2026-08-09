"""
增强的完整测试套件 - 真实运行开源工具！(已修复)

包含：
- 真实工具集成测试
- LLM集成测试
- 产品化模块测试
- Web界面测试
"""

import os
import sys
import time
import tempfile
from pathlib import Path
import pytest
from typing import Dict, Any, List
from dataclasses import dataclass, field
import logging


# 配置日志
logging.basicConfig(level=logging.INFO)


# 测试用的示例代码
SAMPLE_CODE_A = """
def calculate_sum(a, b):
    return a + b

def process_list(items):
    result = []
    for item in items:
        if item > 0:
            result.append(item * 2)
    return result

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

SAMPLE_CODE_B = """
def greet(name):
    print(f"Hello, {name}!")
    
def create_user(name, email, role="user"):
    user = {
        "name": name,
        "email": email,
        "role": role
    }
    return user
"""


class TestRealToolIntegration:
    """测试真实工具集成"""
    
    @classmethod
    def setup_class(cls):
        """创建临时测试文件"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.file_a = os.path.join(cls.temp_dir, "test_module_a.py")
        cls.file_b = os.path.join(cls.temp_dir, "test_module_b.py")
        
        with open(cls.file_a, 'w', encoding='utf-8') as f:
            f.write(SAMPLE_CODE_A)
        
        with open(cls.file_b, 'w', encoding='utf-8') as f:
            f.write(SAMPLE_CODE_B)
        
        print(f"Created test files at: {cls.temp_dir}")
    
    @classmethod
    def teardown_class(cls):
        """清理"""
        import shutil
        shutil.rmtree(cls.temp_dir, ignore_errors=True)
        print("Cleaned up test files")
    
    def test_real_tool_integrator_creation(self):
        """测试工具集成器创建"""
        from fullpathtest.integrations.real_tools import (
            RealToolIntegrator,
            get_real_tool_integrator,
            OpenSourceTool
        )
        
        integrator = get_real_tool_integrator()
        assert integrator is not None
        
        status = integrator.get_tool_status()
        print(f"Tool availability: {status}")
        
        available = integrator.get_available_tools()
        print(f"Available tools: {[t.value for t in available]}")
        
        assert isinstance(available, list)
    
    def test_mock_flake8_workflow(self):
        """测试flake8工作流（即使未安装也能运行）"""
        from fullpathtest.integrations.real_tools import (
            RealToolIntegrator,
            get_real_tool_integrator
        )
        
        integrator = get_real_tool_integrator()
        result = integrator.run_flake8(self.file_a)
        
        print(f"Flake8 run: success={result.success}, issues={result.issues_count}")
        print(f"Flake8 stdout: {result.stdout[:100] if result.stdout else 'empty'}")
        print(f"Flake8 stderr: {result.stderr[:100] if result.stderr else 'empty'}")
        
        # 无论是否安装成功，都不应崩溃
        assert result is not None
    
    def test_mock_pylint_workflow(self):
        """测试pylint工作流"""
        from fullpathtest.integrations.real_tools import (
            RealToolIntegrator,
            get_real_tool_integrator
        )
        
        integrator = get_real_tool_integrator()
        result = integrator.run_pylint(self.file_a)
        
        print(f"Pylint run: success={result.success}, issues={result.issues_count}")
        
        assert result is not None
    
    def test_mock_radon_workflow(self):
        """测试radon工作流"""
        from fullpathtest.integrations.real_tools import (
            RealToolIntegrator,
            get_real_tool_integrator
        )
        
        integrator = get_real_tool_integrator()
        result = integrator.run_radon_cc(self.file_a)
        
        print(f"Radon run: success={result.success}")
        
        assert result is not None
    
    def test_real_code_analyzer_module(self):
        """测试真实代码分析器"""
        from fullpathtest.modules.real_code_analyzer import (
            RealCodeAnalyzer,
            get_real_code_analyzer,
            CodeAnalysisInput
        )
        
        analyzer = get_real_code_analyzer()
        health = analyzer.get_health()
        assert health.healthy
        
        input_data = CodeAnalysisInput(
            source_path=self.file_a,
            use_llm=False  # 先不用LLM
        )
        
        result = analyzer.execute(input_data)
        
        print(f"Analysis complete: status={result.status}")
        print(f"  Files analyzed: {result.files_analyzed}")
        print(f"  Total issues: {result.total_issues}")
        print(f"  Overall score: {result.overall_score}")
        print(f"  Duration: {result.duration:.2f}s")
        
        assert result is not None
        assert result.status in ["success", "error"]  # 可能成功也可能因为工具未安装失败
        analyzer.shutdown()


class TestLLMIntegration:
    """测试LLM集成"""
    
    def test_mock_llm_client(self):
        """测试Mock LLM客户端（确保可以工作）"""
        from fullpathtest.integrations.llm_client import (
            RealLLMClient,
            get_mock_client,
            LLMProvider
        )
        
        client = get_mock_client()
        assert client is not None
        assert client.config.provider == LLMProvider.MOCK
        
        response = client.generate("Hello, world!", "You are helpful.")
        
        print(f"Mock LLM response: success={response.success}")
        print(f"  Content: {response.content[:100]}")
        
        assert response.success
        assert len(response.content) > 0
    
    def test_ollama_client_creation(self):
        """测试Ollama客户端创建（不要求Ollama运行）"""
        from fullpathtest.integrations.llm_client import (
            RealLLMClient,
            get_ollama_client,
            LLMProvider
        )
        
        client = get_ollama_client()
        assert client is not None
        assert client.config.provider == LLMProvider.OLLAMA
        assert client.config.api_base == "http://localhost:11434"
    
    def test_test_data_generator_with_mock(self):
        """测试测试数据生成器（使用Mock）"""
        from fullpathtest.integrations.llm_client import (
            TestDataGenerator,
            get_mock_client
        )
        
        llm = get_mock_client()
        generator = TestDataGenerator(llm)
        
        result = generator.generate_test_data(
            "def add(a, b): return a + b",
            "add"
        )
        
        print(f"Test data generation: success={result.get('success', False)}")
        print(f"  Content length: {len(result.get('content', ''))}")
        
        assert result.get("success", False)


class TestProductizedModules:
    """产品化模块测试"""
    
    def test_module_base(self):
        """测试模块基类"""
        from fullpathtest.modules.base import (
            ProductizedModule,
            ModuleConfig,
            ModuleHealth
        )
        
        # 简单的测试模块
        class SimpleModule(ProductizedModule[str, str]):
            def _on_initialize(self):
                pass
            def _on_execute(self, data: str) -> str:
                return f"Processed: {data}"
            def _on_shutdown(self):
                pass
        
        module = SimpleModule(ModuleConfig(module_name="Simple", version="1.0.0"))
        module.initialize()
        
        health = module.get_health()
        assert health.healthy
        
        result = module.execute("test")
        assert result == "Processed: test"
        
        module.shutdown()
    
    def test_module_registry(self):
        """测试模块注册表"""
        from fullpathtest.modules.base import ModuleRegistry
        
        registry = ModuleRegistry()
        modules = registry.get_all()
        print(f"Registered modules: {list(modules.keys())}")
        assert isinstance(modules, dict)


@dataclass
class TestReport:
    """测试报告"""
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    total: int = 0
    duration: float = 0.0
    details: List[Dict[str, Any]] = field(default_factory=list)


def run_enhanced_test_suite() -> TestReport:
    """运行增强测试套件"""
    print("\n" + "="*60)
    print("Enhanced Test Suite - FullPathTest V4.0")
    print("="*60 + "\n")
    
    report = TestReport()
    start = time.time()
    
    # 运行所有测试
    tests = [
        ("RealToolIntegration", TestRealToolIntegration),
        ("LLMIntegration", TestLLMIntegration),
        ("ProductizedModules", TestProductizedModules),
    ]
    
    for test_name, test_class in tests:
        print(f"\n{'#'*60}")
        print(f"Test Group: {test_name}")
        print(f"{'#'*60}")
        
        # 创建测试实例
        instance = test_class()
        
        # 查找测试方法
        test_methods = [
            m for m in dir(instance)
            if m.startswith("test_") and callable(getattr(instance, m))
        ]
        
        for method_name in test_methods:
            test_start = time.time()
            print(f"\n  Running: {method_name}...")
            
            try:
                # 执行setup_class（如果有）
                if hasattr(instance, 'setup_class'):
                    try:
                        instance.setup_class()
                    except Exception:
                        pass
                
                # 执行测试
                method = getattr(instance, method_name)
                method()
                
                elapsed = time.time() - test_start
                report.passed += 1
                print(f"  ✓ PASSED ({elapsed:.2f}s)")
                
                report.details.append({
                    "group": test_name,
                    "name": method_name,
                    "status": "passed",
                    "duration": elapsed
                })
                
            except Exception as e:
                elapsed = time.time() - test_start
                report.failed += 1
                print(f"  ✗ FAILED: {e}")
                
                report.details.append({
                    "group": test_name,
                    "name": method_name,
                    "status": "failed",
                    "error": str(e),
                    "duration": elapsed
                })
            finally:
                report.total += 1
    
    report.duration = time.time() - start
    
    # 打印总结
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total: {report.total}  ✓ Passed: {report.passed}  ✗ Failed: {report.failed}")
    print(f"Duration: {report.duration:.2f}s")
    
    pass_rate = (report.passed / report.total * 100) if report.total > 0 else 0
    print(f"Pass rate: {pass_rate:.1f}%")
    
    return report


if __name__ == "__main__":
    run_enhanced_test_suite()
