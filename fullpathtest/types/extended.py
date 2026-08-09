"""
扩展类型定义模块

为第21-31层提供额外的类型定义，包括：
- 数据流图
- 依赖关系图
- 符号解析
- 类型推断
- 代码异味检测
- 复杂度分析
- 可测试性分析
- 覆盖目标识别
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple


# ==================== 第21层：数据流图类型 ====================

class DataFlowNodeType(Enum):
    """数据流节点类型"""
    VARIABLE_DECLARE = "variable_declare"
    VARIABLE_READ = "variable_read"
    VARIABLE_WRITE = "variable_write"
    FUNCTION_CALL = "function_call"
    PARAMETER_PASS = "parameter_pass"
    RETURN_VALUE = "return_value"
    FIELD_ACCESS = "field_access"
    ARRAY_INDEX = "array_index"


class DataFlowEdgeType(Enum):
    """数据流边类型"""
    DEFINITION_USE = "definition_use"
    CONTROL_DEPENDENCY = "control_dependency"
    DATA_DEPENDENCY = "data_dependency"
    CALL_GRAPH = "call_graph"


@dataclass
class DataFlowNode:
    """数据流图节点"""
    node_id: str
    node_type: DataFlowNodeType
    name: str
    line_number: int
    scope: str
    data_type: Optional[str] = None
    value: Optional[Any] = None
    is_parameter: bool = False
    is_global: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataFlowEdge:
    """数据流图边"""
    source_id: str
    target_id: str
    edge_type: DataFlowEdgeType
    variable_name: Optional[str] = None
    is_alias: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataFlowGraph:
    """数据流图"""
    graph_id: str
    function_name: str
    nodes: List[DataFlowNode] = field(default_factory=list)
    edges: List[DataFlowEdge] = field(default_factory=list)
    entry_node_id: Optional[str] = None
    exit_node_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataDependency:
    """数据依赖关系"""
    source_file: str
    source_function: str
    source_line: int
    target_file: str
    target_function: str
    target_line: int
    variable_name: str
    dependency_type: str
    is_transitive: bool = False


@dataclass
class DataDependencySet:
    """数据依赖集合"""
    dependencies: List[DataDependency] = field(default_factory=list)
    global_variables: Set[str] = field(default_factory=set)
    parameter_flows: Dict[str, List[str]] = field(default_factory=dict)
    return_value_flows: Dict[str, List[str]] = field(default_factory=dict)


# ==================== 第23层：依赖关系图类型 ====================

class DependencyType(Enum):
    """依赖类型"""
    IMPORT = "import"
    INHERIT = "inherit"
    COMPOSITION = "composition"
    AGGREGATION = "aggregation"
    ASSOCIATION = "association"
    CALL = "call"
    PARAMETER = "parameter"
    RETURN = "return"
    GLOBAL = "global"


class DependencyScope(Enum):
    """依赖范围"""
    FILE_LEVEL = "file_level"
    FUNCTION_LEVEL = "function_level"
    CLASS_LEVEL = "class_level"
    MODULE_LEVEL = "module_level"
    PACKAGE_LEVEL = "package_level"


@dataclass
class DependencyNode:
    """依赖图节点"""
    node_id: str
    name: str
    node_type: DependencyScope
    file_path: str
    line_number: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DependencyEdge:
    """依赖边"""
    source_id: str
    target_id: str
    dependency_type: DependencyType
    weight: float = 1.0
    is_cyclic: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DependencyGraph:
    """依赖关系图"""
    graph_id: str
    nodes: List[DependencyNode] = field(default_factory=list)
    edges: List[DependencyEdge] = field(default_factory=list)
    adjacency_list: Dict[str, List[str]] = field(default_factory=dict)
    reverse_adjacency: Dict[str, List[str]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModuleDependency:
    """模块依赖"""
    module_name: str
    file_path: str
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    is_leaf: bool = False
    is_entry: bool = False


@dataclass
class ModuleDependencyMap:
    """模块依赖映射"""
    modules: Dict[str, ModuleDependency] = field(default_factory=dict)
    cross_module_calls: List[Tuple[str, str]] = field(default_factory=list)


@dataclass
class ImpactAnalysisResult:
    """影响分析结果"""
    target_module: str
    direct_dependents: Set[str] = field(default_factory=set)
    indirect_dependents: Set[str] = field(default_factory=set)
    total_affected_modules: Set[str] = field(default_factory=set)
    breaking_changes: List[str] = field(default_factory=list)
    risk_level: str = "LOW"
    recommendations: List[str] = field(default_factory=list)


# ==================== 第24层：符号解析类型 ====================

class SymbolKind(Enum):
    """符号类型"""
    VARIABLE = "variable"
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    MODULE = "module"
    PARAMETER = "parameter"
    CONSTANT = "constant"
    ENUM = "enum"
    INTERFACE = "interface"
    TYPE_ALIAS = "type_alias"
    GENERIC = "generic"


class SymbolScope(Enum):
    """符号作用域"""
    GLOBAL = "global"
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    BLOCK = "block"


@dataclass
class Symbol:
    """符号"""
    symbol_id: str
    name: str
    kind: SymbolKind
    scope: SymbolScope
    file_path: str
    line_number: int
    column_number: int
    data_type: Optional[str] = None
    definition: Optional[str] = None
    is_exported: bool = False
    is_builtin: bool = False
    references: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SymbolReference:
    """符号引用"""
    reference_id: str
    symbol_id: str
    file_path: str
    line_number: int
    column_number: int
    is_definition: bool = False
    is_usage: bool = True
    context: Optional[str] = None


@dataclass
class NamespaceScope:
    """命名空间作用域"""
    scope_id: str
    scope_type: SymbolScope
    parent_scope_id: Optional[str] = None
    symbols: Dict[str, Symbol] = field(default_factory=dict)
    child_scope_ids: List[str] = field(default_factory=list)
    start_line: int = 0
    end_line: int = 0


@dataclass
class SymbolTable:
    """符号表"""
    table_id: str
    global_scope: NamespaceScope
    scopes: Dict[str, NamespaceScope] = field(default_factory=dict)
    symbols: Dict[str, Symbol] = field(default_factory=dict)
    references: Dict[str, SymbolReference] = field(default_factory=dict)


@dataclass
class TypeInfo:
    """类型信息"""
    type_name: str
    type_kind: str
    is_generic: bool = False
    generic_params: List[str] = field(default_factory=list)
    underlying_type: Optional[str] = None
    members: Dict[str, str] = field(default_factory=dict)


# ==================== 第25层：类型推断类型 ====================

class InferredTypeKind(Enum):
    """推断类型种类"""
    PRIMITIVE = "primitive"
    OBJECT = "object"
    COLLECTION = "collection"
    FUNCTION = "function"
    UNION = "union"
    OPTIONAL = "optional"
    GENERIC = "generic"
    DYNAMIC = "dynamic"
    UNKNOWN = "unknown"


@dataclass
class InferredType:
    """推断出的类型"""
    type_id: str
    kind: InferredTypeKind
    type_name: str
    confidence: float = 1.0
    constraints: List[str] = field(default_factory=list)
    possible_types: List[str] = field(default_factory=list)
    type_parameters: Dict[str, 'InferredType'] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TypeConstraint:
    """类型约束"""
    constraint_id: str
    variable_name: str
    constraint_type: str
    target_type: Optional[str] = None
    source_location: str = ""
    is_violated: bool = False
    message: Optional[str] = None


@dataclass
class TypeError:
    """类型错误"""
    error_id: str
    error_type: str
    message: str
    file_path: str
    line_number: int
    column_number: int
    expected_type: Optional[str] = None
    actual_type: Optional[str] = None
    suggestion: Optional[str] = None
    severity: str = "error"


@dataclass
class TypeVariable:
    """类型变量"""
    var_id: str
    name: str
    constraint: Optional[str] = None
    lower_bound: Optional[str] = None
    is_resolved: bool = False
    resolved_type: Optional[InferredType] = None


@dataclass
class InferredTypeMap:
    """推断类型映射"""
    node_types: Dict[str, InferredType] = field(default_factory=dict)
    variable_types: Dict[str, InferredType] = field(default_factory=dict)
    function_signatures: Dict[str, Dict[str, InferredType]] = field(default_factory=dict)
    constraints: List[TypeConstraint] = field(default_factory=list)
    errors: List[TypeError] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ==================== 第27层：代码异味检测类型 ====================

class SmellType(Enum):
    """代码异味类型"""
    GOD_CLASS = "god_class"
    LARGE_CLASS = "large_class"
    LONG_METHOD = "long_method"
    DUPLICATED_CODE = "duplicated_code"
    DEAD_CODE = "dead_code"
    LONG_PARAMETER_LIST = "long_parameter_list"
    LONG_FUNCTION = "long_function"
    TOO_MANY_RETURN = "too_many_return"
    COMPLEX_CONDITION = "complex_condition"
    DEEP_NESTING = "deep_nesting"
    SHOTGUN_SURGERY = "shotgun_surgery"
    PARALLEL_INHERITANCE = "parallel_inheritance"
    SPIKE = "spike"
    FEATURE_ENVY = "feature_envy"
    INAPPROPRIATE_INTIMACY = "inappropriate_intimacy"
    DATA_CLUMP = "data_clump"
    REFUSED_BEQUEST = "refused_bequest"
    LAZY_CLASS = "lazy_class"
    SPECULATIVE_GENERALITY = "speculative_generality"
    MESSAGE_CHAIN = "message_chain"
    MIDDLE_MAN = "middle_man"


class SmellSeverity(Enum):
    """异味严重程度"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class CodeLocation:
    """代码位置"""
    file_path: str
    start_line: int
    end_line: int
    start_column: int = 0
    end_column: int = 0
    snippet: Optional[str] = None


