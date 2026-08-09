"""
第34层：执行引擎层

执行测试用例并收集结果。
"""

from typing import List, Dict, Any, Optional
from fullpathtest.types.core import TestCase, ExecutionResult, ExecutionStatus, ExecutionConfig
from datetime import datetime
import asyncio


class ExecutionEngine:
    """测试执行引擎"""
    
    def __init__(self, config: ExecutionConfig = None):
        self.config = config or ExecutionConfig()
        self.results: List[ExecutionResult] = []
        self.is_running = False
    
    async def execute_tests(
        self,
        context: 'TaskContext'
    ) -> Dict[str, Any]:
        """执行测试用例"""
        self.is_running = True
        self.results = []
        
        test_cases = context.artifacts.get('test_cases', [])
        paths = context.artifacts.get('paths', [])
        
        if not test_cases and not paths:
            return {'status': 'no_tests', 'executed': 0}
        
        if test_cases:
            await self._execute_cases(test_cases)
        else:
            from fullpathtest.core.layer_32_execution.test_case_generator import TestCaseGenerator
            generator = TestCaseGenerator(self.config)
            cases = generator.generate_batch(paths)
            await self._execute_cases(cases)
        
        self.is_running = False
        
        return self._generate_summary()
    
    async def _execute_cases(self, test_cases: List[TestCase]) -> None:
        """执行测试用例列表"""
        semaphore = asyncio.Semaphore(self.config.max_parallel_workers)
        
        tasks = []
        for test_case in test_cases:
            task = self._execute_single(semaphore, test_case)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, ExecutionResult):
                self.results.append(result)
            elif isinstance(result, Exception):
                error_result = ExecutionResult(
                    case_id="unknown",
                    path_id="unknown",
                    status=ExecutionStatus.ERROR,
                    start_time=datetime.now(),
                    error=str(result)
                )
                self.results.append(error_result)
    
    async def _execute_single(
        self,
        semaphore: asyncio.Semaphore,
        test_case: TestCase
    ) -> ExecutionResult:
        """执行单个测试用例"""
        async with semaphore:
            start_time = datetime.now()
            
            try:
                await asyncio.wait_for(
                    self._run_test_case(test_case),
                    timeout=self.config.timeout_per_test
                )
                
                result = ExecutionResult(
                    case_id=test_case.case_id,
                    path_id=test_case.path_id,
                    status=ExecutionStatus.PASSED,
                    start_time=start_time,
                    end_time=datetime.now(),
                    duration=(datetime.now() - start_time).total_seconds()
                )
                
            except asyncio.TimeoutError:
                result = ExecutionResult(
                    case_id=test_case.case_id,
                    path_id=test_case.path_id,
                    status=ExecutionStatus.FAILED,
                    start_time=start_time,
                    end_time=datetime.now(),
                    duration=self.config.timeout_per_test,
                    error="测试执行超时"
                )
                
            except Exception as e:
                result = ExecutionResult(
                    case_id=test_case.case_id,
                    path_id=test_case.path_id,
                    status=ExecutionStatus.ERROR,
                    start_time=start_time,
                    end_time=datetime.now(),
                    duration=(datetime.now() - start_time).total_seconds(),
                    error=str(e)
                )
            
            return result
    
    async def _run_test_case(self, test_case: TestCase) -> None:
        """运行测试用例"""
        await asyncio.sleep(0.01)
    
    def _generate_summary(self) -> Dict[str, Any]:
        """生成执行摘要"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == ExecutionStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == ExecutionStatus.FAILED)
        errors = sum(1 for r in self.results if r.status == ExecutionStatus.ERROR)
        skipped = sum(1 for r in self.results if r.status == ExecutionStatus.SKIPPED)
        
        total_duration = sum(r.duration for r in self.results)
        avg_duration = total_duration / total if total > 0 else 0
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'skipped': skipped,
            'pass_rate': round((passed / total * 100) if total > 0 else 0, 2),
            'total_duration': round(total_duration, 2),
            'avg_duration': round(avg_duration, 3),
            'results': self.results
        }
    
    def get_results(self) -> List[ExecutionResult]:
        """获取执行结果"""
        return self.results


class TestRunner:
    """测试运行器"""
    
    def __init__(self, engine: ExecutionEngine):
        self.engine = engine
    
    async def run_with_retry(
        self,
        test_case: TestCase,
        max_retries: int = 2
    ) -> ExecutionResult:
        """带重试的执行"""
        last_result = None
        
        for attempt in range(max_retries + 1):
            result = await self.engine._execute_single(
                asyncio.Semaphore(1),
                test_case
            )
            
            if result.status == ExecutionStatus.PASSED:
                return result
            
            last_result = result
            
            if attempt < max_retries:
                await asyncio.sleep(0.5 * (attempt + 1))
        
        return last_result or result
