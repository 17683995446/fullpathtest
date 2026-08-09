"""
Type definitions module.
Contains all core data types used across the system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Callable


class CodeSourceType(Enum):
    """Enumeration for source code types."""
    PYTHON_FILE = "python_file"
    PYTHON_DIRECTORY = "python_directory"
    GIT_REPOSITORY = "git_repository"


@dataclass
class SystemConfiguration:
    """Configuration settings for the entire FullPathTest system."""
    source_path: str = "./"
    output_directory: str = "./fullpathtest_output"
    llm_mode: str = "mock"
    llm_api_key: str = ""
    llm_api_base: str = "http://localhost:11434"
    verbosity_level: int = 0
    generate_report: bool = True


@dataclass
class CodeQualityIssue:
    """Represents a single code quality issue found by analysis."""
    issue_id: str
    issue_type: str
    issue_description: str
    file_path: str
    line_number: int = 0
    column_number: int = 0
    severity_level: str = "medium"
    recommendation: str = ""


@dataclass
class CodeAnalysisResult:
    """Result from a comprehensive code analysis."""
    source_path: str
    total_files_analyzed: int = 0
    total_issues_count: int = 0
    quality_score: float = 0.0
    complexity_score: float = 0.0
    security_score: float = 0.0
    overall_score: float = 0.0
    detected_issues: List[CodeQualityIssue] = field(default_factory=list)
    tool_execution_results: Dict[str, Any] = field(default_factory=dict)
    llm_analysis_summary: Optional[str] = None


__all__ = [
    "CodeSourceType",
    "SystemConfiguration",
    "CodeQualityIssue",
    "CodeAnalysisResult"
]
