"""
第32层：测试用例生成层

基于路径生成可执行的测试用例。
"""

from typing import List, Dict, Any, Optional
from fullpathtest.types.core import Path, TestCase, ExecutionConfig
import uuid


class TestCaseGenerator:
    """测试用例生成器"""
    
    def __init__(self, config: ExecutionConfig = None):
        self.config = config or ExecutionConfig()
    
    def generate_from_path(self, path: Path) -> TestCase:
        """从路径生成测试用例"""
        inputs = self._extract_inputs(path)
        expected_outputs = self._extract_expected_outputs(path)
        preconditions = self._extract_preconditions(path)
        postconditions = self._extract_postconditions(path)
        
        return TestCase(
            case_id=f"TC_{uuid.uuid4().hex[:12]}",
            path_id=path.path_id,
            inputs=inputs,
            expected_outputs=expected_outputs,
            preconditions=preconditions,
            postconditions=postconditions
        )
    
    def generate_batch(self, paths: List[Path]) -> List[TestCase]:
        """批量生成测试用例"""
        return [self.generate_from_path(path) for path in paths]
    
    def _extract_inputs(self, path: Path) -> Dict[str, Any]:
        """提取输入参数"""
        inputs = {}
        
        for node_id in path.node_sequence:
            if 'param' in node_id.lower():
                inputs[f"input_{len(inputs)}"] = self._generate_placeholder_value()
            elif 'arg' in node_id.lower():
                inputs[f"arg_{len(inputs)}"] = self._generate_placeholder_value()
        
        if not inputs:
            inputs["default_input"] = self._generate_placeholder_value()
        
        return inputs
    
    def _extract_expected_outputs(self, path: Path) -> Dict[str, Any]:
        """提取预期输出"""
        outputs = {}
        
        for condition in path.conditions:
            if 'return' in condition.lower():
                outputs["return_value"] = None
            elif 'raise' in condition.lower():
                outputs["exception"] = None
        
        outputs["status"] = "expected"
        
        return outputs
    
    def _extract_preconditions(self, path: Path) -> List[str]:
        """提取前置条件"""
        preconditions = []
        
        if any('loop' in n.lower() for n in path.node_sequence):
            preconditions.append("环境准备完成")
        
        preconditions.append("测试数据就绪")
        
        return preconditions
    
    def _extract_postconditions(self, path: Path) -> List[str]:
        """提取后置条件"""
        postconditions = []
        
        postconditions.append("资源释放")
        postconditions.append("状态验证")
        
        return postconditions
    
    def _generate_placeholder_value(self) -> Any:
        """生成占位值"""
        return "<PLACEHOLDER>"
    
    def generate_assertions(self, test_case: TestCase) -> List[str]:
        """生成断言"""
        assertions = []
        
        for key, value in test_case.expected_outputs.items():
            if key == "status":
                assertions.append(f"assert result['{key}'] == '{value}'")
            elif key == "exception":
                assertions.append(f"assert 'exception' in result")
            else:
                assertions.append(f"assert result.get('{key}') is not None")
        
        return assertions


class TestDataGenerator:
    """测试数据生成器"""
    
    def __init__(self):
        self.test_data_templates = {
            'string': ['test', 'test123', '', 'a' * 100],
            'number': [0, 1, -1, 999999, 0.5],
            'boolean': [True, False],
            'null': [None],
            'array': [[], [1, 2, 3], ['a', 'b']],
            'object': [{}, {'key': 'value'}]
        }
    
    def generate_test_data(self, test_case: TestCase) -> List[Dict[str, Any]]:
        """生成测试数据"""
        data_sets = []
        
        base_data = test_case.inputs.copy()
        data_sets.append(base_data)
        
        for key in base_data.keys():
            if key.startswith('input_') or key.startswith('arg_'):
                for data_type, values in self.test_data_templates.items():
                    for value in values:
                        test_data = base_data.copy()
                        test_data[key] = value
                        data_sets.append(test_data)
        
        return data_sets[:10]
    
    def generate_boundary_data(self, test_case: TestCase) -> List[Dict[str, Any]]:
        """生成边界值数据"""
        boundary_data = []
        
        for key, value in test_case.inputs.items():
            if isinstance(value, (int, float)):
                boundary_data.append({**test_case.inputs, key: 0})
                boundary_data.append({**test_case.inputs, key: value - 1})
                boundary_data.append({**test_case.inputs, key: value + 1})
                boundary_data.append({**test_case.inputs, key: 999999})
        
        return boundary_data[:5]
