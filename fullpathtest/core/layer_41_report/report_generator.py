"""
第41层：报告生成层

生成格式化测试报告。
"""

from typing import Dict, Any, Optional
from fullpathtest.types.core import Report, CoverageReport, DefectInfo, ExecutionResult
from datetime import datetime
from collections import defaultdict


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.template_cache = {}
    
    def generate(
        self,
        task_id: str,
        format_type: str = 'text',
        include_coverage: bool = True,
        include_defects: bool = True
    ) -> 'ReportContent':
        """生成报告"""
        report_data = self._collect_report_data(task_id)
        
        if format_type == 'json':
            return self._generate_json_report(report_data, include_coverage, include_defects)
        elif format_type == 'html':
            return self._generate_html_report(report_data, include_coverage, include_defects)
        else:
            return self._generate_text_report(report_data, include_coverage, include_defects)
    
    def _collect_report_data(self, task_id: str) -> Dict[str, Any]:
        """收集报告数据"""
        from fullpathtest.core.layer_02_lifecycle.task_manager import TaskManager
        
        manager = TaskManager()
        context = manager.get_task_context(task_id)
        
        if not context:
            return {'task_id': task_id, 'status': 'not_found'}
        
        results = context.artifacts.get('execution_results', [])
        coverage = context.artifacts.get('coverage_report', None)
        defects = context.artifacts.get('defects', [])
        
        return {
            'task_id': task_id,
            'status': context.state.name,
            'progress': context.progress,
            'created_at': context.created_at.isoformat(),
            'updated_at': context.updated_at.isoformat(),
            'execution_results': results,
            'coverage': coverage,
            'defects': defects,
            'metadata': context.metadata
        }
    
    def _generate_text_report(
        self,
        data: Dict[str, Any],
        include_coverage: bool,
        include_defects: bool
    ) -> 'ReportContent':
        """生成文本报告"""
        lines = []
        
        lines.append("=" * 80)
        lines.append("FullPathTest 测试报告")
        lines.append("=" * 80)
        lines.append(f"任务ID: {data.get('task_id', 'N/A')}")
        lines.append(f"状态: {data.get('status', 'N/A')}")
        lines.append(f"进度: {data.get('progress', 0):.1f}%")
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        results = data.get('execution_results', [])
        if results:
            lines.append("-" * 80)
            lines.append("执行摘要")
            lines.append("-" * 80)
            passed = sum(1 for r in results if hasattr(r, 'status') and r.status.name == 'PASSED')
            failed = sum(1 for r in results if hasattr(r, 'status') and r.status.name == 'FAILED')
            lines.append(f"总用例数: {len(results)}")
            lines.append(f"通过: {passed}")
            lines.append(f"失败: {failed}")
            lines.append(f"通过率: {passed/len(results)*100:.1f}%" if results else "N/A")
            lines.append("")
        
        if include_coverage and data.get('coverage'):
            lines.append("-" * 80)
            lines.append("覆盖率详情")
            lines.append("-" * 80)
            cov = data['coverage']
            lines.append(f"语句覆盖率: {cov.get('statement_coverage', 0):.1f}%")
            lines.append(f"分支覆盖率: {cov.get('branch_coverage', 0):.1f}%")
            lines.append(f"路径覆盖率: {cov.get('path_coverage', 0):.1f}%")
            lines.append("")
        
        if include_defects and data.get('defects'):
            lines.append("-" * 80)
            lines.append("缺陷列表")
            lines.append("-" * 80)
            for defect in data['defects']:
                lines.append(f"[{defect.get('severity', 'UNKNOWN')}] {defect.get('description', 'N/A')}")
                lines.append(f"  位置: {defect.get('location', 'N/A')}")
                lines.append("")
        
        lines.append("=" * 80)
        lines.append("报告结束")
        lines.append("=" * 80)
        
        return ReportContent(
            content='\n'.join(lines),
            format_type='text',
            task_id=data.get('task_id', 'unknown')
        )
    
    def _generate_json_report(
        self,
        data: Dict[str, Any],
        include_coverage: bool,
        include_defects: bool
    ) -> 'ReportContent':
        """生成JSON报告"""
        import json
        
        report = {
            'report_version': '4.0.0',
            'generated_at': datetime.now().isoformat(),
            'task_id': data.get('task_id'),
            'status': data.get('status'),
            'progress': data.get('progress'),
            'summary': self._generate_summary(data)
        }
        
        if include_coverage and data.get('coverage'):
            report['coverage'] = data['coverage']
        
        if include_defects and data.get('defects'):
            report['defects'] = data['defects']
        
        return ReportContent(
            content=json.dumps(report, indent=2, ensure_ascii=False),
            format_type='json',
            task_id=data.get('task_id', 'unknown')
        )
    
    def _generate_html_report(
        self,
        data: Dict[str, Any],
        include_coverage: bool,
        include_defects: bool
    ) -> 'ReportContent':
        """生成HTML报告"""
        html = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '<meta charset="UTF-8">',
            '<title>FullPathTest 测试报告</title>',
            '<style>',
            'body { font-family: Arial, sans-serif; margin: 40px; }',
            'h1 { color: #333; }',
            'table { border-collapse: collapse; width: 100%; margin: 20px 0; }',
            'th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }',
            'th { background-color: #4CAF50; color: white; }',
            '.passed { color: green; }',
            '.failed { color: red; }',
            '.section { margin: 20px 0; }',
            '</style>',
            '</head>',
            '<body>',
            '<h1>FullPathTest 测试报告</h1>',
            f'<p>任务ID: {data.get("task_id", "N/A")}</p>',
            f'<p>状态: {data.get("status", "N/A")}</p>',
            f'<p>进度: {data.get("progress", 0):.1f}%</p>',
        ]
        
        results = data.get('execution_results', [])
        if results:
            passed = sum(1 for r in results if hasattr(r, 'status') and r.status.name == 'PASSED')
            failed = sum(1 for r in results if hasattr(r, 'status') and r.status.name == 'FAILED')
            
            html.append('<div class="section">')
            html.append('<h2>执行摘要</h2>')
            html.append(f'<p>总用例数: {len(results)}</p>')
            html.append(f'<p class="passed">通过: {passed}</p>')
            html.append(f'<p class="failed">失败: {failed}</p>')
            html.append('</div>')
        
        html.append('</body>')
        html.append('</html>')
        
        return ReportContent(
            content='\n'.join(html),
            format_type='html',
            task_id=data.get('task_id', 'unknown')
        )
    
    def _generate_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成摘要"""
        results = data.get('execution_results', [])
        total = len(results)
        passed = sum(1 for r in results if hasattr(r, 'status') and r.status.name == 'PASSED')
        
        return {
            'total_cases': total,
            'passed': passed,
            'failed': total - passed,
            'pass_rate': round(passed/total*100, 2) if total > 0 else 0
        }


class ReportContent:
    """报告内容"""
    
    def __init__(self, content: str, format_type: str, task_id: str):
        self.content = content
        self.format_type = format_type
        self.task_id = task_id
        self.generated_at = datetime.now()


class ReportExporter:
    """报告导出器"""
    
    def export(self, report: ReportContent, output_path: str) -> bool:
        """导出报告"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report.content)
            return True
        except Exception:
            return False
