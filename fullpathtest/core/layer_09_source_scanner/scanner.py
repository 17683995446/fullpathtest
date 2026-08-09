"""
第9层：源码接入扫描层

统一接入代码来源，支持本地目录、Git仓库、压缩包等。
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
from fullpathtest.types.core import TaskContext, FileMetadata, LanguageType, SourceType
import hashlib
import os
from datetime import datetime
import tarfile
import zipfile


class SourceScanner:
    """源码扫描器"""
    
    LANGUAGE_EXTENSIONS = {
        '.py': LanguageType.PYTHON,
        '.java': LanguageType.JAVA,
        '.go': LanguageType.GOLANG,
        '.rs': LanguageType.RUST,
        '.ts': LanguageType.TYPESCRIPT,
        '.tsx': LanguageType.TYPESCRIPT,
        '.js': LanguageType.JAVASCRIPT,
        '.jsx': LanguageType.JAVASCRIPT,
        '.cs': LanguageType.CSHARP,
        '.cpp': LanguageType.CPP,
        '.cc': LanguageType.CPP,
        '.c': LanguageType.C,
        '.h': LanguageType.C,
        '.hpp': LanguageType.CPP,
    }
    
    EXCLUDE_PATTERNS = {
        '__pycache__', '.git', '.svn', 'node_modules', 'venv', '.venv',
        'env', '.env', 'dist', 'build', 'target', 'bin', 'obj',
        '.idea', '.vscode', '.vs', '*.pyc', '*.class', '*.o',
        'coverage', '.coverage', '.pytest_cache', '.mypy_cache'
    }
    
    def __init__(self):
        self.scanned_files: List[FileMetadata] = []
    
    def scan(self, context: TaskContext) -> List[FileMetadata]:
        """扫描代码源"""
        source_type = context.request.source_type
        source_path = context.request.source_path
        
        if source_type == SourceType.LOCAL_DIRECTORY:
            return self._scan_directory(source_path, context)
        elif source_type == SourceType.GIT_REPOSITORY:
            return self._scan_git_repo(source_path, context)
        elif source_type == SourceType.ARCHIVE_FILE:
            return self._scan_archive(source_path, context)
        else:
            return []
    
    def _scan_directory(self, directory: str, context: TaskContext) -> List[FileMetadata]:
        """扫描本地目录 - 第一性原理：假设所有输入都是有害的"""
        self.scanned_files = []
        
        # 第一性原理：边界条件检查（0, 1, -1, 空, 极限）
        if not directory or not directory.strip():
            raise ValueError("路径不能为空")
        
        # 检查字符串中的特殊字符（在strip之前）
        # 检查所有可能的控制字符
        for char_code in range(32):
            char = chr(char_code)
            if char in directory and char not in ['\t', ' ']:
                raise ValueError(f"路径包含非法控制字符: 0x{char_code:02x}")
        
        directory = directory.strip()
        
        if len(directory) > 10000:
            raise ValueError(f"路径过长: {len(directory)} 字符（最大10000）")
        
        # 再次检查特殊字符（在strip之后）
        dangerous_chars = ['\x00', '\n', '\r', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07', '\x08', '\x0b', '\x0c', '\x0e', '\x0f']
        for char in dangerous_chars:
            if char in directory:
                raise ValueError(f"路径包含非法字符: {repr(char)}")
        
        try:
            dir_path = Path(directory)
        except Exception as e:
            raise ValueError(f"无效的路径格式: {e}")
        
        # 检查路径是否存在
        try:
            if not dir_path.exists():
                raise ValueError(f"目录不存在: {directory}")
        except Exception as e:
            raise ValueError(f"检查路径失败: {e}")
        
        if dir_path.is_file():
            return [self._scan_file(dir_path, context)]
        
        for root, dirs, files in os.walk(dir_path):
            dirs[:] = [d for d in dirs if not self._should_exclude(d)]
            
            for file in files:
                if self._should_exclude(file):
                    continue
                
                file_path = Path(root) / file
                if self._is_source_file(file_path):
                    try:
                        metadata = self._scan_file(file_path, context)
                        self.scanned_files.append(metadata)
                    except Exception:
                        pass
        
        return self.scanned_files
    
    def _scan_file(self, file_path: Path, context: TaskContext) -> FileMetadata:
        """扫描单个文件"""
        relative_path = str(file_path)
        
        if context.request.source_path:
            base_path = Path(context.request.source_path)
            if file_path.is_relative_to(base_path):
                relative_path = str(file_path.relative_to(base_path))
        
        stat = file_path.stat()
        
        with open(file_path, 'rb') as f:
            content = f.read()
            file_hash = hashlib.sha256(content).hexdigest()[:16]
        
        try:
            content_str = content.decode('utf-8')
            line_count = len(content_str.splitlines())
        except Exception:
            line_count = 0
        
        language = self._detect_language(file_path)
        
        is_test = self._is_test_file(file_path)
        
        return FileMetadata(
            file_path=str(file_path),
            relative_path=relative_path,
            language=language,
            size=stat.st_size,
            line_count=line_count,
            last_modified=datetime.fromtimestamp(stat.st_mtime),
            file_hash=file_hash,
            is_test_file=is_test
        )
    
    def _scan_git_repo(self, repo_path: str, context: TaskContext) -> List[FileMetadata]:
        """扫描Git仓库"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'ls-files'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return self._scan_directory(repo_path, context)
            
            files = result.stdout.strip().split('\n')
            self.scanned_files = []
            
            for file in files:
                if not file or self._should_exclude(file):
                    continue
                
                file_path = Path(repo_path) / file
                if file_path.is_file() and self._is_source_file(file_path):
                    try:
                        metadata = self._scan_file(file_path, context)
                        self.scanned_files.append(metadata)
                    except Exception:
                        pass
            
            return self.scanned_files
            
        except Exception:
            return self._scan_directory(repo_path, context)
    
    def _scan_archive(self, archive_path: str, context: TaskContext) -> List[FileMetadata]:
        """扫描压缩包"""
        self.scanned_files = []
        path = Path(archive_path)
        
        if not path.exists():
            raise ValueError(f"文件不存在: {archive_path}")
        
        extract_dir = Path('.fullpathtest/temp') / path.stem
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            if path.suffix in ['.zip']:
                with zipfile.ZipFile(path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            elif path.suffix in ['.tar', '.tar.gz', '.tgz', '.tar.bz2']:
                with tarfile.open(path, 'r:*') as tar_ref:
                    tar_ref.extractall(extract_dir)
            else:
                raise ValueError(f"不支持的压缩格式: {path.suffix}")
            
            self.scanned_files = self._scan_directory(str(extract_dir), context)
            
        except Exception as e:
            raise ValueError(f"解压失败: {e}")
        
        return self.scanned_files
    
    def _is_source_file(self, file_path: Path) -> bool:
        """判断是否为源码文件"""
        return file_path.suffix in self.LANGUAGE_EXTENSIONS
    
    def _detect_language(self, file_path: Path) -> LanguageType:
        """检测编程语言"""
        return self.LANGUAGE_EXTENSIONS.get(file_path.suffix, LanguageType.UNKNOWN)
    
    def _is_test_file(self, file_path: Path) -> bool:
        """判断是否为测试文件"""
        test_patterns = ['test_', '_test.', 'tests/', 'test/', '.test.']
        path_str = str(file_path).lower()
        return any(pattern in path_str for pattern in test_patterns)
    
    def _should_exclude(self, name: str) -> bool:
        """判断是否应该排除"""
        for pattern in self.EXCLUDE_PATTERNS:
            if pattern.startswith('*'):
                if name.endswith(pattern[1:]):
                    return True
            elif pattern in name:
                return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取扫描统计"""
        stats = {
            'total_files': len(self.scanned_files),
            'total_lines': sum(f.line_count for f in self.scanned_files),
            'total_size': sum(f.size for f in self.scanned_files),
            'by_language': {},
            'test_files': 0
        }
        
        for file_meta in self.scanned_files:
            lang = file_meta.language.name
            if lang not in stats['by_language']:
                stats['by_language'][lang] = {'count': 0, 'lines': 0}
            stats['by_language'][lang]['count'] += 1
            stats['by_language'][lang]['lines'] += file_meta.line_count
            
            if file_meta.is_test_file:
                stats['test_files'] += 1
        
        return stats
