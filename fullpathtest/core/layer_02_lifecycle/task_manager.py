"""
任务生命周期管理层

负责单机/分布式任务全生命周期管理，包括任务创建、状态流转、进度跟踪等。
"""

from typing import Dict, Optional, List
from datetime import datetime
from fullpathtest.types.core import TaskContext, TaskRequest, TaskState, ConfigSnapshot
import threading


class TaskManager:
    """任务管理器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._tasks = {}
                    cls._instance._state_lock = threading.Lock()
        return cls._instance
    
    def create_task(self, request: TaskRequest, config: ConfigSnapshot) -> TaskContext:
        """创建新任务"""
        context = TaskContext(
            task_id=request.task_id,
            request=request,
            config=config,
            state=TaskState.INITIALIZING,
            progress=0.0,
            current_layer=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        with self._state_lock:
            self._tasks[request.task_id] = context
        
        return context
    
    def get_task_context(self, task_id: str) -> Optional[TaskContext]:
        """获取任务上下文"""
        with self._state_lock:
            return self._tasks.get(task_id)
    
    def update_state(self, task_id: str, state: TaskState, progress: float = None) -> bool:
        """更新任务状态"""
        with self._state_lock:
            if task_id not in self._tasks:
                return False
            
            task = self._tasks[task_id]
            task.state = state
            task.updated_at = datetime.now()
            
            if progress is not None:
                task.progress = progress
            
            return True
    
    def update_progress(self, task_id: str, progress: float, layer: int = None) -> bool:
        """更新任务进度"""
        with self._state_lock:
            if task_id not in self._tasks:
                return False
            
            task = self._tasks[task_id]
            task.progress = min(100.0, max(0.0, progress))
            task.updated_at = datetime.now()
            
            if layer is not None:
                task.current_layer = layer
            
            return True
    
    def set_error(self, task_id: str, error: str) -> bool:
        """设置任务错误"""
        with self._state_lock:
            if task_id not in self._tasks:
                return False
            
            task = self._tasks[task_id]
            task.state = TaskState.FAILED
            task.error = error
            task.updated_at = datetime.now()
            
            return True
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        return self.update_state(task_id, TaskState.CANCELLED)
    
    def pause_task(self, task_id: str) -> bool:
        """暂停任务"""
        return self.update_state(task_id, TaskState.PAUSED)
    
    def resume_task(self, task_id: str) -> bool:
        """恢复任务"""
        with self._state_lock:
            if task_id not in self._tasks:
                return False
            
            task = self._tasks[task_id]
            if task.state == TaskState.PAUSED:
                task.state = TaskState.INITIALIZING
                task.updated_at = datetime.now()
                return True
            
            return False
    
    def list_tasks(self) -> List[TaskContext]:
        """列出所有任务"""
        with self._state_lock:
            return list(self._tasks.values())
    
    def cleanup_completed(self, max_age_hours: int = 24) -> int:
        """清理已完成的任务"""
        with self._state_lock:
            now = datetime.now()
            to_remove = []
            
            for task_id, task in self._tasks.items():
                if task.state in [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED]:
                    age_hours = (now - task.updated_at).total_seconds() / 3600
                    if age_hours > max_age_hours:
                        to_remove.append(task_id)
            
            for task_id in to_remove:
                del self._tasks[task_id]
            
            return len(to_remove)


class TaskExecutor:
    """任务执行器"""
    
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
    
    def execute_task(self, task_id: str) -> bool:
        """执行任务"""
        context = self.task_manager.get_task_context(task_id)
        if not context:
            return False
        
        try:
            self.task_manager.update_state(task_id, TaskState.PARSING)
            
            from fullpathtest.core.layer_04_nlp.parser import NLPCommandParser
            parser = NLPCommandParser()
            instruction = parser.parse(context)
            
            context.artifacts['instruction'] = instruction
            self.task_manager.update_progress(task_id, 15.0, layer=4)
            
            from fullpathtest.core.layer_09_source_scanner.scanner import SourceScanner
            scanner = SourceScanner()
            file_list = scanner.scan(context)
            
            context.artifacts['files'] = file_list
            self.task_manager.update_progress(task_id, 25.0, layer=9)
            
            return True
            
        except Exception as e:
            self.task_manager.set_error(task_id, str(e))
            return False
    
    def resume_execution(self, task_id: str) -> bool:
        """恢复执行"""
        context = self.task_manager.get_task_context(task_id)
        if not context:
            return False
        
        return self.execute_task(task_id)