@dataclass
class SmellInstance:
    """代码异味实例"""
    smell_id: str
    smell_type: SmellType
    severity: SmellSeverity
    locations: List[CodeLocation] = field(default_factory=list)
    metric_value: float = 0.0
    threshold: float = 0.0
    description: str = ""
    affected_elements: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RefactoringSuggestion:
    """重构建议"""
    suggestion_id: str
    smell_id: str
    smell_type: SmellType
    title: str
    description: str
    steps: List[str] = field(default_factory=list)
    effort: str = "medium"
    risk: str = "low"
    benefits: List[str] = field(default_factory=list)
    example: Optional[str] = None
    related_smells: List[str] = field(default_factory=list)


@dataclass
class CodeSmellReport:
    """代码异味报告"""
    report_id: str
    total_smells: int = 0
    smells_by_type: Dict[SmellType, int] = field(default_factory=dict)
    smells_by_severity: Dict[SmellSeverity, int] = field(default_factory=dict)
    smell_instances: List[SmellInstance] = field(default_factory=list)
    refactoring_suggestions: List[RefactoringSuggestion] = field(default_factory=list)
    metrics_summary: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ==================== 第28层：圈复杂度分析类型 ====================

class ComplexityLevel(Enum):
    """复杂度等级"""
    VERY_LOW = (1, 10)
    LOW = (11, 20)
    MODERATE = (21, 30)
    HIGH = (31, 40)
    VERY_HIGH = (41, 50)
    UNACCEPTABLE = (51, float('inf'))
    
    def __init__(self, min_val, max_val):
        self.min_val = min_val
        self.max_val = max_val
    
    @classmethod
    def from_score(cls, score: float) -> 'ComplexityLevel':
        for level in cls:
            if level.min_val <= score <= level.max_val:
                return level
        return cls.UNACCEPTABLE


