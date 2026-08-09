"""
第14层：代码质量预扫描层

基于静态规则快速扫描代码坏味道、潜在缺陷、规范问题。
"""

from typing import List, Dict, Any
from fullpathtest.types.core import CodeQualityIssue, RiskLevel, StandardizedCode


class CodeQualityScanner:
    """代码质量扫描器"""
    
    ISSUE_PATTERNS = {
        'long_function': {
            'pattern': None,
            'threshold': 100,
            'severity': RiskLevel.MEDIUM
        },
        'complex_condition': {
            'pattern': None,
            'threshold': 5,
            'severity': RiskLevel.HIGH
        },
        'magic_number': {
            'pattern': r'\b\d{3,}\b',
            'severity': RiskLevel.LOW
        },
        'empty_catch': {
            'pattern': r'catch\s*\([^)]*\)\s*\{\s*\}',
            'severity': RiskLevel.MEDIUM
        },
        'unused_variable': {
            'pattern': None,
            'severity': RiskLevel.LOW
        }
    }
    
    def __init__(self):
        self.issues: List[CodeQualityIssue] = []
    
    def scan(self, code: StandardizedCode, file_path: str) -> List[CodeQualityIssue]:
        """扫描代码质量问题"""
        self.issues = []
        
        self._check_long_functions(code)
        self._check_complex_conditions(code)
        self._check_magic_numbers(code, file_path)
        self._check_empty_catch_blocks(code, file_path)
        self._check_code_duplication(code, file_path)
        
        return self.issues
    
    def _check_long_functions(self, code: StandardizedCode) -> None:
        """检查过长函数"""
        line_count = len(code.lines)
        threshold = self.ISSUE_PATTERNS['long_function']['threshold']
        
        if line_count > threshold:
            self.issues.append(CodeQualityIssue(
                file_path=code.file_path,
                line=1,
                issue_type='long_function',
                severity=RiskLevel.MEDIUM,
                message=f"函数过长 ({line_count} 行，超过 {threshold} 行阈值)",
                suggestion="考虑将函数拆分为更小的函数"
            ))
    
    def _check_complex_conditions(self, code: StandardizedCode) -> None:
        """检查复杂条件"""
        import re
        
        for i, line in enumerate(code.lines, 1):
            and_count = line.count('and')
            or_count = line.count('or')
            
            if and_count + or_count >= 5:
                self.issues.append(CodeQualityIssue(
                    file_path=code.file_path,
                    line=i,
                    issue_type='complex_condition',
                    severity=RiskLevel.HIGH,
                    message=f"条件表达式过于复杂 ({and_count} 个AND, {or_count} 个OR)",
                    suggestion="考虑将复杂条件提取为变量或函数"
                ))
    
    def _check_magic_numbers(self, code: StandardizedCode, file_path: str) -> None:
        """检查魔法数字"""
        import re
        
        for i, line in enumerate(code.lines, 1):
            matches = re.findall(r'\b\d{3,}\b', line)
            
            for match in matches:
                if not self._is_constant_definition(line):
                    self.issues.append(CodeQualityIssue(
                        file_path=file_path,
                        line=i,
                        issue_type='magic_number',
                        severity=RiskLevel.LOW,
                        message=f"发现魔法数字: {match}",
                        suggestion="使用有意义的常量替代"
                    ))
    
    def _check_empty_catch_blocks(self, code: StandardizedCode, file_path: str) -> None:
        """检查空catch块"""
        import re
        
        content = '\n'.join(code.lines)
        pattern = r'catch\s*\([^)]*\)\s*\{\s*\}'
        matches = re.finditer(pattern, content, re.MULTILINE)
        
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            self.issues.append(CodeQualityIssue(
                file_path=file_path,
                line=line_num,
                issue_type='empty_catch',
                severity=RiskLevel.MEDIUM,
                message="发现空的异常捕获块",
                suggestion="在catch块中添加日志记录或错误处理"
            ))
    
    def _check_code_duplication(self, code: StandardizedCode, file_path: str) -> None:
        """检查代码重复"""
        seen_lines: Dict[str, List[int]] = {}
        
        for i, line in enumerate(code.lines, 1):
            stripped = line.strip()
            if len(stripped) > 20 and not stripped.startswith('#'):
                if stripped in seen_lines:
                    seen_lines[stripped].append(i)
                else:
                    seen_lines[stripped] = [i]
        
        for line_content, occurrences in seen_lines.items():
            if len(occurrences) >= 3:
                self.issues.append(CodeQualityIssue(
                    file_path=file_path,
                    line=occurrences[0],
                    issue_type='code_duplication',
                    severity=RiskLevel.LOW,
                    message=f"发现重复代码 (出现 {len(occurrences)} 次)",
                    suggestion="考虑将重复代码提取为函数"
                ))
    
    def _is_constant_definition(self, line: str) -> bool:
        """判断是否为常量定义"""
        import re
        patterns = [
            r'^\s*const\s+\w+\s*=',
            r'^\s*final\s+\w+\s*=',
            r'^\s*#define\s+\w+',
            r'^\s*\w+\s*=\s*\d+'
        ]
        return any(re.search(p, line) for p in patterns)
