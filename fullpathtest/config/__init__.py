#!/usr/bin/env python3
"""
FullPathTest Configuration System - V23
Config management with JSON/YAML support, environment variables, validation
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum


class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LLMMode(Enum):
    """LLM operation modes"""
    LOCAL_ONLY = "LOCAL_ONLY"
    CLOUD_ONLY = "CLOUD_ONLY"
    HYBRID = "HYBRID"


class SourceType(Enum):
    """Source code types"""
    LOCAL_DIRECTORY = "LOCAL_DIRECTORY"
    GIT_REPOSITORY = "GIT_REPOSITORY"
    FILE = "FILE"


@dataclass
class Config:
    """Main configuration class"""
    # Basic settings
    app_name: str = "FullPathTest"
    version: str = "23.0.0"
    
    # Logging
    log_level: LogLevel = LogLevel.INFO
    log_file: Optional[str] = None
    
    # Source scanner
    max_files: int = 5
    file_extensions: list = field(default_factory=lambda: [".py", ".js", ".ts", ".java", ".go", ".cpp"])
    exclude_dirs: list = field(default_factory=lambda: [".git", ".venv", "__pycache__", "node_modules"])
    
    # Path generation
    max_paths: int = 10
    path_depth: int = 3
    
    # Test execution
    test_timeout: int = 300
    max_concurrent_tests: int = 5
    
    # LLM settings
    llm_mode: LLMMode = LLMMode.LOCAL_ONLY
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None
    
    # Output settings
    output_dir: str = "./fullpathtest_output"
    html_report: bool = True
    json_report: bool = True
    
    # Cache settings
    cache_enabled: bool = True
    cache_dir: str = "./.fullpathtest_cache"
    cache_ttl: int = 3600
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        result = {}
        for k, v in asdict(self).items():
            if isinstance(v, Enum):
                result[k] = v.value
            else:
                result[k] = v
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create config from dictionary"""
        processed = {}
        for k, v in data.items():
            if k == "log_level":
                processed[k] = LogLevel(v)
            elif k == "llm_mode":
                processed[k] = LLMMode(v)
            elif k in cls.__dataclass_fields__:
                processed[k] = v
        return cls(**processed)


class ConfigManager:
    """Configuration manager with loading, saving, validation"""
    
    DEFAULT_CONFIG_PATH = "fullpathtest_config.json"
    DEFAULT_YAML_PATH = "fullpathtest_config.yaml"
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_path()
        self._config: Optional[Config] = None
        self._load_default()
    
    def _find_config_path(self) -> str:
        """Find the most appropriate config path"""
        if Path(self.DEFAULT_CONFIG_PATH).exists():
            return self.DEFAULT_CONFIG_PATH
        if Path(self.DEFAULT_YAML_PATH).exists():
            return self.DEFAULT_YAML_PATH
        return self.DEFAULT_CONFIG_PATH
    
    def _load_default(self) -> None:
        """Load default configuration"""
        self._config = Config()
        self._load_env_vars()
    
    def _load_env_vars(self) -> None:
        """Load configuration from environment variables"""
        if not self._config:
            return
        
        env_prefix = "FULLPATHTEST_"
        for key in dir(self._config):
            if key.startswith("_"):
                continue
            env_key = env_prefix + key.upper()
            if env_key in os.environ:
                value = os.environ[env_key]
                if key in ["max_files", "max_paths", "path_depth", "test_timeout", 
                           "max_concurrent_tests", "cache_ttl"]:
                    setattr(self._config, key, int(value))
                elif key in ["html_report", "json_report", "cache_enabled"]:
                    setattr(self._config, key, value.lower() in ["true", "1", "yes"])
                elif key == "log_level":
                    setattr(self._config, key, LogLevel(value))
                elif key == "llm_mode":
                    setattr(self._config, key, LLMMode(value))
                else:
                    setattr(self._config, key, value)
    
    def load(self, config_path: Optional[str] = None) -> Config:
        """Load configuration from file"""
        path = config_path or self.config_path
        if not Path(path).exists():
            self.log(f"Config file {path} not found, using defaults")
            return self._config
        
        self.config_path = path
        try:
            if path.endswith('.yaml') or path.endswith('.yml'):
                with open(path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            self._config = Config.from_dict(data)
            self.log(f"Loaded configuration from {path}")
            return self._config
        except Exception as e:
            self.log(f"Error loading config: {e}, using defaults", level="WARNING")
            return self._config
    
    def save(self, config_path: Optional[str] = None) -> None:
        """Save configuration to file"""
        path = config_path or self.config_path
        try:
            data = self._config.to_dict()
            if path.endswith('.yaml') or path.endswith('.yml'):
                with open(path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            else:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            self.log(f"Saved configuration to {path}")
        except Exception as e:
            self.log(f"Error saving config: {e}", level="ERROR")
            raise
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not self._config:
            return False
        
        valid = True
        
        if self._config.max_files < 1 or self._config.max_files > 1000:
            self.log(f"Invalid max_files: {self._config.max_files}, should be 1-1000", level="WARNING")
            valid = False
        
        if self._config.max_paths < 1 or self._config.max_paths > 1000:
            self.log(f"Invalid max_paths: {self._config.max_paths}, should be 1-1000", level="WARNING")
            valid = False
        
        if self._config.test_timeout < 1:
            self.log(f"Invalid test_timeout: {self._config.test_timeout}, should be > 0", level="WARNING")
            valid = False
        
        if self._config.max_concurrent_tests < 1 or self._config.max_concurrent_tests > 100:
            self.log(f"Invalid max_concurrent_tests: {self._config.max_concurrent_tests}, should be 1-100", level="WARNING")
            valid = False
        
        return valid
    
    def get(self) -> Config:
        """Get current configuration"""
        return self._config
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Simple logging"""
        timestamp = type(self).__name__
        print(f"[{timestamp}] [{level}] {message}")


# Global config instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> Config:
    """Get the global configuration"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.get()


def init_config(config_path: Optional[str] = None) -> ConfigManager:
    """Initialize and return the config manager"""
    global _config_manager
    _config_manager = ConfigManager(config_path)
    _config_manager.load()
    return _config_manager


def save_default_config(path: Optional[str] = None) -> None:
    """Save default configuration to file"""
    manager = init_config(path)
    manager.save()
    print(f"Default config saved to {manager.config_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="FullPathTest Configuration Manager")
    parser.add_argument("--init", action="store_true", help="Save default configuration")
    parser.add_argument("--path", type=str, help="Configuration file path")
    
    args = parser.parse_args()
    
    if args.init:
        save_default_config(args.path)
    else:
        config = get_config()
        print("Current configuration:")
        print(json.dumps(config.to_dict(), indent=2))
