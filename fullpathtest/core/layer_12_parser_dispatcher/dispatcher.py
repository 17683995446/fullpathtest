"""
第12层：多语言适配分发层

自动识别编程语言并分发至对应解析器。
"""

from typing import Dict, Type, Optional
from fullpathtest.types.core import LanguageType
from fullpathtest.core.layer_17_lexer.lexer import Lexer
from fullpathtest.core.layer_18_ast.ast_builder import ASTBuilder


class LanguageDetector:
    """编程语言检测器"""
    
    EXTENSION_MAP = {
        '.py': LanguageType.PYTHON,
        '.pyw': LanguageType.PYTHON,
        '.java': LanguageType.JAVA,
        '.go': LanguageType.GOLANG,
        '.rs': LanguageType.RUST,
        '.ts': LanguageType.TYPESCRIPT,
        '.tsx': LanguageType.TYPESCRIPT,
        '.js': LanguageType.JAVASCRIPT,
        '.jsx': LanguageType.JAVASCRIPT,
        '.cs': LanguageType.CSHARP,
        '.cpp': LanguageType.CPP,
        '.cc': LanguageType.CPP,
        '.c': LanguageType.C,
        '.h': LanguageType.C,
        '.hpp': LanguageType.CPP,
    }
    
    SHEBANG_MAP = {
        '#!/usr/bin/env python': LanguageType.PYTHON,
        '#!/usr/bin/python': LanguageType.PYTHON,
        '#!/bin/bash': LanguageType.C,
    }
    
    @classmethod
    def detect_from_extension(cls, file_path: str) -> LanguageType:
        """从扩展名检测"""
        import os
        ext = os.path.splitext(file_path)[1].lower()
        return cls.EXTENSION_MAP.get(ext, LanguageType.UNKNOWN)
    
    @classmethod
    def detect_from_content(cls, content: str) -> LanguageType:
        """从内容检测"""
        if not content:
            return LanguageType.UNKNOWN
        
        lines = content.split('\n')[:5]
        
        for line in lines:
            if line.startswith('#!'):
                for pattern, lang in cls.SHEBANG_MAP.items():
                    if pattern in line:
                        return lang
        
        if 'import java.util' in content or 'public class ' in content:
            return LanguageType.JAVA
        if 'package main' in content or 'func main' in content:
            return LanguageType.GOLANG
        if 'fn main' in content or 'use std::' in content:
            return LanguageType.RUST
        if 'function' in content and ('const ' in content or 'let ' in content):
            return LanguageType.JAVASCRIPT
        if ': ' in content and ('def ' in content or 'import ' in content):
            return LanguageType.PYTHON
        
        return LanguageType.UNKNOWN


class LanguageParserDispatcher:
    """语言解析器分发器"""
    
    def __init__(self):
        self._lexers: Dict[LanguageType, Type[Lexer]] = {
            LanguageType.PYTHON: Lexer,
            LanguageType.JAVA: Lexer,
            LanguageType.JAVASCRIPT: Lexer,
            LanguageType.TYPESCRIPT: Lexer,
            LanguageType.GOLANG: Lexer,
            LanguageType.RUST: Lexer,
            LanguageType.CSHARP: Lexer,
        }
        
        self._builders: Dict[LanguageType, Type[ASTBuilder]] = {
            LanguageType.PYTHON: ASTBuilder,
            LanguageType.JAVA: ASTBuilder,
            LanguageType.JAVASCRIPT: ASTBuilder,
            LanguageType.TYPESCRIPT: ASTBuilder,
            LanguageType.GOLANG: ASTBuilder,
            LanguageType.RUST: ASTBuilder,
            LanguageType.CSHARP: ASTBuilder,
        }
    
    def get_lexer(self, language: LanguageType) -> Optional[Lexer]:
        """获取词法分析器"""
        lexer_class = self._lexers.get(language)
        if lexer_class:
            return lexer_class(language)
        return None
    
    def get_ast_builder(self, language: LanguageType) -> Optional[ASTBuilder]:
        """获取AST构建器"""
        builder_class = self._builders.get(language)
        if builder_class:
            return builder_class(language)
        return None
    
    def dispatch(self, file_path: str, content: str) -> Dict[str, any]:
        """分发解析任务"""
        language = LanguageDetector.detect_from_extension(file_path)
        if language == LanguageType.UNKNOWN:
            language = LanguageDetector.detect_from_content(content)
        
        lexer = self.get_lexer(language)
        builder = self.get_ast_builder(language)
        
        return {
            'language': language,
            'lexer': lexer,
            'ast_builder': builder
        }


class ParserRegistry:
    """解析器注册表"""
    
    def __init__(self):
        self._parsers: Dict[LanguageType, 'ParserPlugin'] = {}
    
    def register(self, language: LanguageType, parser: 'ParserPlugin') -> None:
        """注册解析器"""
        self._parsers[language] = parser
    
    def get(self, language: LanguageType) -> Optional['ParserPlugin']:
        """获取解析器"""
        return self._parsers.get(language)
    
    def list_supported(self) -> list:
        """列出支持的解析器"""
        return list(self._parsers.keys())


class ParserPlugin:
    """解析器插件接口"""
    
    def parse(self, content: str) -> any:
        """解析内容"""
        raise NotImplementedError
    
    def get_language(self) -> LanguageType:
        """获取语言类型"""
        raise NotImplementedError
