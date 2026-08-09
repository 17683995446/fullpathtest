"""
FullPathTest v4.0 - AI集成测试
"""

import sys
import os
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_ai_module_import():
    """测试1: 模块导入"""
    try:
        from full_path_test.ai.ai_integration import (
            LLMProvider,
            LLMConfiguration,
            AICodeAnalyzer,
            create_ai_analyzer,
            MockLLMClient
        )
        print("✓ Test 1: AI模块导入 - PASSED")
        return True
    except Exception as e:
        print(f"✗ Test 1: AI模块导入 - FAILED: {e}")
        return False


def test_llm_configuration():
    """测试2: LLM配置"""
    try:
        from full_path_test.ai.ai_integration import LLMConfiguration, LLMProvider
        
        config = LLMConfiguration(
            provider=LLMProvider.MOCK,
            model="test-model",
            temperature=0.5
        )
        
        assert config.provider == LLMProvider.MOCK
        assert config.model == "test-model"
        assert config.temperature == 0.5
        
        print("✓ Test 2: LLM配置 - PASSED")
        return True
    except Exception as e:
        print(f"✗ Test 2: LLM配置 - FAILED: {e}")
        return False


def test_mock_llm_client():
    """测试3: Mock LLM客户端"""
    try:
        from full_path_test.ai.ai_integration import (
            MockLLMClient,
            LLMConfiguration,
            LLMProvider
        )
        
        config = LLMConfiguration(provider=LLMProvider.MOCK)
        client = MockLLMClient(config)
        
        # 测试代码质量分析
        response = client.generate(
            "analyze this code: def foo(): pass",
            "You are a code reviewer."
        )
        
        assert response is not None
        assert len(response) > 0
        
        print("✓ Test 3: Mock LLM客户端 - PASSED")
        return True
    except Exception as e:
        print(f"✗ Test 3: Mock LLM客户端 - FAILED: {e}")
        return False


def test_cache_manager():
    """测试4: 缓存管理器"""
    try:
        from full_path_test.ai.ai_integration import CacheManager
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        try:
            cache = CacheManager(temp_dir)
            
            # 测试缓存设置和获取
            test_prompt = "test prompt"
            test_response = "test response"
            
            cache.set(test_prompt, "test-model", test_response)
            cached = cache.get(test_prompt, "test-model")
            
            assert cached == test_response
            
            print("✓ Test 4: 缓存管理器 - PASSED")
            return True
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception as e:
        print(f"✗ Test 4: 缓存管理器 - FAILED: {e}")
        return False


def test_code_analysis_request():
    """测试5: 代码分析请求"""
    try:
        from full_path_test.ai.ai_integration import (
            CodeAnalysisRequest,
            AnalysisType
        )
        
        request = CodeAnalysisRequest(
            code="def hello(): print('world')",
            file_path="test.py",
            language="python",
            analysis_types=[AnalysisType.CODE_QUALITY]
        )
        
        assert request.code == "def hello(): print('world')"
        assert request.file_path == "test.py"
        assert AnalysisType.CODE_QUALITY in request.analysis_types
        
        print("✓ Test 5: 代码分析请求 - PASSED")
        return True
    except Exception as e:
        print(f"✗ Test 5: 代码分析请求 - FAILED: {e}")
        return False


