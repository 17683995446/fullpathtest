"""
FullPathTest v4.0 - 问题修复与优化
解决在大规模真实项目中发现的性能问题
"""

import os
import sys
import time
import json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import multiprocessing


class OptimizedFileProcessor:
    """优化后的文件处理器"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or max(1, multiprocessing.cpu_count() - 1)
    
    def process_files_multiprocess(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """使用多进程处理文件"""
        results = []
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._process_single_file, fp): fp for fp in file_paths}
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        'success': False,
                        'error': str(e)
                    })
        
        return results
    
    def process_files_threaded(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """使用多线程处理文件"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers * 2) as executor:
            futures = {executor.submit(self._process_single_file, fp): fp for fp in file_paths}
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        'success': False,
                        'error': str(e)
                    })
        
        return results
    
    def _process_single_file(self, file_path: Path) -> Dict[str, Any]:
        """处理单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            return {
                'success': True,
                'path': str(file_path),
                'size': len(content),
                'lines': len(lines),
                'functions': len([l for l in lines if 'def ' in l]),
                'classes': len([l for l in lines if 'class ' in l])
            }
        except Exception as e:
            return {
                'success': False,
                'path': str(file_path),
                'error': str(e)
            }


class BatchAnalyzer:
    """批量分析器 - 解决内存和性能问题"""
    
    def __init__(self, batch_size: int = 100, max_workers: int = 4):
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.results = []
    
    def analyze_with_batching(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """使用批处理分析文件"""
        all_results = []
        
        # 分批处理
        for i in range(0, len(file_paths), self.batch_size):
            batch = file_paths[i:i + self.batch_size]
            
            # 在每个批次中使用进程池
            processor = OptimizedFileProcessor(max_workers=self.max_workers)
            batch_results = processor.process_files_multiprocess(batch)
            
            all_results.extend(batch_results)
            
            # 定期清理内存
            if i % 500 == 0 and i > 0:
                import gc
                gc.collect()
        
        return all_results


def test_optimized_performance(project_path: str):
    """测试优化后的性能"""
    print("\n" + "="*60)
    print("测试优化后的性能")
    print("="*60)
    
    django_path = Path(project_path)
    py_files = list(django_path.rglob("*.py"))[:1000]  # 测试1000个文件
    
    print(f"📁 测试文件数: {len(py_files)}")
    print(f"🧮 CPU核心数: {multiprocessing.cpu_count()}")
    
    # 测试1: 优化后的批处理
    print("\n🔄 测试1: 优化后的批处理...")
    analyzer = BatchAnalyzer(batch_size=100, max_workers=4)
    
    start_time = time.time()
    results = analyzer.analyze_with_batching(py_files)
    batch_time = time.time() - start_time
    
    success_count = sum(1 for r in results if r.get('success', False))
    print(f"  批处理时间: {batch_time:.2f}秒")
    print(f"  成功率: {success_count}/{len(results)}")
    print(f"  处理速度: {len(results)/batch_time:.1f} 文件/秒")
    
    # 测试2: 不同worker数量的效果
    print("\n🔄 测试2: 不同worker数量...")
    worker_counts = [1, 2, 4, 8]
    times = {}
    
    for workers in worker_counts:
        analyzer = BatchAnalyzer(batch_size=100, max_workers=workers)
        
        start_time = time.time()
        results = analyzer.analyze_with_batching(py_files[:200])  # 使用较小样本
        elapsed = time.time() - start_time
        
        times[workers] = elapsed
        print(f"  {workers} workers: {elapsed:.2f}秒")
    
    # 计算最佳worker数
    baseline = times[1]
    for workers, t in times.items():
        if workers > 1:
            speedup = baseline / t
            print(f"  {workers} workers: 加速比 {speedup:.2f}x")
    
    return {
        'batch_time': batch_time,
        'success_rate': success_count / len(results) if results else 0,
        'worker_comparison': times
    }


def demo_optimized_system():
    """演示优化后的系统"""
    print("\n" + "="*60)
    print("FullPathTest v4.0 - 优化后的性能测试")
    print("="*60 + "\n")
    
    project_path = "/workspace/django_project"
    
    if not Path(project_path).exists():
        print(f"⚠️  Django项目未找到，请先克隆")
        return
    
    # 运行优化测试
    results = test_optimized_performance(project_path)
    
    # 验证优化效果
    print("\n" + "="*60)
    print("优化效果验证")
    print("="*60)
    
    if results['batch_time'] < 10:
        print("✅ 批处理性能良好 (< 10秒)")
    else:
        print("⚠️  批处理性能需要进一步优化")
    
    if results['success_rate'] > 0.95:
        print(f"✅ 成功率很高 ({results['success_rate']*100:.1f}%)")
    else:
        print(f"⚠️  成功率偏低 ({results['success_rate']*100:.1f}%)")
    
    print("\n" + "="*60)
    print("演示完成！")
    print("="*60 + "\n")


if __name__ == "__main__":
    demo_optimized_system()
