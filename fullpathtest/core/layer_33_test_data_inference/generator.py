"""
第33层：测试数据推理层

基于路径约束、数据规则、边界条件，自动生成基础测试数据，包括正常输入、边界输入、空值、极值、非法格式。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from fullpathtest.types.core import TaskContext, ConfigSnapshot, Path
from fullpathtest.core.layer_32_test_data_rule.generator import TestDataRule


@dataclass
class TestDataItem:
    """测试数据项"""
    data_id: str
    data_type: str
    value: Any
    is_boundary: bool = False
    is_exceptional: bool = False


@dataclass
class BasicTestDataSet:
    """基础测试数据集"""
    data_set_id: str
    path_id: str
    normal_data: List[TestDataItem] = field(default_factory=list)
    boundary_data: List[TestDataItem] = field(default_factory=list)
    exceptional_data: List[TestDataItem] = field(default_factory=list)
    empty_data: List[TestDataItem] = field(default_factory=list)


class BasicTestDataGenerator:
    """基础测试数据生成器"""
    
    def __init__(self):
        self.data_sets: Dict[str, BasicTestDataSet] = {}
    
    def generate_data_sets(
        self,
        context: TaskContext,
        config: ConfigSnapshot,
        test_rules: Dict[str, TestDataRule],
        paths: List[Path]
    ) -> Dict[str, BasicTestDataSet]:
        """为每条路径生成基础测试数据集"""
        data_sets = {}
        
        for path in paths:
            rule = test_rules.get(path.path_id)
            if not rule:
                continue
            
            data_set = self._generate_data_set(path, rule)
            data_sets[path.path_id] = data_set
            self.data_sets[path.path_id] = data_set
        
        return data_sets
    
    def _generate_data_set(
        self,
        path: Path,
        rule: TestDataRule
    ) -> BasicTestDataSet:
        """生成单条路径的测试数据集"""
        data_set_id = f"DATA-{path.path_id}"
        
        normal_data = self._generate_normal_data(rule)
        boundary_data = self._generate_boundary_data(rule)
        exceptional_data = self._generate_exceptional_data(rule)
        empty_data = self._generate_empty_data(rule)
        
        return BasicTestDataSet(
            data_set_id=data_set_id,
            path_id=path.path_id,
            normal_data=normal_data,
            boundary_data=boundary_data,
            exceptional_data=exceptional_data,
            empty_data=empty_data
        )
    
    def _generate_normal_data(self, rule: TestDataRule) -> List[TestDataItem]:
        """生成正常数据"""
        items = []
        
        for i, constraint in enumerate(rule.parameter_constraints):
            param_name = constraint.parameter_name
            param_type = constraint.parameter_type
            
            normal_value = self._get_normal_value(param_type, constraint)
            
            item = TestDataItem(
                data_id=f"normal-{param_name}-{i}",
                data_type=param_type,
                value=normal_value,
                is_boundary=False,
                is_exceptional=False
            )
            
            items.append(item)
        
        return items
    
    def _generate_boundary_data(self, rule: TestDataRule) -> List[TestDataItem]:
        """生成边界数据"""
        items = []
        
        for i, constraint in enumerate(rule.parameter_constraints):
            param_name = constraint.parameter_name
            param_type = constraint.parameter_type
            
            boundaries = rule.boundary_values.get(param_name, [])
            
            for j, value in enumerate(boundaries):
                item = TestDataItem(
                    data_id=f"boundary-{param_name}-{i}-{j}",
                    data_type=param_type,
                    value=value,
                    is_boundary=True,
                    is_exceptional=False
                )
                items.append(item)
        
        return items
    
    def _generate_exceptional_data(self, rule: TestDataRule) -> List[TestDataItem]:
        """生成异常数据"""
        items = []
        
        for i, constraint in enumerate(rule.parameter_constraints):
            param_name = constraint.parameter_name
            param_type = constraint.parameter_type
            
            exceptions = rule.exceptional_values.get(param_name, [])
            
            for j, value in enumerate(exceptions):
                item = TestDataItem(
                    data_id=f"exceptional-{param_name}-{i}-{j}",
                    data_type=param_type,
                    value=value,
                    is_boundary=False,
                    is_exceptional=True
                )
                items.append(item)
        
        return items
    
    def _generate_empty_data(self, rule: TestDataRule) -> List[TestDataItem]:
        """生成空值数据"""
        items = []
        
        for i, constraint in enumerate(rule.parameter_constraints):
            param_name = constraint.parameter_name
            param_type = constraint.parameter_type
            
            if constraint.nullable:
                item = TestDataItem(
                    data_id=f"empty-{param_name}-{i}",
                    data_type=param_type,
                    value=None,
                    is_boundary=False,
                    is_exceptional=False
                )
                items.append(item)
        
        return items
    
    def _get_normal_value(self, param_type: str, constraint: Any) -> Any:
        """获取正常值"""
        if param_type == 'int' or param_type == 'number':
            min_val = constraint.min_value or 0
            max_val = constraint.max_value or 100
            return (min_val + max_val) // 2
        
        elif param_type == 'string':
            return "test_string"
        
        elif param_type == 'bool':
            return True
        
        elif param_type == 'list' or param_type == 'array':
            return [1, 2, 3]
        
        elif param_type == 'dict' or param_type == 'object':
            return {"key": "value"}
        
        else:
            return None
    
    def get_data_set_for_path(self, path_id: str) -> Optional[BasicTestDataSet]:
        """获取指定路径的测试数据集"""
        return self.data_sets.get(path_id)
