"""
第8层：需求-代码映射分析层

建立业务需求描述与代码之间的映射关系。
"""

from typing import Dict, List, Any, Optional
from fullpathtest.types.core import (
    TaskContext, RequirementMapping, FileSemanticSummary, FunctionSemantic
)


class RequirementMapper:
    """需求映射器"""
    
    def __init__(self):
        self.mappings: Dict[str, RequirementMapping] = {}
    
    def analyze(
        self,
        context: TaskContext,
        requirements: List[str],
        code_modules: List[Any]
    ) -> List[RequirementMapping]:
        """分析需求代码映射"""
        mappings = []
        
        for req_id, req_text in enumerate(requirements):
            mapping = self._create_mapping(req_id, req_text, code_modules)
            mappings.append(mapping)
            self.mappings[f"REQ_{req_id}"] = mapping
        
        return mappings
    
    def _create_mapping(
        self,
        req_id: int,
        req_text: str,
        code_modules: List[Any]
    ) -> RequirementMapping:
        """创建映射"""
        covered_functions = []
        uncovered_functions = []
        
        for module in code_modules:
            if self._is_covered_by_requirement(module, req_text):
                if isinstance(module, FunctionSemantic):
                    covered_functions.append(module.function.name)
                elif isinstance(module, FileSemanticSummary):
                    covered_functions.extend(module.core_functions)
            else:
                if isinstance(module, FunctionSemantic):
                    uncovered_functions.append(module.function.name)
                elif isinstance(module, FileSemanticSummary):
                    uncovered_functions.extend(module.core_functions)
        
        total = len(covered_functions) + len(uncovered_functions)
        coverage_rate = len(covered_functions) / total if total > 0 else 0.0
        
        return RequirementMapping(
            requirement_id=f"REQ_{req_id}",
            requirement_text=req_text,
            covered_functions=covered_functions,
            uncovered_functions=uncovered_functions,
            coverage_rate=coverage_rate
        )
    
    def _is_covered_by_requirement(self, module: Any, req_text: str) -> bool:
        """判断模块是否被需求覆盖"""
        req_keywords = req_text.lower().split()
        
        if isinstance(module, FunctionSemantic):
            module_text = f"{module.purpose} {module.internal_logic_summary}".lower()
        elif isinstance(module, FileSemanticSummary):
            module_text = f"{module.responsibility} {' '.join(module.core_functions)}".lower()
        else:
            module_text = str(module).lower()
        
        for keyword in req_keywords:
            if len(keyword) > 3 and keyword in module_text:
                return True
        
        return False
    
    def get_coverage_report(self) -> Dict[str, Any]:
        """获取覆盖率报告"""
        if not self.mappings:
            return {'total_requirements': 0, 'overall_coverage': 0.0}
        
        total_coverage = sum(m.coverage_rate for m in self.mappings.values())
        avg_coverage = total_coverage / len(self.mappings)
        
        return {
            'total_requirements': len(self.mappings),
            'overall_coverage': round(avg_coverage * 100, 2),
            'mappings': [
                {
                    'requirement_id': m.requirement_id,
                    'requirement_text': m.requirement_text[:100],
                    'coverage_rate': round(m.coverage_rate * 100, 2),
                    'covered_count': len(m.covered_functions),
                    'uncovered_count': len(m.uncovered_functions)
                }
                for m in self.mappings.values()
            ]
        }
