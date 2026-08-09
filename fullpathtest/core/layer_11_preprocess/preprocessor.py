"""
第11层：文件预处理清洗层

对原始代码文本做纯文本标准化处理。
"""

from typing import List, Optional
from fullpathtest.types.core import StandardizedCode
import re


class CodePreprocessor:
    """代码预处理器"""
    
    COMMENT_PATTERNS = {
        'python': [
            (r'#.*$', ''),
            (r'""".*?"""', '', re.DOTALL),
            (r"'''.*?'''", '', re.DOTALL),
        ],
        'java': [
            (r'//.*$', ''),
            (r'/\*.*?\*/', '', re.DOTALL),
        ],
        'javascript': [
            (r'//.*$', ''),
            (r'/\*.*?\*/', '', re.DOTALL),
        ],
        'go': [
            (r'//.*$', ''),
            (r'/\*.*?\*/', '', re.DOTALL),
        ],
        'rust': [
            (r'//.*$', ''),
            (r'/\*.*?\*/', '', re.DOTALL),
        ],
        'typescript': [
            (r'//.*$', ''),
            (r'/\*.*?\*/', '', re.DOTALL),
        ],
        'csharp': [
            (r'//.*$', ''),
            (r'/\*.*?\*/', '', re.DOTALL),
        ],
        'default': [
            (r'//.*$', ''),
            (r'/\*.*?\*/', '', re.DOTALL),
            (r'#.*$', ''),
        ]
    }
    
    def preprocess(self, content: str, file_path: str) -> StandardizedCode:
        """预处理代码"""
        lines = content.splitlines()
        original_lines = len(lines)
        original_comments = 0
        
        language = self._detect_language_from_path(file_path)
        comment_patterns = self.COMMENT_PATTERNS.get(language, self.COMMENT_PATTERNS['default'])
        
        normalized_lines = []
        for line in lines:
            stripped = line.strip()
            
            if self._is_blank_line(stripped):
                continue
            
            if self._is_comment_line(stripped, language):
                original_comments += 1
                continue
            
            normalized_lines.append(self._normalize_line(line))
        
        removed_blank_lines = original_lines - len(normalized_lines) - original_comments
        
        normalized_content = '\n'.join(normalized_lines)
        
        return StandardizedCode(
            file_path=file_path,
            content=content,
            lines=normalized_lines,
            normalized_content=normalized_content,
            removed_comments=original_comments,
            removed_blank_lines=removed_blank_lines
        )
    
    def _detect_language_from_path(self, file_path: str) -> str:
        """从路径检测语言"""
        if file_path.endswith('.py'):
            return 'python'
        elif file_path.endswith('.java'):
            return 'java'
        elif file_path.endswith('.js'):
            return 'javascript'
        elif file_path.endswith('.ts') or file_path.endswith('.tsx'):
            return 'typescript'
        elif file_path.endswith('.go'):
            return 'go'
        elif file_path.endswith('.rs'):
            return 'rust'
        elif file_path.endswith('.cs'):
            return 'csharp'
        return 'default'
    
    def _is_blank_line(self, line: str) -> bool:
        """判断是否为空行"""
        return len(line.strip()) == 0
    
    def _is_comment_line(self, line: str, language: str) -> bool:
        """判断是否为注释行"""
        if language in ['python']:
            return line.startswith('#')
        else:
            return line.startswith('//') or line.startswith('/*') or line.startswith('*')
    
    def _normalize_line(self, line: str) -> str:
        """标准化代码行"""
        line = line.rstrip()
        line = re.sub(r'\s+', ' ', line)
        return line
    
    def remove_comments(self, content: str, language: str) -> str:
        """移除注释"""
        patterns = self.COMMENT_PATTERNS.get(language, self.COMMENT_PATTERNS['default'])
        
        for pattern, replacement, *flags in patterns:
            flag = flags[0] if flags else 0
            content = re.sub(pattern, replacement, content, flags=flag)
        
        return content
