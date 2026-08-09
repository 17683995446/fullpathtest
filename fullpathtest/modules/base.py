"""
Productized Module Base - 产品化模块基类

为所有模块提供统一的接口、生命周期管理、配置、日志等能力。
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
    """模块状态"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class ModulePriority(Enum):
    """模块优先级"""
    CRITICAL = 0    # 核心依赖，必须最先初始化
    HIGH = 1        # 高优先级
    MEDIUM = 2      # 中等优先级
    LOW = 3         # 低优先级
    OPTIONAL = 4    # 可选模块


@dataclass
class ModuleConfig:
    """模块配置"""
    module_name: str
    version: str = "1.0.0"
    enabled: bool = True
    priority: ModulePriority = ModulePriority.MEDIUM
    config: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    logging_level: str = "INFO"


@dataclass
class ModuleMetrics:
    """模块指标"""
    module_name: str
    startup_time: float = 0.0
    operation_count: int = 0
    error_count: int = 0
    average_response_time: float = 0.0
    last_operation_time: Optional[datetime] = None
    custom_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class ModuleHealth:
    """模块健康状态"""
    module_name: str
    status: ModuleStatus
    healthy: bool
    issues: List[str] = field(default_factory=list)
    last_check: Optional[datetime] = None


class ProductizedModule(ABC, Generic[T, R]):
    """产品化模块基类"""
    
    def __init__(self, config: Optional[ModuleConfig] = None):
        self.config = config or ModuleConfig(module_name=self.__class__.__name__)
        self.status = ModuleStatus.UNINITIALIZED
        self.logger = self._setup_logger()
        self.metrics = ModuleMetrics(module_name=self.config.module_name)
        self._health_checker = ModuleHealthChecker(self)
    
    def _setup_logger(self) -> logging.Logger:
        """设置模块专用日志"""
        logger = logging.getLogger(f"fullpathtest.{self.config.module_name}")
        logger.setLevel(getattr(logging, self.config.logging_level, logging.INFO))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def initialize(self) -> bool:
        """初始化模块"""
        if self.status == ModuleStatus.READY:
            self.logger.warning("Module already initialized")
            return True
        
        import time
        start_time = time.time()
        self.status = ModuleStatus.INITIALIZING
        self.logger.info(f"Initializing module {self.config.module_name}")
        
        try:
            self._on_initialize()
            self.status = ModuleStatus.READY
            self.metrics.startup_time = time.time() - start_time
            self.logger.info(
                f"Module {self.config.module_name} initialized in "
                f"{self.metrics.startup_time:.2f}s"
            )
            return True
        except Exception as e:
            self.status = ModuleStatus.ERROR
            self.metrics.error_count += 1
            self.logger.error(f"Failed to initialize module: {e}", exc_info=True)
            return False
    
    def shutdown(self) -> bool:
        """关闭模块"""
        if self.status in [ModuleStatus.SHUTDOWN, ModuleStatus.UNINITIALIZED]:
            return True
        
        self.logger.info(f"Shutting down module {self.config.module_name}")
        try:
            self._on_shutdown()
            self.status = ModuleStatus.SHUTDOWN
            self.logger.info(f"Module {self.config.module_name} shutdown complete")
            return True
        except Exception as e:
            self.logger.error(f"Failed to shutdown module: {e}", exc_info=True)
            return False
    
    def execute(self, input_data: T) -> R:
        """执行模块核心功能"""
        if self.status != ModuleStatus.READY:
            raise RuntimeError(f"Module {self.config.module_name} is not ready")
        
        import time
        self.status = ModuleStatus.RUNNING
        start_time = time.time()
        
        try:
            result = self._on_execute(input_data)
            self.metrics.operation_count += 1
            self.metrics.last_operation_time = datetime.now()
            self.metrics.average_response_time = (
                (self.metrics.average_response_time * (self.metrics.operation_count - 1) 
                 + (time.time() - start_time)) / self.metrics.operation_count
            )
            self.status = ModuleStatus.READY
            return result
        except Exception as e:
            self.status = ModuleStatus.ERROR
            self.metrics.error_count += 1
            self.logger.error(f"Module execution failed: {e}", exc_info=True)
            raise
    
    def get_health(self) -> ModuleHealth:
        """获取模块健康状态"""
        return self._health_checker.check()
    
    def get_metrics(self) -> ModuleMetrics:
        """获取模块指标"""
        return self.metrics
    
    @abstractmethod
    def _on_initialize(self) -> None:
        """初始化回调，子类实现"""
        pass
    
    @abstractmethod
    def _on_shutdown(self) -> None:
        """关闭回调，子类实现"""
        pass
    
    @abstractmethod
    def _on_execute(self, input_data: T) -> R:
        """执行回调，子类实现"""
        pass


