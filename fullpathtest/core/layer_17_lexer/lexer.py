"""
第17层：词法分析Token化层

将标准化代码文本转换为结构化Token序列。
"""

from typing import List, Optional, Dict, Tuple
from fullpathtest.types.core import Token, TokenStream, LanguageType
import re


class Lexer:
    """词法分析器"""
    
    TOKEN_PATTERNS = {
        'python': [
            ('KEYWORD', r'\b(and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield|True|False|None)\b'),
            ('IDENTIFIER', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
            ('NUMBER', r'\b\d+\.?\d*\b'),
            ('STRING', r'(?:"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')'),
            ('OPERATOR', r'[+\-*/%=<>!&|^~@:,.\[\](){}]'),
            ('NEWLINE', r'\n'),
            ('WHITESPACE', r'[ \t]+'),
            ('COMMENT', r'#.*$'),
        ],
        'java': [
            ('KEYWORD', r'\b(abstract|assert|boolean|break|byte|case|catch|char|class|const|continue|default|do|double|else|enum|extends|final|finally|float|for|goto|if|implements|import|instanceof|int|interface|long|native|new|package|private|protected|public|return|short|static|strictfp|super|switch|synchronized|this|throw|throws|transient|try|void|volatile|while|true|false|null)\b'),
            ('IDENTIFIER', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
            ('NUMBER', r'\b\d+\.?\d*[fFdDlL]?\b'),
            ('STRING', r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\''),
            ('OPERATOR', r'[+\-*/%=<>!&|^~?:,.\[\](){};]'),
            ('NEWLINE', r'\n'),
            ('WHITESPACE', r'[ \t]+'),
            ('COMMENT', r'//.*$|/\*[\s\S]*?\*/'),
        ],
        'default': [
            ('KEYWORD', r'\b(if|else|for|while|return|function|class|import|export|const|let|var|true|false|null|void)\b'),
            ('IDENTIFIER', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
            ('NUMBER', r'\b\d+\.?\d*\b'),
            ('STRING', r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\''),
            ('OPERATOR', r'[+\-*/%=<>!&|^~@:,.\[\](){};]'),
            ('NEWLINE', r'\n'),
            ('WHITESPACE', r'[ \t]+'),
        ]
    }
    
    def __init__(self, language: LanguageType = LanguageType.PYTHON):
        self.language = language
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """编译词法模式"""
        lang_name = self.language.name.lower() if self.language != LanguageType.UNKNOWN else 'python'
        patterns = self.TOKEN_PATTERNS.get(lang_name, self.TOKEN_PATTERNS['default'])
        
        pattern_str = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in patterns)
        self._regex = re.compile(pattern_str)
    
    def tokenize(self, code: str, file_path: str) -> TokenStream:
        """词法分析"""
        tokens = []
        line = 1
        column = 1
        error_count = 0
        
        pos = 0
        while pos < len(code):
            match = self._regex.match(code, pos)
            
            if not match:
                pos += 1
                column += 1
                error_count += 1
                continue
            
            token_type = match.lastgroup
            value = match.group(token_type)
            
            if token_type == 'WHITESPACE':
                column += len(value)
                pos = match.end()
                continue
            
            if token_type == 'NEWLINE':
                line += 1
                column = 1
                pos = match.end()
                continue
            
            if token_type == 'COMMENT':
                pos = match.end()
                continue
            
            token = Token(
                type=token_type,
                value=value,
                line=line,
                column=column,
                length=len(value)
            )
            tokens.append(token)
            
            column += len(value)
            pos = match.end()
        
        return TokenStream(
            file_path=file_path,
            tokens=tokens,
            token_count=len(tokens),
            error_count=error_count
        )
    
    def tokenize_simple(self, code: str) -> List[Dict]:
        """简单词法分析"""
        tokens = []
        pos = 0
        line = 1
        
        while pos < len(code):
            if code[pos] in ' \t':
                pos += 1
                continue
            if code[pos] == '\n':
                line += 1
                pos += 1
                continue
            
            if code[pos].isalpha() or code[pos] == '_':
                start = pos
                while pos < len(code) and (code[pos].isalnum() or code[pos] == '_'):
                    pos += 1
                tokens.append({'type': 'IDENTIFIER', 'value': code[start:pos], 'line': line})
            
            elif code[pos].isdigit():
                start = pos
                while pos < len(code) and (code[pos].isdigit() or code[pos] == '.'):
                    pos += 1
                tokens.append({'type': 'NUMBER', 'value': code[start:pos], 'line': line})
            
            elif code[pos] in '+-*/%=<>!&|^~@:,().[]{};':
                tokens.append({'type': 'OPERATOR', 'value': code[pos], 'line': line})
                pos += 1
            
            elif code[pos] in '"\'':
                quote = code[pos]
                start = pos
                pos += 1
                while pos < len(code) and code[pos] != quote:
                    if code[pos] == '\\':
                        pos += 2
                    else:
                        pos += 1
                pos += 1
                tokens.append({'type': 'STRING', 'value': code[start:pos], 'line': line})
            
            else:
                pos += 1
        
        return tokens
