"""
Project Configuration and Incremental Analysis System
项目配置系统和增量分析功能
支持项目级配置和智能增量分析（只分析变化的文件）
"""

import os
import json
import hashlib
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging

logger = logging.getLogger("config_system")


@dataclass
class ProjectConfiguration:
    """项目配置"""
    project_name: str = "default_project"
    project_root: str = "."
    analysis_tools: List[str] = field(default_factory=lambda: ["flake8", "mypy"])
    max_workers: int = 4
    timeout_seconds: int = 60
    ignore_patterns: List[str] = field(default_factory=lambda: [
        "__pycache__",
        "*.pyc",
        ".git",
        "venv",
        "env",
        ".venv",
        "node_modules",
        ".pytest_cache",
        "*.egg-info"
    ])
    include_patterns: List[str] = field(default_factory=lambda: ["*.py"])
    severity_filter: str = "all"  # all, error, warning, info
    auto_fix: bool = False
    fail_on_error: bool = False
    output_format: str = "json"  # json, html, text


class CacheManager:
    """缓存管理器 - 支持增量分析"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir or ".fullpathtest_cache"
        self.cache_file = os.path.join(self.cache_dir, "analysis_cache.json")
        self.file_hashes: Dict[str, str] = {}
        self.analysis_results: Dict[str, Dict[str, Any]] = {}
        self._load_cache()
    
    def _load_cache(self):
        """加载缓存"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.file_hashes = data.get('file_hashes', {})
                    self.analysis_results = data.get('analysis_results', {})
                logger.info(f"Loaded cache with {len(self.file_hashes)} entries")
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
    
    def _save_cache(self):
        """保存缓存"""
        os.makedirs(self.cache_dir, exist_ok=True)
        try:
            data = {
                'file_hashes': self.file_hashes,
                'analysis_results': self.analysis_results,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved cache with {len(self.file_hashes)} entries")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def calculate_file_hash(self, file_path: str) -> str:
        """计算文件的MD5哈希"""
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                hasher.update(f.read())
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash file {file_path}: {e}")
            return ""
    
    def get_changed_files(self, file_paths: List[str]) -> Set[str]:
        """获取自上次分析后有变化的文件"""
        changed = set()
        
        for file_path in file_paths:
            current_hash = self.calculate_file_hash(file_path)
            previous_hash = self.file_hashes.get(file_path, "")
            
            if current_hash != previous_hash:
                changed.add(file_path)
        
        logger.info(f"Found {len(changed)} changed files out of {len(file_paths)} total")
        return changed
    
    def update_file_hash(self, file_path: str):
        """更新文件哈希"""
        self.file_hashes[file_path] = self.calculate_file_hash(file_path)
    
    def save_analysis_result(self, file_path: str, result: Dict[str, Any]):
        """保存分析结果"""
        self.analysis_results[file_path] = result
        self.update_file_hash(file_path)
    
    def get_cached_result(self, file_path: str) -> Optional[Dict[str, Any]]:
        """获取缓存的分析结果（如果文件未变化）"""
        current_hash = self.calculate_file_hash(file_path)
        previous_hash = self.file_hashes.get(file_path, "")
        
        if current_hash == previous_hash and file_path in self.analysis_results:
            return self.analysis_results[file_path]
        
        return None
    
    def clear_cache(self):
        """清除缓存"""
        self.file_hashes.clear()
        self.analysis_results.clear()
        self._save_cache()
        logger.info("Cache cleared")
    
    def cleanup(self):
        """保存并清理"""
        self._save_cache()


class IncrementalAnalyzer:
    """增量分析器"""
    
    def __init__(self, config: Optional[ProjectConfiguration] = None):
        self.config = config or ProjectConfiguration()
        self.cache_manager = CacheManager()
        self.last_analysis_time: Optional[datetime] = None
    
    def should_analyze_file(self, file_path: str) -> bool:
        """判断文件是否需要分析"""
        if not os.path.exists(file_path):
            return False
        
        cached = self.cache_manager.get_cached_result(file_path)
        return cached is None
    
    def get_files_to_analyze(self, project_root: str) -> Dict[str, List[str]]:
        """获取需要分析的文件列表"""
        all_files = self._discover_python_files(project_root)
        changed_files = self.cache_manager.get_changed_files(all_files)
        
        return {
            "total": all_files,
            "changed": list(changed_files),
            "unchanged": [f for f in all_files if f not in changed_files],
            "cached_results": {
                f: self.cache_manager.get_cached_result(f)
                for f in all_files if f not in changed_files
            }
        }
    
    def _discover_python_files(self, root: str) -> List[str]:
        """发现所有Python文件"""
        python_files = []
        root_path = Path(root)
        
        for pattern in self.config.include_patterns:
            for file_path in root_path.rglob(pattern):
                if not any(ignore in str(file_path) for ignore in self.config.ignore_patterns):
                    if file_path.is_file():
                        python_files.append(str(file_path))
        
        return sorted(set(python_files))
    
    def mark_file_analyzed(self, file_path: str, result: Dict[str, Any]):
        """标记文件已分析"""
        self.cache_manager.save_analysis_result(file_path, result)
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """获取分析摘要"""
        total = len(self.cache_manager.file_hashes)
        cached = len(self.cache_manager.analysis_results)
        
        return {
            "total_files": total,
            "cached_results": cached,
            "last_analysis": self.last_analysis_time.isoformat() if self.last_analysis_time else None,
            "cache_size": len(json.dumps(self.cache_manager.analysis_results)),
        }


class ConfigurationManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or ".fullpathtest.json"
        self.config: Optional[ProjectConfiguration] = None
    
    def load_config(self, project_root: str = ".") -> ProjectConfiguration:
        """加载项目配置"""
        config_path = os.path.join(project_root, self.config_file)
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.config = ProjectConfiguration(**data)
                logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                self.config = ProjectConfiguration()
        else:
            self.config = ProjectConfiguration()
            logger.info("Using default configuration")
        
        return self.config
    
    def save_config(self, project_root: str = "."):
        """保存项目配置"""
        if self.config is None:
            self.config = ProjectConfiguration()
        
        config_path = os.path.join(project_root, self.config_file)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.config), f, indent=2, ensure_ascii=False)
            logger.info(f"Saved configuration to {config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def create_default_config(self, project_root: str = "."):
        """创建默认配置文件"""
        self.config = ProjectConfiguration()
        self.config.project_name = os.path.basename(os.path.abspath(project_root))
        self.config.project_root = project_root
        self.save_config(project_root)
        logger.info(f"Created default configuration in {project_root}")


def demo_incremental_analysis():
    """增量分析演示"""
    print("=" * 80)
    print("Incremental Analysis System - Demo")
    print("=" * 80)
    
    # 创建配置管理器
    config_manager = ConfigurationManager()
    config = config_manager.load_config()
    
    print(f"\nCurrent Configuration:")
    print(f"  Project: {config.project_name}")
    print(f"  Tools: {config.analysis_tools}")
    print(f"  Max workers: {config.max_workers}")
    
    # 创建增量分析器
    analyzer = IncrementalAnalyzer(config)
    
    # 发现文件
    project_path = "full_path_test"
    file_info = analyzer.get_files_to_analyze(project_path)
    
    print(f"\nFile Discovery:")
    print(f"  Total files: {len(file_info['total'])}")
    print(f"  Changed files: {len(file_info['changed'])}")
    print(f"  Unchanged files: {len(file_info['unchanged'])}")
    
    # 摘要
    summary = analyzer.get_analysis_summary()
    print(f"\nAnalysis Summary:")
    print(f"  Total cached: {summary['total_files']}")
    print(f"  Cached results: {summary['cached_results']}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    demo_incremental_analysis()
