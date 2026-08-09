"""
FullPathTest API模块

提供HTTP API接口。
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from fullpathtest import __version__


class TaskCreateRequest(BaseModel):
    """创建任务请求"""
    source_type: str = "dir"
    source_path: str
    language: Optional[str] = None
    coverage_rules: Optional[Dict[str, Any]] = None
    llm_mode: str = "local"


class TaskExecuteRequest(BaseModel):
    """执行任务请求"""
    mode: str = "full"
    parallel: int = 4
    timeout: int = 300


class ReportRequest(BaseModel):
    """报告请求"""
    format: str = "json"
    include_coverage: bool = True
    include_defects: bool = True


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title="FullPathTest API",
        description="极致轻量化全路径代码测试系统 V4.0 API",
        version=__version__
    )
    
    @app.get("/")
    async def root():
        """根路径"""
        return {
            "name": "FullPathTest API",
            "version": __version__,
            "status": "running"
        }
    
    @app.get("/health")
    async def health():
        """健康检查"""
        return {"status": "healthy"}
    
    @app.post("/api/v1/tasks")
    async def create_task(request: TaskCreateRequest):
        """创建任务"""
        try:
            from fullpathtest.core.layer_01_entry.entry_point import EntryPoint
            from fullpathtest.types.core import TaskRequest, SourceType, LLMMode
            
            source_type_map = {
                'dir': SourceType.LOCAL_DIRECTORY,
                'git': SourceType.GIT_REPOSITORY,
                'archive': SourceType.ARCHIVE_FILE
            }
            
            llm_mode_map = {
                'local': LLMMode.LOCAL_ONLY,
                'cloud': LLMMode.CLOUD_ONLY,
                'hybrid': LLMMode.HYBRID,
                'offline': LLMMode.OFFLINE
            }
            
            task_request = TaskRequest(
                task_id=f"TASK-{hash(request.source_path) % 100000}",
                source_type=source_type_map.get(request.source_type, SourceType.LOCAL_DIRECTORY),
                source_path=request.source_path,
                language=request.language,
                llm_mode=llm_mode_map.get(request.llm_mode, LLMMode.LOCAL_ONLY)
            )
            
            entry = EntryPoint()
            context = entry.process_request(task_request)
            
            return {
                "task_id": context.task_id,
                "status": context.state.name,
                "created_at": context.created_at.isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/tasks/{task_id}")
    async def get_task(task_id: str):
        """获取任务状态"""
        try:
            from fullpathtest.core.layer_02_lifecycle.task_manager import TaskManager
            
            manager = TaskManager()
            context = manager.get_task_context(task_id)
            
            if not context:
                raise HTTPException(status_code=404, detail="Task not found")
            
            return {
                "task_id": context.task_id,
                "status": context.state.name,
                "progress": context.progress,
                "current_layer": context.current_layer,
                "created_at": context.created_at.isoformat(),
                "updated_at": context.updated_at.isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/tasks")
    async def list_tasks():
        """列出所有任务"""
        try:
            from fullpathtest.core.layer_02_lifecycle.task_manager import TaskManager
            
            manager = TaskManager()
            tasks = manager.list_tasks()
            
            return {
                "tasks": [
                    {
                        "task_id": t.task_id,
                        "status": t.state.name,
                        "progress": t.progress
                    }
                    for t in tasks
                ]
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/tasks/{task_id}/execute")
    async def execute_task(task_id: str, request: TaskExecuteRequest):
        """执行任务"""
        try:
            from fullpathtest.core.layer_02_lifecycle.task_manager import TaskManager
            from fullpathtest.core.layer_34_execution.execution_engine import ExecutionEngine
            import asyncio
            
            manager = TaskManager()
            context = manager.get_task_context(task_id)
            
            if not context:
                raise HTTPException(status_code=404, detail="Task not found")
            
            context.config.execution_config.max_parallel_workers = request.parallel
            context.config.execution_config.timeout_per_test = request.timeout
            
            engine = ExecutionEngine(context.config)
            
            async def run():
                return await engine.execute_tests(context)
            
            result = asyncio.run(run())
            
            return {
                "task_id": task_id,
                "execution_result": result
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/tasks/{task_id}/report")
    async def get_report(task_id: str, format: str = "json"):
        """获取报告"""
        try:
            from fullpathtest.core.layer_41_report.report_generator import ReportGenerator
            
            generator = ReportGenerator()
            report = generator.generate(task_id, format, True, True)
            
            return {
                "task_id": task_id,
                "content": report.content,
                "format": format
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.delete("/api/v1/tasks/{task_id}")
    async def cancel_task(task_id: str):
        """取消任务"""
        try:
            from fullpathtest.core.layer_02_lifecycle.task_manager import TaskManager
            
            manager = TaskManager()
            success = manager.cancel_task(task_id)
            
            if success:
                return {"message": "Task cancelled", "task_id": task_id}
            else:
                raise HTTPException(status_code=404, detail="Task not found")
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return app
