"""
第15层：敏感代码识别层

识别代码中硬编码密钥、证书、隐私数据处理逻辑等敏感代码。
"""

from typing import List, Dict, Optional
from fullpathtest.types.core import SensitiveCodeLocation, RiskLevel, StandardizedCode
import re


class SensitiveCodeDetector:
    """敏感代码检测器"""
    
    SENSITIVE_PATTERNS = {
        'api_key': {
            'patterns': [
                r'api[_\s]?key["\']?\s*[:=]\s*["\'][a-zA-Z0-9]{20,}["\']',
                r'api[_\s]?secret["\']?\s*[:=]\s*["\'][a-zA-Z0-9]{20,}["\']',
                r'api[_\s]?token["\']?\s*[:=]\s*["\'][a-zA-Z0-9]{20,}["\']',
            ],
            'severity': RiskLevel.CRITICAL
        },
        'password': {
            'patterns': [
                r'password["\']?\s*[:=]\s*["\'][^"\']{6,}["\']',
                r'pwd["\']?\s*[:=]\s*["\'][^"\']{6,}["\']',
                r'passwd["\']?\s*[:=]\s*["\'][^"\']{6,}["\']',
            ],
            'severity': RiskLevel.CRITICAL
        },
        'private_key': {
            'patterns': [
                r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
                r'private[_\s]?key["\']?\s*[:=]\s*["\'][^"\']{50,}["\']',
            ],
            'severity': RiskLevel.CRITICAL
        },
        'database_credentials': {
            'patterns': [
                r'(db|database)[_\s]?(host|server)["\']?\s*[:=]\s*["\'][^"\']+["\']',
                r'(db|database)[_\s]?(user|username)["\']?\s*[:=]\s*["\'][^"\']+["\']',
                r'(db|database)?[_\s]?password["\']?\s*[:=]\s*["\'][^"\']{6,}["\']',
            ],
            'severity': RiskLevel.HIGH
        },
        'email': {
            'patterns': [
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            ],
            'severity': RiskLevel.MEDIUM
        },
        'phone': {
            'patterns': [
                r'1[3-9]\d{9}',
                r'\d{3}-\d{4}-\d{4}',
            ],
            'severity': RiskLevel.MEDIUM
        },
        'credit_card': {
            'patterns': [
                r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}',
            ],
            'severity': RiskLevel.CRITICAL
        },
        'ssn': {
            'patterns': [
                r'\d{3}-\d{2}-\d{4}',
                r'\d{9}',
            ],
            'severity': RiskLevel.CRITICAL
        }
    }
    
    def __init__(self):
        self.sensitive_locations: List[SensitiveCodeLocation] = []
    
    def detect(self, code: StandardizedCode, skip_sensitive: bool = True) -> List[SensitiveCodeLocation]:
        """检测敏感代码"""
        self.sensitive_locations = []
        
        if not skip_sensitive:
            return self.sensitive_locations
        
        for i, line in enumerate(code.lines, 1):
            self._scan_line(code.file_path, line, i)
        
        return self.sensitive_locations
    
    def _scan_line(self, file_path: str, line: str, line_num: int) -> None:
        """扫描单行代码"""
        for sensitive_type, config in self.SENSITIVE_PATTERNS.items():
            patterns = config['patterns']
            severity = config['severity']
            
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.sensitive_locations.append(SensitiveCodeLocation(
                        file_path=file_path,
                        line_start=line_num,
                        line_end=line_num,
                        sensitivity_type=sensitive_type,
                        risk_level=severity,
                        description=f"发现敏感信息: {sensitive_type}"
                    ))
                    break
    
    def get_statistics(self) -> Dict[str, int]:
        """获取统计信息"""
        stats = {}
        for location in self.sensitive_locations:
            sens_type = location.sensitivity_type
            stats[sens_type] = stats.get(sens_type, 0) + 1
        return stats
