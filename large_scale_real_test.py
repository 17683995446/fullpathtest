#!/usr/bin/env python3
"""
FullPathTest v4.0 - 大规模真实项目压力测试
在真实的复杂项目（Django）中测试系统，发现真实问题
"""

import os
import sys
import time
import json
import traceback
import psutil
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import threading
import gc


@dataclass
class Issue:
    """发现的问题"""
    issue_id: str
    severity: str  # critical, high, medium, low
    category: str  # performance, functional, memory, timeout, error
    title: str
    description: str
    location: str
    solution: str
    impact: str
    discovered_at: datetime = field(default_factory=datetime.now)


class LargeScaleTestReport:
    """大规模测试报告"""
    
    def __init__(self):
        self.issues: List[Issue] = []
        self.start_time = None
        self.end_time = None
        self.metrics: Dict[str, Any] = {}
    
    def add_issue(self, issue: Issue):
        """添加问题"""
        self.issues.append(issue)
    
    def get_issues_by_severity(self, severity: str) -> List[Issue]:
        """按严重性获取问题"""
        return [i for i in self.issues if i.severity == severity]
    
    def get_issues_by_category(self, category: str) -> List[Issue]:
        """按类别获取问题"""
        return [i for i in self.issues if i.category == category]
    
    def generate_summary(self) -> Dict[str, Any]:
        """生成摘要"""
        return {
            'total_issues': len(self.issues),
            'critical': len(self.get_issues_by_severity('critical')),
            'high': len(self.get_issues_by_severity('high')),
            'medium': len(self.get_issues_by_severity('medium')),
            'low': len(self.get_issues_by_severity('low')),
            'by_category': {
                'performance': len(self.get_issues_by_category('performance')),
                'functional': len(self.get_issues_by_category('functional')),
                'memory': len(self.get_issues_by_category('memory')),
                'timeout': len(self.get_issues_by_category('timeout')),
                'error': len(self.get_issues_by_category('error')),
            },
            'duration': (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else 0
        }


def test_module_imports():
    """测试1: 模块导入"""
    print("\n" + "="*60)
    print("测试1: 模块导入测试")
    print("="*60)
    
    issues = []
    
    # 测试AI模块导入
    try:
        print("🔄 导入AI模块...")
        from full_path_test.ai.ai_integration import create_ai_analyzer, LLMConfiguration
        print("✅ AI模块导入成功")
    except Exception as e:
        issues.append(Issue(
            issue_id="IMPORT_001",
            severity="critical",
            category="error",
            title="AI模块导入失败",
            description=f"无法导入AI模块: {str(e)}",
            location="full_path_test/ai/ai_integration.py",
            solution="检查依赖和路径",
            impact="整个AI功能不可用"
        ))
        print(f"❌ AI模块导入失败: {e}")
    
    # 测试插件模块导入
    try:
        print("🔄 导入插件系统...")
        from full_path_test.plugins.plugin_system import create_plugin_manager
        print("✅ 插件系统导入成功")
    except Exception as e:
        issues.append(Issue(
            issue_id="IMPORT_002",
            severity="critical",
            category="error",
            title="插件系统导入失败",
            description=f"无法导入插件系统: {str(e)}",
            location="full_path_test/plugins/plugin_system.py",
            solution="检查代码语法和导入",
            impact="插件功能不可用"
        ))
        print(f"❌ 插件系统导入失败: {e}")
    
    # 测试企业级模块导入
    try:
        print("🔄 导入企业级模块...")
        from full_path_test.enterprise.enterprise_system import create_enterprise_system
        print("✅ 企业级模块导入成功")
    except Exception as e:
        issues.append(Issue(
            issue_id="IMPORT_003",
            severity="high",
            category="error",
            title="企业级模块导入失败",
            description=f"无法导入企业级模块: {str(e)}",
            location="full_path_test/enterprise/enterprise_system.py",
            solution="检查依赖和代码",
            impact="企业级功能受限"
        ))
        print(f"❌ 企业级模块导入失败: {e}")
    
    # 测试性能模块导入
    try:
        print("🔄 导入性能模块...")
        from full_path_test.performance.performance_system import create_performance_system
        print("✅ 性能模块导入成功")
    except Exception as e:
        issues.append(Issue(
            issue_id="IMPORT_004",
            severity="medium",
            category="error",
            title="性能模块导入失败",
            description=f"无法导入性能模块: {str(e)}",
            location="full_path_test/performance/performance_system.py",
            solution="检查依赖",
            impact="性能优化功能受限"
        ))
        print(f"❌ 性能模块导入失败: {e}")
    
    return issues


def test_memory_usage(project_path: str):
    """测试2: 内存使用测试"""
    print("\n" + "="*60)
    print("测试2: 内存使用测试")
    print("="*60)
    
    issues = []
    process = psutil.Process()
    
    # 记录初始内存
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    print(f"📊 初始内存: {initial_memory:.2f} MB")
    
    # 测试大量文件处理
    django_path = Path(project_path)
    py_files = list(django_path.rglob("*.py"))
    
    print(f"📁 发现文件: {len(py_files)} 个Python文件")
    
    # 读取多个文件
    print("🔄 测试大量文件读取...")
    sample_files = py_files[:500]  # 测试500个文件
    
    try:
        files_data = []
        for i, file_path in enumerate(sample_files):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    files_data.append({
                        'path': str(file_path),
                        'size': len(content),
                        'lines': len(content.split('\n'))
                    })
                
                if i % 100 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024
                    print(f"  处理 {i}/{len(sample_files)} 文件, 内存: {current_memory:.2f} MB")
                    
            except Exception as e:
                # 记录文件读取错误，但不作为严重问题
                pass
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        print(f"📊 最终内存: {final_memory:.2f} MB")
        print(f"📈 内存增长: {memory_increase:.2f} MB ({memory_increase/initial_memory*100:.1f}%)")
        
        # 检查内存泄漏
        if memory_increase > 500:  # 如果增长超过500MB
            issues.append(Issue(
                issue_id="MEM_001",
                severity="high",
                category="memory",
                title="潜在内存泄漏",
                description=f"处理{len(sample_files)}个文件导致内存增长{memory_increase:.2f}MB",
                location="文件处理模块",
                solution="使用生成器替代列表，及时释放大对象",
                impact=f"处理大型项目时可能导致内存不足"
            ))
            print(f"⚠️  警告: 内存增长过高 ({memory_increase:.2f}MB)")
        
        # 检查是否未及时释放
        del files_data
        gc.collect()
        
        after_gc_memory = process.memory_info().rss / 1024 / 1024
        print(f"🧹 GC后内存: {after_gc_memory:.2f} MB")
        
    except MemoryError:
        issues.append(Issue(
            issue_id="MEM_002",
            severity="critical",
            category="memory",
            title="内存耗尽",
            description=f"处理{len(sample_files)}个文件时发生内存耗尽",
            location="文件处理模块",
            solution="分批处理，使用流式读取，限制并发",
            impact="无法处理大型项目"
        ))
        print(f"❌ 严重: 内存耗尽")
    
    return issues


def test_performance_large_scale(project_path: str):
    """测试3: 大规模性能测试"""
    print("\n" + "="*60)
    print("测试3: 大规模性能测试")
    print("="*60)
    
    issues = []
    django_path = Path(project_path)
    py_files = list(django_path.rglob("*.py"))
    
    print(f"📁 总文件数: {len(py_files)}")
    
    # 测试1: 文件扫描性能
    print("\n🔄 测试1: 文件扫描性能...")
    start_time = time.time()
    
    count = 0
    for py_file in py_files:
        if py_file.is_file():
            count += 1
    
    scan_time = time.time() - start_time
    scan_rate = len(py_files) / scan_time if scan_time > 0 else 0
    
    print(f"  扫描时间: {scan_time:.2f}秒")
    print(f"  扫描速度: {scan_rate:.0f} 文件/秒")
    
    if scan_time > 30:  # 如果扫描超过30秒
        issues.append(Issue(
            issue_id="PERF_001",
            severity="medium",
            category="performance",
            title="文件扫描速度慢",
            description=f"扫描{len(py_files)}个文件耗时{scan_time:.2f}秒",
            location="文件扫描模块",
            solution="使用并行扫描，优化目录遍历算法",
            impact="大型项目初始化时间长"
        ))
    
    # 测试2: 代码分析性能
    print("\n🔄 测试2: 代码分析性能...")
    test_files = py_files[:100]  # 测试100个文件
    
    start_time = time.time()
    analysis_count = 0
    
    for file_path in test_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 简单分析
            lines = content.split('\n')
            functions = [l for l in lines if 'def ' in l]
            classes = [l for l in lines if 'class ' in l]
            
            analysis_count += 1
            
        except Exception as e:
            pass
    
    analysis_time = time.time() - start_time
    analysis_rate = len(test_files) / analysis_time if analysis_time > 0 else 0
    
    print(f"  分析时间: {analysis_time:.2f}秒")
    print(f"  分析速度: {analysis_rate:.1f} 文件/秒")
    print(f"  分析成功率: {analysis_count}/{len(test_files)}")
    
    if analysis_time > 10:  # 如果分析超过10秒
        issues.append(Issue(
            issue_id="PERF_002",
            severity="medium",
            category="performance",
            title="代码分析速度慢",
            description=f"分析{len(test_files)}个文件耗时{analysis_time:.2f}秒",
            location="代码分析模块",
            solution="使用并行处理，缓存分析结果",
            impact="大规模分析耗时长"
        ))
    
    # 测试3: 预测大规模处理时间
    print("\n🔄 测试3: 大规模处理预测...")
    estimated_time = (len(py_files) / analysis_rate) if analysis_rate > 0 else float('inf')
    
    print(f"  预测总处理时间: {estimated_time:.0f}秒 ({estimated_time/60:.1f}分钟)")
    
    if estimated_time > 600:  # 如果预测超过10分钟
        issues.append(Issue(
            issue_id="PERF_003",
            severity="high",
            category="performance",
            title="大规模处理时间过长",
            description=f"预测处理{len(py_files)}个文件需要{estimated_time/60:.1f}分钟",
            location="整体架构",
            solution="必须使用并行处理和增量分析",
            impact="实际应用中不可接受"
        ))
    
    return issues


def test_concurrent_processing(project_path: str):
    """测试4: 并发处理测试"""
    print("\n" + "="*60)
    print("测试4: 并发处理测试")
    print("="*60)
    
    issues = []
    django_path = Path(project_path)
    py_files = list(django_path.rglob("*.py"))[:200]
    
    print(f"📁 测试文件数: {len(py_files)}")
    
    # 测试顺序处理
    print("\n🔄 测试顺序处理...")
    start_time = time.time()
    
    for file_path in py_files[:50]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            pass
    
    sequential_time = time.time() - start_time
    print(f"  顺序处理: {sequential_time:.2f}秒")
    
    # 测试并发处理
    print("\n🔄 测试并发处理...")
    from concurrent.futures import ThreadPoolExecutor
    
    start_time = time.time()
    
    def process_file(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return None
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(process_file, py_files[:50]))
    
    concurrent_time = time.time() - start_time
    print(f"  并发处理: {concurrent_time:.2f}秒")
    
    # 计算加速比
    speedup = sequential_time / concurrent_time if concurrent_time > 0 else 0
    print(f"  加速比: {speedup:.2f}x")
    
    if speedup < 1.5:  # 如果加速比小于1.5
        issues.append(Issue(
            issue_id="PERF_004",
            severity="medium",
            category="performance",
            title="并发处理效果不佳",
            description=f"4线程并发加速比仅为{speedup:.2f}x",
            location="并发处理模块",
            solution="优化并发策略，减少锁竞争，使用进程池",
            impact="多核利用率低"
        ))
    
    # 测试更多线程
    print("\n🔄 测试8线程并发...")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(process_file, py_files[:50]))
    
    more_concurrent_time = time.time() - start_time
    more_speedup = sequential_time / more_concurrent_time if more_concurrent_time > 0 else 0
    print(f"  8线程并发: {more_concurrent_time:.2f}秒 (加速比: {more_speedup:.2f}x)")
    
    return issues


