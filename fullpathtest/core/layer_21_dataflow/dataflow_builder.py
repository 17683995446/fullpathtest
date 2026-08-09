"""
第21层：数据流图构建层
职责：根据代码的数据读写、变量传递、函数调用关系，构建完整的数据流图（DFG）。
输入：AST、CFG、函数依赖图。
输出：DataFlowGraph、DataDependencySet。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from enum import Enum
import hashlib


class DataFlowNodeType(Enum):
    """数据流节点类型"""
    VARIABLE_DECLARE = "variable_declare"      # 变量声明
    VARIABLE_READ = "variable_read"            # 变量读取
    VARIABLE_WRITE = "variable_write"          # 变量写入
    FUNCTION_CALL = "function_call"           # 函数调用
    PARAMETER_PASS = "parameter_pass"         # 参数传递
    RETURN_VALUE = "return_value"             # 返回值
    FIELD_ACCESS = "field_access"             # 字段访问
    ARRAY_INDEX = "array_index"               # 数组索引


class DataFlowEdgeType(Enum):
    """数据流边类型"""
    DEFINITION_USE = "definition_use"         # 定义-使用链
    CONTROL_DEPENDENCY = "control_dependency" # 控制依赖
    DATA_DEPENDENCY = "data_dependency"       # 数据依赖
    CALL_GRAPH = "call_graph"                # 调用图


@dataclass
class DataFlowNode:
    """数据流图节点"""
    node_id: str
    node_type: DataFlowNodeType
    name: str
    line_number: int
    scope: str                               # 作用域
    data_type: Optional[str] = None          # 数据类型
    value: Optional[Any] = None               # 值（如果已知）
    is_parameter: bool = False               # 是否为参数
    is_global: bool = False                  # 是否为全局变量
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.node_id)
    
    def __eq__(self, other):
        if not isinstance(other, DataFlowNode):
            return False
        return self.node_id == other.node_id


@dataclass
class DataFlowEdge:
    """数据流图边"""
    source_id: str
    target_id: str
    edge_type: DataFlowEdgeType
    variable_name: Optional[str] = None      # 关联的变量名
    is_alias: bool = False                   # 是否为别名关系
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
    
    def add_node(self, node: DataFlowNode):
        """添加节点"""
        self.nodes.append(node)
    
    def add_edge(self, edge: DataFlowEdge):
        """添加边"""
        self.edges.append(edge)
    
    def get_node_by_id(self, node_id: str) -> Optional[DataFlowNode]:
        """根据ID获取节点"""
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None
    
    def get_outgoing_edges(self, node_id: str) -> List[DataFlowEdge]:
        """获取节点的出边"""
        return [e for e in self.edges if e.source_id == node_id]
    
    def get_incoming_edges(self, node_id: str) -> List[DataFlowEdge]:
        """获取节点的入边"""
        return [e for e in self.edges if e.target_id == node_id]
    
    def compute_def_use_chains(self) -> Dict[str, List[str]]:
        """计算定义-使用链"""
        def_use = {}
        definitions = {}
        
        for edge in self.edges:
            if edge.edge_type == DataFlowEdgeType.DEFINITION_USE:
                var_name = edge.variable_name
                if var_name:
                    if edge.source_id not in definitions:
                        definitions[edge.source_id] = []
                    definitions[edge.source_id].append(edge.target_id)
                    def_use[edge.source_id] = definitions[edge.source_id]
        
        return def_use


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
    dependency_type: str                     # READ, WRITE, READ_WRITE
    is_transitive: bool = False               # 是否为传递依赖


@dataclass
class DataDependencySet:
    """数据依赖集合"""
    dependencies: List[DataDependency] = field(default_factory=list)
    global_variables: Set[str] = field(default_factory=set)
    parameter_flows: Dict[str, List[str]] = field(default_factory=dict)  # 参数->使用的映射
    return_value_flows: Dict[str, List[str]] = field(default_factory=dict)  # 返回值->使用的映射
    
    def add_dependency(self, dep: DataDependency):
        """添加依赖"""
        self.dependencies.append(dep)
    
    def get_function_dependencies(self, function_name: str) -> List[DataDependency]:
        """获取函数的依赖关系"""
        return [d for d in self.dependencies 
                if d.target_function == function_name]
    
    def get_transitive_dependencies(self) -> List[DataDependency]:
        """获取传递依赖"""
        return [d for d in self.dependencies if d.is_transitive]


class DataFlowGraphBuilder:
    """数据流图构建器"""
    
    def __init__(self):
        self.graphs: Dict[str, DataFlowGraph] = {}
        self.dependency_set = DataDependencySet()
    
    def build_graph(self, ast: Any, cfg: Any, function_name: str) -> DataFlowGraph:
        """构建数据流图"""
        graph_id = hashlib.md5(f"{function_name}_{id(ast)}".encode()).hexdigest()
        
        graph = DataFlowGraph(
            graph_id=graph_id,
            function_name=function_name
        )
        
        self._analyze_variable_flows(ast, graph)
        self._analyze_function_calls(ast, graph)
        self._analyze_parameters(ast, graph)
        self._analyze_returns(ast, graph)
        
        self.graphs[function_name] = graph
        return graph
    
    def _analyze_variable_flows(self, ast: Any, graph: DataFlowGraph):
        """分析变量数据流"""
        pass
    
    def _analyze_function_calls(self, ast: Any, graph: DataFlowGraph):
        """分析函数调用"""
        pass
    
    def _analyze_parameters(self, ast: Any, graph: DataFlowGraph):
        """分析参数传递"""
        pass
    
    def _analyze_returns(self, ast: Any, graph: DataFlowGraph):
        """分析返回值"""
        pass
    
    def build_dependency_graph(self, graphs: Dict[str, DataFlowGraph]) -> DataDependencySet:
        """构建跨函数的依赖图"""
        for func_name, graph in graphs.items():
            for edge in graph.edges:
                if edge.edge_type == DataFlowEdgeType.CALL_GRAPH:
                    source_node = graph.get_node_by_id(edge.source_id)
                    if source_node:
                        dep = DataDependency(
                            source_file=source_node.metadata.get("file", ""),
                            source_function=func_name,
                            source_line=source_node.line_number,
                            target_file=edge.metadata.get("target_file", ""),
                            target_function=edge.metadata.get("target_function", ""),
                            target_line=edge.metadata.get("target_line", 0),
                            variable_name=edge.variable_name or "",
                            dependency_type="CALL"
                        )
                        self.dependency_set.add_dependency(dep)
        
        return self.dependency_set
    
    def get_all_graphs(self) -> Dict[str, DataFlowGraph]:
        """获取所有数据流图"""
        return self.graphs