@dataclass
class ComplexityMetric:
    """复杂度指标"""
    element_name: str
    element_type: str
    file_path: str
    line_number: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    halstead_volume: Optional[float] = None
    maintainability_index: Optional[float] = None
    level: ComplexityLevel = ComplexityLevel.VERY_LOW
    is_hotspot: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplexityHotspot:
    """复杂度热点"""
    hotspot_id: str
    element_name: str
    file_path: str
    start_line: int
    end_line: int
    complexity_score: int
    level: ComplexityLevel
    reasons: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class ComplexityReport:
    """复杂度报告"""
    report_id: str
    total_elements: int = 0
    average_cyclomatic: float = 0.0
    average_cognitive: float = 0.0
    max_cyclomatic: int = 0
    max_cognitive: int = 0
    hotspots: List[ComplexityHotspot] = field(default_factory=list)
    metrics_by_file: Dict[str, List[ComplexityMetric]] = field(default_factory=dict)
    metrics_by_type: Dict[str, List[ComplexityMetric]] = field(default_factory=dict)
    distribution: Dict[str, int] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ==================== 第30层：可测试性分析类型 ====================

class TestabilityIssueType(Enum):
    """可测试性问题类型"""
    HARD_TO_INITIALIZE = "hard_to_initialize"
    HIDDEN_DEPENDENCIES = "hidden_dependencies"
    STATIC_COUPLING = "static_coupling"
    GLOBAL_STATE = "global_state"
    COMPLEX_SETUP = "complex_setup"
    NON_DETERMINISTIC = "non_deterministic"
    EXTERNAL_DEPENDENCIES = "external_dependencies"
    PRIVATE_STATE_ACCESS = "private_state_access"
    INDIRECT_CONTROL_FLOW = "indirect_control_flow"
    SIDE_EFFECTS = "side_effects"


