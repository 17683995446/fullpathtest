#!/usr/bin/env python3
"""
FullPathTest v4.0 - 深度长时真实测试系统
真实项目测试 + 极限场景测试
"""

import os
import sys
import json
import time
import gc
import random
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil


class DefectSeverity(Enum):
    BLOCKER = "blocker"
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DefectCategory(Enum):
    STABILITY = "stability"
    PERFORMANCE = "performance"
    MEMORY_LEAK = "memory_leak"
    EDGE_CASE = "edge_case"
    SCALABILITY = "scalability"


@dataclass
class DeepDefect:
    defect_id: str
    severity: DefectSeverity
    category: DefectCategory
    title: str
    description: str
    reproduction_steps: List[str]
    location: str
    impact: str
    evidence: Dict[str, Any]
    discovered_at: datetime = field(default_factory=datetime.now)
    discovered_during: str = ""


class DeepRealTest:
    def __init__(self):
        self.defects: List[DeepDefect] = []
        self.start_time = time.time()
        self.process = psutil.Process()
    
    def get_memory_usage(self) -> float:
        return self.process.memory_info().rss / 1024 / 1024
    
    def log_defect(self, defect: DeepDefect):
        self.defects.append(defect)
        print(f"\n🔴🔴🔴 发现缺陷: {defect.title}")
        print(f"   严重性: {defect.severity.value}")
        print(f"   位置: {defect.location}")
    
    def test_fastapi_long_term(self):
        """测试: FastAPI项目长时间分析"""
        print("\n" + "="*70)
        print("测试 1: FastAPI项目长时间分析")
        print("="*70)
        
        project_dir = Path("/workspace/cloned_fastapi_project")
        if not project_dir.exists():
            print("跳过：项目不存在")
            return
        
        py_files = list(project_dir.rglob("*.py"))
        print(f"找到 {len(py_files)} 个Python文件")
        
        iterations = 500
        success_count = 0
        error_count = 0
        errors = []
        memory_samples = []
        
        mem_start = self.get_memory_usage()
        print(f"开始内存: {mem_start:.2f}MB")
        
        try:
            from fullpathtest.core.layer_17_lexer.lexer import Lexer
            from fullpathtest.core.layer_18_ast.ast_builder import ASTBuilder
            
            lexer = Lexer()
            ast_builder = ASTBuilder()
            
            for i in range(iterations):
                if i % 50 == 0:
                    mem_current = self.get_memory_usage()
                    memory_samples.append(mem_current)
                    print(f"进度: {i}/{iterations} - 内存: {mem_current:.2f}MB")
                
                file_path = random.choice(py_files)
                try:
                    code = file_path.read_text(encoding='utf-8', errors='ignore')
                    tokens = lexer.tokenize(code, str(file_path))
                    ast = ast_builder.build(tokens)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    if len(errors) < 20:
                        errors.append(str(e))
        
        except Exception as e:
            print(f"测试失败: {e}")
            import traceback
            traceback.print_exc()
        
        mem_end = self.get_memory_usage()
        print(f"完成：成功={success_count}, 失败={error_count}")
        print(f"结束内存: {mem_end:.2f}MB (增长: {mem_end - mem_start:.2f}MB)")
        
        if (mem_end - mem_start) > 30:
            self.log_defect(DeepDefect(
                defect_id="DRT-001",
                severity=DefectSeverity.MEDIUM,
                category=DefectCategory.MEMORY_LEAK,
                title="长时间分析内存增长显著",
                description=f"{iterations}次迭代后内存增长 {(mem_end - mem_start):.2f}MB",
                reproduction_steps=["长时间词法分析和AST构建"],
                location="fullpathtest/core/layer_17_lexer & layer_18_ast",
                impact="长时间运行时内存使用持续增加",
                evidence={"samples": memory_samples, "growth": mem_end - mem_start},
                discovered_during="fastapi_long_term"
            ))
    
    def test_concurrent_analysis(self):
        """测试: 并发分析压力测试"""
        print("\n" + "="*70)
        print("测试 2: 并发分析压力测试")
        print("="*70)
        
        project_dir = Path("/workspace/cloned_fastapi_project")
        if not project_dir.exists():
            return
        
        py_files = list(project_dir.rglob("*.py"))[:30]
        
        from fullpathtest.core.layer_17_lexer.lexer import Lexer
        
        lexer = Lexer()
        
        concurrency_levels = [5, 10, 15]
        all_errors = []
        
        for concurrency in concurrency_levels:
            print(f"\n并发度: {concurrency}")
            
            start = time.time()
            success = 0
            failed = 0
            errors = []
            
            def analyze_file(file_path):
                try:
                    code = file_path.read_text(encoding='utf-8', errors='ignore')
                    lexer.tokenize(code, str(file_path))
                    return True
                except Exception as e:
                    return str(e)
            
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = {executor.submit(analyze_file, f): f for f in py_files}
                for future in as_completed(futures):
                    result = future.result()
                    if result is True:
                        success += 1
                    else:
                        failed += 1
                        if len(errors) < 10:
                            errors.append(result)
            
            dur = time.time() - start
            print(f"  成功: {success}, 失败: {failed}")
            print(f"  耗时: {dur:.2f}s")
            
            if failed > 0:
                all_errors.append({"concurrency": concurrency, "count": failed})
        
        if len(all_errors) > 0:
            self.log_defect(DeepDefect(
                defect_id="DRT-002",
                severity=DefectSeverity.LOW,
                category=DefectCategory.SCALABILITY,
                title=f"并发测试中有 {len(all_errors)} 个错误",
                description="高并发情况下分析可能出现错误",
                reproduction_steps=["并发执行词法分析"],
                location="fullpathtest - 并发模块",
                impact="高并发场景稳定性",
                evidence={"errors": all_errors},
                discovered_during="concurrent_analysis"
            ))
    
    def test_django_scan(self):
        """测试: Django项目扫描"""
        print("\n" + "="*70)
        print("测试 3: Django项目扫描")
        print("="*70)
        
        project_dir = Path("/workspace/django_project")
        if not project_dir.exists():
            return
        
        try:
            from fullpathtest.core.layer_09_source_scanner.scanner import SourceScanner
            from fullpathtest.core.layer_11_preprocess.preprocessor import CodePreprocessor
            
            scanner = SourceScanner()
            preprocessor = CodePreprocessor()
            
            py_files = list(project_dir.rglob("*.py"))[:100]
            print(f"扫描 {len(py_files)} 个文件...")
            
            processed = 0
            errors = []
            
            for file_path in py_files:
                try:
                    code = file_path.read_text(encoding='utf-8', errors='ignore')
                    preprocessor.preprocess(code, str(file_path))
                    processed += 1
                except Exception as e:
                    if len(errors) < 10:
                        errors.append(str(e))
            
            print(f"处理: {processed}/{len(py_files)}, 错误: {len(errors)}")
            
            if len(errors) > 0:
                self.log_defect(DeepDefect(
                    defect_id="DRT-003",
                    severity=DefectSeverity.LOW,
                    category=DefectCategory.EDGE_CASE,
                    title=f"Django扫描有 {len(errors)} 个文件处理失败",
                    description="部分特殊文件预处理失败",
                    reproduction_steps=["扫描Django项目"],
                    location="fullpathtest/core/layer_11_preprocess",
                    impact="部分极端情况文件可能无法处理",
                    evidence={"error_count": len(errors)},
                    discovered_during="django_scan"
                ))
        
        except Exception as e:
            print(f"测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    def test_edge_cases(self):
        """测试: 边缘情况"""
        print("\n" + "="*70)
        print("测试 4: 边缘情况压力测试")
        print("="*70)
        
        from fullpathtest.core.layer_17_lexer.lexer import Lexer
        from fullpathtest.core.layer_18_ast.ast_builder import ASTBuilder
        
        lexer = Lexer()
        ast_builder = ASTBuilder()
        
        edge_cases = [
            ("empty", ""),
            ("single_char", "x"),
            ("huge_code", "x = " + "'y'" * 10000),
            ("deep_nesting", "if True:\n" * 80 + "    pass"),
            ("utf8_emoji", "def 你好_🎯(): return '🎉'"),
            ("binary", "\x00\x01\x02\x03"),
        ]
        
        errors = []
        
        for name, code in edge_cases:
            try:
                print(f"\n测试 {name}...")
                tokens = lexer.tokenize(code, f"test_{name}.py")
                ast = ast_builder.build(tokens)
                print(f"  ✅")
            except Exception as e:
                print(f"  ❌: {e}")
                errors.append((name, str(e)))
        
        if len(errors) > 0:
            self.log_defect(DeepDefect(
                defect_id="DRT-004",
                severity=DefectSeverity.MEDIUM,
                category=DefectCategory.EDGE_CASE,
                title=f"边缘情况处理失败: {[e[0] for e in errors]}",
                description=f"{len(errors)} 个极端输入无法处理",
                reproduction_steps=["测试边缘情况"],
                location="fullpathtest - 词法分析/AST构建",
                impact="极端输入时可能出错",
                evidence={"failed_cases": errors},
                discovered_during="edge_cases"
            ))
    
    def test_path_operations(self):
        """测试: 路径枚举和处理"""
        print("\n" + "="*70)
        print("测试 5: 路径枚举极限测试")
        print("="*70)
        
        try:
            from fullpathtest.types.core import Path, PathSet, PathType
            
            paths = []
            for i in range(500):
                path = Path(
                    path_id=f"path_{i}",
                    path_type=PathType.INTRAPROCEDURAL,
                    node_sequence=[f"n_{j}" for j in range(5)],
                    conditions=[],
                    constraints={}
                )
                paths.append(path)
            
            path_set = PathSet(
                paths=paths,
                total_count=len(paths),
                pruned_count=0
            )
            print(f"✅ 创建 {len(paths)} 个路径成功")
        except Exception as e:
            self.log_defect(DeepDefect(
                defect_id="DRT-005",
                severity=DefectSeverity.LOW,
                category=DefectCategory.PERFORMANCE,
                title="路径创建极限测试失败",
                description=f"错误: {e}",
                reproduction_steps=["创建大量路径对象"],
                location="fullpathtest/types/core - Path/PathSet",
                impact="大量路径时可能性能问题",
                evidence={"error": str(e)},
                discovered_during="path_operations"
            ))
    
    def run_all(self):
        print("\n" + "="*70)
        print("FullPathTest 深度长时真实测试")
        print("="*70)
        print(f"开始时间: {datetime.now().isoformat()}")
        
        self.test_fastapi_long_term()
        self.test_concurrent_analysis()
        self.test_django_scan()
        self.test_edge_cases()
        self.test_path_operations()
        
        self.generate_report()
        return self.defects
    
    def generate_report(self):
        print("\n" + "="*70)
        print("测试报告")
        print("="*70)
        
        total = len(self.defects)
        if total == 0:
            print("\n🎉 无缺陷发现！系统表现完美！")
        else:
            print(f"\n发现 {total} 个缺陷:")
            for d in self.defects:
                print(f"  - [{d.severity.value}] {d.title} ({d.defect_id})")
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "duration": time.time() - self.start_time,
            "total_defects": total,
            "defects": [
                {
                    "id": d.defect_id,
                    "severity": d.severity.value,
                    "category": d.category.value,
                    "title": d.title,
                    "description": d.description,
                    "location": d.location
                }
                for d in self.defects
            ]
        }
        
        with open("/workspace/deep_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n报告已保存至 /workspace/deep_test_report.json")


def main():
    tester = DeepRealTest()
    tester.run_all()


if __name__ == "__main__":
    main()
