"""
Open source tools integration system.
Provides integration with real open source tools for code quality analysis.
"""

import os
import sys
import subprocess
import json
import tempfile
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import logging


class OpenSourceToolName(Enum):
    """Enumeration of supported open source tools."""
    PYLINT_TOOL = "pylint"
    FLAKE8_TOOL = "flake8"
    MYPY_TOOL = "mypy"
    RADON_TOOL = "radon"
    BANDIT_TOOL = "bandit"
    BLACK_TOOL = "black"
    ISORT_TOOL = "isort"
    COVERAGE_TOOL = "coverage"


@dataclass
class OpenSourceToolExecutionResult:
    """Result data from executing an open source tool."""
    tool_name: OpenSourceToolName
    execution_successful: bool
    standard_output: str = ""
    standard_error: str = ""
    parsed_data: Dict[str, Any] = field(default_factory=dict)
    execution_duration: float = 0.0
    detected_issues_count: int = 0


class RealOpenSourceToolIntegrator:
    """Integration system for working with real open source tools."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.available_tools_cache: Dict[OpenSourceToolName, bool] = {}
        self._check_tool_availability()

    def _check_tool_availability(self) -> None:
        """Check which open source tools are available in the environment."""
        for tool in OpenSourceToolName:
            self.available_tools_cache[tool] = self._is_single_tool_available(tool.value)

    def _is_single_tool_available(self, tool_name: str) -> bool:
        """Check if a specific tool is installed and available."""
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

    def execute_flake8_analysis(self, target_file_path: str) -> OpenSourceToolExecutionResult:
        """Run flake8 analysis on a target Python file."""
        result = OpenSourceToolExecutionResult(
            tool_name=OpenSourceToolName.FLAKE8_TOOL,
            execution_successful=False
        )
        
        if not self.available_tools_cache.get(OpenSourceToolName.FLAKE8_TOOL, False):
            result.standard_error = "flake8 tool is not available in current environment"
            return result
        
        try:
            import time
            start_time = time.time()
            
            command = [
                sys.executable, "-m", "flake8",
                "--format=json",
                "--max-line-length=120",
                target_file_path
            ]
            
            process_result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            result.standard_output = process_result.stdout
            result.standard_error = process_result.stderr
            result.execution_successful = process_result.returncode in [0, 1]
            
            try:
                if process_result.stdout.strip():
                    result.parsed_data = json.loads(process_result.stdout)
                    if isinstance(result.parsed_data, list):
                        result.detected_issues_count = len(result.parsed_data)
                else:
                    result.parsed_data = {"status": "clean"}
            except Exception:
                lines = process_result.stdout.strip().split('\n')
                result.parsed_data = {"raw_lines": lines}
                result.detected_issues_count = len([l for l in lines if l.strip()])
            
            result.execution_duration = time.time() - start_time
            
        except Exception as error:
            result.standard_error = str(error)
        
        return result

    def execute_pylint_analysis(self, target_file_path: str) -> OpenSourceToolExecutionResult:
        """Run pylint analysis on a target Python file."""
        result = OpenSourceToolExecutionResult(
            tool_name=OpenSourceToolName.PYLINT_TOOL,
            execution_successful=False
        )
        
        if not self.available_tools_cache.get(OpenSourceToolName.PYLINT_TOOL, False):
            result.standard_error = "pylint tool is not available in current environment"
            return result
        
        try:
            import time
            start_time = time.time()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                temp_output_file = temp_file.name
            
            try:
                command = [
                    sys.executable, "-m", "pylint",
                    "--output-format=json",
                    f"--output={temp_output_file}",
                    target_file_path
                ]
                
                process_result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                result.standard_output = process_result.stdout
                result.standard_error = process_result.stderr
                result.execution_successful = process_result.returncode in [0, 16, 20]
                
                if Path(temp_output_file).exists():
                    with open(temp_output_file, 'r', encoding='utf-8') as f:
                        try:
                            result.parsed_data = json.load(f)
                            result.detected_issues_count = len(result.parsed_data)
                        except Exception:
                            pass
                
                result.execution_duration = time.time() - start_time
                
            finally:
                if Path(temp_output_file).exists():
                    try:
                        os.unlink(temp_output_file)
                    except Exception:
                        pass
            
        except Exception as error:
            result.standard_error = str(error)
        
        return result

    def execute_radon_analysis(self, target_file_path: str) -> OpenSourceToolExecutionResult:
        """Run radon complexity analysis on a target Python file."""
        result = OpenSourceToolExecutionResult(
            tool_name=OpenSourceToolName.RADON_TOOL,
            execution_successful=False
        )
        
        if not self.available_tools_cache.get(OpenSourceToolName.RADON_TOOL, False):
            result.standard_error = "radon tool is not available in current environment"
            return result
        
        try:
            import time
            start_time = time.time()
            
            command = [sys.executable, "-m", "radon", "cc", target_file_path, "--json"]
            
            process_result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            result.standard_output = process_result.stdout
            result.standard_error = process_result.stderr
            result.execution_successful = process_result.returncode == 0
            
            try:
                if process_result.stdout.strip():
                    result.parsed_data = json.loads(process_result.stdout)
            except Exception:
                pass
            
            result.execution_duration = time.time() - start_time
            
        except Exception as error:
            result.standard_error = str(error)
        
        return result

    def get_available_tools_list(self) -> List[OpenSourceToolName]:
        """Get a list of all available tools in the environment."""
        return [tool for tool, available in self.available_tools_cache.items() if available]

    def get_tool_status_summary(self) -> Dict[str, bool]:
        """Get a summary of tool availability."""
        return {tool.value: available for tool, available in self.available_tools_cache.items()}


# Singleton instance
_global_integrator_instance: Optional[RealOpenSourceToolIntegrator] = None


def get_real_open_source_tool_integrator() -> RealOpenSourceToolIntegrator:
    """Get the singleton instance of the real open source tool integrator."""
    global _global_integrator_instance
    if _global_integrator_instance is None:
        _global_integrator_instance = RealOpenSourceToolIntegrator()
    return _global_integrator_instance


__all__ = [
    "OpenSourceToolName",
    "OpenSourceToolExecutionResult",
    "RealOpenSourceToolIntegrator",
    "get_real_open_source_tool_integrator"
]
