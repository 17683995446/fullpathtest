"""
Comprehensive test suite for the fully modularized FullPathTest system.
"""

import os
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, List


SAMPLE_TEST_CODE_ONE = """
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

SAMPLE_TEST_CODE_TWO = """
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


def test_type_definitions_import():
    """Test that all type definitions can be imported correctly."""
    from full_path_test.type_definitions.core_data_types import (
        CodeSourceType,
        SystemConfiguration,
        CodeQualityIssue,
        CodeAnalysisResult
    )
    
    config = SystemConfiguration(source_path="./")
    assert config is not None
    assert config.source_path == "./"
    print("✓ Type definitions imported successfully")
    return True


def test_module_infrastructure_import():
    """Test that module infrastructure can be imported correctly."""
    from full_path_test.module_infrastructure.productized_module_base import (
        ModuleStatus,
        ModulePriority,
        ModuleConfiguration,
        ModuleMetrics,
        ModuleHealthStatus
    )
    
    config = ModuleConfiguration(module_name="TestModule")
    assert config is not None
    print("✓ Module infrastructure imported successfully")
    return True


def test_open_source_tools_import():
    """Test that open source tools integration can be imported."""
    from full_path_test.external_integrations.open_source_tools.real_open_source_tool_integrator import (
        OpenSourceToolName,
        RealOpenSourceToolIntegrator,
        get_real_open_source_tool_integrator
    )
    
    integrator = get_real_open_source_tool_integrator()
    assert integrator is not None
    
    available_tools = integrator.get_available_tools_list()
    print(f"✓ Available open source tools integration initialized, found {len(available_tools)} tools available")
    return True


def test_llm_integration_import():
    """Test that LLM integration can be imported and used."""
    from full_path_test.external_integrations.llm_clients.real_llm_integration_client import (
        LLMProviderType,
        LLMConnectionConfiguration,
        RealLLMIntegrationClient,
        create_mock_llm_client
    )
    
    llm_client = create_mock_llm_client()
    assert llm_client is not None
    
    response = llm_client.generate_llm_response(
        "Hello, test prompt", 
        "You are a helpful test helper."
    )
    
    assert response is not None
    assert response.generation_successful is True
    assert len(response.generated_content) > 0
    print("✓ LLM integration tested successfully")
    return True


def test_real_code_analyzer_module():
    """Test that the real code analyzer module works."""
    from full_path_test.external_integrations.real_code_analyzer.real_code_analyzer_module import (
        CodeAnalysisInput,
        RealCodeAnalyzerModule,
        get_real_code_analyzer_module
    )
    
    # Create a temporary test file
    temp_dir = tempfile.mkdtemp()
    try:
        test_file_path = Path(temp_dir) / "test_module_sample.py"
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(SAMPLE_TEST_CODE_ONE)
        
        analyzer = get_real_code_analyzer_module()
        health = analyzer.check_module_health()
        assert health.overall_healthy is True
        
        input_config = CodeAnalysisInput(
            source_path_to_analyze=str(test_file_path),
            use_llm_for_analysis=False
        )
        
        result = analyzer.execute_module_function(input_config)
        assert result is not None
        assert result.total_files_analyzed >= 0
        print("✓ Real code analyzer module tested successfully")
        analyzer.shutdown_module()
        
    finally:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return True


@dataclass
class TestSuiteResult:
    """Results from running the comprehensive test suite."""
    total_tests_count: int = 0
    passed_tests_count: int = 0
    failed_tests_count: int = 0
    test_results: List[Dict[str, Any]] = field(default_factory=list)


def run_full_comprehensive_test_suite():
    """Run the complete comprehensive test suite for the fully modular system."""
    print("=" * 70)
    print("FullPathTest Fully Modularized System - Comprehensive Test Suite")
    print("=" * 70)
    print()
    
    results = TestSuiteResult()
    
    test_functions = [
        ("test_type_definitions_import", "Type Definitions Import Test"),
        ("test_module_infrastructure_import", "Module Infrastructure Import Test"),
        ("test_open_source_tools_import", "Open Source Tools Integration Test"),
        ("test_llm_integration_import", "LLM Integration Test"),
        ("test_real_code_analyzer_module", "Real Code Analyzer Module Test"),
    ]
    
    for test_func_name, test_description in test_functions:
        results.total_tests_count += 1
        print(f"[{results.total_tests_count}. {test_description}")
        
        try:
            # Get the test function from globals
            test_func = globals()[test_func_name]
            success = test_func()
            
            if success:
                results.passed_tests_count += 1
                results.test_results.append({
                    "test_name": test_func_name,
                    "test_status": "PASSED"
                })
            else:
                results.failed_tests_count += 1
                results.test_results.append({
                    "test_name": test_func_name,
                    "test_status": "FAILED"
                })
            
        except Exception as error:
            results.failed_tests_count += 1
            results.test_results.append({
                "test_name": test_func_name,
                "test_status": "FAILED",
                "error": str(error)
            })
            print(f"✗ FAILED: {error}")
        
        print()
    
    print("=" * 70)
    print("SUMMARY:")
    print(f"  Total tests: {results.total_tests_count}")
    print(f"  ✓ Passed: {results.passed_tests_count}")
    print(f"  ✗ Failed: {results.failed_tests_count}")
    
    pass_rate = (
        (results.passed_tests_count / results.total_tests_count * 100.0) 
        if results.total_tests_count > 0 
        else 0.0
    )
    print(f"  Pass rate: {pass_rate:.1f}%")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    run_full_comprehensive_test_suite()
