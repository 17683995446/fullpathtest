"""
第22层：控制流CFG构建层

构建函数内控制流图CFG。
"""

from typing import List, Dict, Set, Optional
from fullpathtest.types.core import ControlFlowGraph, CFGNode, FunctionSlice, ASTNode
import uuid


class CFGBuilder:
    """控制流图构建器"""
    
    def __init__(self):
        self.cfg: Optional[ControlFlowGraph] = None
    
    def build(self, function: FunctionSlice, ast: ASTNode = None) -> ControlFlowGraph:
        """构建控制流图"""
        cfg_id = str(uuid.uuid4())[:8]
        
        cfg = ControlFlowGraph(
            function_name=function.name,
            file_path=function.file_path,
            nodes={},
            entry_node=f"{cfg_id}_entry",
            exit_nodes=[],
            loop_nodes=[],
            branch_nodes=[]
        )
        
        entry_node = CFGNode(
            node_id=cfg.entry_node,
            node_type='entry',
            statements=[f"Function {function.name} starts"],
            line_start=function.start_line,
            line_end=function.start_line
        )
        cfg.nodes[cfg.entry_node] = entry_node
        
        current_node_id = f"{cfg_id}_0"
        current_node = CFGNode(
            node_id=current_node_id,
            node_type='statement',
            statements=[],
            line_start=function.start_line,
            line_end=function.start_line
        )
        cfg.nodes[current_node_id] = current_node
        entry_node.successors.append(current_node_id)
        
        if ast:
            self._process_ast_nodes(cfg, ast, current_node_id, cfg_id)
        
        exit_node_id = f"{cfg_id}_exit"
        exit_node = CFGNode(
            node_id=exit_node_id,
            node_type='exit',
            statements=[f"Function {function.name} ends"],
            line_start=function.end_line,
            line_end=function.end_line
        )
        cfg.nodes[exit_node_id] = exit_node
        cfg.exit_nodes.append(exit_node_id)
        
        last_statement_node = self._find_last_statement_node(cfg)
        if last_statement_node:
            last_statement_node.successors.append(exit_node_id)
            exit_node.predecessors.append(last_statement_node.node_id)
        
        self.cfg = cfg
        return cfg
    
    def _process_ast_nodes(
        self,
        cfg: ControlFlowGraph,
        node: ASTNode,
        current_node_id: str,
        cfg_id: str
    ) -> Optional[str]:
        """处理AST节点"""
        if node.node_type == 'IF':
            return self._process_if_node(cfg, node, current_node_id, cfg_id)
        elif node.node_type == 'LOOP':
            return self._process_loop_node(cfg, node, current_node_id, cfg_id)
        elif node.node_type == 'RETURN':
            return self._process_return_node(cfg, node, current_node_id)
        else:
            return self._update_current_node(cfg, node, current_node_id)
    
    def _process_if_node(
        self,
        cfg: ControlFlowGraph,
        node: ASTNode,
        current_node_id: str,
        cfg_id: str
    ) -> str:
        """处理if节点"""
        branch_id = f"{cfg_id}_branch_{len(cfg.branch_nodes)}"
        branch_node = CFGNode(
            node_id=branch_id,
            node_type='branch',
            statements=[f"if condition"],
            line_start=node.line,
            line_end=node.line
        )
        cfg.nodes[branch_id] = branch_node
        cfg.branch_nodes.append(branch_id)
        
        cfg.nodes[current_node_id].successors.append(branch_id)
        branch_node.predecessors.append(current_node_id)
        
        true_id = f"{cfg_id}_true_{len(cfg.nodes)}"
        true_node = CFGNode(
            node_id=true_id,
            node_type='statement',
            statements=['if true branch'],
            line_start=node.line,
            line_end=node.line
        )
        cfg.nodes[true_id] = true_node
        branch_node.successors.append(true_id)
        true_node.predecessors.append(branch_id)
        
        false_id = f"{cfg_id}_false_{len(cfg.nodes)}"
        false_node = CFGNode(
            node_id=false_id,
            node_type='statement',
            statements=['if false branch'],
            line_start=node.line,
            line_end=node.line
        )
        cfg.nodes[false_id] = false_node
        branch_node.successors.append(false_id)
        false_node.predecessors.append(branch_id)
        
        merge_id = f"{cfg_id}_merge_{len(cfg.nodes)}"
        merge_node = CFGNode(
            node_id=merge_id,
            node_type='merge',
            statements=[],
            line_start=node.line,
            line_end=node.line
        )
        cfg.nodes[merge_id] = merge_node
        true_node.successors.append(merge_id)
        false_node.successors.append(merge_id)
        merge_node.predecessors.extend([true_id, false_id])
        
        return merge_id
    
    def _process_loop_node(
        self,
        cfg: ControlFlowGraph,
        node: ASTNode,
        current_node_id: str,
        cfg_id: str
    ) -> str:
        """处理循环节点"""
        loop_id = f"{cfg_id}_loop_{len(cfg.loop_nodes)}"
        loop_node = CFGNode(
            node_id=loop_id,
            node_type='loop',
            statements=[f"while loop"],
            line_start=node.line,
            line_end=node.line
        )
        cfg.nodes[loop_id] = loop_node
        cfg.loop_nodes.append(loop_id)
        
        cfg.nodes[current_node_id].successors.append(loop_id)
        loop_node.predecessors.append(current_node_id)
        
        body_id = f"{cfg_id}_body_{len(cfg.nodes)}"
        body_node = CFGNode(
            node_id=body_id,
            node_type='statement',
            statements=['loop body'],
            line_start=node.line,
            line_end=node.line
        )
        cfg.nodes[body_id] = body_node
        loop_node.successors.append(body_id)
        body_node.predecessors.append(loop_id)
        
        body_node.successors.append(loop_id)
        loop_node.predecessors.append(body_id)
        
        return loop_id
    
    def _process_return_node(
        self,
        cfg: ControlFlowGraph,
        node: ASTNode,
        current_node_id: str
    ) -> str:
        """处理return节点"""
        cfg.nodes[current_node_id].node_type = 'return'
        cfg.nodes[current_node_id].statements.append(f"return at line {node.line}")
        return current_node_id
    
    def _update_current_node(
        self,
        cfg: ControlFlowGraph,
        node: ASTNode,
        current_node_id: str
    ) -> str:
        """更新当前节点"""
        if node.value:
            cfg.nodes[current_node_id].statements.append(node.value)
        return current_node_id
    
    def _find_last_statement_node(self, cfg: ControlFlowGraph) -> Optional[CFGNode]:
        """查找最后一个语句节点"""
        for node_id in reversed(cfg.nodes.keys()):
            node = cfg.nodes[node_id]
            if node.node_type == 'statement':
                return node
        return None
    
    def get_paths(self, cfg: ControlFlowGraph) -> List[List[str]]:
        """获取CFG中的所有路径"""
        paths = []
        self._dfs_paths(cfg, cfg.entry_node, [], paths)
        return paths
    
    def _dfs_paths(
        self,
        cfg: ControlFlowGraph,
        current: str,
        path: List[str],
        paths: List[List[str]]
    ) -> None:
        """深度优先遍历路径"""
        path = path + [current]
        node = cfg.nodes.get(current)
        
        if not node:
            return
        
        if node.node_type == 'exit':
            paths.append(path)
            return
        
        if node.node_type == 'loop' and len(path) > 100:
            paths.append(path)
            return
        
        for successor in node.successors:
            self._dfs_paths(cfg, successor, path, paths)
