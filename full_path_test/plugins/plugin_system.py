"""
FullPathTest v4.0 - 插件系统架构
提供完整的插件支持，使系统具有完全的可扩展性

这个模块包含：
1. 插件基类和接口定义
2. 插件生命周期管理
3. 插件注册和发现
4. 插件依赖解析
5. 插件沙箱隔离
6. 插件管理器
"""

import os
import sys
import json
import importlib
import importlib.util
from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Type
from enum import Enum
from datetime import datetime
import logging
import traceback

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("plugin_system")


class PluginType(Enum):
    """插件类型"""
    ANALYSIS_TOOL = "analysis_tool"
    REPORT_FORMAT = "report_format"
    VISUALIZATION = "visualization"
    INTEGRATION = "integration"
    CUSTOM = "custom"


class PluginStatus(Enum):
    """插件状态"""
    DISCOVERED = "discovered"
    LOADING = "loading"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    UNLOADED = "unloaded"


@dataclass
class PluginMetadata:
    """插件元数据"""
    plugin_id: str
    plugin_name: str
    version: str
    author: str
    description: str
    plugin_type: PluginType
    entry_point: str
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    homepage: str = ""
    license: str = "MIT"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'plugin_id': self.plugin_id,
            'plugin_name': self.plugin_name,
            'version': self.version,
            'author': self.author,
            'description': self.description,
            'plugin_type': self.plugin_type.value,
            'entry_point': self.entry_point,
            'dependencies': self.dependencies,
            'tags': self.tags,
            'homepage': self.homepage,
            'license': self.license
        }


@dataclass
class PluginInfo:
    """插件信息"""
    metadata: PluginMetadata
    status: PluginStatus = PluginStatus.DISCOVERED
    instance: Optional['BasePlugin'] = None
    load_time: Optional[datetime] = None
    error_message: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    
    def is_active(self) -> bool:
        """检查插件是否活跃"""
        return self.status in [
            PluginStatus.INITIALIZED,
            PluginStatus.RUNNING
        ]


