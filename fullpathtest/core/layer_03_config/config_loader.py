"""
第3层：全局配置规则层

系统唯一、集中式配置管理层，加载系统默认配置、用户配置、项目配置。
"""

from typing import Dict, Any, Optional
from fullpathtest.types.core import (
    ConfigSnapshot, LLMConfig, CacheConfig, ExecutionConfig,
    SecurityRules, CoverageRules, TaskRequest, LLMMode
)
import os
import yaml
from pathlib import Path


class ConfigLoader:
    """配置加载器"""
    
    DEFAULT_CONFIG_DIR = Path.home() / ".fullpathtest"
    PROJECT_CONFIG_FILE = "fullpathtest.yaml"
    
    def __init__(self):
        self._config_cache: Dict[str, ConfigSnapshot] = {}
    
    def load_config(self, request: TaskRequest) -> ConfigSnapshot:
        """加载配置快照"""
        default_config = self._load_default_config()
        user_config = self._load_user_config()
        project_config = self._load_project_config(request.source_path)
        
        config = self._merge_configs(default_config, user_config, project_config, request)
        
        self._apply_overrides(config, request)
        
        return config
    
    def _load_default_config(self) -> ConfigSnapshot:
        """加载系统默认配置"""
        return ConfigSnapshot(
            llm_config=LLMConfig(),
            coverage_rules=CoverageRules(),
            cache_config=CacheConfig(),
            execution_config=ExecutionConfig(),
            security_rules=SecurityRules()
        )
    
    def _load_user_config(self) -> Optional[Dict[str, Any]]:
        """加载用户配置"""
        user_config_path = self.DEFAULT_CONFIG_DIR / "config.yaml"
        if user_config_path.exists():
            with open(user_config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return None
    
    def _load_project_config(self, source_path: str) -> Optional[Dict[str, Any]]:
        """加载项目配置"""
        project_root = self._find_project_root(source_path)
        if project_root:
            config_path = project_root / self.PROJECT_CONFIG_FILE
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
        return None
    
    def _find_project_root(self, source_path: str) -> Optional[Path]:
        """查找项目根目录"""
        path = Path(source_path).resolve()
        if path.is_file():
            path = path.parent
        
        current = path
        for _ in range(10):
            if (current / self.PROJECT_CONFIG_FILE).exists():
                return current
            parent = current.parent
            if parent == current:
                break
            current = parent
        
        return None
    
    def _merge_configs(
        self,
        default: ConfigSnapshot,
        user: Optional[Dict[str, Any]],
        project: Optional[Dict[str, Any]],
        request: TaskRequest
    ) -> ConfigSnapshot:
        """合并配置"""
        config = ConfigSnapshot()
        
        config.llm_config = default.llm_config
        config.coverage_rules = default.coverage_rules
        config.cache_config = default.cache_config
        config.execution_config = default.execution_config
        config.security_rules = default.security_rules
        
        if project:
            config = self._apply_yaml_config(config, project)
        
        if user:
            config = self._apply_yaml_config(config, user)
        
        return config
    
    def _apply_yaml_config(self, config: ConfigSnapshot, yaml_config: Dict[str, Any]) -> ConfigSnapshot:
        """应用YAML配置"""
        if 'llm' in yaml_config:
            llm_cfg = yaml_config['llm']
            config.llm_config = LLMConfig(
                mode=LLMMode[llm_cfg.get('mode', 'LOCAL_ONLY').upper()] if isinstance(llm_cfg.get('mode'), str) else config.llm_config.mode,
                local_endpoint=llm_cfg.get('local_endpoint', config.llm_config.local_endpoint),
                cloud_provider=llm_cfg.get('cloud_provider', config.llm_config.cloud_provider),
                cloud_endpoint=llm_cfg.get('cloud_endpoint', config.llm_config.cloud_endpoint),
                model_name=llm_cfg.get('model_name', config.llm_config.model_name),
                temperature=llm_cfg.get('temperature', config.llm_config.temperature),
                max_tokens=llm_cfg.get('max_tokens', config.llm_config.max_tokens),
                timeout=llm_cfg.get('timeout', config.llm_config.timeout),
                retry_count=llm_cfg.get('retry_count', config.llm_config.retry_count)
            )
        
        if 'coverage' in yaml_config:
            cov_cfg = yaml_config['coverage']
            config.coverage_rules = CoverageRules(
                statement=cov_cfg.get('statement', config.coverage_rules.statement),
                branch=cov_cfg.get('branch', config.coverage_rules.branch),
                condition=cov_cfg.get('condition', config.coverage_rules.condition),
                path=cov_cfg.get('path', config.coverage_rules.path),
                call_chain=cov_cfg.get('call_chain', config.coverage_rules.call_chain),
                e2e_flow=cov_cfg.get('e2e_flow', config.coverage_rules.e2e_flow),
                max_depth=cov_cfg.get('max_depth', config.coverage_rules.max_depth),
                max_paths_per_function=cov_cfg.get('max_paths_per_function', config.coverage_rules.max_paths_per_function)
            )
        
        if 'cache' in yaml_config:
            cache_cfg = yaml_config['cache']
            config.cache_config = CacheConfig(
                enable_memory_cache=cache_cfg.get('enable_memory_cache', config.cache_config.enable_memory_cache),
                enable_disk_cache=cache_cfg.get('enable_disk_cache', config.cache_config.enable_disk_cache),
                enable_vector_cache=cache_cfg.get('enable_vector_cache', config.cache_config.enable_vector_cache),
                memory_cache_size=cache_cfg.get('memory_cache_size', config.cache_config.memory_cache_size),
                disk_cache_dir=cache_cfg.get('disk_cache_dir', config.cache_config.disk_cache_dir),
                vector_db_path=cache_cfg.get('vector_db_path', config.cache_config.vector_db_path),
                cache_ttl=cache_cfg.get('cache_ttl', config.cache_config.cache_ttl)
            )
        
        if 'execution' in yaml_config:
            exec_cfg = yaml_config['execution']
            config.execution_config = ExecutionConfig(
                max_parallel_workers=exec_cfg.get('max_parallel_workers', config.execution_config.max_parallel_workers),
                timeout_per_test=exec_cfg.get('timeout_per_test', config.execution_config.timeout_per_test),
                max_retries=exec_cfg.get('max_retries', config.execution_config.max_retries),
                enable_coverage=exec_cfg.get('enable_coverage', config.execution_config.enable_coverage),
                enable_profiling=exec_cfg.get('enable_profiling', config.execution_config.enable_profiling)
            )
        
        if 'security' in yaml_config:
            sec_cfg = yaml_config['security']
            config.security_rules = SecurityRules(
                skip_sensitive=sec_cfg.get('skip_sensitive', config.security_rules.skip_sensitive),
                skip_test_code=sec_cfg.get('skip_test_code', config.security_rules.skip_test_code),
                allowed_paths=sec_cfg.get('allowed_paths', config.security_rules.allowed_paths),
                blocked_paths=sec_cfg.get('blocked_paths', config.security_rules.blocked_paths),
                max_file_size=sec_cfg.get('max_file_size', config.security_rules.max_file_size)
            )
        
        return config
    
    def _apply_overrides(self, config: ConfigSnapshot, request: TaskRequest) -> None:
        """应用请求级覆盖"""
        if request.llm_mode:
            config.llm_config.mode = request.llm_mode
        
        if request.coverage_rules:
            config.coverage_rules = request.coverage_rules
    
    def save_user_config(self, config: Dict[str, Any]) -> bool:
        """保存用户配置"""
        try:
            self.DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            config_path = self.DEFAULT_CONFIG_DIR / "config.yaml"
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False)
            return True
        except Exception:
            return False
    
    def create_default_config_file(self) -> Path:
        """创建默认配置文件"""
        self.DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        config_path = self.DEFAULT_CONFIG_DIR / "config.yaml"
        
        default_config = {
            'llm': {
                'mode': 'local',
                'model_name': 'llama3',
                'temperature': 0.3,
                'max_tokens': 4096
            },
            'coverage': {
                'statement': True,
                'branch': True,
                'condition': True,
                'path': True,
                'max_depth': 100,
                'max_paths_per_function': 1000
            },
            'cache': {
                'enable_memory_cache': True,
                'enable_disk_cache': True,
                'enable_vector_cache': True
            },
            'execution': {
                'max_parallel_workers': 4,
                'timeout_per_test': 300
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        return config_path
