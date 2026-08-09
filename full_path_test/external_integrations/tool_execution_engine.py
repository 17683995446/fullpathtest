"""
Production-Ready Tool Execution Engine
真实工具执行引擎 - 完整实现版本
能够实际运行各种开源工具并处理结果
"""

import os
import sys
import json
import subprocess
import tempfile
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import concurrent.futures
import threading


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tool_executor")


class ToolExecutionStatus(Enum):
    """工具执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    NOT_FOUND = "not_found"


@dataclass
class ToolExecutionResult:
    """工具执行结果"""
    tool_name: str
    status: ToolExecutionStatus
    execution_time: float = 0.0
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    issues: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""


@dataclass
class AnalysisConfiguration:
    """分析配置"""
    max_workers: int = 4
    timeout_seconds: int = 60
    continue_on_error: bool = True
    generate_json_output: bool = True
    generate_html_report: bool = False
    verbose: bool = True


class Tool(ABC):
    """工具基类"""
    
    def __init__(self, name: str, command_template: List[str]):
        self.name = name
        self.command_template = command_template
    
    @abstractmethod
    def parse_output(self, stdout: str, stderr: str, return_code: int) -> List[Dict[str, Any]]:
        """解析工具输出"""
        pass
    
    @abstractmethod
    def get_command(self, file_path: str) -> List[str]:
        """获取执行命令"""
        pass


class Flake8Tool(Tool):
    """Flake8 代码检查工具"""
    
    def __init__(self):
        super().__init__("flake8", ["flake8"])
    
    def get_command(self, file_path: str) -> List[str]:
        return [
            sys.executable, "-m", "flake8",
            "--format=json",
            "--max-line-length=120",
            "--select=E9,F63,F7,F82",
            file_path
        ]
    
    def parse_output(self, stdout: str, stderr: str, return_code: int) -> List[Dict[str, Any]]:
        """解析 Flake8 JSON 输出"""
        issues = []
        try:
            if stdout.strip():
                data = json.loads(stdout)
                if isinstance(data, list):
                    for item in data:
                        issues.append({
                            "type": "style",
                            "severity": "warning",
                            "tool": "flake8",
                            "file": item.get("filename", ""),
                            "line": item.get("line_number", 0),
                            "column": item.get("column_number", 0),
                            "message": item.get("text", ""),
                            "code": item.get("code", ""),
                        })
        except json.JSONDecodeError:
            logger.warning(f"Flake8: Failed to parse JSON output")
        
        return issues


class PylintTool(Tool):
    """Pylint 代码检查工具"""
    
    def __init__(self):
        super().__init__("pylint", ["pylint"])
    
    def get_command(self, file_path: str) -> List[str]:
        return [
            sys.executable, "-m", "pylint",
            "--output-format=json",
            "--disable=C,R",
            file_path
        ]
    
    def parse_output(self, stdout: str, stderr: str, return_code: int) -> List[Dict[str, Any]]:
        """解析 Pylint JSON 输出"""
        issues = []
        try:
            lines = stdout.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                try:
                    item = json.loads(line)
                    issues.append({
                        "type": "quality",
                        "severity": "info" if item.get('type') == 'info' else "warning",
                        "tool": "pylint",
                        "file": item.get('filename', ''),
                        "line": item.get('line', 0),
                        "column": item.get('column', 0),
                        "message": item.get('message', ''),
                        "code": item.get('message-id', ''),
                    })
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            logger.warning(f"Pylint: Error parsing output: {e}")
        
        return issues


class MypyTool(Tool):
    """Mypy 类型检查工具"""
    
    def __init__(self):
        super().__init__("mypy", ["mypy"])
    
    def get_command(self, file_path: str) -> List[str]:
        return [
            sys.executable, "-m", "mypy",
            "--no-error-summary",
            file_path
        ]
    
    def parse_output(self, stdout: str, stderr: str, return_code: int) -> List[Dict[str, Any]]:
        """解析 Mypy 输出"""
        issues = []
        for line in stdout.split('\n'):
            if not line.strip():
                continue
            
            parts = line.split(':', 4)
            if len(parts) >= 5:
                file_path = parts[0]
                line_num = parts[1]
                col = parts[2] if len(parts) > 2 else "0"
                msg_type = parts[3]
                message = parts[4] if len(parts) > 4 else ""
                
                if msg_type in ['error', 'warning']:
                    issues.append({
                        "type": "type",
                        "severity": "error" if msg_type == 'error' else "warning",
                        "tool": "mypy",
                        "file": file_path,
                        "line": int(line_num) if line_num.isdigit() else 0,
                        "column": int(col) if col.isdigit() else 0,
                        "message": message.strip(),
                        "code": "",
                    })
        
        return issues


class BanditTool(Tool):
    """Bandit 安全检查工具"""
    
    def __init__(self):
        super().__init__("bandit", ["bandit"])
    
    def get_command(self, file_path: str) -> List[str]:
        return [
            sys.executable, "-m", "bandit",
            "-f", "json",
            "-r", file_path
        ]
    
    def parse_output(self, stdout: str, stderr: str, return_code: int) -> List[Dict[str, Any]]:
        """解析 Bandit JSON 输出"""
        issues = []
        try:
            if stdout.strip():
                data = json.loads(stdout)
                results = data.get('results', [])
                for item in results:
                    issues.append({
                        "type": "security",
                        "severity": "warning",
                        "tool": "bandit",
                        "file": item.get('filename', ''),
                        "line": item.get('line_number', 0),
                        "column": 0,
                        "message": f"{item.get('issue_text', '')} ({item.get('issue_cwe', '')})",
                        "code": item.get('issue_id', ''),
                    })
        except json.JSONDecodeError:
            logger.warning(f"Bandit: Failed to parse JSON output")
        
        return issues


class RealToolExecutionEngine:
    """真实工具执行引擎"""
    
    def __init__(self, config: Optional[AnalysisConfiguration] = None):
        self.config = config or AnalysisConfiguration()
        self.tools: Dict[str, Tool] = {}
        self.available_tools: List[str] = []
        self.results: List[ToolExecutionResult] = []
        self._register_tools()
        self._check_tool_availability()
        self.progress_callback: Optional[Callable] = None
        self.lock = threading.Lock()
    
    def _register_tools(self):
        """注册所有工具"""
        self.tools = {
            "flake8": Flake8Tool(),
            "pylint": PylintTool(),
            "mypy": MypyTool(),
            "bandit": BanditTool(),
        }
    
    def _check_tool_availability(self):
        """检查工具可用性"""
        self.available_tools = []
        for tool_name, tool in self.tools.items():
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "show", tool_name],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.available_tools.append(tool_name)
                    logger.info(f"Tool '{tool_name}' is available")
                else:
                    logger.warning(f"Tool '{tool_name}' is NOT installed")
            except Exception as e:
                logger.warning(f"Tool '{tool_name}' check failed: {e}")
        
        logger.info(f"Available tools: {self.available_tools}")
    
    def set_progress_callback(self, callback: Callable[[int, int], None]):
        """设置进度回调"""
        self.progress_callback = callback
    
    def execute_single_tool(
        self, 
        tool_name: str, 
        file_path: str, 
        timeout: Optional[int] = None
    ) -> ToolExecutionResult:
        """执行单个工具对单个文件"""
        if tool_name not in self.available_tools:
            return ToolExecutionResult(
                tool_name=tool_name,
                status=ToolExecutionStatus.NOT_FOUND,
                error_message=f"Tool '{tool_name}' is not available"
            )
        
        tool = self.tools.get(tool_name)
        if not tool:
            return ToolExecutionResult(
                tool_name=tool_name,
                status=ToolExecutionStatus.FAILED,
                error_message=f"Tool '{tool_name}' not found"
            )
        
        start_time = time.time()
        command = tool.get_command(file_path)
        
        try:
            timeout_val = timeout or self.config.timeout_seconds
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout_val
            )
            
            execution_time = time.time() - start_time
            issues = tool.parse_output(result.stdout, result.stderr, result.returncode)
            
            status = ToolExecutionStatus.SUCCESS if result.returncode in [0, 1] else ToolExecutionStatus.FAILED
            
            return ToolExecutionResult(
                tool_name=tool_name,
                status=status,
                execution_time=execution_time,
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.returncode,
                issues=issues,
                metrics={
                    "issue_count": len(issues),
                    "file": file_path,
                }
            )
            
        except subprocess.TimeoutExpired:
            return ToolExecutionResult(
                tool_name=tool_name,
                status=ToolExecutionStatus.TIMEOUT,
                execution_time=timeout_val,
                error_message=f"Tool execution timed out after {timeout_val}s"
            )
        except Exception as e:
            return ToolExecutionResult(
                tool_name=tool_name,
                status=ToolExecutionStatus.FAILED,
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def execute_tools_on_file(
        self, 
        file_path: str, 
        tool_names: Optional[List[str]] = None
    ) -> List[ToolExecutionResult]:
        """在单个文件上执行多个工具"""
        tools_to_use = tool_names or self.available_tools
        results = []
        
        for tool_name in tools_to_use:
            result = self.execute_single_tool(tool_name, file_path)
            results.append(result)
            self.results.append(result)
        
        return results
    
    def execute_batch_analysis(
        self, 
        file_paths: List[str], 
        tool_names: Optional[List[str]] = None
    ) -> List[ToolExecutionResult]:
        """批量执行工具分析"""
        total_tasks = len(file_paths) * len(tool_names or self.available_tools)
        completed_tasks = 0
        
        all_results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = []
            
            for file_path in file_paths:
                for tool_name in (tool_names or self.available_tools):
                    future = executor.submit(
                        self.execute_single_tool, 
                        tool_name, 
                        file_path
                    )
                    futures.append((future, file_path, tool_name))
            
            for future, file_path, tool_name in futures:
                try:
                    result = future.result(timeout=self.config.timeout_seconds)
                    all_results.append(result)
                    completed_tasks += 1
                    
                    if self.progress_callback:
                        self.progress_callback(completed_tasks, total_tasks)
                    
                    if self.config.verbose and completed_tasks % 10 == 0:
                        logger.info(f"Progress: {completed_tasks}/{total_tasks} tasks completed")
                    
                except Exception as e:
                    logger.error(f"Task failed: {tool_name} on {file_path}: {e}")
                    all_results.append(ToolExecutionResult(
                        tool_name=tool_name,
                        status=ToolExecutionStatus.FAILED,
                        error_message=str(e)
                    ))
        
        self.results = all_results
        return all_results
    
    def get_summary(self) -> Dict[str, Any]:
        """获取执行摘要"""
        total = len(self.results)
        success = sum(1 for r in self.results if r.status == ToolExecutionStatus.SUCCESS)
        failed = sum(1 for r in self.results if r.status == ToolExecutionStatus.FAILED)
        not_found = sum(1 for r in self.results if r.status == ToolExecutionStatus.NOT_FOUND)
        
        total_issues = sum(len(r.issues) for r in self.results)
        total_time = sum(r.execution_time for r in self.results)
        
        issues_by_type: Dict[str, int] = {}
        for r in self.results:
            for issue in r.issues:
                issue_type = issue.get("type", "unknown")
                issues_by_type[issue_type] = issues_by_type.get(issue_type, 0) + 1
        
        return {
            "total_executions": total,
            "successful": success,
            "failed": failed,
            "not_found": not_found,
            "total_issues": total_issues,
            "total_time": total_time,
            "average_time": total_time / total if total > 0 else 0,
            "issues_by_type": issues_by_type,
            "available_tools": self.available_tools,
        }
    
    def save_results(self, output_file: str = "tool_execution_results.json"):
        """保存执行结果"""
        data = {
            "summary": self.get_summary(),
            "results": [
                {
                    "tool": r.tool_name,
                    "status": r.status.value,
                    "execution_time": r.execution_time,
                    "issue_count": len(r.issues),
                    "issues": r.issues,
                    "metrics": r.metrics,
                    "error": r.error_message,
                }
                for r in self.results
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {output_file}")


def main():
    """主函数 - 演示真实工具执行"""
    print("=" * 80)
    print("Real Tool Execution Engine - Demo")
    print("=" * 80)
    
    # 创建引擎
    config = AnalysisConfiguration(
        max_workers=4,
        timeout_seconds=30,
        verbose=True
    )
    engine = RealToolExecutionEngine(config)
    
    # 选择几个测试文件
    test_files = [
        "full_path_test/type_definitions/core_data_types.py",
        "full_path_test/module_infrastructure/productized_module_base.py",
        "full_path_test/external_integrations/llm_clients/real_llm_integration_client.py",
    ]
    
    print(f"\nAnalyzing {len(test_files)} files with available tools...")
    
    # 执行分析
    results = engine.execute_batch_analysis(test_files)
    
    # 打印摘要
    summary = engine.get_summary()
    
    print("\n" + "=" * 80)
    print("EXECUTION SUMMARY")
    print("=" * 80)
    print(f"Total executions:     {summary['total_executions']}")
    print(f"Successful:           {summary['successful']}")
    print(f"Failed:               {summary['failed']}")
    print(f"Total issues found:   {summary['total_issues']}")
    print(f"Total time:           {summary['total_time']:.2f}s")
    print(f"Average time:         {summary['average_time']:.3f}s")
    print(f"\nIssues by type:")
    for issue_type, count in summary['issues_by_type'].items():
        print(f"  - {issue_type}: {count}")
    
    # 保存结果
    engine.save_results()
    print("\nResults saved to tool_execution_results.json")


if __name__ == "__main__":
    main()
