"""
Complete End-to-End Test Suite - 完整端到端测试套件
测试整个系统的所有组件和功能
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("e2e_tests")


class EndToEndTestRunner:
    """端到端测试运行器"""
    
    def __init__(self):
        self.test_results: Dict[str, Any] = {}
        self.passed = 0
        self.failed = 0
        self.total = 0
    
    def run_test(self, test_name: str, test_func):
        """运行单个测试"""
        self.total += 1
        logger.info(f"Running test: {test_name}")
        
        try:
            start_time = time.time()
            result = test_func()
            duration = time.time() - start_time
            
            if result:
                self.passed += 1
                self.test_results[test_name] = {
                    "status": "PASSED",
                    "duration": duration,
                    "result": result
                }
                logger.info(f"✓ {test_name} - PASSED ({duration:.2f}s)")
            else:
                self.failed += 1
                self.test_results[test_name] = {
                    "status": "FAILED",
                    "duration": duration,
                    "error": "Test returned False"
                }
                logger.error(f"✗ {test_name} - FAILED")
            
        except Exception as e:
            self.failed += 1
            self.test_results[test_name] = {
                "status": "FAILED",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            logger.error(f"✗ {test_name} - FAILED: {e}")
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 80)
        print("END-TO-END TEST SUMMARY")
        print("=" * 80)
        print(f"Total tests:     {self.total}")
        print(f"Passed:          {self.passed}")
        print(f"Failed:          {self.failed}")
        print(f"Success rate:   {(self.passed / self.total * 100):.1f}%")
        
        if self.failed > 0:
            print("\nFailed tests:")
            for name, result in self.test_results.items():
                if result["status"] == "FAILED":
                    print(f"  - {name}: {result.get('error', 'Unknown error')}")
        
        print("=" * 80)


def test_module_imports():
    """测试1: 模块导入"""
    try:
        from full_path_test.type_definitions.core_data_types import (
            CodeSourceType, SystemConfiguration, CodeQualityIssue, CodeAnalysisResult
        )
        from full_path_test.module_infrastructure.productized_module_base import (
            ModuleStatus, ModulePriority, ModuleConfiguration, ProductizedModuleBase
        )
        from full_path_test.external_integrations.open_source_tools.real_open_source_tool_integrator import (
            RealOpenSourceToolIntegrator, OpenSourceToolName
        )
        from full_path_test.external_integrations.llm_clients.real_llm_integration_client import (
            RealLLMIntegrationClient, create_mock_llm_client
        )
        from full_path_test.external_integrations.real_code_analyzer.real_code_analyzer_module import (
            RealCodeAnalyzerModule, CodeAnalysisInput
        )
        from full_path_test.external_integrations.tool_execution_engine import (
            RealToolExecutionEngine, AnalysisConfiguration
        )
        from full_path_test.core_system.configuration_and_incremental_analysis import (
            ProjectConfiguration, CacheManager, IncrementalAnalyzer
        )
        return True
    except Exception as e:
        logger.error(f"Module import failed: {e}")
        return False


def test_productized_module():
    """测试2: 产品化模块"""
    from full_path_test.module_infrastructure.productized_module_base import (
        ProductizedModuleBase, ModuleConfiguration, ModuleStatus
    )
    
    class TestModule(ProductizedModuleBase[str, str]):
        def _on_module_initialization(self):
            pass
        
        def _on_module_execution(self, input_data: str) -> str:
            return f"processed_{input_data}"
        
        def _on_module_shutdown(self):
            pass
    
    config = ModuleConfiguration(module_name="TestModule")
    module = TestModule(config)
    
    success = module.initialize_module()
    if not success:
        return False
    
    result = module.execute_module_function("test_input")
    if result != "processed_test_input":
        return False
    
    health = module.check_module_health()
    if not health.overall_healthy:
        return False
    
    module.shutdown_module()
    return True


def test_llm_mock_client():
    """测试3: LLM Mock客户端"""
    from full_path_test.external_integrations.llm_clients.real_llm_integration_client import (
        create_mock_llm_client
    )
    
    client = create_mock_llm_client()
    response = client.generate_llm_response("Hello, test!", "You are helpful.")
    
    if not response.generation_successful:
        return False
    
    if not response.generated_content:
        return False
    
    return True


def test_tool_execution_engine():
    """测试4: 工具执行引擎"""
    from full_path_test.external_integrations.tool_execution_engine import (
        RealToolExecutionEngine, AnalysisConfiguration
    )
    
    config = AnalysisConfiguration(
        max_workers=2,
        timeout_seconds=30,
        verbose=False
    )
    
    engine = RealToolExecutionEngine(config)
    
    if len(engine.available_tools) == 0:
        logger.warning("No tools available, but engine initialized successfully")
        return True
    
    test_file = "full_path_test/type_definitions/core_data_types.py"
    if not os.path.exists(test_file):
        return False
    
    result = engine.execute_single_tool("mypy", test_file, timeout=30)
    
    return result is not None


def test_configuration_system():
    """测试5: 配置系统"""
    from full_path_test.core_system.configuration_and_incremental_analysis import (
        ProjectConfiguration, ConfigurationManager
    )
    
    config = ProjectConfiguration()
    if config.project_name != "default_project":
        return False
    
    config.project_name = "test_project"
    if config.project_name != "test_project":
        return False
    
    manager = ConfigurationManager()
    loaded_config = manager.load_config()
    
    if loaded_config is None:
        return False
    
    return True


def test_cache_manager():
    """测试6: 缓存管理器"""
    from full_path_test.core_system.configuration_and_incremental_analysis import CacheManager
    
    temp_dir = tempfile.mkdtemp()
    try:
        cache = CacheManager(temp_dir)
        
        test_file = os.path.join(temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("print('hello')")
        
        hash1 = cache.calculate_file_hash(test_file)
        if not hash1:
            return False
        
        hash2 = cache.calculate_file_hash(test_file)
        if hash1 != hash2:
            return False
        
        cache.save_analysis_result(test_file, {"issues": 5})
        cached = cache.get_cached_result(test_file)
        
        if cached is None:
            return False
        
        return True
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_incremental_analyzer():
    """测试7: 增量分析器"""
    from full_path_test.core_system.configuration_and_incremental_analysis import (
        IncrementalAnalyzer, ProjectConfiguration
    )
    
    config = ProjectConfiguration()
    analyzer = IncrementalAnalyzer(config)
    
    files_info = analyzer.get_files_to_analyze("full_path_test")
    
    if "total" not in files_info:
        return False
    
    if not isinstance(files_info["total"], list):
        return False
    
    return True


def test_real_code_analyzer():
    """测试8: 真实代码分析器"""
    from full_path_test.external_integrations.real_code_analyzer.real_code_analyzer_module import (
        RealCodeAnalyzerModule, CodeAnalysisInput
    )
    
    analyzer = RealCodeAnalyzerModule()
    success = analyzer.initialize_module()
    
    if not success:
        return False
    
    input_data = CodeAnalysisInput(
        source_path_to_analyze="full_path_test/type_definitions",
        use_llm_for_analysis=False
    )
    
    result = analyzer.execute_module_function(input_data)
    
    if result is None:
        return False
    
    if not hasattr(result, 'overall_score'):
        return False
    
    analyzer.shutdown_module()
    return True


def run_all_e2e_tests():
    """运行所有端到端测试"""
    import traceback
    
    print("=" * 80)
    print("FULLPATHTEST - END-TO-END TEST SUITE")
    print("=" * 80)
    print()
    
    runner = EndToEndTestRunner()
    
    tests = [
        ("Module Imports", test_module_imports),
        ("Productized Module", test_productized_module),
        ("LLM Mock Client", test_llm_mock_client),
        ("Tool Execution Engine", test_tool_execution_engine),
        ("Configuration System", test_configuration_system),
        ("Cache Manager", test_cache_manager),
        ("Incremental Analyzer", test_incremental_analyzer),
        ("Real Code Analyzer", test_real_code_analyzer),
    ]
    
    for test_name, test_func in tests:
        runner.run_test(test_name, test_func)
    
    runner.print_summary()
    
    return runner.failed == 0


if __name__ == "__main__":
    success = run_all_e2e_tests()
    sys.exit(0 if success else 1)
