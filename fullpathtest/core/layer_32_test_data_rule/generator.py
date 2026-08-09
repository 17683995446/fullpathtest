"""
第32层：测试数据生成指导层

为每条最终路径推导分支条件、参数约束、状态前置、输入范围、边界值、异常值，生成结构化数据生成规则。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from fullpathtest.types.core import TaskContext, ConfigSnapshot, Path


@dataclass
class ParameterConstraint:
    """参数约束"""
    parameter_name: str
    parameter_type: str
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    allowed_values: List[Any] = field(default_factory=list)
    format_pattern: Optional[str] = None
    required: bool = True
    nullable: bool = False


@dataclass
class BranchCondition:
    """分支条件"""
    condition_id: str
    expression: str
    expected_result: Any
    line_number: int


@dataclass
class TestDataRule:
    """测试数据生成规则"""
    rule_id: str
    path_id: str
    parameter_constraints: List[ParameterConstraint] = field(default_factory=list)
    branch_conditions: List[BranchCondition] = field(default_factory=list)
    preconditions: List[str] = field(default_factory=list)
    boundary_values: Dict[str, List[Any]] = field(default_factory=dict)
    exceptional_values: Dict[str, List[Any]] = field(default_factory=dict)
    state_requirements: Dict[str, Any] = field(default_factory=dict)


class TestDataRuleGenerator:
    """测试数据规则生成器"""
    
    def __init__(self):
        self.rules: Dict[str, TestDataRule] = {}
    
    def generate_rules(
        self,
        context: TaskContext,
        config: ConfigSnapshot,
        paths: List[Path],
        branch_constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, TestDataRule]:
        """为每条路径生成数据规则"""
        rules = {}
        
        for path in paths:
            rule_id = f"RULE-{path.path_id}"
            
            constraints = self._extract_parameter_constraints(path)
            conditions = self._extract_branch_conditions(path)
            preconditions = self._extract_preconditions(path)
            boundaries = self._generate_boundary_values(constraints)
            exceptions = self._generate_exceptional_values(constraints)
            state_reqs = self._extract_state_requirements(path)
            
            rule = TestDataRule(
                rule_id=rule_id,
                path_id=path.path_id,
                parameter_constraints=constraints,
                branch_conditions=conditions,
                preconditions=preconditions,
                boundary_values=boundaries,
                exceptional_values=exceptions,
                state_requirements=state_reqs
            )
            
            rules[path.path_id] = rule
            self.rules[path.path_id] = rule
        
        return rules
    
    def _extract_parameter_constraints(self, path: Path) -> List[ParameterConstraint]:
        """提取参数约束"""
        constraints = []
        
        # 安全访问 constraint_conditions，避免 AttributeError
        if hasattr(path, 'constraint_conditions') and path.constraint_conditions:
            for constraint in path.constraint_conditions:
                param_name = constraint.get('parameter', '')
                param_type = constraint.get('type', 'string')
                
                constraint_obj = ParameterConstraint(
                    parameter_name=param_name,
                    parameter_type=param_type,
                    min_value=constraint.get('min'),
                    max_value=constraint.get('max'),
                    allowed_values=constraint.get('allowed', []),
                    format_pattern=constraint.get('pattern'),
                    required=constraint.get('required', True)
                )
                
                constraints.append(constraint_obj)
        
        if not constraints:
            constraints.append(ParameterConstraint(
                parameter_name="input",
                parameter_type="any",
                required=True
            ))
        
        return constraints
    
    def _extract_branch_conditions(self, path: Path) -> List[BranchCondition]:
        """提取分支条件"""
        conditions = []
        
        for i, node_id in enumerate(path.node_sequence):
            if node_id.startswith('branch') or 'if' in node_id.lower():
                condition = BranchCondition(
                    condition_id=f"COND-{i}",
                    expression=f"condition_{i} == true",
                    expected_result=True,
                    line_number=i + 1
                )
                conditions.append(condition)
        
        return conditions
    
    def _extract_preconditions(self, path: Path) -> List[str]:
        """提取前置条件"""
        preconditions = []
        
        # 安全访问 business_scenarios
        if hasattr(path, 'business_scenarios') and path.business_scenarios:
            for scenario in path.business_scenarios:
                preconditions.append(f"业务场景: {scenario}")
        
        # 安全访问 preconditions
        if hasattr(path, 'preconditions') and path.preconditions:
            preconditions.extend(path.preconditions)
        
        if not preconditions:
            preconditions.append("系统处于正常运行状态")
        
        return preconditions
    
    def _generate_boundary_values(self, constraints: List[ParameterConstraint]) -> Dict[str, List[Any]]:
        """生成边界值"""
        boundaries = {}
        
        for constraint in constraints:
            param_name = constraint.parameter_name
            param_type = constraint.parameter_type
            
            values = self._get_type_boundaries(param_type, constraint)
            boundaries[param_name] = values
        
        return boundaries
    
    def _get_type_boundaries(self, param_type: str, constraint: ParameterConstraint) -> List[Any]:
        """根据类型获取边界值"""
        if param_type == 'int' or param_type == 'number':
            min_val = constraint.min_value or 0
            max_val = constraint.max_value or 100
            return [min_val, min_val + 1, max_val - 1, max_val]
        
        elif param_type == 'string':
            return ["", "a", "a" * 100, "special!@#$"]
        
        elif param_type == 'bool':
            return [True, False]
        
        elif param_type == 'list' or param_type == 'array':
            return [[], [1], [1, 2, 3], list(range(100))]
        
        else:
            return [None, ""]
    
    def _generate_exceptional_values(self, constraints: List[ParameterConstraint]) -> Dict[str, List[Any]]:
        """生成异常值"""
        exceptions = {}
        
        for constraint in constraints:
            param_name = constraint.parameter_name
            param_type = constraint.parameter_type
            
            values = self._get_type_exceptions(param_type, constraint)
            exceptions[param_name] = values
        
        return exceptions
    
    def _get_type_exceptions(self, param_type: str, constraint: ParameterConstraint) -> List[Any]:
        """根据类型获取异常值"""
        if param_type == 'int' or param_type == 'number':
            return [
                -999999,
                999999,
                float('inf'),
                float('nan'),
                None
            ]
        
        elif param_type == 'string':
            return [
                None,
                "",
                "\0",
                "a" * 10000,
                "你好世界"
            ]
        
        elif param_type == 'list' or param_type == 'array':
            return [
                None,
                [],
                list(range(10000))
            ]
        
        else:
            return [None]
    
    def _extract_state_requirements(self, path: Path) -> Dict[str, Any]:
        """提取状态需求"""
        requirements = {}
        
        requirements['path_type'] = path.path_type.name
        requirements['risk_level'] = path.risk_level.name if hasattr(path, 'risk_level') else 'MEDIUM'
        
        return requirements
    
    def get_rule_for_path(self, path_id: str) -> Optional[TestDataRule]:
        """获取指定路径的数据规则"""
        return self.rules.get(path_id)
