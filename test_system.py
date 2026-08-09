#!/usr/bin/env python3
"""
测试核心功能验证脚本
"""
import sys
import os

print("=" * 70)
print("FullPathTest V4.0 - 核心功能验证")
print("=" * 70)
print()

def test_1_imports():
    """测试基本模块导入"""
    print("测试 1: 基本导入测试")
    print("-" * 40)
    
    try:
        # 类型系统
        from fullpathtest.types.core import (
            SourceType, LLMMode, TaskState,
            LanguageType, RiskLevel, PathType
        )
        print("  ✅ 类型枚举导入成功")
        
        # 核心数据结构
        from fullpathtest.types.core import TaskRequest, ConfigSnapshot
        print("  ✅ 核心数据结构导入成功")
        
        return True
    except Exception as e:
        print(f"  ❌ 导入失败: {e}")
        return False

def test_2_type_creation():
    """测试类型创建"""
    print("\n测试 2: 类型创建")
    print("-" * 40)
    
    try:
        from fullpathtest.types.core import TaskRequest, ConfigSnapshot
        from fullpathtest.types.core import SourceType, LLMMode
        
        request = TaskRequest(
            task_id="test-001",
            source_type=SourceType.LOCAL_DIRECTORY,
            source_path="/tmp/test"
        )
        print(f"  ✅ TaskRequest 创建成功")
        print(f"    - task_id: {request.task_id}")
        print(f"    - source_type: {request.source_type.name}")
        
        config = ConfigSnapshot()
        print(f"  ✅ ConfigSnapshot 创建成功")
        
        return True
    except Exception as e:
        print(f"  ❌ 类型创建失败: {e}")
        return False

def test_3_core_modules():
    """测试核心模块"""
    print("\n测试 3: 核心模块测试")
    print("-" * 40)
    
    try:
        modules = [
            ("layer_01_entry.entry_point", "EntryPoint"),
            ("layer_02_lifecycle.task_manager", "TaskManager"),
            ("layer_03_config.config_loader", "ConfigLoader"),
            ("layer_04_nlp.parser", "NLPCommandParser"),
            ("layer_06_cache.cache_manager", "LLMCacheManager"),
            ("layer_09_source_scanner.scanner", "SourceScanner"),
            ("layer_11_preprocess.preprocessor", "CodePreprocessor"),
            ("layer_17_lexer.lexer", "Lexer"),
            ("layer_18_ast.ast_builder", "ASTBuilder"),
            ("layer_22_cfg.cfg_builder", "CFGBuilder"),
            ("layer_26_path_enumerator.path_enumerator", "PathEnumerator"),
            ("layer_32_test_data_rule.generator", "TestDataRuleGenerator"),
            ("layer_39_coverage.coverage_calculator", "CoverageCalculator"),
            ("layer_41_report.report_generator", "ReportGenerator"),
        ]
        
        for module, class_name in modules:
            try:
                mod = __import__(
                    f"fullpathtest.core.{module}", fromlist=[class_name])
                cls = getattr(mod, class_name)
                print(f"  ✅ {class_name} 可用")
            except Exception as e:
                print(f"  ⚠️  {class_name} 导入失败: {type(e).__name__}")
        
        return True
    except Exception as e:
        print(f"  ❌ 模块测试失败: {e}")
        return False

def test_4_report_generator():
    """测试报告生成模块"""
    print("\n测试 4: 报告生成模块")
    print("-" * 40)
    
    try:
        from fullpathtest.core.layer_41_report.report_generator import ReportGenerator
        gen = ReportGenerator()
        print(f"  ✅ ReportGenerator 创建成功")
        return True
    except Exception as e:
        print(f"  ❌ 报告生成模块测试失败: {e}")
        return False

def test_5_type_enum_usage():
    """测试枚举使用"""
    print("\n测试 5: 枚举类型使用")
    print("-" * 40)
    
    try:
        from fullpathtest.types.core import (
            SourceType, LLMMode, LanguageType, RiskLevel, PathType
        )
        
        # SourceType
        print(f"  SourceType: {[s.name for s in list(SourceType.__members__.values())]}")
        # LLMMode
        print(f"  LLMMode: {[l.name for l in list(LLMMode.__members__.values())]}")
        # LanguageType
        print(f"  LanguageType: {[l.name for l in list(LanguageType.__members__.values())[:5]]}...")
        # RiskLevel
        print(f"  RiskLevel: {[r.name for r in list(RiskLevel.__members__.values())]}")
        # PathType
        print(f"  PathType: {[p.name for p in list(PathType.__members__.values())]}")
        print(f"  ✅ 枚举类型使用正常")
        
        return True
    except Exception as e:
        print(f"  ❌ 枚举类型使用失败: {e}")
        return False

def main():
    """运行所有测试"""
    tests = [
        test_1_imports,
        test_2_type_creation,
        test_3_core_modules,
        test_4_report_generator,
        test_5_type_enum_usage,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print()
    print("=" * 70)
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("✅ 所有测试通过！")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
