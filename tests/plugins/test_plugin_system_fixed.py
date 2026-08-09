"""
FullPathTest v4.0 - 插件系统测试（修复版）
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_plugin_base_class():
    """测试1: 插件基类"""
    try:
        from full_path_test.plugins.plugin_system import BasePlugin, PluginMetadata, PluginType
        
        class TestPlugin(BasePlugin):
            PLUGIN_ID = "test_plugin"
            PLUGIN_NAME = "Test Plugin"
            VERSION = "1.0.0"
            
            def on_execute(self, **kwargs):
                return "executed"
        
        plugin = TestPlugin()
        metadata = plugin.get_metadata()
        
        assert metadata.plugin_id == "test_plugin"
        assert metadata.version == "1.0.0"
        
        # 测试初始化和执行
        plugin.initialize()
        assert plugin.is_initialized
        
        result = plugin.execute()
        assert result == "executed"
        
        plugin.shutdown()
        
        print("✓ Test 1: 插件基类 - PASSED")
        return True
    except Exception as e:
        print(f"✗ Test 1: 插件基类 - FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_plugin_registry():
    """测试2: 插件注册表"""
    try:
        from full_path_test.plugins.plugin_system import (
            PluginRegistry,
            PluginInfo,
            PluginMetadata,
            PluginType,
            PluginStatus
        )
        
        registry = PluginRegistry()
        
        # 注册插件
        metadata = PluginMetadata(
            plugin_id="test",
            plugin_name="Test",
            version="1.0",
            author="Test",
            description="Test plugin",
            plugin_type=PluginType.ANALYSIS_TOOL,
            entry_point="TestPlugin"
        )
        
        plugin_info = PluginInfo(metadata=metadata)
        registry.register(plugin_info)
        
        # 获取插件
        retrieved = registry.get("test")
        assert retrieved is not None
        assert retrieved.metadata.plugin_id == "test"
        
        # 获取所有插件
        all_plugins = registry.get_all()
        assert len(all_plugins) == 1
        
        # 按类型获取
        analysis_plugins = registry.get_by_type(PluginType.ANALYSIS_TOOL)
        assert len(analysis_plugins) == 1
        
        print("✓ Test 2: 插件注册表 - PASSED")
        return True
    except Exception as e:
        print(f"✗ Test 2: 插件注册表 - FAILED: {e}")
        return False


def test_plugin_manager():
    """测试3: 插件管理器"""
    try:
        from full_path_test.plugins.plugin_system import (
            PluginManager,
            create_plugin_manager
        )
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        try:
            manager = create_plugin_manager(temp_dir)
            
            assert manager is not None
            assert manager.plugin_dir == Path(temp_dir)
            
            # 发现插件（应该为空）
            discovered = manager.discover_plugins()
            assert isinstance(discovered, list)
            
            # 获取状态
            status = manager.get_plugin_status()
            assert 'total' in status
            assert 'active' in status
            
            print("✓ Test 3: 插件管理器 - PASSED")
            return True
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"✗ Test 3: 插件管理器 - FAILED: {e}")
        return False


def test_dependency_resolver():
    """测试4: 依赖解析器"""
    try:
        from full_path_test.plugins.plugin_system import (
            PluginRegistry,
            PluginDependencyResolver,
            PluginInfo,
            PluginMetadata,
            PluginType
        )
        
        registry = PluginRegistry()
        resolver = PluginDependencyResolver(registry)
        
        # 注册插件
        metadata1 = PluginMetadata(
            plugin_id="plugin1",
            plugin_name="Plugin1",
            version="1.0",
            author="Test",
            description="Test",
            plugin_type=PluginType.CUSTOM,
            entry_point="Plugin1",
            dependencies=[]
        )
        
        metadata2 = PluginMetadata(
            plugin_id="plugin2",
            plugin_name="Plugin2",
            version="1.0",
            author="Test",
            description="Test",
            plugin_type=PluginType.CUSTOM,
            entry_point="Plugin2",
            dependencies=["plugin1"]
        )
        
        registry.register(PluginInfo(metadata=metadata1))
        registry.register(PluginInfo(metadata=metadata2))
        
        # 解析依赖
        order = resolver.resolve_dependencies("plugin2")
        assert "plugin1" in order
        assert "plugin2" in order
        assert order.index("plugin1") < order.index("plugin2")
        
        # 检查循环依赖
        cycle = resolver.check_circular_dependency("plugin1")
        assert cycle is None  # 不应该有循环依赖
        
        print("✓ Test 4: 依赖解析器 - PASSED")
        return True
    except Exception as e:
        print(f"✗ Test 4: 依赖解析器 - FAILED: {e}")
        return False


def test_plugin_sandbox():
    """测试5: 插件沙箱"""
    try:
        from full_path_test.plugins.plugin_system import PluginSandbox
        
        sandbox = PluginSandbox()
        
        # 测试正常执行
        def test_func():
            return 42
        
        result = sandbox.execute_in_sandbox(test_func)
        assert result.success
        assert result.output == 42
        
        # 测试异常处理
        def error_func():
            raise ValueError("Test error")
        
        result = sandbox.execute_in_sandbox(error_func)
        assert not result.success
        assert "ValueError" in result.error
        
        print("✓ Test 5: 插件沙箱 - PASSED")
        return True
    except Exception as e:
        print(f"✗ Test 5: 插件沙箱 - FAILED: {e}")
        return False


def test_plugin_types():
    """测试6: 插件类型"""
    try:
        from full_path_test.plugins.plugin_system import (
            AnalysisToolPlugin,
            ReportFormatPlugin,
            VisualizationPlugin,
            BasePlugin
        )
        
        # 测试分析工具插件
        class MyAnalyzer(AnalysisToolPlugin):
            PLUGIN_ID = "my_analyzer"
            
            def analyze(self, file_path, options=None):
                return {"result": "ok"}
            
            def get_supported_types(self):
                return [".py"]
            
            def on_execute(self, **kwargs):
                return self.analyze(kwargs.get("file_path"))
        
        analyzer = MyAnalyzer()
        assert ".py" in analyzer.get_supported_types()
        
        print("✓ Test 6: 插件类型 - PASSED")
        return True
    except Exception as e:
        print(f"✗ Test 6: 插件类型 - FAILED: {e}")
        return False


def test_plugin_lifecycle():
    """测试7: 插件生命周期"""
    try:
        from full_path_test.plugins.plugin_system import BasePlugin
        
        class LifecyclePlugin(BasePlugin):
            PLUGIN_ID = "lifecycle_test"
            
            def __init__(self):
                super().__init__()
                self.init_called = False
                self.shutdown_called = False
            
            def on_initialize(self):
                self.init_called = True
                return True
            
            def on_shutdown(self):
                self.shutdown_called = True
            
            def on_execute(self, **kwargs):
                return "executed"
        
        plugin = LifecyclePlugin()
        
        # 测试初始化
        assert plugin.initialize()
        assert plugin.init_called
        assert plugin.is_initialized
        
        # 测试执行
        result = plugin.execute()
        assert result == "executed"
        
        # 测试关闭
        plugin.shutdown()
        assert plugin.shutdown_called
        assert not plugin.is_initialized
        
        print("✓ Test 7: 插件生命周期 - PASSED")
        return True
    except Exception as e:
        print(f"✗ Test 7: 插件生命周期 - FAILED: {e}")
        return False


def test_plugin_config():
    """测试8: 插件配置（修复版）"""
    try:
        from full_path_test.plugins.plugin_system import BasePlugin
        
        class ConfigPlugin(BasePlugin):
            PLUGIN_ID = "config_test"
            
            def on_execute(self, **kwargs):
                return self.config.get("key", "default")
        
        plugin = ConfigPlugin()
        
        # 设置配置
        plugin.set_config({"key": "value", "number": 42})
        
        # 初始化插件（关键步骤！）
        plugin.initialize()
        
        # 执行
        result = plugin.execute()
        assert result == "value"
        
        print("✓ Test 8: 插件配置 - PASSED")
        return True
    except Exception as e:
        print(f"✗ Test 8: 插件配置 - FAILED: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("FullPathTest v4.0 - 插件系统测试套件")
    print("="*60 + "\n")
    
    tests = [
        test_plugin_base_class,
        test_plugin_registry,
        test_plugin_manager,
        test_dependency_resolver,
        test_plugin_sandbox,
        test_plugin_types,
        test_plugin_lifecycle,
        test_plugin_config,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
        print()
    
    print("="*60)
    print("测试总结")
    print("="*60)
    print(f"总测试数: {len(tests)}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"成功率: {(passed/len(tests)*100):.1f}%")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
