"""
第20层：函数语义理解层

对单个函数进行语义解析，理解功能意图、参数含义、返回值规则。
"""

from typing import List, Dict, Optional
from fullpathtest.types.core import FunctionSlice, FunctionSemantic, FileSemanticSummary


class FunctionSemanticAnalyzer:
    """函数语义分析器"""
    
    def __init__(self):
        self.analysis_cache: Dict[str, FunctionSemantic] = {}
    
    def analyze(
        self,
        function: FunctionSlice,
        file_summary: FileSemanticSummary
    ) -> FunctionSemantic:
        """分析函数语义"""
        cache_key = f"{function.file_path}:{function.name}"
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        purpose = self._extract_purpose(function)
        param_meanings = self._extract_parameter_meanings(function)
        return_rules = self._extract_return_rules(function)
        exceptions = self._extract_exception_scenarios(function)
        logic_summary = self._summarize_logic(function)
        dependencies = self._extract_dependencies(function)
        side_effects = self._extract_side_effects(function)
        
        semantic = FunctionSemantic(
            function=function,
            purpose=purpose,
            parameter_meanings=param_meanings,
            return_value_rules=return_rules,
            exception_scenarios=exceptions,
            internal_logic_summary=logic_summary,
            dependencies=dependencies,
            side_effects=side_effects
        )
        
        self.analysis_cache[cache_key] = semantic
        return semantic
    
    def _extract_purpose(self, function: FunctionSlice) -> str:
        """提取函数目的"""
        name = function.name
        
        if 'init' in name.lower() or '__init__' in name:
            return "初始化对象状态"
        elif 'get' in name.lower() or 'fetch' in name.lower():
            return "获取数据或资源"
        elif 'set' in name.lower() or 'update' in name.lower():
            return "设置或更新数据"
        elif 'add' in name.lower() or 'create' in name.lower():
            return "创建新资源"
        elif 'delete' in name.lower() or 'remove' in name.lower():
            return "删除资源"
        elif 'validate' in name.lower() or 'check' in name.lower():
            return "验证输入或状态"
        elif 'process' in name.lower() or 'handle' in name.lower():
            return "处理业务逻辑"
        else:
            return f"执行{name}操作"
    
    def _extract_parameter_meanings(self, function: FunctionSlice) -> Dict[str, str]:
        """提取参数含义"""
        meanings = {}
        
        for param in function.parameters:
            name = param.get('name', '')
            param_type = param.get('type', 'unknown')
            
            if 'id' in name.lower():
                meanings[name] = "唯一标识符"
            elif 'name' in name.lower():
                meanings[name] = "名称"
            elif 'count' in name.lower() or 'num' in name.lower():
                meanings[name] = "数量"
            elif 'flag' in name.lower() or 'enabled' in name.lower():
                meanings[name] = "开关标志"
            elif 'callback' in name.lower() or 'handler' in name.lower():
                meanings[name] = "回调处理函数"
            elif param_type in ['int', 'float', 'number']:
                meanings[name] = "数值参数"
            elif param_type in ['str', 'string']:
                meanings[name] = "字符串参数"
            else:
                meanings[name] = f"{param_type}类型参数"
        
        return meanings
    
    def _extract_return_rules(self, function: FunctionSlice) -> str:
        """提取返回规则"""
        if function.return_type:
            return_type = function.return_type
            if 'List' in return_type or 'Array' in return_type:
                return f"返回{return_type}类型的列表，可能为空"
            elif 'bool' in return_type or 'Boolean' in return_type:
                return "返回布尔值表示操作是否成功"
            elif 'void' in return_type or 'None' in return_type:
                return "无返回值"
            else:
                return f"返回{return_type}类型的结果"
        return "返回操作结果"
    
    def _extract_exception_scenarios(self, function: FunctionSlice) -> List[str]:
        """提取异常场景"""
        exceptions = []
        
        if function.exceptions:
            for exc in function.exceptions:
                exceptions.append(f"可能抛出{exc}异常")
        
        for param in function.parameters:
            if param.get('type') in ['str', 'string']:
                exceptions.append("参数为空时可能抛出异常")
            elif param.get('type') in ['int', 'float', 'number']:
                exceptions.append("参数类型不匹配时可能抛出异常")
        
        return exceptions
    
    def _summarize_logic(self, function: FunctionSlice) -> str:
        """总结内部逻辑"""
        param_count = len(function.parameters)
        complexity = function.complexity
        
        if param_count == 0:
            return "该函数为无参数函数，执行简单操作"
        elif param_count <= 3:
            return f"该函数接收{param_count}个参数，执行中等复杂度操作"
        else:
            return f"该函数接收{param_count}个参数，执行复杂业务逻辑"
    
    def _extract_dependencies(self, function: FunctionSlice) -> List[str]:
        """提取依赖项"""
        return ["标准库", "项目内部模块"]
    
    def _extract_side_effects(self, function: FunctionSlice) -> List[str]:
        """提取副作用"""
        side_effects = []
        
        if 'global' in str(function.parameters).lower():
            side_effects.append("可能修改全局状态")
        
        if function.name.startswith('set_') or function.name.startswith('update_'):
            side_effects.append("修改对象状态")
        
        if 'print' in function.name or 'log' in function.name:
            side_effects.append("产生输出")
        
        if not side_effects:
            side_effects.append("无明显副作用")
        
        return side_effects