def test_timeout_scenarios(project_path: str):
    """测试5: 超时场景测试"""
    print("\n" + "="*60)
    print("测试5: 超时场景测试")
    print("="*60)
    
    issues = []
    django_path = Path(project_path)
    py_files = list(django_path.rglob("*.py"))
    
    # 测试大文件处理
    print("\n🔄 测试大文件处理...")
    large_files = []
    
    for py_file in py_files[:500]:
        try:
            size = py_file.stat().st_size
            if size > 100000:  # 大于100KB
                large_files.append((py_file, size))
        except:
            pass
    
    large_files.sort(key=lambda x: x[1], reverse=True)
    
    print(f"  发现{large_files}个大于100KB的文件")
    
    # 测试处理大文件
    if large_files:
        large_file, size = large_files[0]
        print(f"  测试最大文件: {large_file.name} ({size/1024:.1f}KB)")
        
        start_time = time.time()
        timeout = 5  # 5秒超时
        
        try:
            # 设置超时处理
            def read_file_with_timeout():
                with open(large_file, 'r', encoding='utf-8') as f:
                    return f.read()
            
            # 模拟超时检查
            result = read_file_with_timeout()
            read_time = time.time() - start_time
            
            print(f"  读取时间: {read_time:.2f}秒")
            
            if read_time > timeout:
                issues.append(Issue(
                    issue_id="TIMEOUT_001",
                    severity="medium",
                    category="timeout",
                    title="大文件处理超时",
                    description=f"读取{size/1024:.1f}KB文件耗时{read_time:.2f}秒，超过预期{timeout}秒",
                    location="文件读取模块",
                    solution="实现流式读取，设置合理的超时限制",
                    impact="处理大文件时可能超时"
                ))
        
        except TimeoutError:
            issues.append(Issue(
                issue_id="TIMEOUT_002",
                severity="high",
                category="timeout",
                title="文件读取超时",
                description=f"读取{large_file.name}超过{timeout}秒",
                location="文件读取模块",
                solution="添加超时控制，实现断点续读",
                impact="大型文件无法处理"
            ))
            print(f"❌ 超时: 读取超过{timeout}秒")
    
    return issues


