"""
第13层：代码语义摘要生成层

为每个代码文件生成精简、准确、结构化的语义摘要。
"""

from typing import List, Dict, Any
from fullpathtest.types.core import FileSemanticSummary, LightAST, FunctionSlice


class SemanticSummarizer:
    """语义摘要生成器"""
    
    def __init__(self):
        self.summary_cache: Dict[str, FileSemanticSummary] = {}
    
    def summarize(self, file_path: str, ast: LightAST) -> FileSemanticSummary:
        """生成文件语义摘要"""
        if file_path in self.summary_cache:
            return self.summary_cache[file_path]
        
        responsibility = self._extract_responsibility(ast)
        core_functions = self._extract_core_functions(ast)
        entry_points = self._extract_entry_points(ast)
        exports = self._extract_exports(ast)
        imports = ast.imports
        data_flow = self._analyze_data_flow(ast)
        relationships = self._analyze_relationships(ast)
        
        summary = FileSemanticSummary(
            file_path=file_path,
            responsibility=responsibility,
            core_functions=core_functions,
            entry_points=entry_points,
            exports=exports,
            imports=imports,
            data_flow_summary=data_flow,
            relationships=relationships
        )
        
        self.summary_cache[file_path] = summary
        return summary
    
    def _extract_responsibility(self, ast: LightAST) -> str:
        """提取文件职责"""
        class_nodes = [n for n in ast.nodes if n.node_type == 'CLASS']
        function_count = len(ast.functions)
        
        if class_nodes:
            class_names = [n.attributes.get('name', 'Unknown') for n in class_nodes]
            return f"类定义模块，包含类: {', '.join(class_names)}"
        elif function_count > 0:
            return f"功能模块，包含 {function_count} 个函数"
        else:
            return "辅助模块"
    
    def _extract_core_functions(self, ast: LightAST) -> List[str]:
        """提取核心函数"""
        core_functions = []
        
        for func in ast.functions:
            name = func.attributes.get('name', 'unknown')
            if name not in ['__init__', '__str__', '__repr__']:
                core_functions.append(name)
        
        return core_functions[:10]
    
    def _extract_entry_points(self, ast: LightAST) -> List[str]:
        """提取入口点"""
        entry_points = []
        
        for node in ast.nodes:
            if node.node_type == 'FUNCTION':
                name = node.attributes.get('name', '')
                if name in ['main', 'run', 'start', 'execute', 'process']:
                    entry_points.append(name)
        
        return entry_points
    
    def _extract_exports(self, ast: LightAST) -> List[str]:
        """提取导出"""
        exports = []
        
        for node in ast.nodes:
            if node.node_type == 'CLASS':
                exports.append(node.attributes.get('name', ''))
            elif node.node_type == 'FUNCTION':
                exports.append(node.attributes.get('name', ''))
        
        return exports[:20]
    
    def _analyze_data_flow(self, ast: LightAST) -> str:
        """分析数据流"""
        input_nodes = []
        output_nodes = []
        process_nodes = []
        
        for node in ast.nodes:
            node_type = node.node_type.lower()
            if 'input' in node_type or 'param' in node_type:
                input_nodes.append(node_type)
            elif 'output' in node_type or 'return' in node_type:
                output_nodes.append(node_type)
            else:
                process_nodes.append(node_type)
        
        return f"输入: {len(input_nodes)} -> 处理: {len(process_nodes)} -> 输出: {len(output_nodes)}"
    
    def _analyze_relationships(self, ast: LightAST) -> Dict[str, List[str]]:
        """分析关系"""
        relationships = {
            'imports': ast.imports[:10],
            'exports': [],
            'calls': []
        }
        
        for node in ast.nodes:
            if node.node_type == 'CLASS':
                relationships['exports'].append(node.attributes.get('name', ''))
        
        return relationships
    
    def batch_summarize(self, file_ast_pairs: List[tuple]) -> List[FileSemanticSummary]:
        """批量生成摘要"""
        return [self.summarize(path, ast) for path, ast in file_ast_pairs]
