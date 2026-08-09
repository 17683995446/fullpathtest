"""
FullPathTest v4.0 - 性能优化
包含多进程、高级缓存、性能监控
"""

import os
import sys
import time
import hashlib
import logging
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Generic, TypeVar
from functools import wraps
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("performance")

# 类型变量
V = TypeVar('V')


@dataclass
class CacheEntry:
    """缓存条目"""
    value: Any
    timestamp: datetime
    access_count: int = 0
    ttl: int = 3600  # 秒


class LRUCache(Generic[V]):
    """LRU缓存"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[V]:
        """获取缓存"""
        with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                now = datetime.now()
                
                if (now - entry.timestamp).total_seconds() < entry.ttl:
                    entry.access_count += 1
                    self.cache.move_to_end(key)
                    self.hits += 1
                    return entry.value
                
                del self.cache[key]
            
            self.misses += 1
            return None
    
    def set(self, key: str, value: V, ttl: int = None):
        """设置缓存"""
        with self._lock:
            if len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
            
            self.cache[key] = CacheEntry(
                value=value,
                timestamp=datetime.now(),
                ttl=ttl or self.default_ttl
            )
    
    def delete(self, key: str):
        """删除缓存"""
        with self._lock:
            if key in self.cache:
                del self.cache[key]
    
    def clear(self):
        """清空缓存"""
        with self._lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        total = self.hits + self.misses
        hit_rate = self.hits / total * 100 if total > 0 else 0
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate, 2)
        }


class FileCache:
    """文件缓存"""
    
    def __init__(self, cache_dir: str = ".cache", default_ttl: int = 7200):
        self.cache_dir = Path(cache_dir)
        self.default_ttl = default_ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{safe_key}.cache"
    
    def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        now = datetime.now()
        mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        
        if (now - mtime).total_seconds() > self.default_ttl:
            return None
        
        with open(cache_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def set(self, key: str, value: str):
        """设置缓存"""
        cache_path = self._get_cache_path(key)
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(value)
    
    def clear(self):
        """清空缓存"""
        import shutil
        shutil.rmtree(self.cache_dir, ignore_errors=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)


def lru_cache_decorator(max_size: int = 100):
    """LRU缓存装饰器"""
    cache = LRUCache(max_size=max_size)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            result = cache.get(key)
            if result is not None:
                return result
            
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        
        return wrapper
    return decorator


class ParallelExecutor:
    """并行执行器"""
    
    def __init__(self, max_workers: int = None, use_processes: bool = True):
        self.max_workers = max_workers or max(1, cpu_count() - 1)
        self.use_processes = use_processes
    
    def map(self, func: Callable, items: List[Any]) -> List[Any]:
        """并行映射"""
        results = []
        
        if self.use_processes:
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                for result in executor.map(func, items):
                    results.append(result)
        else:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                for result in executor.map(func, items):
                    results.append(result)
        
        return results
    
    def execute_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """执行任务列表"""
        results = []
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for task in tasks:
                func = task.get('func')
                args = task.get('args', ())
                kwargs = task.get('kwargs', {})
                
                futures.append(executor.submit(func, *args, **kwargs))
            
            for future in as_completed(futures):
                try:
                    results.append({
                        'success': True,
                        'result': future.result()
                    })
                except Exception as e:
                    results.append({
                        'success': False,
                        'error': str(e)
                    })
        
        return results


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.start_times: Dict[str, float] = {}
    
    def start(self, operation_name: str):
        """开始计时"""
        self.start_times[operation_name] = time.time()
    
    def end(self, operation_name: str) -> float:
        """结束计时，返回耗时（秒）"""
        if operation_name not in self.start_times:
            return 0
        
        duration = time.time() - self.start_times.pop(operation_name)
        
        if operation_name not in self.metrics:
            self.metrics[operation_name] = []
        
        self.metrics[operation_name].append(duration)
        return duration
    
    def get_metric_stats(self, operation_name: str) -> Dict[str, Any]:
        """获取指标统计"""
        if operation_name not in self.metrics or len(self.metrics[operation_name]) == 0:
            return {}
        
        times = self.metrics[operation_name]
        return {
            'count': len(times),
            'min': min(times),
            'max': max(times),
            'avg': sum(times) / len(times),
            'sum': sum(times)
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有统计"""
        return {
            name: self.get_metric_stats(name)
            for name in self.metrics
        }


