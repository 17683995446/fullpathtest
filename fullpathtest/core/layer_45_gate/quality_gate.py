"""
第45层：质量门禁层

执行准入检查。
"""

from typing import Dict, Any, List, Optional
from fullpathtest.types.core import CoverageReport, DefectInfo


class QualityGate:
    """质量门禁"""
    
    def __init__(self):
        self.thresholds = {
            'min_pass_rate': 80.0,
            'min_coverage': 70.0,
            'max_critical_defects': 0,
            'max_high_defects': 5
        }
    
    def check(
        self,
        pass_rate: float,
        coverage: CoverageReport,
        defects: List[DefectInfo]
    ) -> 'GateResult':
        """执行门禁检查"""
        checks = []
        
        checks.append(self._check_pass_rate(pass_rate))
        checks.append(self._check_statement_coverage(coverage.statement_coverage))
        checks.append(self._check_branch_coverage(coverage.branch_coverage))
        checks.append(self._check_defects(defects))
        
        passed = all(check['passed'] for check in checks)
        
        return GateResult(
            passed=passed,
            checks=checks,
            summary=self._generate_summary(checks)
        )
    
    def _check_pass_rate(self, pass_rate: float) -> Dict[str, Any]:
        """检查通过率"""
        passed = pass_rate >= self.thresholds['min_pass_rate']
        return {
            'name': '通过率检查',
            'passed': passed,
            'actual': pass_rate,
            'threshold': self.thresholds['min_pass_rate'],
            'message': f"通过率 {pass_rate:.1f}% {'≥' if passed else '<'} {self.thresholds['min_pass_rate']:.1f}%"
        }
    
    def _check_statement_coverage(self, coverage: float) -> Dict[str, Any]:
        """检查语句覆盖率"""
        passed = coverage >= self.thresholds['min_coverage']
        return {
            'name': '语句覆盖率检查',
            'passed': passed,
            'actual': coverage,
            'threshold': self.thresholds['min_coverage'],
            'message': f"语句覆盖率 {coverage:.1f}% {'≥' if passed else '<'} {self.thresholds['min_coverage']:.1f}%"
        }
    
    def _check_branch_coverage(self, coverage: float) -> Dict[str, Any]:
        """检查分支覆盖率"""
        min_branch = 50.0
        passed = coverage >= min_branch
        return {
            'name': '分支覆盖率检查',
            'passed': passed,
            'actual': coverage,
            'threshold': min_branch,
            'message': f"分支覆盖率 {coverage:.1f}% {'≥' if passed else '<'} {min_branch:.1f}%"
        }
    
    def _check_defects(self, defects: List[DefectInfo]) -> Dict[str, Any]:
        """检查缺陷"""
        critical = sum(1 for d in defects if d.severity.name == 'CRITICAL')
        high = sum(1 for d in defects if d.severity.name == 'HIGH')
        
        passed = (
            critical <= self.thresholds['max_critical_defects'] and
            high <= self.thresholds['max_high_defects']
        )
        
        return {
            'name': '缺陷检查',
            'passed': passed,
            'actual': {'critical': critical, 'high': high},
            'threshold': self.thresholds,
            'message': f"关键缺陷 {critical}, 高优先级缺陷 {high}"
        }
    
    def _generate_summary(self, checks: List[Dict[str, Any]]) -> str:
        """生成摘要"""
        passed_count = sum(1 for c in checks if c['passed'])
        total_count = len(checks)
        
        if passed_count == total_count:
            return f"质量门禁通过 ({passed_count}/{total_count})"
        else:
            failed = [c['name'] for c in checks if not c['passed']]
            return f"质量门禁未通过 ({passed_count}/{total_count}): {', '.join(failed)}"


class GateResult:
    """门禁结果"""
    
    def __init__(self, passed: bool, checks: List[Dict[str, Any]], summary: str):
        self.passed = passed
        self.checks = checks
        self.summary = summary


class QualityGateManager:
    """质量门禁管理器"""
    
    def __init__(self):
        self.gates: Dict[str, QualityGate] = {
            'default': QualityGate(),
            'critical': self._create_critical_gate(),
            'fast': self._create_fast_gate()
        }
    
    def _create_critical_gate(self) -> QualityGate:
        """创建关键级门禁"""
        gate = QualityGate()
        gate.thresholds = {
            'min_pass_rate': 95.0,
            'min_coverage': 90.0,
            'max_critical_defects': 0,
            'max_high_defects': 0
        }
        return gate
    
    def _create_fast_gate(self) -> QualityGate:
        """创建快速门禁"""
        gate = QualityGate()
        gate.thresholds = {
            'min_pass_rate': 70.0,
            'min_coverage': 50.0,
            'max_critical_defects': 0,
            'max_high_defects': 10
        }
        return gate
    
    def execute_gate(
        self,
        gate_name: str,
        pass_rate: float,
        coverage: CoverageReport,
        defects: List[DefectInfo]
    ) -> GateResult:
        """执行指定门禁"""
        gate = self.gates.get(gate_name, self.gates['default'])
        return gate.check(pass_rate, coverage, defects)
    
    def register_gate(self, name: str, gate: QualityGate) -> None:
        """注册新门禁"""
        self.gates[name] = gate
