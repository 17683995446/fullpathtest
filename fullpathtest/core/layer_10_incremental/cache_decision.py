"""
第10层：增量缓存决策层

基于文件哈希判断是否需要重新解析。
"""

from typing import List, Dict, Set, Tuple
from fullpathtest.types.core import TaskContext, FileMetadata
import hashlib
import json
from pathlib import Path


class IncrementalCacheDecision:
    """增量缓存决策器"""
    
    def __init__(self):
        self.cache_index: Dict[str, Dict] = {}
        self._load_cache_index()
    
    def _load_cache_index(self) -> None:
        """加载缓存索引"""
        index_path = Path('.fullpathtest/cache/index.json')
        if index_path.exists():
            try:
                with open(index_path, 'r') as f:
                    self.cache_index = json.load(f)
            except Exception:
                self.cache_index = {}
    
    def _save_cache_index(self) -> None:
        """保存缓存索引"""
        index_path = Path('.fullpathtest/cache/index.json')
        index_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(index_path, 'w') as f:
                json.dump(self.cache_index, f, indent=2)
        except Exception:
            pass
    
    def decide(
        self,
        context: TaskContext,
        files: List[FileMetadata]
    ) -> Tuple[List[FileMetadata], List[Dict]]:
        """决定哪些文件需要解析"""
        need_parse = []
        cache_hit = []
        
        for file_meta in files:
            cache_key = self._generate_cache_key(file_meta.file_path)
            cached = self.cache_index.get(cache_key)
            
            if cached and cached.get('hash') == file_meta.file_hash:
                cache_hit.append({
                    'file_path': file_meta.file_path,
                    'hash': file_meta.file_hash,
                    'cached_result': cached
                })
            else:
                need_parse.append(file_meta)
                self.cache_index[cache_key] = {
                    'hash': file_meta.file_hash,
                    'file_path': file_meta.file_path,
                    'line_count': file_meta.line_count,
                    'parsed_at': None
                }
        
        self._save_cache_index()
        
        return need_parse, cache_hit
    
    def _generate_cache_key(self, file_path: str) -> str:
        """生成缓存键"""
        return hashlib.sha256(file_path.encode()).hexdigest()[:16]
    
    def update_cache(self, file_path: str, result: Dict) -> None:
        """更新缓存"""
        cache_key = self._generate_cache_key(file_path)
        if cache_key in self.cache_index:
            self.cache_index[cache_key]['parsed_at'] = str(Path(file_path).stat().st_mtime)
            self.cache_index[cache_key]['result'] = result
            self._save_cache_index()
    
    def invalidate_file(self, file_path: str) -> None:
        """使文件缓存失效"""
        cache_key = self._generate_cache_key(file_path)
        if cache_key in self.cache_index:
            del self.cache_index[cache_key]
            self._save_cache_index()
    
    def clear_cache(self) -> None:
        """清空缓存"""
        self.cache_index = {}
        self._save_cache_index()


class ChangeDetector:
    """变更检测器"""
    
    def __init__(self):
        self.previous_hashes: Dict[str, str] = {}
    
    def detect_changes(
        self,
        current_files: List[FileMetadata]
    ) -> Set[str]:
        """检测变更的文件"""
        changed = set()
        
        for file_meta in current_files:
            prev_hash = self.previous_hashes.get(file_meta.file_path)
            
            if prev_hash is None or prev_hash != file_meta.file_hash:
                changed.add(file_meta.file_path)
                self.previous_hashes[file_meta.file_path] = file_meta.file_hash
        
        return changed
    
    def save_state(self, files: List[FileMetadata]) -> None:
        """保存状态"""
        state_path = Path('.fullpathtest/cache/state.json')
        state_path.parent.mkdir(parents=True, exist_ok=True)
        
        state = {f.file_path: f.file_hash for f in files}
        
        with open(state_path, 'w') as f:
            json.dump(state, f)
    
    def load_state(self) -> None:
        """加载状态"""
        state_path = Path('.fullpathtest/cache/state.json')
        if state_path.exists():
            try:
                with open(state_path, 'r') as f:
                    self.previous_hashes = json.load(f)
            except Exception:
                self.previous_hashes = {}
