
"""
FullPathTest v4.0 - 文件系统安全工具
处理文件系统边界情况，防止陷阱
"""

import os
import stat
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class FileSystemTrapHandler:
    """文件系统陷阱处理器"""
    
    def __init__(self, max_depth: int = 20, follow_symlinks: bool = False):
        self.max_depth = max_depth
        self.follow_symlinks = follow_symlinks
        self._visited_inodes = set()
    
    def is_safe_path(self, path: Path) -> bool:
        """检查路径是否安全"""
        try:
            # 检查是否为绝对路径
            if not path.is_absolute():
                return False
            
            # 解析真实路径（处理符号链接）
            try:
                real_path = path.resolve(strict=False)
            except (OSError, RuntimeError):
                return False
            
            # 检查深度
            parts = real_path.parts
            if len(parts) > self.max_depth:
                logger.warning(f"路径深度超过限制: {len(parts)} > {self.max_depth}")
                return False
            
            # 检查符号链接循环
            if not self.follow_symlinks:
                try:
                    stat_info = path.stat()
                    inode = (stat_info.st_dev, stat_info.st_ino)
                    
                    if inode in self._visited_inodes:
                        logger.warning(f"检测到符号链接循环")
                        return False
                    
                    self._visited_inodes.add(inode)
                except OSError:
                    return False
            
            # 检查权限
            try:
                if not os.access(path, os.R_OK):
                    logger.warning(f"路径不可读: {path}")
                    return False
            except OSError:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"路径安全检查失败: {e}")
            return False
    
    def safe_list_dir(self, dir_path: Path) -> List[Path]:
        """安全地列出目录内容"""
        safe_files = []
        
        if not dir_path.is_dir():
            return safe_files
        
        try:
            for item in dir_path.iterdir():
                # 检查每个项的安全性
                if self.is_safe_path(item):
                    safe_files.append(item)
                else:
                    logger.debug(f"跳过不安全的路径: {item}")
        except PermissionError:
            logger.warning(f"权限不足，无法列出目录: {dir_path}")
        except Exception as e:
            logger.error(f"列出目录时出错: {e}")
        
        return safe_files
    
    def safe_rglob(self, root: Path, pattern: str) -> List[Path]:
        """安全地递归搜索文件"""
        results = []
        self._visited_inodes.clear()
        
        def _safe_rglob_recursive(path: Path, depth: int = 0):
            if depth > self.max_depth:
                return
            
            if not path.is_dir():
                return
            
            # 列出目录
            for item in self.safe_list_dir(path):
                try:
                    if item.is_file() and item.match(pattern):
                        results.append(item)
                    elif item.is_dir() and self.follow_symlinks:
                        _safe_rglob_recursive(item, depth + 1)
                except Exception:
                    pass
        
        _safe_rglob_recursive(root)
        return results
    
    def check_special_names(self, filename: str) -> bool:
        """检查是否为特殊文件名"""
        dangerous_names = [
            "..",
            "",
            "/",
            "\\",
            "\x00",  # null byte
        ]
        
        if filename in dangerous_names:
            return False
        
        # 检查特殊字符
        dangerous_chars = ['\x00', '\n', '\r', '/', '\\']
        for char in dangerous_chars:
            if char in filename:
                return False
        
        return True
    
    def reset(self):
        """重置访问记录"""
        self._visited_inodes.clear()


def safe_file_operation(file_path: str, operation: str = 'read'):
    """安全的文件操作包装器
    
    Args:
        file_path: 文件路径
        operation: 操作类型 ('read', 'write')
    
    Returns:
        文件内容或None
    """
    path = Path(file_path)
    
    # 创建处理器
    handler = FileSystemTrapHandler(follow_symlinks=False)
    
    # 安全检查
    if not handler.check_special_names(path.name):
        logger.error(f"危险的文件名: {path.name}")
        return None
    
    if not handler.is_safe_path(path):
        logger.error(f"不安全的路径: {path}")
        return None
    
    # 执行操作
    try:
        if operation == 'read':
            return path.read_text(encoding='utf-8')
        elif operation == 'write':
            path.write_text('', encoding='utf-8')
            return True
    except Exception as e:
        logger.error(f"文件操作失败: {e}")
        return None
    
    return None


# 导出
__all__ = [
    'FileSystemTrapHandler',
    'safe_file_operation',
]
