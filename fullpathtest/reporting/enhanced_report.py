"""
增强的报告生成器

支持多种格式的报告生成，包括HTML、JSON、Markdown、PDF等。
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class ReportSection:
    """报告章节"""
    title: str
    content: str
    level: int = 1
    subsections: List['ReportSection'] = None
    
    def __post_init__(self):
        if self.subsections is None:
            self.subsections = []


class EnhancedReportGenerator:
    """增强的报告生成器"""
    
    def __init__(self):
        self.sections: List[ReportSection] = []
        self.metadata: Dict[str, Any] = {}
    
    def add_section(self, title: str, content: str, level: int = 1):
        """添加章节"""
        section = ReportSection(title=title, content=content, level=level)
        self.sections.append(section)
    
    def add_subsection(self, parent_title: str, title: str, content: str):
        """添加子章节"""
        for section in self.sections:
            if section.title == parent_title:
                section.subsections.append(
                    ReportSection(title=title, content=content, level=section.level + 1)
                )
                break
    
    def generate_markdown(self) -> str:
        """生成Markdown格式报告"""
        lines = []
        lines.append("# FullPathTest 测试报告\n")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append("---\n\n")
        
        for section in self.sections:
            lines.append(f"{'#' * section.level} {section.title}\n\n")
            lines.append(f"{section.content}\n\n")
            
            for subsection in section.subsections:
                lines.append(f"{'#' * subsection.level} {subsection.title}\n\n")
                lines.append(f"{subsection.content}\n\n")
        
        return ''.join(lines)
    
    def generate_json(self) -> str:
        """生成JSON格式报告"""
        data = {
            'metadata': self.metadata,
            'generated_at': datetime.now().isoformat(),
            'sections': [
                {
                    'title': s.title,
                    'content': s.content,
                    'level': s.level,
                    'subsections': [
                        {'title': sub.title, 'content': sub.content, 'level': sub.level}
                        for sub in s.subsections
                    ]
                }
                for s in self.sections
            ]
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def generate_html(self) -> str:
        """生成HTML格式报告"""
        html_parts = [
            '<!DOCTYPE html>',
            '<html lang="zh-CN">',
            '<head>',
            '    <meta charset="UTF-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            '    <title>FullPathTest 测试报告</title>',
            '    <style>',
            '        body { font-family: Arial, sans-serif; margin: 40px; }',
            '        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }',
            '        h2 { color: #34495e; margin-top: 30px; }',
            '        h3 { color: #7f8c8d; }',
            '        .metadata { background: #ecf0f1; padding: 15px; border-radius: 5px; }',
            '        .section { margin: 20px 0; }',
            '        table { border-collapse: collapse; width: 100%; margin: 20px 0; }',
            '        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }',
            '        th { background-color: #3498db; color: white; }',
            '    </style>',
            '</head>',
            '<body>',
            '    <h1>📊 FullPathTest 测试报告</h1>',
            '    <div class="metadata">',
            f'        <p><strong>生成时间</strong>: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>',
            '    </div>'
        ]
        
        for section in self.sections:
            html_parts.append(f'    <div class="section">')
            html_parts.append(f'        <h{section.level}>{section.title}</h{section.level}>')
            html_parts.append(f'        <p>{section.content}</p>')
            
            for subsection in section.subsections:
                html_parts.append(f'        <h{subsection.level}>{subsection.title}</h{subsection.level}>')
                html_parts.append(f'        <p>{subsection.content}</p>')
            
            html_parts.append('    </div>')
        
        html_parts.extend([
            '</body>',
            '</html>'
        ])
        
        return '\n'.join(html_parts)


def generate_coverage_report(coverage_data: Dict[str, Any]) -> str:
    """生成覆盖率报告"""
    generator = EnhancedReportGenerator()
    
    generator.add_section(
        "代码覆盖率概览",
        f"总体覆盖率: {coverage_data.get('total_coverage', 0):.2f}%"
    )
    
    generator.add_section(
        "语句覆盖",
        f"已覆盖: {coverage_data.get('covered_statements', 0)} / "
        f"总计: {coverage_data.get('total_statements', 0)}",
        level=2
    )
    
    generator.add_section(
        "分支覆盖",
        f"已覆盖: {coverage_data.get('covered_branches', 0)} / "
        f"总计: {coverage_data.get('total_branches', 0)}",
        level=2
    )
    
    return generator.generate_markdown()


def generate_defect_report(defects: List[Dict[str, Any]]) -> str:
    """生成缺陷报告"""
    generator = EnhancedReportGenerator()
    
    generator.add_section(
        "缺陷概览",
        f"发现缺陷总数: {len(defects)}"
    )
    
    for i, defect in enumerate(defects, 1):
        generator.add_section(
            f"缺陷 #{i}: {defect.get('title', 'Unknown')}",
            f"严重程度: {defect.get('severity', 'Unknown')}\n"
            f"位置: {defect.get('location', 'Unknown')}\n"
            f"描述: {defect.get('description', 'No description')}",
            level=2
        )
    
    return generator.generate_markdown()