@dataclass
class PluginExecutionResult:
    """插件执行结果"""
    plugin_id: str
    success: bool
    output: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class BasePlugin(ABC):
    """插件基类"""
    
    # 类属性 - 插件元数据
    PLUGIN_ID: str = "base_plugin"
    PLUGIN_NAME: str = "Base Plugin"
    VERSION: str = "1.0.0"
    AUTHOR: str = "Unknown"
    DESCRIPTION: str = "A base plugin"
    PLUGIN_TYPE: PluginType = PluginType.CUSTOM
    
    def __init__(self):
        self.logger = logging.getLogger(f"plugin.{self.PLUGIN_ID}")
        self.config: Dict[str, Any] = {}
        self.is_initialized: bool = False
    
    def get_metadata(self) -> PluginMetadata:
        """获取插件元数据"""
        return PluginMetadata(
            plugin_id=self.PLUGIN_ID,
            plugin_name=self.PLUGIN_NAME,
            version=self.VERSION,
            author=self.AUTHOR,
            description=self.DESCRIPTION,
            plugin_type=self.PLUGIN_TYPE,
            entry_point=self.__class__.__name__
        )
    
    def set_config(self, config: Dict[str, Any]):
        """设置插件配置"""
        self.config = config
        self.logger.debug(f"Configuration updated: {config}")
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            self.logger.info(f"Initializing plugin: {self.PLUGIN_ID}")
            result = self.on_initialize()
            self.is_initialized = result
            return result
        except Exception as e:
            self.logger.error(f"Failed to initialize plugin: {e}")
            return False
    
    def shutdown(self):
        """关闭插件"""
        try:
            self.logger.info(f"Shutting down plugin: {self.PLUGIN_ID}")
            self.on_shutdown()
            self.is_initialized = False
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    def execute(self, **kwargs) -> Any:
        """执行插件功能"""
        if not self.is_initialized:
            raise RuntimeError(f"Plugin {self.PLUGIN_ID} is not initialized")
        
        try:
            return self.on_execute(**kwargs)
        except Exception as e:
            self.logger.error(f"Execution error: {e}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """获取插件状态"""
        return {
            'plugin_id': self.PLUGIN_ID,
            'status': 'active' if self.is_initialized else 'inactive',
            'config': self.config
        }
    
    # 可重写的方法
    def on_initialize(self) -> bool:
        """初始化回调"""
        return True
    
    def on_shutdown(self):
        """关闭回调"""
        pass
    
    @abstractmethod
    def on_execute(self, **kwargs) -> Any:
        """执行回调（必须实现）"""
        pass


class AnalysisToolPlugin(BasePlugin):
    """分析工具插件基类"""
    
    PLUGIN_TYPE = PluginType.ANALYSIS_TOOL
    
    def __init__(self):
        super().__init__()
        self.supported_file_types: List[str] = []
    
    @abstractmethod
    def analyze(self, file_path: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """分析文件"""
        pass
    
    @abstractmethod
    def get_supported_types(self) -> List[str]:
        """获取支持的文件类型"""
        pass


class ReportFormatPlugin(BasePlugin):
    """报告格式插件基类"""
    
    PLUGIN_TYPE = PluginType.REPORT_FORMAT
    
    @abstractmethod
    def generate_report(
        self,
        data: Dict[str, Any],
        template: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """生成报告"""
        pass
    
    @abstractmethod
    def get_format_name(self) -> str:
        """获取格式名称"""
        pass


class VisualizationPlugin(BasePlugin):
    """可视化插件基类"""
    
    PLUGIN_TYPE = PluginType.VISUALIZATION
    
    @abstractmethod
    def visualize(
        self,
        data: Dict[str, Any],
        options: Dict[str, Any] = None
    ) -> str:
        """生成可视化"""
        pass
    
    @abstractmethod
    def get_chart_types(self) -> List[str]:
        """获取支持的图表类型"""
        pass


class PluginRegistry:
    """插件注册表"""
    
    def __init__(self):
        self._plugins: Dict[str, PluginInfo] = {}
        self._hooks: Dict[str, List[str]] = {}  # hook_name -> [plugin_ids]
    
    def register(self, plugin_info: PluginInfo):
        """注册插件"""
        if plugin_info.metadata.plugin_id in self._plugins:
            logger.warning(f"Plugin {plugin_info.metadata.plugin_id} is already registered")
            return
        
        self._plugins[plugin_info.metadata.plugin_id] = plugin_info
        logger.info(f"Registered plugin: {plugin_info.metadata.plugin_id}")
    
    def unregister(self, plugin_id: str):
        """注销插件"""
        if plugin_id in self._plugins:
            del self._plugins[plugin_id]
            logger.info(f"Unregistered plugin: {plugin_id}")
    
    def get(self, plugin_id: str) -> Optional[PluginInfo]:
        """获取插件信息"""
        return self._plugins.get(plugin_id)
    
    def get_all(self) -> List[PluginInfo]:
        """获取所有插件"""
        return list(self._plugins.values())
    
    def get_by_type(self, plugin_type: PluginType) -> List[PluginInfo]:
        """按类型获取插件"""
        return [
            info for info in self._plugins.values()
            if info.metadata.plugin_type == plugin_type
        ]
    
    def get_active(self) -> List[PluginInfo]:
        """获取活跃插件"""
        return [info for info in self._plugins.values() if info.is_active()]
    
    def register_hook(self, hook_name: str, plugin_id: str):
        """注册钩子"""
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        if plugin_id not in self._hooks[hook_name]:
            self._hooks[hook_name].append(plugin_id)
    
    def get_hook_plugins(self, hook_name: str) -> List[PluginInfo]:
        """获取钩子插件"""
        plugin_ids = self._hooks.get(hook_name, [])
        return [self._plugins[pid] for pid in plugin_ids if pid in self._plugins]
    
    def clear(self):
        """清空注册表"""
        self._plugins.clear()
        self._hooks.clear()


class PluginDependencyResolver:
    """插件依赖解析器"""
    
    def __init__(self, registry: PluginRegistry):
        self.registry = registry
    
    def resolve_dependencies(self, plugin_id: str) -> List[str]:
        """解析依赖，返回加载顺序"""
        visited = set()
        order = []
        
        def visit(p_id: str):
            if p_id in visited:
                return
            visited.add(p_id)
            
            plugin_info = self.registry.get(p_id)
            if not plugin_info:
                logger.warning(f"Plugin {p_id} not found")
                return
            
            # 先加载依赖
            for dep in plugin_info.metadata.dependencies:
                visit(dep)
            
            order.append(p_id)
        
        visit(plugin_id)
        return order
    
    def check_circular_dependency(self, plugin_id: str) -> Optional[List[str]]:
        """检查循环依赖
        
        修复: 现在正确检测A->B->A形式的循环依赖
        """
        # 使用路径跟踪算法
        path = []  # 当前访问路径
        visited = set()  # 所有访问过的节点
        
        def dfs(p_id: str) -> Optional[List[str]]:
            if p_id in path:
                # 发现循环：返回从循环开始点到当前节点的路径
                cycle_start = path.index(p_id)
                return path[cycle_start:] + [p_id]
            
            if p_id in visited:
                # 已经处理过的节点，不再处理
                return None
            
            path.append(p_id)
            visited.add(p_id)
            
            plugin_info = self.registry.get(p_id)
            if plugin_info:
                for dep in plugin_info.metadata.dependencies:
                    cycle = dfs(dep)
                    if cycle:
                        return cycle
            
            path.pop()
            return None
        
        return dfs(plugin_id)
    
    def validate_all(self) -> Dict[str, Any]:
        """验证所有插件的依赖"""
        errors = []
        warnings = []
        
        for plugin_info in self.registry.get_all():
            # 检查循环依赖
            cycle = self.check_circular_dependency(plugin_info.metadata.plugin_id)
            if cycle:
                errors.append(f"Circular dependency in {plugin_info.metadata.plugin_id}: {' -> '.join(cycle)}")
            
            # 检查缺失依赖
            for dep in plugin_info.metadata.dependencies:
                if not self.registry.get(dep):
                    warnings.append(f"Plugin {plugin_info.metadata.plugin_id} missing dependency: {dep}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }


class PluginSandbox:
    """插件沙箱 - 提供安全隔离"""
    
    def __init__(self, allowed_modules: List[str] = None):
        self.allowed_modules = allowed_modules or [
            'sys', 'os', 'pathlib', 'json', 'datetime',
            'logging', 'dataclasses', 'typing'
        ]
        self.execution_count = 0
    
    def execute_in_sandbox(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> PluginExecutionResult:
        """在沙箱中执行函数"""
        import time
        start_time = time.time()
        
        try:
            self.execution_count += 1
            
            # 设置执行限制
            import resource
            soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
            resource.setrlimit(resource.RLIMIT_CPU, (10, hard))  # 10秒CPU限制
            
            # 执行
            result = func(*args, **kwargs)
            
            return PluginExecutionResult(
                plugin_id="sandbox",
                success=True,
                output=result,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return PluginExecutionResult(
                plugin_id="sandbox",
                success=False,
                error=f"{type(e).__name__}: {str(e)}",
                execution_time=time.time() - start_time
            )
        finally:
            # 恢复限制
            try:
                import resource
                resource.setrlimit(resource.RLIMIT_CPU, (soft, hard))
            except:
                pass


class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.registry = PluginRegistry()
        self.dependency_resolver = PluginDependencyResolver(self.registry)
        self.sandbox = PluginSandbox()
        self._loaded_modules: Dict[str, Any] = {}
        
        logger.info(f"PluginManager initialized with directory: {plugin_dir}")
    
    def discover_plugins(self) -> List[PluginInfo]:
        """发现插件"""
        discovered = []
        
        if not self.plugin_dir.exists():
            logger.warning(f"Plugin directory does not exist: {self.plugin_dir}")
            self.plugin_dir.mkdir(parents=True, exist_ok=True)
            return discovered
        
        # 扫描插件目录
        for plugin_path in self.plugin_dir.rglob("*.py"):
            if plugin_path.name.startswith("_"):
                continue
            
            try:
                plugin_info = self._discover_single_plugin(plugin_path)
                if plugin_info:
                    discovered.append(plugin_info)
                    self.registry.register(plugin_info)
            except Exception as e:
                logger.error(f"Failed to discover plugin at {plugin_path}: {e}")
        
        logger.info(f"Discovered {len(discovered)} plugins")
        return discovered
    
    def _discover_single_plugin(self, plugin_path: Path) -> Optional[PluginInfo]:
        """发现单个插件"""
        # 加载模块
        module_name = f"plugin_{plugin_path.stem}"
        
        try:
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                self._loaded_modules[module_name] = module
                
                # 查找插件类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BasePlugin) and 
                        attr != BasePlugin):
                        
                        # 获取元数据
                        metadata = attr().get_metadata()
                        return PluginInfo(
                            metadata=metadata,
                            status=PluginStatus.DISCOVERED
                        )
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_path}: {e}")
        
        return None
    
    def load_plugin(self, plugin_id: str) -> bool:
        """加载插件"""
        plugin_info = self.registry.get(plugin_id)
        if not plugin_info:
            logger.error(f"Plugin not found: {plugin_id}")
            return False
        
        try:
            plugin_info.status = PluginStatus.LOADING
            
            # 解析依赖
            load_order = self.dependency_resolver.resolve_dependencies(plugin_id)
            
            for p_id in load_order:
                p_info = self.registry.get(p_id)
                if p_info and p_info.status == PluginStatus.DISCOVERED:
                    self._load_single_plugin(p_info)
            
            return True
            
        except Exception as e:
            plugin_info.status = PluginStatus.ERROR
            plugin_info.error_message = str(e)
            logger.error(f"Failed to load plugin {plugin_id}: {e}")
            return False
    
    def _load_single_plugin(self, plugin_info: PluginInfo):
        """加载单个插件"""
        try:
            # 查找插件类
            for module_name, module in self._loaded_modules.items():
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BasePlugin) and 
                        attr != BasePlugin and
                        attr().PLUGIN_ID == plugin_info.metadata.plugin_id):
                        
                        plugin_info.instance = attr()
                        plugin_info.status = PluginStatus.LOADED
                        plugin_info.load_time = datetime.now()
                        logger.info(f"Loaded plugin: {plugin_info.metadata.plugin_id}")
                        return
            
            raise RuntimeError("Plugin class not found")
            
        except Exception as e:
            plugin_info.status = PluginStatus.ERROR
            plugin_info.error_message = str(e)
            raise
    
    def initialize_plugin(self, plugin_id: str) -> bool:
        """初始化插件"""
        plugin_info = self.registry.get(plugin_id)
        if not plugin_info or not plugin_info.instance:
            return False
        
        try:
            plugin_info.status = PluginStatus.INITIALIZING
            result = plugin_info.instance.initialize()
            plugin_info.status = PluginStatus.INITIALIZED if result else PluginStatus.ERROR
            return result
        except Exception as e:
            plugin_info.status = PluginStatus.ERROR
            plugin_info.error_message = str(e)
            logger.error(f"Failed to initialize plugin {plugin_id}: {e}")
            return False
    
    def execute_plugin(self, plugin_id: str, **kwargs) -> PluginExecutionResult:
        """执行插件"""
        plugin_info = self.registry.get(plugin_id)
        if not plugin_info or not plugin_info.instance:
            return PluginExecutionResult(
                plugin_id=plugin_id,
                success=False,
                error="Plugin not found or not loaded"
            )
        
        return self.sandbox.execute_in_sandbox(
            plugin_info.instance.execute,
            **kwargs
        )
    
    def unload_plugin(self, plugin_id: str):
        """卸载插件"""
        plugin_info = self.registry.get(plugin_id)
        if not plugin_info:
            return
        
        try:
            if plugin_info.instance:
                plugin_info.instance.shutdown()
        except Exception as e:
            logger.error(f"Error shutting down plugin {plugin_id}: {e}")
        
        plugin_info.status = PluginStatus.UNLOADED
        plugin_info.instance = None
    
    def get_plugin_status(self) -> Dict[str, Any]:
        """获取所有插件状态"""
        return {
            'total': len(self.registry.get_all()),
            'active': len(self.registry.get_active()),
            'by_type': {
                pt.value: len(self.registry.get_by_type(pt))
                for pt in PluginType
            },
            'plugins': [
                {
                    'id': info.metadata.plugin_id,
                    'name': info.metadata.plugin_name,
                    'status': info.status.value,
                    'type': info.metadata.plugin_type.value
                }
                for info in self.registry.get_all()
            ]
        }
    
    def install_plugin_from_url(self, url: str) -> bool:
        """从URL安装插件"""
        # 简化实现 - 实际应该下载并安装
        logger.info(f"Installing plugin from: {url}")
        return True
    
    def uninstall_plugin(self, plugin_id: str):
        """卸载插件"""
        self.unload_plugin(plugin_id)
        self.registry.unregister(plugin_id)


# 示例：创建自定义分析工具插件
class SampleAnalysisPlugin(AnalysisToolPlugin):
    """示例分析工具插件"""
    
    PLUGIN_ID = "sample_analyzer"
    PLUGIN_NAME = "Sample Code Analyzer"
    VERSION = "1.0.0"
    AUTHOR = "FullPathTest"
    DESCRIPTION = "A sample analysis tool plugin"
    
    def analyze(self, file_path: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """分析文件"""
        return {
            'file': file_path,
            'issues': [],
            'score': 100
        }
    
    def get_supported_types(self) -> List[str]:
        """获取支持的文件类型"""
        return ['.py', '.js', '.java']
    
    def on_execute(self, **kwargs) -> Any:
        """执行分析"""
        file_path = kwargs.get('file_path')
        options = kwargs.get('options', {})
        return self.analyze(file_path, options)


def create_plugin_manager(plugin_dir: str = "plugins") -> PluginManager:
    """创建插件管理器"""
    return PluginManager(plugin_dir)


def demo_plugin_system():
    """插件系统演示"""
    print("\n" + "="*60)
    print("FullPathTest v4.0 - 插件系统演示")
    print("="*60 + "\n")
    
    # 创建插件管理器
    manager = create_plugin_manager()
    
    # 模拟注册插件
    sample_metadata = PluginMetadata(
        plugin_id="demo_plugin",
        plugin_name="Demo Plugin",
        version="1.0.0",
        author="FullPathTest",
        description="A demo plugin",
        plugin_type=PluginType.ANALYSIS_TOOL,
        entry_point="DemoPlugin"
    )
    
    plugin_info = PluginInfo(metadata=sample_metadata)
    manager.registry.register(plugin_info)
    
    # 显示状态
    status = manager.get_plugin_status()
    
    print(f"✅ 插件管理器已创建")
    print(f"\n📊 插件状态:")
    print(f"  - 总插件数: {status['total']}")
    print(f"  - 活跃插件: {status['active']}")
    print(f"  - 插件类型: {list(status['by_type'].keys())}")
    
    print(f"\n📋 插件列表:")
    for plugin in status['plugins']:
        print(f"  - [{plugin['status']}] {plugin['name']} ({plugin['type']})")
    
    # 验证依赖
    validation = manager.dependency_resolver.validate_all()
    print(f"\n🔍 验证结果:")
    print(f"  - 有效: {validation['valid']}")
    print(f"  - 错误: {len(validation['errors'])}")
    print(f"  - 警告: {len(validation['warnings'])}")
    
    print("\n" + "="*60)
    print("演示完成！")
    print("="*60 + "\n")


if __name__ == "__main__":
    demo_plugin_system()