class ModuleHealthChecker:
    """模块健康检查器"""
    
    def __init__(self, module: ProductizedModule):
        self.module = module
        self.last_check_time: Optional[datetime] = None
    
    def check(self) -> ModuleHealth:
        """执行健康检查"""
        from datetime import datetime
        
        self.last_check_time = datetime.now()
        
        health = ModuleHealth(
            module_name=self.module.config.module_name,
            status=self.module.status,
            healthy=True,
            last_check=self.last_check_time
        )
        
        # 基础检查
        if self.module.status == ModuleStatus.ERROR:
            health.healthy = False
            health.issues.append("Module is in error state")
        
        if self.module.metrics.error_count > 10:
            health.healthy = False
            health.issues.append(f"High error count: {self.module.metrics.error_count}")
        
        # 扩展检查
        self._perform_extended_health_checks(health)
        
        return health
    
    def _perform_extended_health_checks(self, health: ModuleHealth) -> None:
        """执行扩展健康检查，子类可覆盖"""
        pass


class ModuleRegistry:
    """模块注册表"""
    
    def __init__(self):
        self.modules: Dict[str, ProductizedModule] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
        self.initialization_order: List[str] = []
    
    def register(self, module: ProductizedModule) -> None:
        """注册模块"""
        name = module.config.module_name
        self.modules[name] = module
        self.dependency_graph[name] = module.config.dependencies
        self._update_initialization_order()
    
    def get(self, name: str) -> Optional[ProductizedModule]:
        """获取模块"""
        return self.modules.get(name)
    
    def get_all(self) -> Dict[str, ProductizedModule]:
        """获取所有模块"""
        return self.modules
    
    def initialize_all(self) -> bool:
        """按依赖顺序初始化所有模块"""
        success = True
        for module_name in self.initialization_order:
            module = self.modules[module_name]
            if module.config.enabled:
                if not module.initialize():
                    success = False
        return success
    
    def shutdown_all(self) -> None:
        """关闭所有模块"""
        for module_name in reversed(self.initialization_order):
            if module_name in self.modules:
                self.modules[module_name].shutdown()
    
    def get_system_health(self) -> Dict[str, ModuleHealth]:
        """获取系统健康状态"""
        return {name: module.get_health() 
                for name, module in self.modules.items()}
    
    def _update_initialization_order(self) -> None:
        """更新初始化顺序（拓扑排序）"""
        from collections import deque
        
        in_degree = {name: 0 for name in self.modules}
        for name in self.modules:
            for dep in self.dependency_graph[name]:
                if dep in self.modules:
                    in_degree[name] += 1
        
        queue = deque()
        for name, degree in in_degree.items():
            if degree == 0:
                queue.append(name)
        
        result = []
        while queue:
            current = queue.popleft()
            result.append(current)
            
            for name, deps in self.dependency_graph.items():
                if current in deps and name in self.modules:
                    in_degree[name] -= 1
                    if in_degree[name] == 0:
                        queue.append(name)
        
        self.initialization_order = result


# 全局模块注册表
_module_registry: Optional[ModuleRegistry] = None

def get_module_registry() -> ModuleRegistry:
    """获取模块注册表单例"""
    global _module_registry
    if _module_registry is None:
        _module_registry = ModuleRegistry()
    return _module_registry
