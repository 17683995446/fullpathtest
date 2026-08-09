"""
第23层：依赖关系图构建层
职责：构建模块间、函数间、文件间的完整依赖关系图，支持循环检测、依赖分析、影响范围计算。
输入：源代码文件集合、函数签名集合、导入声明集合。
输出：DependencyGraph、ModuleDependencyMap、ImpactAnalysisResult。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
from enum import Enum
import hashlib
from collections import defaultdict


class DependencyType(Enum):
    """依赖类型"""
    IMPORT = "import"                        # 导入依赖
    INHERIT = "inherit"                      # 继承依赖
    COMPOSITION = "composition"              # 组合依赖
    AGGREGATION = "aggregation"             # 聚合依赖
    ASSOCIATION = "association"              # 关联依赖
    CALL = "call"                           # 函数调用依赖
    PARAMETER = "parameter"                 # 参数依赖
    RETURN = "return"                       # 返回值依赖
    GLOBAL = "global"                       # 全局变量依赖


class DependencyScope(Enum):
    """依赖范围"""
    FILE_LEVEL = "file_level"               # 文件级
    FUNCTION_LEVEL = "function_level"        # 函数级
    CLASS_LEVEL = "class_level"             # 类级
    MODULE_LEVEL = "module_level"           # 模块级
    PACKAGE_LEVEL = "package_level"        # 包级


@dataclass
class DependencyNode:
    """依赖图节点"""
    node_id: str
    name: str
    node_type: DependencyScope
    file_path: str
    line_number: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.node_id)
    
    def __eq__(self, other):
        if not isinstance(other, DependencyNode):
            return False
        return self.node_id == other.node_id


@dataclass
class DependencyEdge:
    """依赖边"""
    source_id: str
    target_id: str
    dependency_type: DependencyType
    weight: float = 1.0                       # 依赖权重
    is_cyclic: bool = False                  # 是否在循环中
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
    
    def add_node(self, node: DependencyNode):
        """添加节点"""
        self.nodes.append(node)
        if node.node_id not in self.adjacency_list:
            self.adjacency_list[node.node_id] = []
        if node.node_id not in self.reverse_adjacency:
            self.reverse_adjacency[node.node_id] = []
    
    def add_edge(self, edge: DependencyEdge):
        """添加边"""
        self.edges.append(edge)
        if edge.source_id not in self.adjacency_list:
            self.adjacency_list[edge.source_id] = []
        self.adjacency_list[edge.source_id].append(edge.target_id)
        
        if edge.target_id not in self.reverse_adjacency:
            self.reverse_adjacency[edge.target_id] = []
        self.reverse_adjacency[edge.target_id].append(edge.source_id)
    
    def get_node_by_id(self, node_id: str) -> Optional[DependencyNode]:
        """根据ID获取节点"""
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None
    
    def get_dependencies(self, node_id: str) -> List[DependencyEdge]:
        """获取节点的依赖（出边）"""
        return [e for e in self.edges if e.source_id == node_id]
    
    def get_dependents(self, node_id: str) -> List[DependencyEdge]:
        """获取依赖该节点的节点（入边）"""
        return [e for e in self.edges if e.target_id == node_id]
    
    def find_cycles(self) -> List[List[str]]:
        """检测循环依赖"""
        visited = set()
        rec_stack = set()
        cycles = []
        path = []
        
        def dfs(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)
            
            for neighbor in self.adjacency_list.get(node_id, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
            
            path.pop()
            rec_stack.remove(node_id)
            return False
        
        for node in self.nodes:
            if node.node_id not in visited:
                dfs(node.node_id)
        
        return cycles
    
    def topological_sort(self) -> List[str]:
        """拓扑排序"""
        in_degree = defaultdict(int)
        for edge in self.edges:
            in_degree[edge.target_id] += 1
        
        queue = [node.node_id for node in self.nodes if in_degree[node.node_id] == 0]
        result = []
        
        while queue:
            node_id = queue.pop(0)
            result.append(node_id)
            
            for neighbor in self.adjacency_list.get(node_id, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    def compute_impact_set(self, node_id: str) -> Set[str]:
        """计算影响集合"""
        impact = set()
        visited = set()
        queue = [node_id]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            impact.add(current)
            
            for neighbor in self.adjacency_list.get(current, []):
                if neighbor not in visited:
                    queue.append(neighbor)
        
        return impact


@dataclass
class ModuleDependency:
    """模块依赖"""
    module_name: str
    file_path: str
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    is_leaf: bool = False                     # 是否为叶子模块
    is_entry: bool = False                   # 是否为入口模块


@dataclass
class ModuleDependencyMap:
    """模块依赖映射"""
    modules: Dict[str, ModuleDependency] = field(default_factory=dict)
    cross_module_calls: List[Tuple[str, str]] = field(default_factory=list)
    
    def add_module(self, module: ModuleDependency):
        """添加模块"""
        self.modules[module.module_name] = module
    
    def get_dependency_chain(self, from_module: str, to_module: str) -> List[str]:
        """获取依赖链"""
        if from_module not in self.modules or to_module not in self.modules:
            return []
        
        visited = set()
        queue = [(from_module, [from_module])]
        
        while queue:
            current, path = queue.pop(0)
            if current == to_module:
                return path
            
            if current in visited:
                continue
            visited.add(current)
            
            module = self.modules.get(current)
            if module:
                for dep in module.dependencies:
                    if dep not in visited:
                        queue.append((dep, path + [dep]))
        
        return []
    
    def find_leaf_modules(self) -> List[str]:
        """查找叶子模块（没有依赖其他模块）"""
        return [m.module_name for m in self.modules.values() if m.is_leaf]


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


class DependencyGraphBuilder:
    """依赖关系图构建器"""
    
    def __init__(self):
        self.graph = None
        self.module_map = None
    
    def build_from_source_files(self, source_files: List[Any]) -> DependencyGraph:
        """从源文件构建依赖图"""
        graph_id = hashlib.md5("dependency_graph".encode()).hexdigest()
        self.graph = DependencyGraph(graph_id=graph_id)
        
        for file in source_files:
            self._process_file(file)
        
        self._detect_cyclic_dependencies()
        
        return self.graph
    
    def _process_file(self, file: Any):
        """处理单个文件"""
        file_node = DependencyNode(
            node_id=hashlib.md5(f"file_{file.path}".encode()).hexdigest(),
            name=file.path,
            node_type=DependencyScope.FILE_LEVEL,
            file_path=file.path
        )
        self.graph.add_node(file_node)
        
        if hasattr(file, 'imports'):
            for imp in file.imports:
                self._process_import(file.path, imp)
        
        if hasattr(file, 'functions'):
            for func in file.functions:
                self._process_function(file.path, func)
    
    def _process_import(self, source_file: str, imp: Any):
        """处理导入语句"""
        pass
    
    def _process_function(self, file_path: str, func: Any):
        """处理函数"""
        func_node = DependencyNode(
            node_id=hashlib.md5(f"func_{file_path}_{func.name}".encode()).hexdigest(),
            name=func.name,
            node_type=DependencyScope.FUNCTION_LEVEL,
            file_path=file_path,
            line_number=getattr(func, 'line_number', None)
        )
        self.graph.add_node(func_node)
    
    def _detect_cyclic_dependencies(self):
        """检测循环依赖"""
        cycles = self.graph.find_cycles()
        
        for cycle in cycles:
            for i in range(len(cycle) - 1):
                for edge in self.graph.edges:
                    if edge.source_id == cycle[i] and edge.target_id == cycle[i + 1]:
                        edge.is_cyclic = True
    
    def analyze_impact(self, module_name: str) -> ImpactAnalysisResult:
        """分析模块变更影响"""
        target_id = None
        for node in self.graph.nodes:
            if node.name == module_name:
                target_id = node.node_id
                break
        
        if not target_id:
            return ImpactAnalysisResult(target_module=module_name)
        
        all_affected = self.graph.compute_impact_set(target_id)
        
        direct = {e.source_id for e in self.graph.get_dependents(target_id)}
        indirect = all_affected - direct - {target_id}
        
        result = ImpactAnalysisResult(
            target_module=module_name,
            direct_dependents=direct,
            indirect_dependents=indirect,
            total_affected_modules=all_affected
        )
        
        if len(all_affected) > 10:
            result.risk_level = "HIGH"
            result.recommendations.append("变更风险较高，建议分批发布")
        elif len(all_affected) > 5:
            result.risk_level = "MEDIUM"
            result.recommendations.append("建议进行完整的回归测试")
        else:
            result.risk_level = "LOW"
            result.recommendations.append("变更影响较小，进行基本测试即可")
        
        return result
    
    def build_module_map(self) -> ModuleDependencyMap:
        """构建模块依赖映射"""
        self.module_map = ModuleDependencyMap()
        
        for node in self.graph.nodes:
            if node.node_type == DependencyScope.FILE_LEVEL:
                module = ModuleDependency(
                    module_name=node.name,
                    file_path=node.file_path
                )
                self.module_map.add_module(module)
        
        return self.module_map
    
    def get_graph(self) -> Optional[DependencyGraph]:
        """获取依赖图"""
        return self.graph
    
    def get_module_map(self) -> Optional[ModuleDependencyMap]:
        """获取模块映射"""
        return self.module_map
