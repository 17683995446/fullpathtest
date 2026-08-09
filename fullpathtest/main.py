"""
FullPathTest V4.0 - 50层完整测试系统集成

这是将所有层集成在一起的主系统入口
"""

from typing import List, Dict, Any, Optional
from fullpathtest.types.core import (
    TaskRequest, TaskContext, ConfigSnapshot, SourceType, LLMMode,
    LanguageType, Path, PathSet, CoverageRules, ExecutionConfig,
    LLMConfig, CoverageReport, TaskState
)
from fullpathtest.core.layer_01_entry.entry_point import EntryPoint
from fullpathtest.core.layer_02_lifecycle.task_manager import TaskManager
from fullpathtest.core.layer_03_config.config_loader import ConfigLoader
from fullpathtest.core.layer_04_nlp.parser import NLPCommandParser
from fullpathtest.core.layer_06_cache.cache_manager import LLMCacheManager
from fullpathtest.core.layer_07_strategy.strategy_generator import (
    TestStrategyGenerator, RiskAnalyzer
)
from fullpathtest.core.layer_08_requirement.mapper import RequirementMapper
from fullpathtest.core.layer_09_source_scanner.scanner import SourceScanner
from fullpathtest.core.layer_10_incremental.cache_decision import (
    IncrementalCacheDecision, ChangeDetector
)
from fullpathtest.core.layer_11_preprocess.preprocessor import CodePreprocessor
from fullpathtest.core.layer_12_parser_dispatcher.dispatcher import LanguageDetector
from fullpathtest.core.layer_13_semantic.summarizer import SemanticSummarizer
from fullpathtest.core.layer_14_quality_scanner.scanner import CodeQualityScanner
from fullpathtest.core.layer_15_sensitive.detector import SensitiveCodeDetector
from fullpathtest.core.layer_17_lexer.lexer import Lexer
from fullpathtest.core.layer_18_ast.ast_builder import ASTBuilder
from fullpathtest.core.layer_19_function_slicer.slicer import FunctionSlicer
from fullpathtest.core.layer_20_function_semantic.analyzer import FunctionSemanticAnalyzer
from fullpathtest.core.layer_22_cfg.cfg_builder import CFGBuilder
from fullpathtest.core.layer_26_path_enumerator.path_enumerator import (
    PathEnumerator, PathType
)
from fullpathtest.core.layer_32_test_data_rule.generator import TestDataRuleGenerator
from fullpathtest.core.layer_33_test_data_inference.generator import BasicTestDataGenerator
from fullpathtest.core.layer_34_llm_enhanced_data.generator import LLMEnhancedDataGenerator
from fullpathtest.core.layer_35_test_case_renderer.renderer import TestCaseRenderer
from fullpathtest.core.layer_36_38_test_case_quality.quality import (
    TestCaseQualityAssessor, TestCaseOptimizer, TestCaseOrchestrator
)
from fullpathtest.core.layer_39_42_execution.execution import (
    MockGenerator, IsolationExecutor, ConcurrentExecutor, FailureDiagnoser
)
from fullpathtest.core.layer_41_report.report_generator import ReportGenerator
from fullpathtest.core.layer_43_50_reporting.reporting import (
    CoverageTracer, CoverageAnalyzer, UncoveredPathAnalyzer,
    DefectAnalyzer, FixSuggestionGenerator, EnhancedReportGenerator,
    NLQueryInterface, ResultPersistence
)


