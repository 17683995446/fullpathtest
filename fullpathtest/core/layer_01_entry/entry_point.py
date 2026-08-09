"""
第1层：交互入口层

作为系统唯一对外接入层，提供CLI、HTTP API、配置文件三种标准接入方式。
仅完成请求接收、格式校验、权限校验与参数标准化。
"""

from typing import Optional, Dict, Any
from fullpathtest.types.core import TaskRequest, SourceType, LLMMode, CoverageRules
import uuid
from datetime import datetime


class RequestValidator:
    """请求格式校验器"""
    
    @staticmethod
    def validate_source_path(path: str, source_type: SourceType) -> bool:
        """校验源路径有效性"""
        if not path:
            return False
        
        if source_type == SourceType.LOCAL_DIRECTORY:
            import os
            return os.path.exists(path)
        
        return True
    
    @staticmethod
    def validate_coverage_rules(rules: CoverageRules) -> bool:
        """校验覆盖规则有效性"""
        if rules.max_depth <= 0 or rules.max_depth > 1000:
            return False
        if rules.max_paths_per_function <= 0:
            return False
        return True
    
    @staticmethod
    def validate_llm_mode(mode: LLMMode) -> bool:
        """校验LLM模式"""
        return mode in [LLMMode.LOCAL_ONLY, LLMMode.CLOUD_ONLY, 
                       LLMMode.HYBRID, LLMMode.OFFLINE]


class EntryPoint:
    """系统入口点"""
    
    def __init__(self):
        self.validator = RequestValidator()
    
    def create_entry(self, source_path: str) -> Dict[str, Any]:
        """创建入口点 - 修复Bug: 添加缺失的方法"""
        from pathlib import Path
        import os
        
        path = Path(source_path)
        
        if not path.exists():
            raise FileNotFoundError(f"路径不存在: {source_path}")
        
        if path.is_file():
            return {
                'type': 'file',
                'path': str(path.absolute()),
                'name': path.name,
                'size': path.stat().st_size
            }
        elif path.is_dir():
            return {
                'type': 'directory',
                'path': str(path.absolute()),
                'name': path.name,
                'files': len(list(path.rglob('*.py')))
            }
        else:
            raise ValueError(f"无效的路径类型: {source_path}")
    
    def process_request(self, request: TaskRequest) -> 'TaskContext':
        """处理标准化请求"""
        from fullpathtest.core.layer_02_lifecycle.task_manager import TaskManager
        from fullpathtest.core.layer_03_config.config_loader import ConfigLoader
        
        if not self.validator.validate_source_path(request.source_path, request.source_type):
            raise ValueError(f"无效的源路径: {request.source_path}")
        
        if not self.validator.validate_coverage_rules(request.coverage_rules):
            raise ValueError("无效的覆盖规则")
        
        if not self.validator.validate_llm_mode(request.llm_mode):
            raise ValueError("无效的LLM模式")
        
        config_loader = ConfigLoader()
        config = config_loader.load_config(request)
        
        task_manager = TaskManager()
        context = task_manager.create_task(request, config)
        
        return context
    
    def process_cli_args(self, args: Dict[str, Any]) -> TaskRequest:
        """处理CLI参数"""
        task_id = f"FPT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        
        coverage_rules = CoverageRules(
            statement='statement' in args.get('coverage', ['statement']),
            branch='branch' in args.get('coverage', ['branch']),
            condition='condition' in args.get('coverage', ['condition']),
            path='path' in args.get('coverage', ['path']),
            call_chain='call' in args.get('coverage', []),
            e2e_flow='e2e' in args.get('coverage', []),
            max_depth=args.get('max_depth', 100),
            max_paths_per_function=args.get('max_paths', 1000)
        )
        
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
        
        return TaskRequest(
            task_id=task_id,
            source_type=source_type_map.get(args.get('source_type', 'dir'), SourceType.LOCAL_DIRECTORY),
            source_path=args['source'],
            language=args.get('language'),
            coverage_rules=coverage_rules,
            llm_mode=llm_mode_map.get(args.get('llm_mode', 'local'), LLMMode.LOCAL_ONLY),
            metadata=args.get('metadata', {})
        )
    
    def process_http_request(self, request_body: Dict[str, Any]) -> TaskRequest:
        """处理HTTP请求"""
        return self.process_cli_args(request_body)
    
    def process_config_file(self, config_path: str) -> Dict[str, Any]:
        """处理配置文件"""
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
