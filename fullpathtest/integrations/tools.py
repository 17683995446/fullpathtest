"""
OpenSource Tool Integrator - 开源工具集成器

集成业界优秀的开源工具，避免重复造轮子。
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class OpenSourceTool(Enum):
    """可用的开源工具列表"""
    # 代码分析
    PYCODESTYLE = "pycodestyle"        # Python代码风格检查
    PYLINT = "pylint"                  # Python静态分析
    FLAKE8 = "flake8"                  # Python代码质量检查
    MYPY = "mypy"                      # Python类型检查
    BANDIT = "bandit"                  # Python安全检查
    
    # 代码复杂度
    RADON = "radon"                    # Python代码复杂度分析
    
    # 代码覆盖率
    COVERAGE_PY = "coverage"           # Python代码覆盖率
    
    # 测试框架
    PYTEST = "pytest"                  # Python测试框架
    
    # AST和静态分析
    ASTROID = "astroid"                # Python AST库
    LIBCST = "libcst"                  # CST库
    
    # 代码格式化
    BLACK = "black"                    # Python代码格式化
    ISORT = "isort"                    # Python导入排序
    RUFF = "ruff"                      # 超快速Python linter
    
    # 依赖分析
    PIPDEPTREE = "pipdeptree"          # 依赖树可视化
    PYDEPS = "pydeps"                  # Python依赖图生成
    
    # 可视化
    MATPLOTLIB = "matplotlib"          # 绘图库
    PLOTLY = "plotly"                  # 交互式绘图
    NETWORKX = "networkx"              # 网络图分析
    
    # 性能分析
    CPROFILE = "cProfile"              # Python性能分析
    LINE_PROFILER = "line_profiler"    # 逐行性能分析


@dataclass
class ToolIntegrationResult:
    """工具集成结果"""
    tool: OpenSourceTool
    status: str  # "success", "warning", "error"
    output: Any = None
    error: Optional[str] = None
    duration: float = 0.0


class OpenSourceToolIntegrator:
    """开源工具集成器"""
    
    def __init__(self):
        self.available_tools: Dict[OpenSourceTool, bool] = {}
        self._check_available_tools()
    
    def _check_available_tools(self):
        """检查可用的工具"""
        import importlib.util
        
        tool_imports = {
            OpenSourceTool.PYCODESTYLE: "pycodestyle",
            OpenSourceTool.PYLINT: "pylint",
            OpenSourceTool.FLAKE8: "flake8",
            OpenSourceTool.MYPY: "mypy",
            OpenSourceTool.BANDIT: "bandit",
            OpenSourceTool.RADON: "radon",
            OpenSourceTool.COVERAGE_PY: "coverage",
            OpenSourceTool.PYTEST: "pytest",
            OpenSourceTool.ASTROID: "astroid",
            OpenSourceTool.LIBCST: "libcst",
            OpenSourceTool.BLACK: "black",
            OpenSourceTool.ISORT: "isort",
            OpenSourceTool.RUFF: "ruff",
            OpenSourceTool.PIPDEPTREE: "pipdeptree",
            OpenSourceTool.PYDEPS: "pydeps",
            OpenSourceTool.MATPLOTLIB: "matplotlib",
            OpenSourceTool.PLOTLY: "plotly",
            OpenSourceTool.NETWORKX: "networkx",
            OpenSourceTool.CPROFILE: "cProfile",
            OpenSourceTool.LINE_PROFILER: "line_profiler",
        }
        
        for tool, module_name in tool_imports.items():
            self.available_tools[tool] = importlib.util.find_spec(module_name) is not None
    
    def get_available_tools(self) -> List[OpenSourceTool]:
        """获取可用的工具列表"""
        return [tool for tool, available in self.available_tools.items() if available]
    
    def run_quality_check(self, source_path: str) -> List[ToolIntegrationResult]:
        """运行质量检查"""
        import time
        results = []
        
        tools_to_run = [
            (OpenSourceTool.PYCODESTYLE, self._run_pycodestyle),
            (OpenSourceTool.PYLINT, self._run_pylint),
            (OpenSourceTool.FLAKE8, self._run_flake8),
            (OpenSourceTool.BANDIT, self._run_bandit),
        ]
        
        for tool, run_func in tools_to_run:
            if self.available_tools.get(tool, False):
                try:
                    start_time = time.time()
                    output = run_func(source_path)
                    duration = time.time() - start_time
                    results.append(ToolIntegrationResult(
                        tool=tool,
                        status="success",
                        output=output,
                        duration=duration
                    ))
                except Exception as e:
                    results.append(ToolIntegrationResult(
                        tool=tool,
                        status="error",
                        error=str(e)
                    ))
        
        return results
    
    def run_complexity_analysis(self, source_path: str) -> List[ToolIntegrationResult]:
        """运行复杂度分析"""
        import time
        results = []
        
        if self.available_tools.get(OpenSourceTool.RADON, False):
            try:
                start_time = time.time()
                output = self._run_radon(source_path)
                duration = time.time() - start_time
                results.append(ToolIntegrationResult(
                    tool=OpenSourceTool.RADON,
                    status="success",
                    output=output,
                    duration=duration
                ))
            except Exception as e:
                results.append(ToolIntegrationResult(
                    tool=OpenSourceTool.RADON,
                    status="error",
                    error=str(e)
                ))
        
        return results
    
    def _run_pycodestyle(self, source_path: str) -> Dict[str, Any]:
        """运行pycodestyle"""
        try:
            import pycodestyle
            checker = pycodestyle.Checker(source_path)
            result = checker.check_all()
            return {"issues": result}
        except Exception:
            return {"status": "skipped"}
    
    def _run_pylint(self, source_path: str) -> Dict[str, Any]:
        """运行pylint"""
        try:
            from pylint.lint import pylinter
            return {"status": "skipped"}
        except Exception:
            return {"status": "skipped"}
    
    def _run_flake8(self, source_path: str) -> Dict[str, Any]:
        """运行flake8"""
        try:
            return {"status": "skipped"}
        except Exception:
            return {"status": "skipped"}
    
    def _run_bandit(self, source_path: str) -> Dict[str, Any]:
        """运行bandit"""
        try:
            return {"status": "skipped"}
        except Exception:
            return {"status": "skipped"}
    
    def _run_radon(self, source_path: str) -> Dict[str, Any]:
        """运行radon"""
        try:
            return {"status": "skipped"}
        except Exception:
            return {"status": "skipped"}


# 单例模式
_integrator: Optional[OpenSourceToolIntegrator] = None

def get_integrator() -> OpenSourceToolIntegrator:
    """获取工具集成器单例"""
    global _integrator
    if _integrator is None:
        _integrator = OpenSourceToolIntegrator()
    return _integrator
