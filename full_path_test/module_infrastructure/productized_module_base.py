"""
Module infrastructure base classes.
Provides productized module base with lifecycle, health, and metrics.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging


T = TypeVar('T')
R = TypeVar('R')


class ModuleStatus(Enum):
    """Enumeration representing the current status of a module."""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY_FOR_EXECUTION = "ready_for_execution"
    RUNNING_EXECUTION = "running_execution"
    IN_ERROR_STATE = "in_error_state"
    SHUTDOWN_COMPLETED = "shutdown_completed"


class ModulePriority(Enum):
    """Priority level for module initialization and execution."""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    OPTIONAL = 4


@dataclass
class ModuleConfiguration:
    """Configuration settings for a productized module."""
    module_name: str
    module_version: str = "1.0.0"
    enabled_flag: bool = True
    priority_level: ModulePriority = ModulePriority.MEDIUM
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    dependencies_list: List[str] = field(default_factory=list)
    logging_level: str = "INFO"


@dataclass
class ModuleMetrics:
    """Runtime performance and operational metrics for a module."""
    module_name: str
    startup_duration: float = 0.0
    operation_count: int = 0
    error_count: int = 0
    average_response_time: float = 0.0
    last_operation_timestamp: Optional[datetime] = None
    custom_metrics_data: Dict[str, float] = field(default_factory=dict)


@dataclass
class ModuleHealthStatus:
    """Health check status for a module."""
    module_name: str
    overall_healthy: bool
    current_status: ModuleStatus
    detected_issues: List[str] = field(default_factory=list)
    last_health_check_timestamp: Optional[datetime] = None


class ProductizedModuleBase(ABC, Generic[T, R]):
    """Abstract base class for all productized modules in the system."""

    def __init__(self, module_config: Optional[ModuleConfiguration] = None):
        self.configuration = module_config or ModuleConfiguration(module_name=self.__class__.__name__)
        self.current_status = ModuleStatus.UNINITIALIZED
        self.logger = self._initialize_module_logger()
        self.metrics = ModuleMetrics(module_name=self.configuration.module_name)

    def _initialize_module_logger(self) -> logging.Logger:
        """Set up a module-specific logger instance."""
        logger = logging.getLogger(f"full_path_test.{self.configuration.module_name}")
        logger.setLevel(getattr(logging, self.configuration.logging_level, logging.INFO))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

    def initialize_module(self) -> bool:
        """Initialize the module and prepare for execution."""
        if self.current_status == ModuleStatus.READY_FOR_EXECUTION:
            self.logger.warning("Module already initialized")
            return True
        
        import time
        start_time = time.time()
        self.current_status = ModuleStatus.INITIALIZING
        self.logger.info(f"Initializing module {self.configuration.module_name}")
        
        try:
            self._on_module_initialization()
            self.current_status = ModuleStatus.READY_FOR_EXECUTION
            self.metrics.startup_duration = time.time() - start_time
            self.logger.info(
                f"Module {self.configuration.module_name} initialized in "
                f"{self.metrics.startup_duration:.2f}s"
            )
            return True
        except Exception as error:
            self.current_status = ModuleStatus.IN_ERROR_STATE
            self.metrics.error_count += 1
            self.logger.error(f"Failed to initialize module: {error}", exc_info=True)
            return False

    def shutdown_module(self) -> bool:
        """Perform cleanup and shutdown the module."""
        if self.current_status in [ModuleStatus.SHUTDOWN_COMPLETED, ModuleStatus.UNINITIALIZED]:
            return True
        
        self.logger.info(f"Shutting down module {self.configuration.module_name}")
        try:
            self._on_module_shutdown()
            self.current_status = ModuleStatus.SHUTDOWN_COMPLETED
            self.logger.info(f"Module {self.configuration.module_name} shutdown complete")
            return True
        except Exception as error:
            self.logger.error(f"Failed to shutdown module: {error}", exc_info=True)
            return False

    def execute_module_function(self, input_data: T) -> R:
        """Execute the primary functionality of the module."""
        if self.current_status != ModuleStatus.READY_FOR_EXECUTION:
            raise RuntimeError(f"Module {self.configuration.module_name} is not ready for execution")
        
        import time
        self.current_status = ModuleStatus.RUNNING_EXECUTION
        start_time = time.time()
        
        try:
            result = self._on_module_execution(input_data)
            self.metrics.operation_count += 1
            self.metrics.last_operation_timestamp = datetime.now()
            self.metrics.average_response_time = (
                (self.metrics.average_response_time * (self.metrics.operation_count - 1) 
                 + (time.time() - start_time)) / self.metrics.operation_count
            )
            self.current_status = ModuleStatus.READY_FOR_EXECUTION
            return result
        except Exception as error:
            self.current_status = ModuleStatus.IN_ERROR_STATE
            self.metrics.error_count += 1
            self.logger.error(f"Module execution failed: {error}", exc_info=True)
            raise

    def check_module_health(self) -> ModuleHealthStatus:
        """Retrieve the current health status of the module."""
        from datetime import datetime
        
        health = ModuleHealthStatus(
            module_name=self.configuration.module_name,
            overall_healthy=True,
            current_status=self.current_status,
            last_health_check_timestamp=datetime.now()
        )
        
        if self.current_status == ModuleStatus.IN_ERROR_STATE:
            health.overall_healthy = False
            health.detected_issues.append("Module is currently in error state")
        
        if self.metrics.error_count > 10:
            health.overall_healthy = False
            health.detected_issues.append(f"High error count detected: {self.metrics.error_count}")
        
        return health

    def get_module_metrics(self) -> ModuleMetrics:
        """Retrieve runtime metrics for this module."""
        return self.metrics

    @abstractmethod
    def _on_module_initialization(self) -> None:
        """Callback for module-specific initialization code."""
        pass

    @abstractmethod
    def _on_module_shutdown(self) -> None:
        """Callback for module-specific cleanup code."""
        pass

    @abstractmethod
    def _on_module_execution(self, input_data: T) -> R:
        """Callback for module-specific execution logic."""
        pass


__all__ = [
    "ModuleStatus",
    "ModulePriority",
    "ModuleConfiguration",
    "ModuleMetrics",
    "ModuleHealthStatus",
    "ProductizedModuleBase"
]
