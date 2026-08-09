"""
FullPathTest - 极致轻量化全路径代码测试系统 V4.0

完整的50层架构全路径代码测试系统。
"""

__version__ = "4.0.0"
__author__ = "FullPathTest Team"

from fullpathtest.types.core import (
    TaskRequest,
    TaskContext,
    TaskState,
    ConfigSnapshot,
    SourceType,
    LLMMode,
    LanguageType,
    RiskLevel,
    Path,
    PathSet,
    PathType,
    ControlFlowGraph,
    FunctionSlice,
    Token,
    ASTNode,
)

from fullpathtest.integration import FullPathTestSystem, create_system, SystemConfig

__all__ = [
    # 核心类型
    "TaskRequest",
    "TaskContext",
    "TaskState",
    "ConfigSnapshot",
    "SourceType",
    "LLMMode",
    "LanguageType",
    "RiskLevel",
    "Path",
    "PathSet",
    "PathType",
    "ControlFlowGraph",
    "FunctionSlice",
    "Token",
    "ASTNode",
    # 系统集成
    "FullPathTestSystem",
    "create_system",
    "SystemConfig",
]
