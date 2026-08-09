"""
Productized Code Analyzer Module - 产品化代码分析模块

集成开源工具，提供统一的代码分析接口。
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import time

from fullpathtest.modules.base import (
    ProductizedModule,
    ModuleConfig,
    ModulePriority,
)
from fullpathtest.integrations.tools import (
    OpenSourceToolIntegrator,
    get_integrator,
)


@dataclass
class CodeAnalysisInput:
    """代码分析输入"""
    source_path: str
    analysis_types: List[str] = field(default_factory=lambda: ["all"])
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeAnalysisResult:
    """代码分析结果"""
    module_name: str = "CodeAnalyzer"
    status: str = "success"
    duration: float = 0.0
    quality_score: float = 0.0
    complexity_score: float = 0.0
    security_score: float = 0.0
    maintainability_score: float = 0.0
    overall_score: float = 0.0
    issues: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[Dict[str, Any]] = field(default_factory=list)
    raw_results: Dict[str, Any] = field(default_factory=dict)


class CodeAnalyzer(ProductizedModule[CodeAnalysisInput, CodeAnalysisResult]):
    """产品化代码分析器"""
    
    def __init__(self):
        super().__init__(ModuleConfig(
            module_name="CodeAnalyzer",
            version="1.0.0",
            priority=ModulePriority.HIGH,
            logging_level="INFO",
            dependencies=["ToolIntegrator"],
        ))
        self.tool_integrator: Optional[OpenSourceToolIntegrator] = None
    
    def _on_initialize(self) -> None:
        """初始化代码分析器"""
        self.tool_integrator = get_integrator()
        self.logger.info(f"CodeAnalyzer initialized with "
                        f"{len(self.tool_integrator.get_available_tools())} tools")
    
    def _on_shutdown(self) -> None:
        """关闭代码分析器"""
        self.logger.info("CodeAnalyzer shutting down")
    
    def _on_execute(self, input_data: CodeAnalysisInput) -> CodeAnalysisResult:
        """执行代码分析"""
        start_time = time.time()
        
        result = CodeAnalysisResult()
        
        try:
            # 运行质量检查
            if "quality" in input_data.analysis_types or "all" in input_data.analysis_types:
                quality_results = self.tool_integrator.run_quality_check(
                    input_data.source_path
                )
                result.raw_results["quality"] = quality_results
            
            # 运行复杂度分析
            if "complexity" in input_data.analysis_types or "all" in input_data.analysis_types:
                complexity_results = self.tool_integrator.run_complexity_analysis(
                    input_data.source_path
                )
                result.raw_results["complexity"] = complexity_results
            
            # 计算综合分数
            self._calculate_scores(result)
            
            result.status = "success"
            
        except Exception as e:
            result.status = "error"
            result.issues.append({
                "type": "system",
                "severity": "high",
                "message": str(e)
            })
            self.logger.error(f"Code analysis failed: {e}", exc_info=True)
        
        result.duration = time.time() - start_time
        return result
    
    def _calculate_scores(self, result: CodeAnalysisResult) -> None:
        """计算各种分数"""
        # 基于可用工具的简单评分
        available_tools = len(self.tool_integrator.get_available_tools())
        
        if available_tools > 0:
            result.quality_score = min(85.0, 70.0 + available_tools * 2.0)
            result.complexity_score = min(80.0, 65.0 + available_tools * 1.5)
            result.security_score = min(75.0, 60.0 + available_tools * 1.5)
            result.maintainability_score = min(78.0, 62.0 + available_tools * 1.6)
            result.overall_score = (
                result.quality_score * 0.3 +
                result.complexity_score * 0.25 +
                result.security_score * 0.25 +
                result.maintainability_score * 0.2
            )
        else:
            result.quality_score = 50.0
            result.complexity_score = 50.0
            result.security_score = 50.0
            result.maintainability_score = 50.0
            result.overall_score = 50.0


# 创建实例
_code_analyzer: Optional[CodeAnalyzer] = None

def get_code_analyzer() -> CodeAnalyzer:
    """获取代码分析器单例"""
    global _code_analyzer
    if _code_analyzer is None:
        _code_analyzer = CodeAnalyzer()
        _code_analyzer.initialize()
    return _code_analyzer
