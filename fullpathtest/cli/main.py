#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FullPathTest CLI - 极致轻量化全路径代码测试系统命令行接口

提供完整的命令行界面，支持代码扫描、测试执行、报告生成等功能。
"""

import sys
from typing import Optional, List, Dict, Any
import click
from pathlib import Path
import asyncio

from fullpathtest import __version__
from fullpathtest.types.core import (
    TaskRequest, SourceType, LLMMode, CoverageRules,
    TaskContext, ConfigSnapshot, LLMConfig, CacheConfig
)


class CLIContext:
    """CLI执行上下文"""
    def __init__(self):
        self.verbose: bool = False
        self.config_path: Optional[Path] = None
        self.output_format: str = "text"
        self.context: Optional[TaskContext] = None


@click.group()
@click.version_option(version=__version__)
@click.option('-v', '--verbose', is_flag=True, help='启用详细输出')
@click.option('-c', '--config', type=click.Path(exists=True), help='配置文件路径')
@click.pass_context
def cli(ctx: click.Context, verbose: bool, config: Optional[str]) -> None:
    """FullPathTest - 极致轻量化全路径代码测试系统 V4.0"""
    cli_ctx = CLIContext()
    cli_ctx.verbose = verbose
    cli_ctx.config_path = Path(config) if config else None
    ctx.obj = cli_ctx


@cli.command()
@click.argument('source', type=str)
@click.option('--language', '-l', type=str, help='指定编程语言')
@click.option('--source-type', '-t', type=click.Choice(['dir', 'git', 'archive'], case_sensitive=False), 
              default='dir', help='代码来源类型')
@click.option('--coverage', '-cov', multiple=True, 
              type=click.Choice(['statement', 'branch', 'condition', 'path', 'call', 'e2e']),
              help='覆盖规则类型')
@click.option('--llm-mode', type=click.Choice(['local', 'cloud', 'hybrid', 'offline']),
              default='local', help='LLM运行模式')
@click.option('--output', '-o', type=click.Path(), help='输出文件路径')
@click.option('--max-paths', type=int, default=10000, help='最大路径数量')
@click.pass_context
def scan(ctx: click.Context, source: str, language: Optional[str], source_type: str,
         coverage: tuple, llm_mode: str, output: Optional[str], max_paths: int) -> int:
    """扫描代码源并生成测试策略"""
    cli_ctx: CLIContext = ctx.obj
    
    click.echo(f"[*] FullPathTest V{__version__} - 代码扫描")
    click.echo(f"[*] 代码源: {source}")
    click.echo(f"[*] 源类型: {source_type}")
    
    # 构建任务请求
    source_type_map = {'dir': SourceType.LOCAL_DIRECTORY, 'git': SourceType.GIT_REPOSITORY, 
                       'archive': SourceType.ARCHIVE_FILE}
    llm_mode_map = {'local': LLMMode.LOCAL_ONLY, 'cloud': LLMMode.CLOUD_ONLY,
                    'hybrid': LLMMode.HYBRID, 'offline': LLMMode.OFFLINE}
    
    coverage_rules = CoverageRules(
        statement='statement' in coverage or len(coverage) == 0,
        branch='branch' in coverage or len(coverage) == 0,
        condition='condition' in coverage or len(coverage) == 0,
        path='path' in coverage or len(coverage) == 0,
        call_chain='call' in coverage,
        e2e_flow='e2e' in coverage
    )
    
    task_request = TaskRequest(
        task_id=_generate_task_id(),
        source_type=source_type_map.get(source_type, SourceType.LOCAL_DIRECTORY),
        source_path=source,
        language=language,
        coverage_rules=coverage_rules,
        llm_mode=llm_mode_map.get(llm_mode, LLMMode.LOCAL_ONLY),
        metadata={'max_paths': max_paths}
    )
    
    click.echo(f"[*] 覆盖规则: {', '.join(coverage) if coverage else 'all'}")
    click.echo(f"[*] LLM模式: {llm_mode}")
    
    # 执行扫描
    try:
        from fullpathtest.core.layer_01_entry.entry_point import EntryPoint
        entry = EntryPoint()
        context = entry.process_request(task_request)
        
        click.echo(f"[+] 任务创建成功: {context.task_id}")
        click.echo(f"[+] 任务状态: {context.state.name}")
        
        return 0
    except Exception as e:
        click.echo(f"[-] 扫描失败: {e}", err=True)
        return 1


@cli.command()
@click.argument('task_id', type=str)
@click.option('--mode', '-m', type=click.Choice(['full', 'incremental', 'targeted']),
              default='full', help='执行模式')
@click.option('--parallel', '-p', type=int, default=4, help='并行工作数')
@click.option('--timeout', '-t', type=int, default=300, help='单个用例超时(秒)')
@click.pass_context
def execute(ctx: click.Context, task_id: str, mode: str, parallel: int, timeout: int) -> int:
    """执行指定任务的测试用例"""
    cli_ctx: CLIContext = ctx.obj
    
    click.echo(f"[*] 执行测试任务: {task_id}")
    click.echo(f"[*] 执行模式: {mode}")
    click.echo(f"[*] 并行度: {parallel}")
    
    try:
        from fullpathtest.core.layer_02_lifecycle.task_manager import TaskManager
        manager = TaskManager()
        context = manager.get_task_context(task_id)
        
        if not context:
            click.echo(f"[-] 任务不存在: {task_id}", err=True)
            return 1
        
        # 更新执行配置
        context.config.execution_config.max_parallel_workers = parallel
        context.config.execution_config.timeout_per_test = timeout
        
        from fullpathtest.core.layer_32_execution.execution_engine import ExecutionEngine
        engine = ExecutionEngine()
        
        async def run_execution():
            return await engine.execute_tests(context)
        
        result = asyncio.run(run_execution())
        
        click.echo(f"[+] 执行完成")
        click.echo(f"[+] 通过: {result.get('passed', 0)}")
        click.echo(f"[-] 失败: {result.get('failed', 0)}")
        
        return 0 if result.get('failed', 0) == 0 else 1
    except Exception as e:
        click.echo(f"[-] 执行失败: {e}", err=True)
        return 1


@cli.command()
@click.argument('task_id', type=str)
@click.option('--format', '-f', type=click.Choice(['text', 'html', 'json', 'xml']),
              default='text', help='报告格式')
@click.option('--output', '-o', type=click.Path(), help='输出文件路径')
@click.option('--include-coverage', is_flag=True, help='包含覆盖率详情')
@click.option('--include-defects', is_flag=True, help='包含缺陷信息')
@click.pass_context
def report(ctx: click.Context, task_id: str, format: str, output: Optional[str],
           include_coverage: bool, include_defects: bool) -> int:
    """生成测试报告"""
    cli_ctx: CLIContext = ctx.obj
    
    click.echo(f"[*] 生成报告: {task_id}")
    click.echo(f"[*] 报告格式: {format}")
    
    try:
        from fullpathtest.core.layer_41_report.report_generator import ReportGenerator
        
        generator = ReportGenerator()
        report_obj = generator.generate(task_id, format, include_coverage, include_defects)
        
        if output:
            Path(output).write_text(report_obj.content, encoding='utf-8')
            click.echo(f"[+] 报告已保存: {output}")
        else:
            click.echo(report_obj.content)
        
        return 0
    except Exception as e:
        click.echo(f"[-] 报告生成失败: {e}", err=True)
        return 1


@cli.command()
@click.argument('task_id', type=str)
@click.pass_context
def status(ctx: click.Context, task_id: str) -> int:
    """查询任务状态"""
    try:
        from fullpathtest.core.layer_02_lifecycle.task_manager import TaskManager
        manager = TaskManager()
        context = manager.get_task_context(task_id)
        
        if not context:
            click.echo(f"[-] 任务不存在: {task_id}", err=True)
            return 1
        
        click.echo(f"任务ID: {context.task_id}")
        click.echo(f"状态: {context.state.name}")
        click.echo(f"进度: {context.progress:.1f}%")
        click.echo(f"当前层: {context.current_layer}")
        click.echo(f"创建时间: {context.created_at}")
        click.echo(f"更新时间: {context.updated_at}")
        
        if context.error:
            click.echo(f"错误: {context.error}")
        
        return 0
    except Exception as e:
        click.echo(f"[-] 查询失败: {e}", err=True)
        return 1


@cli.command()
@click.pass_context
def list_tasks(ctx: click.Context) -> int:
    """列出所有任务"""
    try:
        from fullpathtest.core.layer_02_lifecycle.task_manager import TaskManager
        manager = TaskManager()
        tasks = manager.list_tasks()
        
        if not tasks:
            click.echo("没有运行中的任务")
            return 0
        
        click.echo(f"{'任务ID':<36} {'状态':<15} {'进度':<10} {'创建时间':<20}")
        click.echo("-" * 85)
        
        for task in tasks:
            click.echo(f"{task.task_id:<36} {task.state.name:<15} {task.progress:.1f}% {' '*4} {task.created_at.strftime('%Y-%m-%d %H:%M:%S'):<20}")
        
        return 0
    except Exception as e:
        click.echo(f"[-] 查询失败: {e}", err=True)
        return 1


@cli.command()
@click.argument('task_id', type=str)
@click.pass_context
def cancel(ctx: click.Context, task_id: str) -> int:
    """取消运行中的任务"""
    try:
        from fullpathtest.core.layer_02_lifecycle.task_manager import TaskManager
        manager = TaskManager()
        manager.cancel_task(task_id)
        
        click.echo(f"[+] 任务已取消: {task_id}")
        return 0
    except Exception as e:
        click.echo(f"[-] 取消失败: {e}", err=True)
        return 1


@cli.command()
@click.argument('task_id', type=str)
@click.pass_context
def resume(ctx: click.Context, task_id: str) -> int:
    """恢复暂停的任务"""
    try:
        from fullpathtest.core.layer_02_lifecycle.task_manager import TaskManager
        manager = TaskManager()
        manager.resume_task(task_id)
        
        click.echo(f"[+] 任务已恢复: {task_id}")
        return 0
    except Exception as e:
        click.echo(f"[-] 恢复失败: {e}", err=True)
        return 1


@cli.command()
@click.option('--server', '-s', is_flag=True, help='启动HTTP服务器')
@click.option('--host', default='0.0.0.0', help='监听地址')
@click.option('--port', type=int, default=8000, help='监听端口')
@click.pass_context
def serve(ctx: click.Context, server: bool, host: str, port: int) -> int:
    """启动HTTP API服务"""
    if not server:
        click.echo(ctx.get_help())
        return 0
    
    try:
        import uvicorn
        from fullpathtest.api.app import create_app
        
        click.echo(f"[*] 启动API服务器: {host}:{port}")
        app = create_app()
        uvicorn.run(app, host=host, port=port)
        
        return 0
    except ImportError:
        click.echo("[-] 请安装uvicorn: pip install uvicorn", err=True)
        return 1
    except Exception as e:
        click.echo(f"[-] 服务启动失败: {e}", err=True)
        return 1


@cli.command()
@click.pass_context
def info(ctx: click.Context) -> int:
    """显示系统信息"""
    click.echo(f"FullPathTest 版本: {__version__}")
    click.echo(f"Python 版本: {sys.version}")
    click.echo(f"支持语言: Python, Java, Go, Rust, TypeScript, C#")
    click.echo()
    click.echo("架构: 50层极致轻量化全路径测试系统")
    click.echo("- 第1-8层: 入口与语义理解")
    click.echo("- 第9-16层: 代码接入与分析")
    click.echo("- 第17-31层: 代码解析与路径生成")
    click.echo("- 第32-40层: 测试执行与监控")
    click.echo("- 第41-50层: 报告与系统集成")
    
    return 0


def _generate_task_id() -> str:
    """生成唯一任务ID"""
    import uuid
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    short_uuid = str(uuid.uuid4())[:8]
    return f"FPT-{timestamp}-{short_uuid}"


def main():
    """CLI入口点"""
    try:
        return cli(obj=None)
    except KeyboardInterrupt:
        click.echo("\n[!] 操作已取消", err=True)
        return 130
    except Exception as e:
        click.echo(f"[-] 未知错误: {e}", err=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
