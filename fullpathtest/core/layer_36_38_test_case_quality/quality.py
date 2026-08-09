"""
第36-38层：用例质量评估、优化、编排层
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from fullpathtest.types.core import TaskContext, ConfigSnapshot, Path, RiskLevel
from fullpathtest.core.layer_35_test_case_renderer.renderer import TestCaseCode


@dataclass
class QualityIssue:
    """质量问题"""
    issue_id: str
    issue_type: str
    severity: RiskLevel
    description: str
    line_number: int = -1


@dataclass
class QualityScore:
    """质量评分"""
    overall_score: float
    coverage_score: float
    correctness_score: float
    readability_score: float
    stability_score: float
    assertion_coverage_score: float
    issues: List[QualityIssue] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class OptimizedTestCase:
    """优化后测试用例"""
    original_case_id: str
    optimized_content: str
    improvements: List[str]
    quality_score: QualityScore


@dataclass
class TestCaseExecutionPlan:
    """用例执行计划"""
    plan_id: str
    execution_order: List[str]
    modules: Dict[str, List[str]] = field(default_factory=dict)
    priority_groups: Dict[int, List[str]] = field(default_factory=dict)
    estimated_total_time: float = 0.0
    version: str = "1.0.0"


class TestCaseQualityAssessor:
    """用例质量评估器"""
    
    def __init__(self):
        self.scores: Dict[str, QualityScore] = {}
    
    def assess_quality(
        self,
        context: TaskContext,
        config: ConfigSnapshot,
        test_cases: Dict[str, TestCaseCode],
        paths: List[Path]
    ) -> Dict[str, QualityScore]:
        """评估用例质量"""
        scores = {}
        
        for path in paths:
            test_case = test_cases.get(path.path_id)
            if not test_case:
                continue
            
            score = self._assess_case_quality(test_case, path)
            scores[path.path_id] = score
            self.scores[path.path_id] = score
        
        return scores
    
    def _assess_case_quality(self, case: TestCaseCode, path: Path) -> QualityScore:
        """评估单个用例质量"""
        issues = []
        suggestions = []
        
        coverage_score = self._calculate_coverage_score(case, path)
        correctness_score = self._calculate_correctness_score(case)
        readability_score = self._calculate_readability_score(case)
        stability_score = self._calculate_stability_score(case)
        assertion_coverage = self._calculate_assertion_coverage(case)
        
        if assertion_coverage < 0.5:
            issues.append(QualityIssue(
                issue_id="assertion_missing",
                issue_type="missing_assertions",
                severity=RiskLevel.MEDIUM,
                description="用例缺少断言语句"
            ))
            suggestions.append("添加适当的断言来验证测试结果")
        
        if readability_score < 0.6:
            issues.append(QualityIssue(
                issue_id="low_readability",
                issue_type="readability",
                severity=RiskLevel.LOW,
                description="用例可读性较差"
            ))
            suggestions.append("添加注释、使用有意义的变量名")
        
        overall_score = (
            coverage_score * 0.25 +
            correctness_score * 0.25 +
            readability_score * 0.20 +
            stability_score * 0.20 +
            assertion_coverage * 0.10
        )
        
        return QualityScore(
            overall_score=overall_score,
            coverage_score=coverage_score,
            correctness_score=correctness_score,
            readability_score=readability_score,
            stability_score=stability_score,
            assertion_coverage_score=assertion_coverage,
            issues=issues,
            suggestions=suggestions
        )
    
    def _calculate_coverage_score(self, case: TestCaseCode, path: Path) -> float:
        """计算覆盖率分数"""
        return min(1.0, len(path.node_sequence) / 20.0)
    
    def _calculate_correctness_score(self, case: TestCaseCode) -> float:
        """计算正确性分数"""
        content = case.code_content.lower()
        score = 0.8
        
        if "todo" in content:
            score -= 0.2
        if "not implemented" in content:
            score -= 0.3
        
        return max(0.0, score)
    
    def _calculate_readability_score(self, case: TestCaseCode) -> float:
        """计算可读性分数"""
        content = case.code_content
        
        comment_ratio = self._calculate_comment_ratio(content)
        avg_line_length = self._calculate_avg_line_length(content)
        
        score = 0.7
        if comment_ratio > 0.1:
            score += 0.1
        if avg_line_length < 80:
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_comment_ratio(self, content: str) -> float:
        lines = content.split('\n')
        comment_lines = [l for l in lines if '#' in l or '//' in l]
        return len(comment_lines) / len(lines) if lines else 0
    
    def _calculate_avg_line_length(self, content: str) -> float:
        lines = content.split('\n')
        if not lines:
            return 0
        return sum(len(l) for l in lines) / len(lines)
    
    def _calculate_stability_score(self, case: TestCaseCode) -> float:
        """计算稳定性分数"""
        content = case.code_content.lower()
        score = 0.7
        
        if "time." in content or "random" in content:
            score -= 0.2
        
        return max(0.0, score)
    
    def _calculate_assertion_coverage(self, case: TestCaseCode) -> float:
        """计算断言覆盖率"""
        content = case.code_content.lower()
        assertion_keywords = ['assert', 'expect', 'should', 'verify']
        
        assertion_count = sum(1 for keyword in assertion_keywords if keyword in content)
        
        if assertion_count == 0:
            return 0.0
        elif assertion_count >= 2:
            return 1.0
        else:
            return 0.5


class TestCaseOptimizer:
    """测试用例优化器"""
    
    def __init__(self):
        self.optimized_cases: Dict[str, OptimizedTestCase] = {}
    
    def optimize_test_cases(
        self,
        context: TaskContext,
        config: ConfigSnapshot,
        original_cases: Dict[str, TestCaseCode],
        quality_scores: Dict[str, QualityScore]
    ) -> Dict[str, OptimizedTestCase]:
        """优化测试用例"""
        optimized = {}
        
        for path_id, case in original_cases.items():
            score = quality_scores.get(path_id)
            if not score:
                continue
            
            optimized_case = self._optimize_case(case, score)
            optimized[path_id] = optimized_case
            self.optimized_cases[path_id] = optimized_case
        
        return optimized
    
    def _optimize_case(
        self,
        original_case: TestCaseCode,
        score: QualityScore
    ) -> OptimizedTestCase:
        """优化单个用例"""
        improvements = []
        content = original_case.code_content
        
        for suggestion in score.suggestions:
            if "断言" in suggestion or "assert" in suggestion.lower():
                content = self._add_basic_assertions(content)
                improvements.append("添加了基本断言")
            
            if "注释" in suggestion or "comment" in suggestion.lower():
                content = self._improve_comments(content)
                improvements.append("改善了注释")
        
        return OptimizedTestCase(
            original_case_id=original_case.code_id,
            optimized_content=content,
            improvements=improvements,
            quality_score=score
        )
    
    def _add_basic_assertions(self, content: str) -> str:
        """添加基本断言"""
        if "assert" not in content.lower():
            return content + "\n    assert result is not None"
        return content
    
    def _improve_comments(self, content: str) -> str:
        """改善注释"""
        return content


class TestCaseOrchestrator:
    """用例集合编排器"""
    
    def __init__(self):
        self.plans: Dict[str, TestCaseExecutionPlan] = {}
    
    def create_execution_plan(
        self,
        context: TaskContext,
        config: ConfigSnapshot,
        optimized_cases: Dict[str, OptimizedTestCase],
        dependency_graph: Optional[Dict[str, List[str]]] = None
    ) -> TestCaseExecutionPlan:
        """创建执行计划"""
        plan_id = f"PLAN-{context.task_id}"
        
        execution_order = list(optimized_cases.keys())
        execution_order.sort(key=lambda x: optimized_cases[x].quality_score.overall_score, reverse=True)
        
        modules = self._group_by_module(optimized_cases)
        priority_groups = self._group_by_priority(optimized_cases)
        estimated_time = self._estimate_total_time(optimized_cases)
        
        plan = TestCaseExecutionPlan(
            plan_id=plan_id,
            execution_order=execution_order,
            modules=modules,
            priority_groups=priority_groups,
            estimated_total_time=estimated_time
        )
        
        self.plans[plan_id] = plan
        return plan
    
    def _group_by_module(self, cases: Dict[str, OptimizedTestCase]) -> Dict[str, List[str]]:
        """按模块分组"""
        modules = {}
        
        for case_id, case in cases.items():
            module = case_id.split('_')[0] if '_' in case_id else "default"
            if module not in modules:
                modules[module] = []
            modules[module].append(case_id)
        
        return modules
    
    def _group_by_priority(self, cases: Dict[str, OptimizedTestCase]) -> Dict[int, List[str]]:
        """按优先级分组"""
        groups = {1: [], 2: [], 3: [], 4: [], 5: []}
        
        for case_id, case in cases.items():
            score = case.quality_score.overall_score
            if score >= 0.9:
                groups[1].append(case_id)
            elif score >= 0.75:
                groups[2].append(case_id)
            elif score >= 0.5:
                groups[3].append(case_id)
            elif score >= 0.25:
                groups[4].append(case_id)
            else:
                groups[5].append(case_id)
        
        return groups
    
    def _estimate_total_time(self, cases: Dict[str, OptimizedTestCase]) -> float:
        """估算总执行时间"""
        return len(cases) * 0.5
    
    def get_plan(self, plan_id: str) -> Optional[TestCaseExecutionPlan]:
        """获取执行计划"""
        return self.plans.get(plan_id)
