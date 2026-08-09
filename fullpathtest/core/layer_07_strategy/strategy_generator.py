"""
第7层：测试目标语义理解层

基于用户任务指令与项目代码结构，理解测试范围、业务目标、风险重点。
"""

from typing import Dict, List, Any, Optional
from fullpathtest.types.core import TaskContext, TestStrategy, FileSemanticSummary, TestRiskScore, RiskLevel


class TestStrategyGenerator:
    """测试策略生成器"""
    
    def __init__(self):
        self.strategy_cache: Dict[str, TestStrategy] = {}
    
    def generate_strategy(self, context: TaskContext) -> TestStrategy:
        """生成测试策略"""
        strategy_id = f"STRAT_{context.task_id}"
        
        module_priorities = self._calculate_module_priorities(context)
        scenario_weights = self._calculate_scenario_weights(context)
        coverage_depth = self._determine_coverage_depth(context)
        execution_mode = self._determine_execution_mode(context)
        
        strategy = TestStrategy(
            strategy_id=strategy_id,
            module_priorities=module_priorities,
            scenario_weights=scenario_weights,
            coverage_depth=coverage_depth,
            execution_mode=execution_mode,
            risk_adaptive=True,
            parallel_degree=context.config.execution_config.max_parallel_workers
        )
        
        self.strategy_cache[strategy_id] = strategy
        context.artifacts['strategy'] = strategy
        
        return strategy
    
    def _calculate_module_priorities(self, context: TaskContext) -> Dict[str, int]:
        """计算模块优先级"""
        priorities = {}
        
        instruction = context.artifacts.get('instruction')
        if instruction and hasattr(instruction, 'target_modules'):
            for i, module in enumerate(instruction.target_modules):
                priorities[module] = len(instruction.target_modules) - i
        
        if instruction and hasattr(instruction, 'priority_areas'):
            for area in instruction.priority_areas:
                if area not in priorities:
                    priorities[area] = 5
        
        return priorities
    
    def _calculate_scenario_weights(self, context: TaskContext) -> Dict[str, float]:
        """计算场景权重"""
        weights = {}
        
        weights['normal_flow'] = 1.0
        weights['error_handling'] = 0.8
        weights['boundary'] = 0.9
        weights['security'] = 1.0
        weights['performance'] = 0.6
        
        instruction = context.artifacts.get('instruction')
        if instruction and hasattr(instruction, 'business_scenarios'):
            for scenario in instruction.business_scenarios:
                if scenario in weights:
                    weights[scenario] = 1.0
        
        return weights
    
    def _determine_coverage_depth(self, context: TaskContext) -> str:
        """确定覆盖深度"""
        coverage_rules = context.request.coverage_rules
        
        if coverage_rules.path and coverage_rules.branch and coverage_rules.condition:
            return 'deep'
        elif coverage_rules.branch:
            return 'medium'
        else:
            return 'shallow'
    
    def _determine_execution_mode(self, context: TaskContext) -> str:
        """确定执行模式"""
        max_workers = context.config.execution_config.max_parallel_workers
        
        if max_workers > 1:
            return 'parallel'
        elif max_workers == 1:
            return 'sequential'
        else:
            return 'adaptive'


class RiskAnalyzer:
    """风险分析器"""
    
    def __init__(self):
        self.risk_cache: Dict[str, TestRiskScore] = {}
    
    def analyze_risks(
        self,
        context: TaskContext,
        files: List[FileSemanticSummary]
    ) -> List[TestRiskScore]:
        """分析测试风险"""
        risk_scores = []
        
        for file_summary in files:
            risk_score = self._analyze_file_risk(context, file_summary)
            risk_scores.append(risk_score)
        
        risk_scores.sort(key=lambda x: x.risk_score, reverse=True)
        
        return risk_scores
    
    def _analyze_file_risk(
        self,
        context: TaskContext,
        file_summary: FileSemanticSummary
    ) -> TestRiskScore:
        """分析文件风险"""
        factors = {}
        recommendations = []
        
        complexity_factor = self._calculate_complexity_factor(file_summary)
        factors['complexity'] = complexity_factor
        
        if complexity_factor > 0.7:
            recommendations.append("该文件复杂度较高，建议增加测试覆盖")
        
        business_factor = self._calculate_business_factor(file_summary)
        factors['business_importance'] = business_factor
        
        if business_factor > 0.8:
            recommendations.append("该文件涉及核心业务，必须保证高覆盖率")
        
        change_factor = self._calculate_change_factor(file_summary)
        factors['change_frequency'] = change_factor
        
        if change_factor > 0.6:
            recommendations.append("该文件变更频繁，建议持续监控")
        
        risk_score = (
            complexity_factor * 0.3 +
            business_factor * 0.4 +
            change_factor * 0.3
        )
        
        risk_level = self._score_to_level(risk_score)
        
        return TestRiskScore(
            file_path=file_summary.file_path,
            risk_score=risk_score,
            risk_level=risk_level,
            factors=factors,
            recommendations=recommendations
        )
    
    def _calculate_complexity_factor(self, file_summary: FileSemanticSummary) -> float:
        """计算复杂度因子"""
        core_functions = len(file_summary.core_functions)
        imports = len(file_summary.imports)
        
        if core_functions > 10 or imports > 20:
            return 0.9
        elif core_functions > 5 or imports > 10:
            return 0.6
        else:
            return 0.3
    
    def _calculate_business_factor(self, file_summary: FileSemanticSummary) -> float:
        """计算业务重要性因子"""
        entry_points = len(file_summary.entry_points)
        exports = len(file_summary.exports)
        
        if entry_points > 0 and exports > 0:
            return 0.9
        elif entry_points > 0 or exports > 0:
            return 0.6
        else:
            return 0.3
    
    def _calculate_change_factor(self, file_summary: FileSemanticSummary) -> float:
        """计算变更频率因子"""
        return 0.5
    
    def _score_to_level(self, score: float) -> RiskLevel:
        """分数转等级"""
        if score >= 0.8:
            return RiskLevel.CRITICAL
        elif score >= 0.6:
            return RiskLevel.HIGH
        elif score >= 0.4:
            return RiskLevel.MEDIUM
        elif score >= 0.2:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL
