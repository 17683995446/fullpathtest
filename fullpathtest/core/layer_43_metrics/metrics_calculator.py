"""
第43层：指标计算层

计算质量指标。
"""

from typing import Dict, Any, List
from fullpathtest.types.core import ExecutionResult, CoverageReport, DefectInfo
from collections import defaultdict


class MetricsCalculator:
    """指标计算器"""
    
    def calculate(self, results: List[ExecutionResult], coverage: CoverageReport) -> Dict[str, float]:
        """计算质量指标"""
        metrics = {}
        
        metrics['pass_rate'] = self._calculate_pass_rate(results)
        metrics['fail_rate'] = self._calculate_fail_rate(results)
        metrics['error_rate'] = self._calculate_error_rate(results)
        
        metrics['statement_coverage'] = coverage.statement_coverage
        metrics['branch_coverage'] = coverage.branch_coverage
        metrics['path_coverage'] = coverage.path_coverage
        
        metrics['avg_execution_time'] = self._calculate_avg_time(results)
        metrics['total_execution_time'] = self._calculate_total_time(results)
        
        metrics['quality_score'] = self._calculate_quality_score(metrics)
        
        return metrics
    
    def _calculate_pass_rate(self, results: List[ExecutionResult]) -> float:
        """计算通过率"""
        if not results:
            return 0.0
        passed = sum(1 for r in results if r.status.name == 'PASSED')
        return round(passed / len(results) * 100, 2)
    
    def _calculate_fail_rate(self, results: List[ExecutionResult]) -> float:
        """计算失败率"""
        if not results:
            return 0.0
        failed = sum(1 for r in results if r.status.name == 'FAILED')
        return round(failed / len(results) * 100, 2)
    
    def _calculate_error_rate(self, results: List[ExecutionResult]) -> float:
        """计算错误率"""
        if not results:
            return 0.0
        errors = sum(1 for r in results if r.status.name == 'ERROR')
        return round(errors / len(results) * 100, 2)
    
    def _calculate_avg_time(self, results: List[ExecutionResult]) -> float:
        """计算平均执行时间"""
        if not results:
            return 0.0
        total = sum(r.duration for r in results)
        return round(total / len(results), 3)
    
    def _calculate_total_time(self, results: List[ExecutionResult]) -> float:
        """计算总执行时间"""
        return round(sum(r.duration for r in results), 2)
    
    def _calculate_quality_score(self, metrics: Dict[str, float]) -> float:
        """计算质量分数"""
        pass_weight = 0.4
        coverage_weight = 0.4
        performance_weight = 0.2
        
        pass_score = metrics['pass_rate'] / 100
        coverage_score = (
            metrics['statement_coverage'] +
            metrics['branch_coverage'] +
            metrics['path_coverage']
        ) / 300
        
        perf_score = 1.0
        if metrics['avg_execution_time'] > 10:
            perf_score = max(0, 1.0 - (metrics['avg_execution_time'] - 10) / 100)
        
        quality = (
            pass_score * pass_weight +
            coverage_score * coverage_weight +
            perf_score * performance_weight
        )
        
        return round(quality * 100, 2)


class TrendAnalyzer:
    """趋势分析器"""
    
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
    
    def add_metrics(self, metrics: Dict[str, float]) -> None:
        """添加指标记录"""
        self.history.append(metrics)
        if len(self.history) > 100:
            self.history.pop(0)
    
    def analyze_trends(self) -> Dict[str, Any]:
        """分析趋势"""
        if len(self.history) < 2:
            return {'trend': 'insufficient_data'}
        
        recent = self.history[-5:]
        
        pass_rate_trend = self._calculate_trend([m['pass_rate'] for m in recent])
        coverage_trend = self._calculate_trend([m['statement_coverage'] for m in recent])
        performance_trend = self._calculate_trend([m['avg_execution_time'] for m in recent])
        
        return {
            'pass_rate_trend': pass_rate_trend,
            'coverage_trend': coverage_trend,
            'performance_trend': performance_trend,
            'sample_count': len(recent)
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """计算趋势"""
        if len(values) < 2:
            return 'stable'
        
        first_half_avg = sum(values[:len(values)//2]) / (len(values)//2)
        second_half_avg = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        diff = second_half_avg - first_half_avg
        
        if abs(diff) < 1:
            return 'stable'
        elif diff > 0:
            return 'improving'
        else:
            return 'declining'
