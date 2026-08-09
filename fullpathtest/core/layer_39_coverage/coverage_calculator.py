"""
第39层：覆盖计算层

计算代码覆盖率统计。
"""

from typing import Dict, List, Any
from fullpathtest.types.core import CoverageReport, ExecutionResult, CoverageLevel
from collections import defaultdict


class CoverageCalculator:
    """覆盖率计算器"""
    
    def __init__(self):
        self.covered_statements = set()
        self.total_statements = 0
        self.covered_branches = set()
        self.total_branches = 0
        self.covered_paths = set()
        self.total_paths = 0
    
    def calculate(self, results: List[ExecutionResult]) -> CoverageReport:
        """计算覆盖率"""
        report = CoverageReport()
        
        for result in results:
            if result.status.value >= 0:
                self._process_coverage_data(result.coverage_data)
        
        report.total_statements = self.total_statements
        report.covered_statements = len(self.covered_statements)
        report.statement_coverage = self._calculate_percentage(
            report.covered_statements,
            report.total_statements
        )
        
        report.total_branches = self.total_branches
        report.covered_branches = len(self.covered_branches)
        report.branch_coverage = self._calculate_percentage(
            report.covered_branches,
            report.total_branches
        )
        
        report.total_paths = self.total_paths
        report.covered_paths = len(self.covered_paths)
        report.path_coverage = self._calculate_percentage(
            report.covered_paths,
            report.total_paths
        )
        
        report.uncovered_items = self._get_uncovered_items()
        
        return report
    
    def _process_coverage_data(self, coverage_data: Dict[str, Any]) -> None:
        """处理覆盖率数据"""
        if 'statements' in coverage_data:
            for stmt in coverage_data['statements']:
                self.covered_statements.add(stmt)
                self.total_statements += 1
        
        if 'branches' in coverage_data:
            for branch in coverage_data['branches']:
                self.covered_branches.add(branch)
                self.total_branches += 1
        
        if 'paths' in coverage_data:
            for path in coverage_data['paths']:
                self.covered_paths.add(path)
                self.total_paths += 1
    
    def _calculate_percentage(self, covered: int, total: int) -> float:
        """计算百分比"""
        if total == 0:
            return 0.0
        return round((covered / total) * 100, 2)
    
    def _get_uncovered_items(self) -> List[str]:
        """获取未覆盖项"""
        uncovered = []
        uncovered.extend([f"stmt_{i}" for i in range(self.total_statements) 
                         if i not in self.covered_statements])
        return uncovered[:100]
    
    def calculate_by_module(self, results: List[ExecutionResult]) -> Dict[str, CoverageReport]:
        """按模块计算覆盖率"""
        module_reports = defaultdict(lambda: CoverageCalculator())
        
        for result in results:
            module = result.case_id.split('_')[0] if result.case_id else 'unknown'
            if 'statements' in result.coverage_data:
                module_reports[module]._process_coverage_data(result.coverage_data)
        
        return {module: calc.calculate([]) for module, calc in module_reports.items()}


class LineCoverageAnalyzer:
    """行覆盖率分析器"""
    
    def __init__(self):
        self.line_hits = defaultdict(int)
        self.total_lines = 0
    
    def analyze(self, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析行覆盖率"""
        result = {
            'covered_lines': [],
            'uncovered_lines': [],
            'coverage_percentage': 0.0
        }
        
        if 'lines' in coverage_data:
            for line_info in coverage_data['lines']:
                line_num = line_info.get('line')
                hit_count = line_info.get('hits', 0)
                
                if hit_count > 0:
                    result['covered_lines'].append(line_num)
                    self.line_hits[line_num] = max(self.line_hits[line_num], hit_count)
                else:
                    result['uncovered_lines'].append(line_num)
        
        result['coverage_percentage'] = self._calculate_coverage(result)
        
        return result
    
    def _calculate_coverage(self, result: Dict[str, Any]) -> float:
        """计算覆盖率"""
        covered = len(result['covered_lines'])
        total = covered + len(result['uncovered_lines'])
        if total == 0:
            return 0.0
        return round((covered / total) * 100, 2)


class BranchCoverageAnalyzer:
    """分支覆盖率分析器"""
    
    def analyze(self, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析分支覆盖率"""
        result = {
            'total_branches': 0,
            'covered_branches': 0,
            'branch_pairs': [],
            'coverage_percentage': 0.0
        }
        
        if 'branches' in coverage_data:
            for branch_info in coverage_data['branches']:
                result['total_branches'] += 1
                if branch_info.get('hits', 0) > 0:
                    result['covered_branches'] += 1
                    result['branch_pairs'].append({
                        'line': branch_info.get('line'),
                        'branch_id': branch_info.get('id'),
                        'covered': True
                    })
        
        if result['total_branches'] > 0:
            result['coverage_percentage'] = round(
                (result['covered_branches'] / result['total_branches']) * 100, 2
            )
        
        return result