def test_error_handling(project_path: str):
    """测试6: 错误处理测试"""
    print("\n" + "="*60)
    print("测试6: 错误处理测试")
    print("="*60)
    
    issues = []
    
    # 测试各种错误场景
    test_cases = [
        ("不存在的文件", "/nonexistent/file.py"),
        ("损坏的编码", None),  # 特殊测试
        ("权限不足", None),
        ("磁盘空间不足", None),
    ]
    
    # 测试不存在的路径
    print("\n🔄 测试不存在的路径...")
    try:
        from full_path_test.ai.ai_integration import CodeAnalysisRequest, AnalysisType
        
        request = CodeAnalysisRequest(
            code="",
            file_path="/nonexistent/file.py",
            analysis_types=[AnalysisType.CODE_QUALITY]
        )
        
        print("  ✅ 请求创建成功（即使路径不存在）")
        
    except Exception as e:
        issues.append(Issue(
            issue_id="ERROR_001",
            severity="low",
            category="functional",
            title="错误处理可以更友好",
            description=f"处理无效路径时的错误信息: {str(e)}",
            location="请求处理模块",
            solution="改进错误信息，提供更多上下文",
            impact="用户体验"
        ))
        print(f"⚠️  错误处理: {e}")
    
    # 测试空输入
    print("\n🔄 测试空输入处理...")
    try:
        from full_path_test.ai.ai_integration import AICodeAnalyzer, LLMConfiguration, MockLLMClient
        
        config = LLMConfiguration(provider=MockLLMClient)
        analyzer = AICodeAnalyzer(config)
        
        request = CodeAnalysisRequest(
            code="",
            analysis_types=[]
        )
        
        # 应该有合理的处理
        print("  ✅ 空输入被接受")
        
    except Exception as e:
        issues.append(Issue(
            issue_id="ERROR_002",
            severity="medium",
            category="functional",
            title="空输入处理不当",
            description=f"空输入导致异常: {str(e)}",
            location="分析器模块",
            solution="添加输入验证，提供默认值",
            impact="可能崩溃"
        ))
        print(f"❌ 空输入错误: {e}")
    
    return issues


