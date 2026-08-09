"""
OpenSource Tool Integrator - 真实的开源工具集成器

集成真实的开源工具，避免重复造轮子！
支持：
- 代码质量检查 (pylint, flake8, mypy)
- 代码格式化 (black, isort)
- 复杂度分析 (radon)
- 安全检查 (bandit)
- 代码覆盖率 (coverage)
"""

import os
import sys
import subprocess
import json
import tempfile
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import logging


class OpenSourceTool(Enum):
    """可用的开源工具列表"""
    PYLINT = "pylint"
    FLAKE8 = "flake8"
    MYPY = "mypy"
    RADON = "radon"
    BANDIT = "bandit"
    BLACK = "black"
    ISORT = "isort"
    COVERAGE = "coverage"


@dataclass
class ToolExecutionResult:
    """工具执行结果"""
    tool: OpenSourceTool
    success: bool
    stdout: str = ""
    stderr: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0
    issues_count: int = 0


class RealToolIntegrator:
    """真实工具集成器 - 真正调用开源工具"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.available_tools: Dict[OpenSourceTool, bool] = {}
        self._check_available_tools()
    
    def _check_available_tools(self) -> None:
        """检查哪些工具可用"""
        for tool in OpenSourceTool:
            self.available_tools[tool] = self._is_tool_available(tool.value)
    
    def _is_tool_available(self, tool_name: str) -> bool:
        """检查工具是否安装"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", tool_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            try:
                result = subprocess.run(
                    [tool_name, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return result.returncode == 0
            except Exception:
                return False
    
    def run_pylint(self, file_path: str) -> ToolExecutionResult:
        """运行pylint进行代码质量检查"""
        result = ToolExecutionResult(tool=OpenSourceTool.PYLINT, success=False)
        
        if not self.available_tools.get(OpenSourceTool.PYLINT, False):
            result.stderr = "pylint not installed"
            return result
        
        try:
            import time
            start = time.time()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                output_file = f.name
            
            try:
                cmd = [
                    sys.executable, "-m", "pylint",
                    "--output-format=json",
                    f"--output={output_file}",
                    file_path
                ]
                
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                result.stdout = proc.stdout
                result.stderr = proc.stderr
                result.success = proc.returncode in [0, 16, 20]  # pylint退出码
                
                if Path(output_file).exists():
                    with open(output_file, 'r', encoding='utf-8') as f:
                        try:
                            result.data = json.load(f)
                            result.issues_count = len(result.data)
                        except Exception as e:
                            result.data = {"raw": proc.stdout}
                
                result.duration = time.time() - start
                
            finally:
                if Path(output_file).exists():
                    try:
                        os.unlink(output_file)
                    except:
                        pass
            
        except Exception as e:
            result.stderr = str(e)
        
        return result
    
    def run_flake8(self, file_path: str) -> ToolExecutionResult:
        """运行flake8进行代码质量检查"""
        result = ToolExecutionResult(tool=OpenSourceTool.FLAKE8, success=False)
        
        if not self.available_tools.get(OpenSourceTool.FLAKE8, False):
            result.stderr = "flake8 not installed"
            return result
        
        try:
            import time
            start = time.time()
            
            cmd = [
                sys.executable, "-m", "flake8",
                "--format=json",
                "--max-line-length=120",
                file_path
            ]
            
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            result.stdout = proc.stdout
            result.stderr = proc.stderr
            result.success = proc.returncode in [0, 1]
            
            try:
                if proc.stdout.strip():
                    result.data = json.loads(proc.stdout)
                    if isinstance(result.data, list):
                        result.issues_count = len(result.data)
                else:
                    result.data = {"status": "clean"}
            except Exception:
                lines = proc.stdout.strip().split('\n')
                result.data = {"raw_lines": lines}
                result.issues_count = len([l for l in lines if l.strip()])
            
            result.duration = time.time() - start
            
        except Exception as e:
            result.stderr = str(e)
        
        return result
    
    def run_radon_cc(self, file_path: str) -> ToolExecutionResult:
        """运行radon进行圈复杂度分析"""
        result = ToolExecutionResult(tool=OpenSourceTool.RADON, success=False)
        
        if not self.available_tools.get(OpenSourceTool.RADON, False):
            result.stderr = "radon not installed"
            return result
        
        try:
            import time
            start = time.time()
            
            cmd = [sys.executable, "-m", "radon", "cc", file_path, "--json"]
            
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            result.stdout = proc.stdout
            result.stderr = proc.stderr
            result.success = proc.returncode == 0
            
            try:
                if proc.stdout.strip():
                    result.data = json.loads(proc.stdout)
            except Exception:
                pass
            
            result.duration = time.time() - start
            
        except Exception as e:
            result.stderr = str(e)
        
        return result
    
    def run_bandit(self, file_path: str) -> ToolExecutionResult:
        """运行bandit进行安全检查"""
        result = ToolExecutionResult(tool=OpenSourceTool.BANDIT, success=False)
        
        if not self.available_tools.get(OpenSourceTool.BANDIT, False):
            result.stderr = "bandit not installed"
            return result
        
        try:
            import time
            start = time.time()
            
            cmd = [
                sys.executable, "-m", "bandit",
                "-f", "json",
                "-r", file_path
            ]
            
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            result.stdout = proc.stdout
            result.stderr = proc.stderr
            result.success = proc.returncode in [0, 1, 2]
            
            try:
                if proc.stdout.strip():
                    result.data = json.loads(proc.stdout)
                    result.issues_count = len(result.data.get("results", []))
            except Exception:
                pass
            
            result.duration = time.time() - start
            
        except Exception as e:
            result.stderr = str(e)
        
        return result
    
    def run_mypy(self, file_path: str) -> ToolExecutionResult:
        """运行mypy进行类型检查"""
        result = ToolExecutionResult(tool=OpenSourceTool.MYPY, success=False)
        
        if not self.available_tools.get(OpenSourceTool.MYPY, False):
            result.stderr = "mypy not installed"
            return result
        
        try:
            import time
            start = time.time()
            
            cmd = [sys.executable, "-m", "mypy", file_path, "--no-error-summary"]
            
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            result.stdout = proc.stdout
            result.stderr = proc.stderr
            result.success = proc.returncode in [0, 1, 2]
            
            if proc.stdout.strip():
                lines = [l for l in proc.stdout.split('\n') if l.strip()]
                result.data = {"raw_lines": lines}
                result.issues_count = len(lines)
            
            result.duration = time.time() - start
            
        except Exception as e:
            result.stderr = str(e)
        
        return result
    
    def run_all_analysis(self, file_path: str) -> Dict[OpenSourceTool, ToolExecutionResult]:
        """运行所有分析工具"""
        results: Dict[OpenSourceTool, ToolExecutionResult] = {}
        
        if Path(file_path).exists() and file_path.endswith('.py'):
            self.logger.info(f"Analyzing file: {file_path}")
            
            if self.available_tools.get(OpenSourceTool.FLAKE8):
                results[OpenSourceTool.FLAKE8] = self.run_flake8(file_path)
            
            if self.available_tools.get(OpenSourceTool.PYLINT):
                results[OpenSourceTool.PYLINT] = self.run_pylint(file_path)
            
            if self.available_tools.get(OpenSourceTool.RADON):
                results[OpenSourceTool.RADON] = self.run_radon_cc(file_path)
            
            if self.available_tools.get(OpenSourceTool.BANDIT):
                results[OpenSourceTool.BANDIT] = self.run_bandit(file_path)
        
        return results
    
    def get_available_tools(self) -> List[OpenSourceTool]:
        """获取可用工具列表"""
        return [tool for tool, available in self.available_tools.items() if available]
    
    def get_tool_status(self) -> Dict[str, bool]:
        """获取工具状态"""
        return {tool.value: available for tool, available in self.available_tools.items()}


# 单例
_integrator_instance: Optional[RealToolIntegrator] = None


def get_real_tool_integrator() -> RealToolIntegrator:
    """获取真实工具集成器"""
    global _integrator_instance
    if _integrator_instance is None:
        _integrator_instance = RealToolIntegrator()
    return _integrator_instance
