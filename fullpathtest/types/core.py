"""
核心类型定义模块

定义系统内部使用的所有核心数据结构，包括任务、配置、路径等。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple, Union


class SourceType(Enum):
    """代码来源类型枚举"""
    LOCAL_DIRECTORY = auto()
    GIT_REPOSITORY = auto()
    ARCHIVE_FILE = auto()
    MULTI_SERVICE = auto()
    REMOTE_URL = auto()


class LLMMode(Enum):
    """LLM运行模式"""
    LOCAL_ONLY = auto()
    CLOUD_ONLY = auto()
    HYBRID = auto()
    OFFLINE = auto()


class TaskState(Enum):
    """任务状态枚举"""
    CREATED = auto()
    INITIALIZING = auto()
    PARSING = auto()
    ANALYZING = auto()
    GENERATING_PATHS = auto()
    EXECUTING = auto()
    REPORTING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()
    PAUSED = auto()


class CoverageLevel(Enum):
    """代码覆盖级别"""
    STATEMENT = auto()
    BRANCH = auto()
    CONDITION = auto()
    PATH = auto()
    CALL_CHAIN = auto()
    E2E_FLOW = auto()


class LanguageType(Enum):
    """支持的编程语言"""
    PYTHON = auto()
    JAVA = auto()
    GOLANG = auto()
    RUST = auto()
    TYPESCRIPT = auto()
    CSHARP = auto()
    JAVASCRIPT = auto()
    CPP = auto()
    C = auto()
    UNKNOWN = auto()


class RiskLevel(Enum):
    """风险等级"""
    CRITICAL = auto()
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()
    MINIMAL = auto()


class PathType(Enum):
    """路径类型"""
    INTRAPROCEDURAL = auto()
    INTERPROCEDURAL = auto()
    CROSS_SERVICE = auto()
    E2E = auto()


class ExecutionStatus(Enum):
    """执行状态"""
    PENDING = auto()
    RUNNING = auto()
    PASSED = auto()
    FAILED = auto()
    SKIPPED = auto()
    ERROR = auto()


@dataclass
class CoverageRules:
    """覆盖规则配置"""
    statement: bool = True
    branch: bool = True
    condition: bool = True
    path: bool = True
    call_chain: bool = False
    e2e_flow: bool = False
    max_depth: int = 100
    max_paths_per_function: int = 1000


@dataclass
class LLMConfig:
    """LLM配置"""
    mode: LLMMode = LLMMode.LOCAL_ONLY
    local_endpoint: str = "http://localhost:11434/api/generate"
    cloud_provider: str = "openai"
    cloud_endpoint: str = "https://api.openai.com/v1/chat/completions"
    model_name: str = "llama3"
    temperature: float = 0.3
    max_tokens: int = 4096
    timeout: int = 120
    retry_count: int = 3


@dataclass
class CacheConfig:
    """缓存配置"""
    enable_memory_cache: bool = True
    enable_disk_cache: bool = True
    enable_vector_cache: bool = True
    memory_cache_size: int = 1000
    disk_cache_dir: str = ".fullpathtest/cache"
    vector_db_path: str = ".fullpathtest/vectors"
    cache_ttl: int = 86400


@dataclass
class ExecutionConfig:
    """执行配置"""
    max_parallel_workers: int = 4
    timeout_per_test: int = 300
    max_retries: int = 2
    enable_coverage: bool = True
    enable_profiling: bool = False


@dataclass
class SecurityRules:
    """安全规则配置"""
    skip_sensitive: bool = True
    skip_test_code: bool = False
    allowed_paths: List[str] = field(default_factory=list)
    blocked_paths: List[str] = field(default_factory=list)
    max_file_size: int = 10 * 1024 * 1024


@dataclass
class ConfigSnapshot:
    """不可变配置快照"""
    llm_config: LLMConfig = field(default_factory=LLMConfig)
    coverage_rules: CoverageRules = field(default_factory=CoverageRules)
    cache_config: CacheConfig = field(default_factory=CacheConfig)
    execution_config: ExecutionConfig = field(default_factory=ExecutionConfig)
    security_rules: SecurityRules = field(default_factory=SecurityRules)
    language_overrides: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TaskRequest:
    """标准化任务请求"""
    task_id: str
    source_type: SourceType
    source_path: str
    language: Optional[str] = None
    coverage_rules: CoverageRules = field(default_factory=CoverageRules)
    llm_mode: LLMMode = LLMMode.LOCAL_ONLY
    test_strategy: Optional[Dict[str, Any]] = None
    priority: int = 5
    timeout: int = 3600
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskContext:
    """全局任务上下文"""
    task_id: str
    request: TaskRequest
    config: ConfigSnapshot
    state: TaskState = TaskState.CREATED
    progress: float = 0.0
    current_layer: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    artifacts: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskInstruction:
    """结构化任务指令"""
    task_id: str
    intent: str
    target_modules: List[str] = field(default_factory=list)
    coverage_requirements: CoverageRules = field(default_factory=CoverageRules)
    priority_areas: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    business_scenarios: List[str] = field(default_factory=list)


@dataclass
class FileMetadata:
    """源码文件元数据"""
    file_path: str
    relative_path: str
    language: LanguageType
    size: int
    line_count: int
    last_modified: datetime
    file_hash: str
    is_test_file: bool = False
    encoding: str = "utf-8"


@dataclass
class StandardizedCode:
    """标准化代码文本"""
    file_path: str
    content: str
    lines: List[str] = field(default_factory=list)
    normalized_content: str = ""
    removed_comments: int = 0
    removed_blank_lines: int = 0


@dataclass
class Token:
    """词法Token"""
    type: str
    value: str
    line: int
    column: int
    length: int
    children: List['Token'] = field(default_factory=list)


@dataclass
class TokenStream:
    """Token流"""
    file_path: str
    tokens: List[Token] = field(default_factory=list)
    token_count: int = 0
    error_count: int = 0


@dataclass
class ASTNode:
    """AST节点"""
    node_type: str
    value: Optional[str] = None
    line: int = 0
    column: int = 0
    children: List['ASTNode'] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LightAST:
    """轻量级抽象语法树"""
    file_path: str
    root: Optional[ASTNode] = None
    nodes: List[ASTNode] = field(default_factory=list)
    functions: List['FunctionSlice'] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FunctionSlice:
    """函数切片"""
    name: str
    file_path: str
    start_line: int
    end_line: int
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    return_type: Optional[str] = None
    exceptions: List[str] = field(default_factory=list)
    ast: Optional[LightAST] = None
    complexity: int = 1
    is_async: bool = False
    is_test: bool = False


@dataclass
class FunctionSemantic:
    """函数语义描述"""
    function: FunctionSlice
    purpose: str
    parameter_meanings: Dict[str, str] = field(default_factory=dict)
    return_value_rules: str = ""
    exception_scenarios: List[str] = field(default_factory=list)
    internal_logic_summary: str = ""
    dependencies: List[str] = field(default_factory=list)
    side_effects: List[str] = field(default_factory=list)


@dataclass
class FileSemanticSummary:
    """文件级语义摘要"""
    file_path: str
    responsibility: str
    core_functions: List[str] = field(default_factory=list)
    entry_points: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    data_flow_summary: str = ""
    relationships: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class CodeQualityIssue:
    """代码质量问题"""
    file_path: str
    line: int
    issue_type: str
    severity: RiskLevel
    message: str
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None


@dataclass
class TestRiskScore:
    """测试风险评分"""
    file_path: str
    risk_score: float
    risk_level: RiskLevel
    function_name: Optional[str] = None
    factors: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class DependencyEdge:
    """依赖边"""
    source_file: str
    source_function: str
    target_file: str
    target_function: str
    call_type: str
    is_conditional: bool = False


@dataclass
class GlobalDependencyGraph:
    """全局函数依赖图"""
    nodes: Dict[str, FunctionSlice] = field(default_factory=dict)
    edges: List[DependencyEdge] = field(default_factory=list)
    entry_points: List[str] = field(default_factory=list)
    external_calls: List[str] = field(default_factory=list)


@dataclass
class CFGNode:
    """控制流图节点"""
    node_id: str
    node_type: str
    statements: List[str] = field(default_factory=list)
    line_start: int = 0
    line_end: int = 0
    successors: List[str] = field(default_factory=list)
    predecessors: List[str] = field(default_factory=list)


@dataclass
class ControlFlowGraph:
    """控制流图"""
    function_name: str
    file_path: str
    nodes: Dict[str, CFGNode] = field(default_factory=dict)
    entry_node: str = ""
    exit_nodes: List[str] = field(default_factory=list)
    loop_nodes: List[str] = field(default_factory=list)
    branch_nodes: List[str] = field(default_factory=list)


@dataclass
class BusinessScenario:
    """业务场景"""
    scenario_id: str
    name: str
    description: str
    scenario_type: str
    is_critical: bool
    related_functions: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)


@dataclass
class SemanticPath:
    """带语义标签的路径"""
    path_id: str
    path_type: PathType
    nodes: List[str]
    risk_level: RiskLevel
    business_scenarios: List[str] = field(default_factory=list)
    coverage_requirements: List[CoverageLevel] = field(default_factory=list)
    constraint_conditions: Dict[str, Any] = field(default_factory=dict)
    is_reachable: bool = True
    is_essential: bool = False


@dataclass
class Path:
    """测试路径"""
    path_id: str
    path_type: PathType
    cfgs: List[ControlFlowGraph] = field(default_factory=list)
    node_sequence: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    estimated_execution_time: float = 0.0


@dataclass
class PathSet:
    """路径集合"""
    paths: List[Path] = field(default_factory=list)
    total_count: int = 0
    pruned_count: int = 0
    unreachable_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestCase:
    """测试用例"""
    case_id: str
    path_id: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    expected_outputs: Dict[str, Any] = field(default_factory=dict)
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    setup_code: Optional[str] = None
    teardown_code: Optional[str] = None


@dataclass
class ExecutionResult:
    """执行结果"""
    case_id: str
    path_id: str
    status: ExecutionStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: float = 0.0
    output: Optional[str] = None
    error: Optional[str] = None
    coverage_data: Dict[str, Any] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)


@dataclass
class CoverageReport:
    """覆盖率报告"""
    total_statements: int = 0
    covered_statements: int = 0
    statement_coverage: float = 0.0
    total_branches: int = 0
    covered_branches: int = 0
    branch_coverage: float = 0.0
    total_paths: int = 0
    covered_paths: int = 0
    path_coverage: float = 0.0
    uncovered_items: List[str] = field(default_factory=list)


@dataclass
class DefectInfo:
    """缺陷信息"""
    defect_id: str
    severity: RiskLevel
    description: str
    location: str
    related_paths: List[str] = field(default_factory=list)
    stack_trace: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)


@dataclass
class Report:
    """测试报告"""
    task_id: str
    coverage: CoverageReport
    summary: Dict[str, Any] = field(default_factory=dict)
    defects: List[DefectInfo] = field(default_factory=list)
    execution_results: List[ExecutionResult] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class LLMRequest:
    """LLM请求"""
    prompt: str
    system_prompt: Optional[str] = None
    model: str = "llama3"
    temperature: float = 0.3
    max_tokens: int = 4096
    stop: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """LLM响应"""
    content: str
    model: str
    finish_reason: str
    usage: Dict[str, int] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class CacheEntry:
    """缓存条目"""
    cache_key: str
    content: Any
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    size_bytes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestStrategy:
    """测试策略"""
    strategy_id: str
    module_priorities: Dict[str, int] = field(default_factory=dict)
    scenario_weights: Dict[str, float] = field(default_factory=dict)
    coverage_depth: str = "medium"
    execution_mode: str = "sequential"
    risk_adaptive: bool = True
    parallel_degree: int = 1


@dataclass
class RequirementMapping:
    """需求-代码映射"""
    requirement_id: str
    requirement_text: str
    covered_functions: List[str] = field(default_factory=list)
    uncovered_functions: List[str] = field(default_factory=list)
    coverage_rate: float = 0.0


@dataclass
class SensitiveCodeLocation:
    """敏感代码位置"""
    file_path: str
    line_start: int
    line_end: int
    sensitivity_type: str
    risk_level: RiskLevel
    description: str


@dataclass
class SystemMetrics:
    """系统指标"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_execution_time: float = 0.0
    cache_hit_rate: float = 0.0
    path_coverage_rate: float = 0.0
    llm_call_count: int = 0
    llm_cache_hit_count: int = 0