def benchmark(func: Callable, iterations: int = 100) -> Dict[str, Any]:
    """基准测试函数"""
    times = []
    
    for _ in range(iterations):
        start = time.time()
        func()
        times.append(time.time() - start)
    
    return {
        'iterations': iterations,
        'total': sum(times),
        'avg': sum(times) / len(times),
        'min': min(times),
        'max': max(times),
        'throughput': iterations / sum(times) if sum(times) > 0 else 0
    }


class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self):
        self.lru_cache = LRUCache(max_size=5000)
        self.file_cache = FileCache()
        self.monitor = PerformanceMonitor()
        self.executor = ParallelExecutor()
    
    def analyze_performance(self, func: Callable, sample_inputs: List[Any]) -> Dict[str, Any]:
        """分析函数性能"""
        stats = benchmark(lambda: func(sample_inputs[0] if sample_inputs else None))
        return stats
    
    def optimize_workflow(self, tasks: List[Dict[str, Any]], parallel: bool = True) -> List[Any]:
        """优化工作流执行"""
        if parallel and len(tasks) > 1:
            return self.executor.execute_tasks(tasks)
        
        results = []
        for task in tasks:
            func = task.get('func')
            args = task.get('args', ())
            kwargs = task.get('kwargs', {})
            try:
                results.append(func(*args, **kwargs))
            except Exception as e:
                results.append(None)
        
        return results


def create_performance_system() -> PerformanceOptimizer:
    """创建性能系统"""
    return PerformanceOptimizer()


def demo_performance_system():
    """性能系统演示"""
    print("\n" + "="*60)
    print("FullPathTest v4.0 - 性能优化演示")
    print("="*60 + "\n")
    
    # 创建系统
    system = create_performance_system()
    
    # 测试LRU缓存
    print("🧪 测试LRU缓存...")
    cache = system.lru_cache
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    
    value = cache.get("key1")
    print(f"  - 缓存值: {value}")
    
    stats = cache.get_stats()
    print(f"  - 命中率: {stats['hit_rate']}%")
    
    # 测试性能监控
    print("\n📊 测试性能监控...")
    
    def slow_function(n):
        total = 0
        for i in range(n):
            total += i * i
        return total
    
    system.monitor.start("slow_op")
    result = slow_function(1000000)
    duration = system.monitor.end("slow_op")
    
    print(f"  - 耗时: {duration:.3f}秒")
    print(f"  - 结果: {result}")
    
    # 测试并行执行
    print("\n🚀 测试并行执行...")
    
    items = [100000, 200000, 300000, 400000]
    
    start = time.time()
    results = [slow_function(i) for i in items]
    sequential_time = time.time() - start
    
    print(f"  - 串行执行: {sequential_time:.3f}秒")
    
    try:
        executor = ParallelExecutor(use_processes=False)
        start = time.time()
        parallel_results = executor.map(slow_function, items)
        parallel_time = time.time() - start
        
        speedup = sequential_time / parallel_time if parallel_time > 0 else 1
        print(f"  - 并行执行: {parallel_time:.3f}秒")
        print(f"  - 加速比: {speedup:.2f}x")
    except Exception as e:
        print(f"  - 并行测试跳过（多进程限制）")
    
    # 显示性能统计
    print("\n📈 性能统计:")
    stats = system.monitor.get_all_stats()
    for name, data in stats.items():
        if data:
            print(f"  - {name}: avg={data.get('avg',0):.3f}s, count={data.get('count',0)}")
    
    print("\n" + "="*60)
    print("演示完成！")
    print("="*60 + "\n")


if __name__ == "__main__":
    demo_performance_system()