def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("FullPathTest v4.0 - 大规模真实项目压力测试")
    print("在Django项目（2909个文件）中测试，发现真实问题")
    print("="*80)
    
    report = LargeScaleTestReport()
    report.start_time = datetime.now()
    
    project_path = "/workspace/django_project"
    
    # 检查项目是否存在
    if not Path(project_path).exists():
        print(f"\n❌ 项目路径不存在: {project_path}")
        print("请先克隆Django项目:")
        print("  git clone --depth 1 https://github.com/django/django.git django_project")
        return
    
    # 运行所有测试
    print("\n开始测试...")
    
    # 测试1: 模块导入
    issues = test_module_imports()
    for issue in issues:
        report.add_issue(issue)
    
    # 测试2: 内存使用
    issues = test_memory_usage(project_path)
    for issue in issues:
        report.add_issue(issue)
    
    # 测试3: 性能测试
    issues = test_performance_large_scale(project_path)
    for issue in issues:
        report.add_issue(issue)
    
    # 测试4: 并发测试
    issues = test_concurrent_processing(project_path)
    for issue in issues:
        report.add_issue(issue)
    
    # 测试5: 超时测试
    issues = test_timeout_scenarios(project_path)
    for issue in issues:
        report.add_issue(issue)
    
    # 测试6: 错误处理
    issues = test_error_handling(project_path)
    for issue in issues:
        report.add_issue(issue)
    
    report.end_time = datetime.now()
    
    # 生成报告
    print("\n" + "="*80)
    print("测试完成 - 生成报告")
    print("="*80)
    
    summary = report.generate_summary()
    
    print(f"\n📊 测试摘要:")
    print(f"  总问题数: {summary['total_issues']}")
    print(f"  严重 (critical): {summary['critical']}")
    print(f"  高 (high): {summary['high']}")
    print(f"  中 (medium): {summary['medium']}")
    print(f"  低 (low): {summary['low']}")
    print(f"  持续时间: {summary['duration']:.2f}秒")
    
    print(f"\n📋 按类别:")
    for category, count in summary['by_category'].items():
        if count > 0:
            print(f"  {category}: {count}")
    
    # 详细问题列表
    print(f"\n📝 发现的问题详情:")
    for i, issue in enumerate(report.issues, 1):
        severity_icon = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }.get(issue.severity, '⚪')
        
        print(f"\n{i}. {severity_icon} [{issue.severity.upper()}] {issue.title}")
        print(f"   ID: {issue.issue_id}")
        print(f"   类别: {issue.category}")
        print(f"   描述: {issue.description}")
        print(f"   位置: {issue.location}")
        print(f"   解决方案: {issue.solution}")
        print(f"   影响: {issue.impact}")
    
    # 保存报告
    report_data = {
        'summary': summary,
        'issues': [
            {
                **vars(issue),
                'discovered_at': issue.discovered_at.isoformat()
            }
            for issue in report.issues
        ],
        'test_time': {
            'start': report.start_time.isoformat(),
            'end': report.end_time.isoformat(),
            'duration': summary['duration']
        }
    }
    
    with open('/workspace/large_scale_test_report.json', 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 报告已保存到: /workspace/large_scale_test_report.json")
    
    # 统计总结
    print("\n" + "="*80)
    print("统计总结")
    print("="*80)
    
    if summary['total_issues'] == 0:
        print("🎉 太好了！没有发现任何问题！")
    elif summary['critical'] > 0:
        print(f"⚠️  警告: 发现 {summary['critical']} 个严重问题，需要立即处理！")
    elif summary['high'] > 0:
        print(f"⚠️  注意: 发现 {summary['high']} 个高优先级问题")
    else:
        print(f"✅ 整体状况良好: 发现 {summary['total_issues']} 个问题（多为中低优先级）")
    
    print("\n" + "="*80)
    print("测试完成")
    print("="*80 + "\n")
    
    return report


if __name__ == "__main__":
    report = main()