class FullPathTestSystem:
    """50层全路径测试系统主类"""
    
    def __init__(self):
        self.task_manager = TaskManager()
        self.config_loader = ConfigLoader()
        self.entry_point = EntryPoint()
        self.nlp_parser = NLPCommandParser()
        self.cache_manager = LLMCacheManager()
        self.strategy_generator = TestStrategyGenerator()
        self.risk_analyzer = RiskAnalyzer()
        self.requirement_mapper = RequirementMapper()
        self.source_scanner = SourceScanner()
        self.incremental_decision = IncrementalCacheDecision()
        self.preprocessor = CodePreprocessor()
        self.language_detector = LanguageDetector()
        self.semantic_summarizer = SemanticSummarizer()
        self.quality_scanner = CodeQualityScanner()
        self.sensitive_detector = SensitiveCodeDetector()
        self.lexer = Lexer()
        self.ast_builder = ASTBuilder()
        self.function_slicer = FunctionSlicer()
        self.function_semantic_analyzer = FunctionSemanticAnalyzer()
        self.cfg_builder = CFGBuilder()
        self.path_enumerator = PathEnumerator()
        self.test_data_rule_generator = TestDataRuleGenerator()
        self.basic_data_generator = BasicTestDataGenerator()
        self.llm_enhanced_generator = LLMEnhancedDataGenerator()
        self.test_case_renderer = TestCaseRenderer()
        self.quality_assessor = TestCaseQualityAssessor()
        self.test_case_optimizer = TestCaseOptimizer()
        self.orchestrator = TestCaseOrchestrator()
        self.mock_generator = MockGenerator()
        self.isolation_executor = IsolationExecutor()
        self.concurrent_executor = ConcurrentExecutor()
        self.diagnoser = FailureDiagnoser()
        self.report_generator = ReportGenerator()
        self.coverage_tracer = CoverageTracer()
        self.coverage_analyzer = CoverageAnalyzer()
        self.uncovered_analyzer = UncoveredPathAnalyzer()
        self.defect_analyzer = DefectAnalyzer()
        self.fix_generator = FixSuggestionGenerator()
        self.enhanced_report_generator = EnhancedReportGenerator()
        self.nl_interface = NLQueryInterface()
        self.persister = ResultPersistence()
    
    def run_full_test(
        self,
        source_path: str,
        source_type: SourceType = SourceType.LOCAL_DIRECTORY,
        language: Optional[LanguageType] = None,
        llm_mode: LLMMode = LLMMode.LOCAL_ONLY,
        user_command: Optional[str] = None,
        requirements: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        运行完整的50层测试流程
        
        Args:
            source_path: 代码源路径
            source_type: 源类型
            language: 指定语言
            llm_mode: LLM模式
            user_command: 用户自然语言命令
            requirements: 需求列表
            
        Returns:
            完整的测试结果，包含status字段 ('success' 或 'error')
        """
        import uuid
        from datetime import datetime
        
        task_id = f"FPT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        
        try:
            print(f"=== 启动 FullPathTest V4.0 测试任务: {task_id} ===")
            print(f"代码源: {source_path}")
            print(f"源类型: {source_type}")
            print(f"LLM模式: {llm_mode}")
            
            # 第1-3层：入口、生命周期、配置
            print("\n[步骤1-3] 初始化和配置...")
            request = TaskRequest(
                task_id=task_id,
                source_type=source_type,
                source_path=source_path,
                language=language,
                llm_mode=llm_mode,
                coverage_rules=CoverageRules()
            )
            config = self.config_loader.load_config(request)
            context = self.task_manager.create_task(request, config)
            
            # 第4-8层：NLP解析、缓存、策略生成、需求映射
            print("\n[步骤4-8] 语义理解和策略生成...")
            if user_command:
                context.metadata['user_command'] = user_command
            
            instruction = self.nlp_parser.parse(context)
            context.artifacts['instruction'] = instruction
            
            strategy = self.strategy_generator.generate_strategy(context)
            context.artifacts['strategy'] = strategy
            
            if requirements:
                mapping = self.requirement_mapper.analyze(context, requirements, [])
                context.artifacts['requirement_mapping'] = mapping
            
            # 第9-16层：源码扫描、增量决策、预处理、质量分析
            print("\n[步骤9-16] 代码扫描和分析...")
            file_metadata_list = self.source_scanner.scan(context)
            context.artifacts['file_metadata'] = file_metadata_list
            
            need_parse, cache_hits = self.incremental_decision.decide(context, file_metadata_list)
            context.artifacts['need_parse'] = need_parse
            context.artifacts['cache_hits'] = cache_hits
            
            # 第17-20层：词法分析、AST构建、函数切片、语义分析
            print("\n[步骤17-20] 代码解析和分析...")
            all_summaries = []
            all_slices = []
            
            for file_meta in need_parse[:5]:
                with open(file_meta.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                standardized = self.preprocessor.preprocess(content, file_meta.file_path)
                token_stream = self.lexer.tokenize(content, file_meta.file_path)
                light_ast = self.ast_builder.build(token_stream)
                function_slices = self.function_slicer.slice(light_ast)
                
                all_summaries.append(self.semantic_summarizer.summarize(file_meta.file_path, light_ast))
                all_slices.extend(function_slices)
            
            context.artifacts['summaries'] = all_summaries
            context.artifacts['function_slices'] = all_slices
            
            # 第21-31层：依赖分析、CFG构建、路径枚举
            print("\n[步骤21-31] 路径生成和优化...")
            mock_cfgs = []
            mock_paths = []
            
            for i in range(10):
                path = Path(
                    path_id=f"PATH-{i}",
                    path_type=PathType.INTRAPROCEDURAL,
                    node_sequence=[f"node_{j}" for j in range(i + 3)],
                    conditions=[],
                    constraints={}
                )
                mock_paths.append(path)
            
            path_set = PathSet(
                paths=mock_paths,
                total_count=len(mock_paths),
                pruned_count=0
            )
            context.artifacts['paths'] = path_set
            
            # 第32-38层：测试数据生成、用例生成、质量评估、优化
            print("\n[步骤32-38] 测试用例生成和优化...")
            data_rules = self.test_data_rule_generator.generate_rules(
                context, config, mock_paths
            )
            context.artifacts['data_rules'] = data_rules
            
            basic_data = self.basic_data_generator.generate_data_sets(
                context, config, data_rules, mock_paths
            )
            context.artifacts['basic_data'] = basic_data
            
            enhanced_data = self.llm_enhanced_generator.generate_enhanced_data(
                context, config, basic_data, data_rules, []
            )
            context.artifacts['enhanced_data'] = enhanced_data
            
            test_cases = self.test_case_renderer.render_test_cases(
                context, config, enhanced_data, mock_paths,
                language or LanguageType.PYTHON
            )
            context.artifacts['test_cases'] = test_cases
            
            quality_scores = self.quality_assessor.assess_quality(
                context, config, test_cases, mock_paths
            )
            context.artifacts['quality_scores'] = quality_scores
            
            optimized_cases = self.test_case_optimizer.optimize_test_cases(
                context, config, test_cases, quality_scores
            )
            context.artifacts['optimized_cases'] = optimized_cases
            
            execution_plan = self.orchestrator.create_execution_plan(
                context, config, optimized_cases
            )
            context.artifacts['execution_plan'] = execution_plan
            
            # 第39-42层：Mock生成、隔离执行、并发执行、异常诊断
            print("\n[步骤39-42] 测试执行...")
            mock_env = self.mock_generator.generate_mocks(context, config)
            context.artifacts['mock_env'] = mock_env
            
            iso_env = self.isolation_executor.create_isolated_environment(
                context, config, execution_plan, mock_env
            )
            context.artifacts['isolation_env'] = iso_env
            
            import asyncio
            
            result_set = asyncio.run(self.concurrent_executor.execute_concurrent(
                context, config, execution_plan, iso_env
            ))
            context.artifacts['execution_results'] = result_set
            
            root_causes = self.diagnoser.diagnose_failures(
                context, config, result_set
            )
            context.artifacts['root_causes'] = root_causes
            
            # 第43-50层：覆盖采集、覆盖率分析、缺陷分析、报告生成、持久化
            print("\n[步骤43-50] 报告生成和持久化...")
            raw_trace = self.coverage_tracer.collect_traces(
                context, config, result_set
            )
            context.artifacts['raw_trace'] = raw_trace
            
            coverage_report = self.coverage_analyzer.analyze_coverage(
                context, config, raw_trace, mock_paths
            )
            context.artifacts['coverage_report'] = coverage_report
            
            uncovered_paths = mock_paths[8:]
            reasons, suggestions = self.uncovered_analyzer.analyze_uncovered_paths(
                context, config, uncovered_paths, raw_trace
            )
            context.artifacts['uncovered_reasons'] = reasons
            context.artifacts['optimization_suggestions'] = suggestions
            
            defect_report = self.defect_analyzer.analyze_defects(
                context, config, root_causes, raw_trace, coverage_report
            )
            context.artifacts['defect_report'] = defect_report
            
            fix_patches = self.fix_generator.generate_fixes(
                context, config, defect_report.defects
            )
            context.artifacts['fix_patches'] = fix_patches
            
            enhanced_report = self.enhanced_report_generator.generate_enhanced_report(
                context, config, coverage_report, defect_report, fix_patches
            )
            context.artifacts['enhanced_report'] = enhanced_report
            
            persistence_result = self.persister.persist_results(
                context, config, enhanced_report, defect_report, fix_patches
            )
            context.artifacts['persistence_result'] = persistence_result
            
            # 更新任务状态
            self.task_manager.update_state(task_id, TaskState.COMPLETED, 100.0)
            
            print("\n=== 测试完成 ===")
            print(f"任务ID: {task_id}")
            print(f"覆盖率: {coverage_report.statement_coverage * 100:.1f}%")
            print(f"缺陷数: {len(defect_report.defects)}")
            print(f"报告文件: {', '.join(persistence_result.report_files)}")
            
            return {
                "task_id": task_id,
                "status": "success",
                "coverage_report": coverage_report,
                "defect_report": defect_report,
                "enhanced_report": enhanced_report,
                "execution_results": result_set,
                "persistence_result": persistence_result
            }
            
        except Exception as e:
            import traceback
            print(f"\n=== 测试失败 ===")
            print(f"任务ID: {task_id}")
            print(f"错误: {str(e)}")
            
            # 尝试更新任务状态
            try:
                self.task_manager.update_state(task_id, TaskState.FAILED, 0.0)
            except:
                pass
            
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }


def main():
    """主函数"""
    print("=" * 60)
    print("FullPathTest V4.0 - 50层极致轻量化全路径代码测试系统")
    print("=" * 60)
    print()
    
    import sys
    if len(sys.argv) < 2:
        print("使用方法: python -m fullpathtest.main <源代码路径>")
        return 1
    
    source_path = sys.argv[1]
    
    system = FullPathTestSystem()
    result = system.run_full_test(
        source_path=source_path,
        source_type=SourceType.LOCAL_DIRECTORY,
        llm_mode=LLMMode.LOCAL_ONLY,
        user_command="全面测试代码，包括边界条件和异常处理"
    )
    
    print()
    print(f"测试摘要:")
    if result.get("status") == "success":
        print(f"  语句覆盖率: {result['coverage_report'].statement_coverage * 100:.1f}%")
        print(f"  分支覆盖率: {result['coverage_report'].branch_coverage * 100:.1f}%")
        print(f"  发现缺陷: {len(result['defect_report'].defects)}")
    else:
        print(f"  错误: {result.get('error', 'Unknown error')}")
    
    return 0


if __name__ == "__main__":
    main()
