"""
第29层：路径优先级排序层

根据业务重要性、风险评分、覆盖缺口对路径进行全局优先级排序。
"""

from typing import List, Dict, Any
from fullpathtest.types.core import Path, PathSet, TestRiskScore, CoverageReport, RiskLevel


class PathPrioritySorter:
    """路径优先级排序器"""
    
    def __init__(self):
        self.priority_weights = {
            'business_importance': 0.3,
            'risk_score': 0.3,
            'coverage_gap': 0.2,
            'change_frequency': 0.1,
            'defect_history': 0.1
        }
    
    def sort(
        self,
        path_set: PathSet,
        risk_scores: List[TestRiskScore],
        coverage: CoverageReport
    ) -> List[Path]:
        """对路径进行优先级排序"""
        scored_paths = []
        
        for path in path_set.paths:
            score = self._calculate_priority_score(path, risk_scores, coverage)
            scored_paths.append((score, path))
        
        scored_paths.sort(key=lambda x: x[0], reverse=True)
        
        sorted_paths = [path for _, path in scored_paths]
        
        for i, path in enumerate(sorted_paths):
            path.priority = len(sorted_paths) - i
        
        return sorted_paths
    
    def _calculate_priority_score(
        self,
        path: Path,
        risk_scores: List[TestRiskScore],
        coverage: CoverageReport
    ) -> float:
        """计算优先级分数"""
        business_score = self._calculate_business_score(path)
        risk_score = self._calculate_risk_score(path, risk_scores)
        coverage_score = self._calculate_coverage_score(path, coverage)
        change_score = self._calculate_change_score(path)
        defect_score = self._calculate_defect_score(path)
        
        total_score = (
            business_score * self.priority_weights['business_importance'] +
            risk_score * self.priority_weights['risk_score'] +
            coverage_score * self.priority_weights['coverage_gap'] +
            change_score * self.priority_weights['change_frequency'] +
            defect_score * self.priority_weights['defect_history']
        )
        
        return total_score
    
    def _calculate_business_score(self, path: Path) -> float:
        """计算业务重要性分数"""
        score = 0.5
        
        if path.path_type.name in ['E2E', 'CROSS_SERVICE']:
            score += 0.3
        
        if len(path.business_scenarios) > 0:
            score += 0.2
        
        return min(1.0, score)
    
    def _calculate_risk_score(self, path: Path, risk_scores: List[TestRiskScore]) -> float:
        """计算风险分数"""
        path_risk = RiskLevel.MEDIUM
        
        for node in path.node_sequence:
            for risk in risk_scores:
                if node in risk.file_path:
                    path_risk = risk.risk_level
                    break
        
        risk_map = {
            RiskLevel.CRITICAL: 1.0,
            RiskLevel.HIGH: 0.8,
            RiskLevel.MEDIUM: 0.5,
            RiskLevel.LOW: 0.3,
            RiskLevel.MINIMAL: 0.1
        }
        
        return risk_map.get(path_risk, 0.5)
    
    def _calculate_coverage_score(self, path: Path, coverage: CoverageReport) -> float:
        """计算覆盖缺口分数"""
        if coverage.total_paths == 0:
            return 0.5
        
        coverage_rate = coverage.covered_paths / coverage.total_paths
        
        return 1.0 - coverage_rate
    
    def _calculate_change_score(self, path: Path) -> float:
        """计算变更频率分数"""
        return 0.5
    
    def _calculate_defect_score(self, path: Path) -> float:
        """计算缺陷历史分数"""
        return 0.3


class AdaptivePrioritySorter(PathPrioritySorter):
    """自适应优先级排序器"""
    
    def __init__(self):
        super().__init__()
        self.adjustment_factors = {}
    
    def adjust_weights(self, historical_data: Dict[str, float]) -> None:
        """根据历史数据调整权重"""
        if 'high_defect_paths' in historical_data:
            self.priority_weights['defect_history'] = min(0.2, historical_data['high_defect_paths'] * 0.1)
        
        if 'critical_business_paths' in historical_data:
            self.priority_weights['business_importance'] = min(0.4, historical_data['critical_business_paths'] * 0.1)
    
    def recalculate(self, path_set: PathSet, context: Dict[str, Any]) -> List[Path]:
        """重新计算优先级"""
        if 'historical_performance' in context:
            self.adjust_weights(context['historical_performance'])
        
        risk_scores = context.get('risk_scores', [])
        coverage = context.get('coverage', None)
        
        return self.sort(path_set, risk_scores, coverage)
