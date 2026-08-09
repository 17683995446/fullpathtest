"""
第18层：轻量AST构建层

基于Token流构建最小可用抽象语法树。
"""

from typing import List, Optional, Dict, Any
from fullpathtest.types.core import ASTNode, LightAST, TokenStream, Token, LanguageType


class ASTBuilder:
    """AST构建器"""
    
    def __init__(self, language: LanguageType = LanguageType.PYTHON):
        self.language = language
    
    def build(self, token_stream: TokenStream) -> LightAST:
        """构建AST"""
        tokens = token_stream.tokens
        
        root = ASTNode(node_type='ROOT', line=0, column=0)
        
        current_node = root
        node_stack = [root]
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token.type == 'KEYWORD':
                if token.value in ['def', 'function', 'func']:
                    func_node = self._parse_function(tokens, i, token_stream.file_path)
                    current_node.children.append(func_node)
                    i = self._skip_to_end_of_function(tokens, i)
                    continue
                
                elif token.value in ['class', 'struct']:
                    class_node = self._parse_class(tokens, i, token_stream.file_path)
                    current_node.children.append(class_node)
                    i = self._skip_to_matching_brace(tokens, i)
                    continue
                
                elif token.value in ['if', 'elif', 'else']:
                    if_node = self._parse_if_statement(tokens, i)
                    current_node.children.append(if_node)
                    i += 1
                    continue
                
                elif token.value in ['for', 'while']:
                    loop_node = self._parse_loop_statement(tokens, i)
                    current_node.children.append(loop_node)
                    i += 1
                    continue
                
                elif token.value == 'return':
                    return_node = ASTNode(
                        node_type='RETURN',
                        value=token.value,
                        line=token.line,
                        column=token.column
                    )
                    current_node.children.append(return_node)
                    i += 1
                    continue
            
            i += 1
        
        ast = LightAST(
            file_path=token_stream.file_path,
            root=root,
            nodes=self._flatten_ast(root),
            functions=self._extract_functions(root),
            imports=self._extract_imports(tokens)
        )
        
        return ast
    
    def _parse_function(self, tokens: List[Token], start: int, file_path: str) -> ASTNode:
        """解析函数定义"""
        func_node = ASTNode(
            node_type='FUNCTION',
            line=tokens[start].line if start < len(tokens) else 0,
            column=tokens[start].column if start < len(tokens) else 0,
            children=[]
        )
        
        i = start + 1
        while i < len(tokens) and tokens[i].type != 'OPERATOR':
            i += 1
        
        if i < len(tokens):
            func_node.attributes['name'] = tokens[i].value
        
        brace_count = 0
        func_node.children.append(tokens[start])
        
        for j in range(start, len(tokens)):
            if tokens[j].value == '{':
                brace_count += 1
            elif tokens[j].value == '}':
                brace_count -= 1
                if brace_count == 0:
                    break
            func_node.children.append(tokens[j])
        
        return func_node
    
    def _parse_class(self, tokens: List[Token], start: int, file_path: str) -> ASTNode:
        """解析类定义"""
        class_node = ASTNode(
            node_type='CLASS',
            line=tokens[start].line if start < len(tokens) else 0,
            column=tokens[start].column if start < len(tokens) else 0,
            children=[]
        )
        
        i = start + 1
        while i < len(tokens) and tokens[i].type != 'IDENTIFIER':
            i += 1
        
        if i < len(tokens):
            class_node.attributes['name'] = tokens[i].value
        
        return class_node
    
    def _parse_if_statement(self, tokens: List[Token], start: int) -> ASTNode:
        """解析if语句"""
        if_node = ASTNode(
            node_type='IF',
            line=tokens[start].line,
            column=tokens[start].column,
            children=[]
        )
        
        brace_count = 0
        for i in range(start, len(tokens)):
            if tokens[i].value == '{':
                brace_count += 1
            elif tokens[i].value == '}':
                brace_count -= 1
                if brace_count == 0:
                    break
            if_node.children.append(tokens[i])
        
        return if_node
    
    def _parse_loop_statement(self, tokens: List[Token], start: int) -> ASTNode:
        """解析循环语句"""
        loop_node = ASTNode(
            node_type='LOOP',
            line=tokens[start].line,
            column=tokens[start].column,
            children=[]
        )
        
        brace_count = 0
        for i in range(start, len(tokens)):
            if tokens[i].value == '{':
                brace_count += 1
            elif tokens[i].value == '}':
                brace_count -= 1
                if brace_count == 0:
                    break
            loop_node.children.append(tokens[i])
        
        return loop_node
    
    def _skip_to_end_of_function(self, tokens: List[Token], start: int) -> int:
        """跳到函数结束"""
        brace_count = 0
        for i in range(start, len(tokens)):
            if tokens[i].value == '{':
                brace_count += 1
            elif tokens[i].value == '}':
                brace_count -= 1
                if brace_count == 0:
                    return i + 1
        return len(tokens)
    
    def _skip_to_matching_brace(self, tokens: List[Token], start: int) -> int:
        """跳到匹配的右括号"""
        brace_count = 0
        for i in range(start, len(tokens)):
            if tokens[i].value == '{':
                brace_count += 1
            elif tokens[i].value == '}':
                brace_count -= 1
                if brace_count == 0:
                    return i + 1
        return len(tokens)
    
    def _flatten_ast(self, node: ASTNode) -> List[ASTNode]:
        """扁平化AST"""
        nodes = [node]
        for child in node.children:
            if isinstance(child, ASTNode):
                nodes.extend(self._flatten_ast(child))
        return nodes
    
    def _extract_functions(self, root: ASTNode) -> List[ASTNode]:
        """提取函数节点"""
        functions = []
        for node in self._flatten_ast(root):
            if node.node_type == 'FUNCTION':
                functions.append(node)
        return functions
    
    def _extract_imports(self, tokens: List[Token]) -> List[str]:
        """提取导入语句"""
        imports = []
        i = 0
        while i < len(tokens):
            if tokens[i].type == 'KEYWORD' and tokens[i].value in ['import', 'from', 'require', 'include']:
                import_tokens = []
                j = i
                while j < len(tokens) and tokens[j].value != '\n' and tokens[j].value != ';':
                    import_tokens.append(tokens[j].value)
                    j += 1
                if import_tokens:
                    imports.append(' '.join(import_tokens))
                i = j
            else:
                i += 1
        return imports