class TestabilityLevel(Enum):
    """可测试性等级"""
    EXCELLENT = ("excellent", 90, 100)
    GOOD = ("good", 70, 89)
    MODERATE = ("moderate", 50, 69)
    POOR = ("poor", 30, 49)
    VERY_POOR = ("very_poor", 0, 29)
    
    def __init__(self, name: str, min_val: int, max_val: int):
        self.level_name = name
        self.min_val = min_val
        self.max_val = max_val
    
    @classmethod
    def from_score(cls, score: float) -> 'TestabilityLevel':
        for level in cls:
            if level.min_val <= score <= level.max_val:
                return level
        return cls.VERY_POOR


@dataclass
class TestabilityIssue:
    """可测试性问题"""
    issue_id: str
    issue_type: TestabilityIssueType
    severity: str
    element_name: str
    element_type: str
    file_path: str
    line_number: int
    description: str
    impact: str
    suggestions: List[str] = field(default_factory=list)
    example_code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestabilityScore:
    """可测试性评分"""
    overall_score: float
    level: TestabilityLevel
    initialization_score: float = 0.0
    dependency_score: float = 0.0
    structure_score: float = 0.0
    predictability_score: float = 0.0
    analysis_details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestabilityReport:
    """可测试性报告"""
    report_id: str
    overall_score: float
    overall_level: TestabilityLevel
    element_scores: Dict[str, TestabilityScore] = field(default_factory=dict)
    issues: List[TestabilityIssue] = field(default_factory=list)
    issues_by_type: Dict[TestabilityIssueType, int] = field(default_factory=dict)
    critical_functions: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    testability_metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ==================== 第31层：覆盖目标识别类型 ====================

class TargetPriority(Enum):
    """目标优先级"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    MINIMAL = 5


class TargetType(Enum):
    """目标类型"""
    FUNCTION = "function"
    BRANCH = "branch"
    PATH = "path"
    STATEMENT = "statement"
    CONDITION = "condition"
    REQUIREMENT = "requirement"
    RISK_AREA = "risk_area"


class CoverageStrategy(Enum):
    """覆盖策略"""
    COMPLETE = "complete"
    PRIORITY_BASED = "priority_based"
    RISK_BASED = "risk_based"
    CHANGE_BASED = "change_based"
    HYBRID = "hybrid"


@dataclass
class CoverageTarget:
    """覆盖目标"""
    target_id: str
    target_type: TargetType
    name: str
    file_path: str
    line_number: int
    priority: TargetPriority
    risk_score: float = 0.0
    complexity: float = 0.0
    frequency: int = 0
    is_critical_path: bool = False
    related_requirements: List[str] = field(default_factory=list)
    dependent_targets: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BranchTarget:
    """分支覆盖目标"""
    branch_id: str
    condition_line: int
    true_branch_target: Optional[str] = None
    false_branch_target: Optional[str] = None
    is_covered: bool = False
    test_cases_needed: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PathTarget:
    """路径覆盖目标"""
    path_id: str
    path_type: str
    nodes: List[str] = field(default_factory=list)
    edges: List[Tuple[str, str]] = field(default_factory=list)
    is_critical: bool = False
    is_reachable: bool = True
    constraints: List[str] = field(default_factory=list)
    test_cases_needed: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RequirementTarget:
    """需求覆盖目标"""
    requirement_id: str
    requirement_name: str
    description: str
    priority: TargetPriority
    test_cases_needed: int = 0
    covered_test_cases: List[str] = field(default_factory=list)
    traceability_matrix: Dict[str, List[str]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CoverageTargetSet:
    """覆盖目标集合"""
    targets: List[CoverageTarget] = field(default_factory=list)
    function_targets: Dict[str, List[CoverageTarget]] = field(default_factory=dict)
    branch_targets: List[BranchTarget] = field(default_factory=list)
    path_targets: List[PathTarget] = field(default_factory=list)
    requirement_targets: List[RequirementTarget] = field(default_factory=list)
    priority_rankings: List[CoverageTarget] = field(default_factory=list)


@dataclass
class PriorityRanking:
    """优先级排序"""
    rankings: List[Tuple[str, float, TargetPriority]] = field(default_factory=list)
