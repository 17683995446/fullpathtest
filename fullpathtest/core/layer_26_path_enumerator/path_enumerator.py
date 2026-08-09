"""
第26层：全路径枚举生成层

基于带标记CFG进行深度优先遍历，生成全路径。
"""

from typing import List, Dict, Set, Optional, Tuple
from fullpathtest.types.core import (
    Path, PathSet, PathType, ControlFlowGraph, CFGNode, SemanticPath, RiskLevel
)
import uuid
from collections import deque


class PathEnumerator:
    """路径枚举器"""
    
    def __init__(self, max_depth: int = 100, max_paths: int = 10000):
        self.max_depth = max_depth
        self.max_paths = max_paths
        self.enumerated_count = 0
    
    def enumerate_paths(
        self,
        cfg: ControlFlowGraph,
        coverage_rules: Dict = None
    ) -> PathSet:
        """枚举所有路径"""
        paths = []
        path_ids = set()
        
        self._enumerate_dfs(cfg, cfg.entry_node, [], paths, path_ids)
        
        return PathSet(
            paths=paths,
            total_count=len(paths),
            pruned_count=0,
            unreachable_count=0
        )
    
    def _enumerate_dfs(
        self,
        cfg: ControlFlowGraph,
        current: str,
        path: List[str],
        paths: List[Path],
        path_ids: Set[str]
    ) -> None:
        """深度优先路径枚举"""
        if self.enumerated_count >= self.max_paths:
            return
        
        if len(path) > self.max_depth:
            return
        
        path = path + [current]
        
        node = cfg.nodes.get(current)
        if not node:
            return
        
        if node.node_type == 'exit':
            path_obj = self._create_path(cfg, path)
            paths.append(path_obj)
            self.enumerated_count += 1
            return
        
        for successor in node.successors:
            self._enumerate_dfs(cfg, successor, path, paths, path_ids)
    
    def _create_path(self, cfg: ControlFlowGraph, node_sequence: List[str]) -> Path:
        """创建路径对象"""
        conditions = []
        for node_id in node_sequence:
            node = cfg.nodes.get(node_id)
            if node and node.node_type == 'branch':
                conditions.append(f"branch at {node_id}")
        
        return Path(
            path_id=f"PATH_{uuid.uuid4().hex[:12]}",
            path_type=PathType.INTRAPROCEDURAL,
            cfgs=[cfg],
            node_sequence=node_sequence,
            conditions=conditions,
            constraints={},
            priority=5,
            estimated_execution_time=len(node_sequence) * 0.01
        )
    
    def enumerate_with_loops(
        self,
        cfg: ControlFlowGraph,
        max_loop_unrolls: int = 3
    ) -> List[Path]:
        """带循环展开的路径枚举"""
        paths = []
        self._enumerate_with_unroll(cfg, cfg.entry_node, [], paths, 0, max_loop_unrolls)
        return paths
    
    def _enumerate_with_unroll(
        self,
        cfg: ControlFlowGraph,
        current: str,
        path: List[str],
        paths: List[Path],
        loop_count: int,
        max_unrolls: int
    ) -> None:
        """带展开计数的枚举"""
        if self.enumerated_count >= self.max_paths:
            return
        
        path = path + [current]
        
        node = cfg.nodes.get(current)
        if not node:
            return
        
        if node.node_type == 'exit':
            path_obj = self._create_path(cfg, path)
            paths.append(path_obj)
            self.enumerated_count += 1
            return
        
        if node.node_type == 'loop':
            if loop_count >= max_unrolls:
                if node.successors:
                    self._enumerate_with_unroll(
                        cfg,
                        node.successors[-1],
                        path,
                        paths,
                        0,
                        max_unrolls
                    )
                return
            else:
                for successor in node.successors:
                    self._enumerate_with_unroll(
                        cfg,
                        successor,
                        path,
                        paths,
                        loop_count + 1 if node.node_type == 'loop' else 0,
                        max_unrolls
                    )
        else:
            for successor in node.successors:
                self._enumerate_with_unroll(
                    cfg,
                    successor,
                    path,
                    paths,
                    0,
                    max_unrolls
                )


class InterproceduralPathEnumerator:
    """跨函数路径枚举器"""
    
    def __init__(self):
        self.enumerator = PathEnumerator()
    
    def enumerate_cross_function_paths(
        self,
        cfgs: Dict[str, ControlFlowGraph],
        call_graph: Dict[str, List[str]]
    ) -> PathSet:
        """枚举跨函数路径"""
        all_paths = []
        
        for func_name, cfg in cfgs.items():
            paths = self.enumerator.enumerate_paths(cfg)
            all_paths.extend(paths)
        
        return PathSet(
            paths=all_paths,
            total_count=len(all_paths),
            pruned_count=0,
            unreachable_count=0
        )


class PathFactory:
    """路径工厂"""
    
    @staticmethod
    def create_path(
        path_id: str,
        path_type: PathType,
        node_sequence: List[str],
        conditions: List[str] = None,
        risk_level: RiskLevel = RiskLevel.MEDIUM
    ) -> Path:
        """创建路径"""
        return Path(
            path_id=path_id,
            path_type=path_type,
            node_sequence=node_sequence,
            conditions=conditions or [],
            constraints={},
            priority=5,
            estimated_execution_time=len(node_sequence) * 0.01
        )
    
    @staticmethod
    def create_semantic_path(
        path: Path,
        business_scenarios: List[str],
        risk_level: RiskLevel
    ) -> SemanticPath:
        """创建语义路径"""
        return SemanticPath(
            path_id=path.path_id,
            path_type=path.path_type,
            nodes=path.node_sequence,
            business_scenarios=business_scenarios,
            risk_level=risk_level,
            coverage_requirements=[],
            constraint_conditions={},
            is_reachable=True,
            is_essential=False
        )
