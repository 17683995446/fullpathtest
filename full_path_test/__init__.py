"""
FullPathTest top-level module initialization.
Exports the core functionality of the system.
"""

from full_path_test.type_definitions.core_data_types import (
    CodeSourceType,
    SystemConfiguration,
    CodeQualityIssue,
    CodeAnalysisResult
)

from full_path_test.module_infrastructure.productized_module_base import (
    ModuleStatus,
    ModulePriority,
    ModuleConfiguration,
    ModuleMetrics,
    ModuleHealthStatus,
    ProductizedModuleBase
)

from full_path_test.external_integrations.open_source_tools.real_open_source_tool_integrator import (
    OpenSourceToolName,
    OpenSourceToolExecutionResult,
    RealOpenSourceToolIntegrator,
    get_real_open_source_tool_integrator
)

from full_path_test.external_integrations.llm_clients.real_llm_integration_client import (
    LLMProviderType,
    LLMConnectionConfiguration,
    LLMGenerationResponse,
    RealLLMIntegrationClient,
    create_local_ollama_client,
    create_mock_llm_client
)

from full_path_test.external_integrations.real_code_analyzer.real_code_analyzer_module import (
    CodeAnalysisInput,
    RealCodeAnalyzerModule,
    get_real_code_analyzer_module
)

__version__ = "2.0.0"
__author__ = "FullPathTest Team"

__all__ = [
    # Type definitions
    "CodeSourceType",
    "SystemConfiguration",
    "CodeQualityIssue",
    "CodeAnalysisResult",
    
    # Module infrastructure
    "ModuleStatus",
    "ModulePriority",
    "ModuleConfiguration",
    "ModuleMetrics",
    "ModuleHealthStatus",
    "ProductizedModuleBase",
    
    # Open source tools integration
    "OpenSourceToolName",
    "OpenSourceToolExecutionResult",
    "RealOpenSourceToolIntegrator",
    "get_real_open_source_tool_integrator",
    
    # LLM integration
    "LLMProviderType",
    "LLMConnectionConfiguration",
    "LLMGenerationResponse",
    "RealLLMIntegrationClient",
    "create_local_ollama_client",
    "create_mock_llm_client",
    
    # Real code analyzer
    "CodeAnalysisInput",
    "RealCodeAnalyzerModule",
    "get_real_code_analyzer_module"
]