def test_ai_code_analyzer():
    """测试6: AI代码分析器"""
    try:
        from full_path_test.ai.ai_integration import (
            AICodeAnalyzer,
            create_ai_analyzer,
            CodeAnalysisRequest,
            AnalysisType
        )
        
        # 创建分析器
        analyzer = create_ai_analyzer()
        
        # 示例代码
        sample_code = """
def add(a, b):
    return a + b

def process(items):
    result = []
    for item in items:
        result.append(item * 2)
    return result
"""
        
        # 创建请求
        request = CodeAnalysisRequest(
            code=sample_code,
            file_path="test.py",
            analysis_types=[AnalysisType.CODE_QUALITY]
        )
        
        # 执行分析
        start_time = time.time()
        response = analyzer.analyze_code(request)
        duration = time.time() - start_time
        
        # 验证结果
        assert response.success, "Analysis should succeed"
        assert response.score > 0, "Score should be positive"
        assert response.processing_time > 0, "Processing time should be recorded"
        
        print(f"✓ Test 6: AI代码分析器 - PASSED (耗时: {duration:.2f}s)")
        print(f"  - 评分: {response.score}/100")
        print(f"  - 问题数: {len(response.issues)}")
        print(f"  - 建议数: {len(response.suggestions)}")
        
        return True
    except Exception as e:
        print(f"✗ Test 6: AI代码分析器 - FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_analysis_types():
    """测试7: 多类型分析"""
    try:
        from full_path_test.ai.ai_integration import (
            create_ai_analyzer,
            CodeAnalysisRequest,
            AnalysisType
        )
        
        analyzer = create_ai_analyzer()
        
        sample_code = """
import os
def process():
    data = input()
    result = os.system(data)
    return result
"""
        
        # 测试多种分析类型
        analysis_types = [
            AnalysisType.CODE_QUALITY,
            AnalysisType.SECURITY,
            AnalysisType.PERFORMANCE
        ]
        
        for analysis_type in analysis_types:
            request = CodeAnalysisRequest(
                code=sample_code,
                analysis_types=[analysis_type]
            )
            
            response = analyzer.analyze_code(request)
            assert response.success, f"{analysis_type} analysis should succeed"
            
            print(f"  ✓ {analysis_type.value} 分析成功")
        
        print("✓ Test 7: 多类型分析 - PASSED")
        return True
    except Exception as e:
        print(f"✗ Test 7: 多类型分析 - FAILED: {e}")
        return False


def test_fix_suggestion():
    """测试8: 修复建议生成"""
    try:
        from full_path_test.ai.ai_integration import (
            create_ai_analyzer
        )
        
        analyzer = create_ai_analyzer()
        
        code = """
def process(data):
    return data['key'].split(',')
"""
        
        issue = "Potential KeyError if 'key' not in data"
        
        fix = analyzer.suggest_fixes(code, issue)
        
        assert fix is not None
        assert fix.original_code == code
        
        print("✓ Test 8: 修复建议生成 - PASSED")
        return True
    except Exception as e:
        print(f"✗ Test 8: 修复建议生成 - FAILED: {e}")
        return False


def test_performance():
    """测试9: 性能测试"""
    try:
        from full_path_test.ai.ai_integration import (
            create_ai_analyzer,
            CodeAnalysisRequest,
            AnalysisType
        )
        
        analyzer = create_ai_analyzer()
        
        sample_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)
"""
        
        # 性能测试
        iterations = 5
        times = []
        
        for i in range(iterations):
            start = time.time()
            request = CodeAnalysisRequest(
                code=sample_code,
                analysis_types=[AnalysisType.PERFORMANCE]
            )
            analyzer.analyze_code(request)
            times.append(time.time() - start)
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        print(f"✓ Test 9: 性能测试 - PASSED")
        print(f"  - 平均耗时: {avg_time:.2f}s")
        print(f"  - 最快: {min_time:.2f}s")
        print(f"  - 最慢: {max_time:.2f}s")
        
        return True
    except Exception as e:
        print(f"✗ Test 9: 性能测试 - FAILED: {e}")
        return False


def test_error_handling():
    """测试10: 错误处理"""
    try:
        from full_path_test.ai.ai_integration import (
            create_ai_analyzer,
            CodeAnalysisRequest
        )
        
        analyzer = create_ai_analyzer()
        
        # 测试空代码
        request = CodeAnalysisRequest(
            code="",
            analysis_types=[]
        )
        
        # 应该能够处理而不崩溃
        response = analyzer.analyze_code(request)
        
        # 至少不应该抛出异常
        assert response is not None
        
        print("✓ Test 10: 错误处理 - PASSED")
        return True
    except Exception as e:
        print(f"✗ Test 10: 错误处理 - FAILED: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("FullPathTest v4.0 - AI集成测试套件")
    print("="*60 + "\n")
    
    tests = [
        test_ai_module_import,
        test_llm_configuration,
        test_mock_llm_client,
        test_cache_manager,
        test_code_analysis_request,
        test_ai_code_analyzer,
        test_multiple_analysis_types,
        test_fix_suggestion,
        test_performance,
        test_error_handling,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        if test_func():
            passed += 1
        else:
            failed += 1
        print()
    
    print("="*60)
    print("测试总结")
    print("="*60)
    print(f"总测试数: {len(tests)}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"成功率: {(passed/len(tests)*100):.1f}%")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
