"""
第6层：LLM全局缓存管理层

全系统LLM请求结果统一缓存，支持内存、磁盘、向量库三级缓存。
"""

from typing import Optional, Dict, Any, Tuple
from fullpathtest.types.core import LLMRequest, CacheEntry
import hashlib
import json
import time
from collections import OrderedDict
from pathlib import Path
import pickle
import shutil


class MemoryCache:
    """内存缓存"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key in self._cache:
            entry = self._cache[key]
            entry.accessed_at = time.time()
            entry.access_count += 1
            self._cache.move_to_end(key)
            self._hits += 1
            return entry.content
        self._misses += 1
        return None
    
    def set(self, key: str, content: Any) -> None:
        """设置缓存"""
        if key in self._cache:
            self._cache[key] = CacheEntry(
                cache_key=key,
                content=content,
                created_at=time.time(),
                accessed_at=time.time()
            )
        else:
            if len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)
            
            self._cache[key] = CacheEntry(
                cache_key=key,
                content=content,
                created_at=time.time(),
                accessed_at=time.time()
            )
        self._cache.move_to_end(key)
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        total = self._hits + self._misses
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': self._hits / total if total > 0 else 0.0
        }


class DiskCache:
    """磁盘缓存"""
    
    def __init__(self, cache_dir: str = ".fullpathtest/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._index_file = self.cache_dir / "index.pkl"
        self._load_index()
    
    def _load_index(self) -> None:
        """加载索引"""
        if self._index_file.exists():
            try:
                with open(self._index_file, 'rb') as f:
                    self._index: Dict[str, Dict[str, Any]] = pickle.load(f)
            except Exception:
                self._index = {}
        else:
            self._index = {}
    
    def _save_index(self) -> None:
        """保存索引"""
        try:
            with open(self._index_file, 'wb') as f:
                pickle.dump(self._index, f)
        except Exception:
            pass
    
    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        key_hash = hashlib.sha256(key.encode()).hexdigest()[:16]
        return self.cache_dir / f"{key_hash}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key not in self._index:
            return None
        
        cache_file = self._get_cache_path(key)
        if not cache_file.exists():
            del self._index[key]
            return None
        
        entry = self._index[key]
        if entry.get('ttl', 0) > 0 and time.time() > entry['created_at'] + entry['ttl']:
            self.delete(key)
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                content = pickle.load(f)
            entry['accessed_at'] = time.time()
            entry['access_count'] = entry.get('access_count', 0) + 1
            self._save_index()
            return content
        except Exception:
            return None
    
    def set(self, key: str, content: Any, ttl: int = 86400) -> None:
        """设置缓存"""
        cache_file = self._get_cache_path(key)
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(content, f)
            
            self._index[key] = {
                'file': str(cache_file),
                'created_at': time.time(),
                'accessed_at': time.time(),
                'access_count': 0,
                'ttl': ttl
            }
            self._save_index()
        except Exception:
            pass
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        if key in self._index:
            cache_file = self._get_cache_path(key)
            try:
                if cache_file.exists():
                    cache_file.unlink()
                del self._index[key]
                self._save_index()
                return True
            except Exception:
                return False
        return False
    
    def clear(self) -> None:
        """清空缓存"""
        try:
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._index = {}
            self._save_index()
        except Exception:
            pass
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        total_access = sum(e.get('access_count', 0) for e in self._index.values())
        return {
            'entry_count': len(self._index),
            'total_access': total_access,
            'cache_dir': str(self.cache_dir)
        }


class VectorCache:
    """向量缓存（简化实现）"""
    
    def __init__(self, db_path: str = ".fullpathtest/vectors"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        self._vectors: Dict[str, list] = {}
        self._load_vectors()
    
    def _load_vectors(self) -> None:
        """加载向量"""
        index_file = self.db_path / "vectors.pkl"
        if index_file.exists():
            try:
                with open(index_file, 'rb') as f:
                    self._vectors = pickle.load(f)
            except Exception:
                self._vectors = {}
    
    def _save_vectors(self) -> None:
        """保存向量"""
        index_file = self.db_path / "vectors.pkl"
        try:
            with open(index_file, 'wb') as f:
                pickle.dump(self._vectors, f)
        except Exception:
            pass
    
    def add_vector(self, key: str, vector: list) -> None:
        """添加向量"""
        self._vectors[key] = vector
        self._save_vectors()
    
    def search_similar(self, query_vector: list, top_k: int = 5) -> list:
        """搜索相似向量"""
        similarities = []
        for key, vector in self._vectors.items():
            similarity = self._cosine_similarity(query_vector, vector)
            similarities.append((key, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def _cosine_similarity(self, v1: list, v2: list) -> float:
        """计算余弦相似度"""
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm1 = sum(a * a for a in v1) ** 0.5
        norm2 = sum(b * b for b in v2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)


class LLMCacheManager:
    """LLM缓存管理器"""
    
    def __init__(
        self,
        memory_cache: Optional[MemoryCache] = None,
        disk_cache: Optional[DiskCache] = None,
        vector_cache: Optional[VectorCache] = None
    ):
        self.memory = memory_cache or MemoryCache()
        self.disk = disk_cache or DiskCache()
        self.vector = vector_cache or VectorCache()
    
    def generate_cache_key(self, request: LLMRequest) -> str:
        """生成缓存键"""
        key_data = {
            'prompt': request.prompt,
            'system': request.system_prompt,
            'model': request.model,
            'temperature': request.temperature,
            'max_tokens': request.max_tokens
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def get(self, request: LLMRequest) -> Tuple[Optional[Any], str]:
        """获取缓存结果"""
        cache_key = self.generate_cache_key(request)
        
        result = self.memory.get(cache_key)
        if result is not None:
            return result, 'memory'
        
        result = self.disk.get(cache_key)
        if result is not None:
            self.memory.set(cache_key, result)
            return result, 'disk'
        
        return None, 'miss'
    
    def set(self, request: LLMRequest, content: Any) -> None:
        """设置缓存"""
        cache_key = self.generate_cache_key(request)
        
        self.memory.set(cache_key, content)
        self.disk.set(cache_key, content)
    
    def invalidate(self, cache_key: str) -> None:
        """使缓存失效"""
        self.memory.delete(cache_key)
        self.disk.delete(cache_key)
    
    def clear_all(self) -> None:
        """清空所有缓存"""
        self.memory.clear()
        self.disk.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        return {
            'memory': self.memory.get_stats(),
            'disk': self.disk.get_stats()
        }
