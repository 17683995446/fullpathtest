"""
第19层：函数单元切片层

将AST按函数、方法、闭包、匿名函数垂直切分，形成独立可并行处理的最小执行单元。
"""

from typing import List, Dict, Optional
from fullpathtest.types.core import FunctionSlice, LightAST, ASTNode


class FunctionSlicer:
    """函数切片器"""
    
    def __init__(self):
        self.slices: List[FunctionSlice] = []
    
    def slice(self, ast: LightAST) -> List[FunctionSlice]:
        """将AST切分为函数单元"""
        self.slices = []
        
        for func_node in ast.functions:
            func_slice = self._create_function_slice(ast, func_node)
            self.slices.append(func_slice)
        
        return self.slices
    
    def _create_function_slice(self, ast: LightAST, func_node: ASTNode) -> FunctionSlice:
        """创建函数切片"""
        name = func_node.attributes.get('name', 'anonymous')
        line_start = func_node.line
        line_end = self._find_function_end(ast, func_node)
        
        parameters = self._extract_parameters(func_node)
        return_type = self._extract_return_type(func_node)
        exceptions = self._extract_exceptions(func_node)
        
        return FunctionSlice(
            name=name,
            file_path=ast.file_path,
            start_line=line_start,
            end_line=line_end,
            parameters=parameters,
            return_type=return_type,
            exceptions=exceptions,
            complexity=1,
            is_async=False,
            is_test=self._is_test_function(name)
        )
    
    def _find_function_end(self, ast: LightAST, func_node: ASTNode) -> int:
        """查找函数结束行"""
        brace_count = 0
        found_first_brace = False
        
        for child in func_node.children:
            if isinstance(child, ASTNode):
                if child.value == '{':
                    brace_count += 1
                    found_first_brace = True
                elif child.value == '}':
                    brace_count -= 1
                    if found_first_brace and brace_count == 0:
                        return child.line
        
        return func_node.line + 10
    
    def _extract_parameters(self, func_node: ASTNode) -> List[Dict[str, str]]:
        """提取参数列表"""
        params = []
        param_text = ""
        
        for child in func_node.children:
            if isinstance(child, str) and '(' in param_text:
                param_text += child
            elif isinstance(child, ASTNode):
                param_text += child.value or ""
        
        param_text = param_text.split('(')[1].split(')')[0] if '(' in param_text else ""
        
        for param in param_text.split(','):
            param = param.strip()
            if param and param != 'void':
                parts = param.split()
                if len(parts) >= 2:
                    params.append({'type': parts[0], 'name': parts[-1]})
                elif len(parts) == 1:
                    params.append({'type': 'unknown', 'name': parts[0]})
        
        return params
    
    def _extract_return_type(self, func_node: ASTNode) -> Optional[str]:
        """提取返回类型"""
        for child in func_node.children:
            if isinstance(child, str) and '->' in child:
                parts = child.split('->')
                return parts[-1].strip()
        return None
    
    def _extract_exceptions(self, func_node: ASTNode) -> List[str]:
        """提取异常列表"""
        exceptions = []
        return exceptions
    
    def _is_test_function(self, name: str) -> bool:
        """判断是否为测试函数"""
        test_patterns = ['test', 'Test', 'TEST', 'spec', 'Spec']
        return any(pattern in name for pattern in test_patterns)
