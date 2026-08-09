"""
FullPathTest v4.0 - AI增强集成模块
提供完整的AI代码分析能力

这个模块包含：
1. 多Provider LLM集成（Ollama/OpenAI/Mock）
2. 智能代码分析
3. 自动问题修复建议
4. 代码质量评估
5. 性能问题诊断
"""

import os
import json
import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from datetime import datetime
import hashlib

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_integration")


class LLMProvider(Enum):
    """支持的LLM提供商"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MOCK = "mock"


class AnalysisType(Enum):
    """分析类型"""
    CODE_QUALITY = "code_quality"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"
    BUG_DETECTION = "bug_detection"
    REFACTORING = "refactoring"
    DOCUMENTATION = "documentation"


@dataclass
class LLMConfiguration:
    """LLM配置"""
    provider: LLMProvider = LLMProvider.MOCK
    model: str = "llama3.2:1b"
    api_base: str = "http://localhost:11434"
    api_key: str = ""
    temperature: float = 0.3
    max_tokens: int = 2048
    timeout: int = 60
    retry_count: int = 3
    retry_delay: float = 1.0
    cache_enabled: bool = True
    cache_dir: str = ".llm_cache"


@dataclass
class CodeAnalysisRequest:
    """代码分析请求"""
    code: str
    file_path: str = ""
    language: str = "python"
    analysis_types: List[AnalysisType] = field(default_factory=lambda: [AnalysisType.CODE_QUALITY])
    context: Dict[str, Any] = field(default_factory=dict)
    user_instruction: Optional[str] = None


@dataclass
class CodeAnalysisResponse:
    """代码分析响应"""
    success: bool
    analysis_type: AnalysisType
    summary: str = ""
    issues: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    score: float = 0.0
    model_used: str = ""
    tokens_used: int = 0
    processing_time: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FixSuggestion:
    """修复建议"""
    issue_description: str
    original_code: str
    suggested_fix: str
    explanation: str
    confidence: float = 0.0
    file_path: str = ""
    line_number: int = 0


class CacheManager:
    """LLM响应缓存管理器"""
    
    def __init__(self, cache_dir: str = ".llm_cache"):
        self.cache_dir = cache_dir
        self.memory_cache: Dict[str, Any] = {}
        os.makedirs(cache_dir, exist_ok=True)
    
    def _generate_cache_key(self, prompt: str, model: str) -> str:
        """生成缓存键"""
        content = f"{prompt}:{model}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, prompt: str, model: str) -> Optional[str]:
        """获取缓存的响应"""
        cache_key = self._generate_cache_key(prompt, model)
        
        # 先检查内存缓存
        if cache_key in self.memory_cache:
            logger.debug(f"Cache hit (memory): {cache_key[:8]}")
            return self.memory_cache[cache_key]
        
        # 检查磁盘缓存
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.memory_cache[cache_key] = data.get('response')
                    logger.debug(f"Cache hit (disk): {cache_key[:8]}")
                    return data.get('response')
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        
        return None
    
    def set(self, prompt: str, model: str, response: str):
        """设置缓存"""
        cache_key = self._generate_cache_key(prompt, model)
        
        # 保存到内存缓存
        self.memory_cache[cache_key] = response
        
        # 保存到磁盘缓存
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'prompt': prompt,
                    'response': response,
                    'model': model,
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def clear(self):
        """清除所有缓存"""
        self.memory_cache.clear()
        
        import shutil
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir, exist_ok=True)


class BaseLLMClient(ABC):
    """LLM客户端基类"""
    
    def __init__(self, config: LLMConfiguration):
        self.config = config
        self.cache = CacheManager(config.cache_dir) if config.cache_enabled else None
        self.request_count = 0
        self.total_tokens = 0
    
    @abstractmethod
    def _make_request(self, prompt: str, system: str) -> str:
        """发起LLM请求（子类实现）"""
        pass
    
    def generate(
        self, 
        prompt: str, 
        system: str = "You are a helpful AI assistant.",
        use_cache: bool = True
    ) -> str:
        """生成响应"""
        start_time = time.time()
        
        # 检查缓存
        if use_cache and self.cache:
            cached = self.cache.get(prompt, self.config.model)
            if cached:
                logger.info(f"Using cached response for prompt: {prompt[:50]}...")
                return cached
        
        # 发起请求（带重试）
        response = None
        for attempt in range(self.config.retry_count):
            try:
                response = self._make_request(prompt, system)
                break
            except Exception as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < self.config.retry_count - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
                else:
                    raise
        
        # 更新统计
        self.request_count += 1
        processing_time = time.time() - start_time
        
        # 保存到缓存
        if use_cache and self.cache and response:
            self.cache.set(prompt, self.config.model, response)
        
        logger.info(f"LLM request completed in {processing_time:.2f}s")
        return response
    
    def get_stats(self) -> Dict[str, Any]:
        """获取使用统计"""
        return {
            "request_count": self.request_count,
            "total_tokens": self.total_tokens,
            "model": self.config.model,
            "provider": self.config.provider.value
        }


class MockLLMClient(BaseLLMClient):
    """Mock LLM客户端（用于测试）"""
    
    def _make_request(self, prompt: str, system: str) -> str:
        """模拟LLM请求"""
        logger.info("Using Mock LLM Client")
        
        # 根据prompt类型返回不同的响应
        if "analyze" in prompt.lower() or "quality" in prompt.lower():
            return self._mock_code_quality_response(prompt)
        elif "security" in prompt.lower():
            return self._mock_security_response(prompt)
        elif "performance" in prompt.lower():
            return self._mock_performance_response(prompt)
        elif "fix" in prompt.lower() or "bug" in prompt.lower():
            return self._mock_fix_suggestion(prompt)
        else:
            return self._mock_general_response(prompt)
    
    def _mock_code_quality_response(self, prompt: str) -> str:
        """模拟代码质量分析响应"""
        return json.dumps({
            "summary": "代码质量分析完成。发现2个可优化点和1个潜在问题。",
            "issues": [
                {
                    "severity": "warning",
                    "type": "style",
                    "message": "函数名可以更描述性",
                    "line": 15,
                    "suggestion": "考虑使用更清晰的函数命名"
                },
                {
                    "severity": "info",
                    "type": "complexity",
                    "message": "函数复杂度较高",
                    "line": 25,
                    "suggestion": "考虑拆分为更小的函数"
                }
            ],
            "score": 85.5,
            "suggestions": [
                "添加类型注解以提高代码可读性",
                "考虑使用 dataclass 替代普通类",
                "添加文档字符串"
            ]
        }, ensure_ascii=False)
    
    def _mock_security_response(self, prompt: str) -> str:
        """模拟安全分析响应"""
        return json.dumps({
            "summary": "安全分析完成。未发现高危漏洞。",
            "issues": [
                {
                    "severity": "info",
                    "type": "security",
                    "message": "建议使用环境变量管理敏感配置",
                    "line": 10
                }
            ],
            "score": 95.0,
            "suggestions": [
                "实施输入验证",
                "使用参数化查询防止SQL注入",
                "定期更新依赖包"
            ]
        }, ensure_ascii=False)
    
    def _mock_performance_response(self, prompt: str) -> str:
        """模拟性能分析响应"""
        return json.dumps({
            "summary": "性能分析完成。发现1个潜在性能问题。",
            "issues": [
                {
                    "severity": "warning",
                    "type": "performance",
                    "message": "循环中重复创建对象",
                    "line": 30,
                    "suggestion": "考虑在循环外创建对象"
                }
            ],
            "score": 88.0,
            "suggestions": [
                "使用列表推导式替代普通循环",
                "考虑使用生成器处理大数据集",
                "添加适当的缓存机制"
            ]
        }, ensure_ascii=False)
    
    def _mock_fix_suggestion(self, prompt: str) -> str:
        """模拟修复建议响应"""
        return json.dumps({
            "issue": "代码中存在潜在的空指针引用",
            "original": "def process(data):\n    return data['key'].split()",
            "fix": "def process(data):\n    if data and 'key' in data:\n        return data['key'].split()\n    return []",
            "explanation": "添加了空值检查以防止KeyError"
        }, ensure_ascii=False)
    
    def _mock_general_response(self, prompt: str) -> str:
        """模拟通用响应"""
        return json.dumps({
            "response": f"这是一个基于您提供的代码的分析结果。代码片段长度：{len(prompt)}字符。",
            "recommendations": ["代码看起来基本合理", "建议添加更多注释"]
        }, ensure_ascii=False)


class OllamaLLMClient(BaseLLMClient):
    """Ollama本地LLM客户端"""
    
    def __init__(self, config: LLMConfiguration):
        super().__init__(config)
        self.config.provider = LLMProvider.OLLAMA
    
    def _make_request(self, prompt: str, system: str) -> str:
        """发起Ollama请求"""
        logger.info(f"Calling Ollama API: {self.config.api_base}")
        
        try:
            import urllib.request
            import urllib.error
            
            url = f"{self.config.api_base}/api/generate"
            
            payload = {
                "model": self.config.model,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens
                }
            }
            
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                url,
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('response', '')
                
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            raise


class OpenAILLMClient(BaseLLMClient):
    """OpenAI API客户端"""
    
    def __init__(self, config: LLMConfiguration):
        super().__init__(config)
        self.config.provider = LLMProvider.OPENAI
    
    def _make_request(self, prompt: str, system: str) -> str:
        """发起OpenAI请求"""
        logger.info(f"Calling OpenAI API: {self.config.model}")
        
        # 检查是否有openai库
        try:
            import openai
        except ImportError:
            logger.warning("OpenAI library not installed, falling back to mock")
            mock = MockLLMClient(self.config)
            return mock._make_request(prompt, system)
        
        try:
            openai.api_key = self.config.api_key
            if self.config.api_base:
                openai.api_base = self.config.api_base
            
            response = openai.ChatCompletion.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            self.total_tokens += response.usage.total_tokens
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise


class AICodeAnalyzer:
    """AI代码分析器"""
    
    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client
    
    def analyze_code(self, request: CodeAnalysisRequest) -> CodeAnalysisResponse:
        """分析代码"""
        start_time = time.time()
        
        # 构建分析提示词
        prompts = self._build_analysis_prompts(request)
        
        # 执行分析
        try:
            response = self.llm_client.generate(
                prompts['main'],
                prompts['system']
            )
            
            # 解析响应
            result = self._parse_analysis_response(response, request.analysis_types[0])
            result.processing_time = time.time() - start_time
            result.model_used = self.llm_client.config.model
            result.success = True
            
            return result
            
        except Exception as e:
            logger.error(f"Code analysis failed: {e}")
            return CodeAnalysisResponse(
                success=False,
                analysis_type=request.analysis_types[0],
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    def _build_analysis_prompts(self, request: CodeAnalysisRequest) -> Dict[str, str]:
        """构建分析提示词"""
        analysis_type = request.analysis_types[0]
        
        system_prompt = {
            AnalysisType.CODE_QUALITY: "You are an expert Python code reviewer. Analyze code quality and provide structured JSON output.",
            AnalysisType.SECURITY: "You are a security expert. Analyze code for security vulnerabilities and provide structured JSON output.",
            AnalysisType.PERFORMANCE: "You are a performance optimization expert. Analyze code for performance issues and provide structured JSON output.",
            AnalysisType.BUG_DETECTION: "You are a bug detection expert. Find potential bugs and provide structured JSON output.",
            AnalysisType.REFACTORING: "You are a refactoring expert. Suggest improvements and provide structured JSON output.",
        }.get(analysis_type, "You are a helpful code analysis assistant.")
        
        main_prompt = f"""Analyze the following {request.language} code:

```{request.language}
{request.code}
```

File: {request.file_path or 'unknown'}

Provide a JSON response with:
- summary: Brief summary of findings
- issues: List of issues found (with severity, type, message, line)
- score: Quality score (0-100)
- suggestions: List of improvement suggestions

{request.user_instruction or ''}
"""
        
        return {
            'system': system_prompt,
            'main': main_prompt
        }
    
    def _parse_analysis_response(
        self, 
        response: str, 
        analysis_type: AnalysisType
    ) -> CodeAnalysisResponse:
        """解析分析响应"""
        try:
            # 尝试解析JSON
            data = json.loads(response)
            
            return CodeAnalysisResponse(
                success=True,
                analysis_type=analysis_type,
                summary=data.get('summary', ''),
                issues=data.get('issues', []),
                suggestions=data.get('suggestions', []),
                score=float(data.get('score', 0))
            )
        except json.JSONDecodeError:
            # 如果不是JSON，返回文本响应
            return CodeAnalysisResponse(
                success=True,
                analysis_type=analysis_type,
                summary=response,
                issues=[],
                suggestions=[]
            )
    
    def suggest_fixes(self, code: str, issue: str) -> FixSuggestion:
        """生成修复建议"""
        prompt = f"""分析以下代码问题并提供修复建议：

问题: {issue}

代码:
```
{code}
```

提供JSON响应：
{{
    "issue": "问题描述",
    "original": "原始代码",
    "fix": "修复后的代码",
    "explanation": "修复说明"
}}
"""
        
        try:
            response = self.llm_client.generate(prompt)
            data = json.loads(response)
            
            return FixSuggestion(
                issue_description=data.get('issue', issue),
                original_code=data.get('original', code),
                suggested_fix=data.get('fix', code),
                explanation=data.get('explanation', ''),
                confidence=0.9
            )
        except Exception as e:
            logger.error(f"Fix suggestion failed: {e}")
            return FixSuggestion(
                issue_description=issue,
                original_code=code,
                suggested_fix=code,
                explanation=f"Failed to generate suggestion: {e}",
                confidence=0.0
            )


def create_llm_client(config: Optional[LLMConfiguration] = None) -> BaseLLMClient:
    """创建LLM客户端工厂"""
    config = config or LLMConfiguration()
    
    if config.provider == LLMProvider.MOCK:
        return MockLLMClient(config)
    elif config.provider == LLMProvider.OLLAMA:
        return OllamaLLMClient(config)
    elif config.provider == LLMProvider.OPENAI:
        return OpenAILLMClient(config)
    else:
        return MockLLMClient(config)


def create_ai_analyzer(config: Optional[LLMConfiguration] = None) -> AICodeAnalyzer:
    """创建AI代码分析器"""
    client = create_llm_client(config)
    return AICodeAnalyzer(client)


# 示例使用
def demo_ai_analysis():
    """AI分析演示"""
    print("\n" + "="*60)
    print("FullPathTest v4.0 - AI增强分析演示")
    print("="*60 + "\n")
    
    # 创建Mock客户端（用于演示）
    config = LLMConfiguration(
        provider=LLMProvider.MOCK,
        model="mock-llm",
        cache_enabled=True
    )
    
    # 创建分析器
    analyzer = create_ai_analyzer(config)
    
    # 示例代码
    sample_code = '''
def calculate_sum(numbers):
    result = 0
    for n in numbers:
        result = result + n
    return result

def process_data(data):
    return data['key'].split(',')
'''
    
    # 创建分析请求
    request = CodeAnalysisRequest(
        code=sample_code,
        file_path="sample.py",
        language="python",
        analysis_types=[AnalysisType.CODE_QUALITY, AnalysisType.SECURITY]
    )
    
    # 执行分析
    print("🔍 开始AI代码分析...")
    response = analyzer.analyze_code(request)
    
    # 显示结果
    print(f"\n✅ 分析{'成功' if response.success else '失败'}")
    if response.success:
        print(f"\n📊 代码质量评分: {response.score}/100")
        print(f"\n📝 摘要:")
        print(f"   {response.summary}")
        
        if response.issues:
            print(f"\n🐛 发现问题 ({len(response.issues)}个):")
            for i, issue in enumerate(response.issues, 1):
                print(f"   {i}. [{issue.get('severity', 'info').upper()}] {issue.get('message', '')}")
        
        if response.suggestions:
            print(f"\n💡 改进建议:")
            for i, suggestion in enumerate(response.suggestions, 1):
                print(f"   {i}. {suggestion}")
        
        print(f"\n⏱️ 处理时间: {response.processing_time:.2f}秒")
        print(f"🤖 使用模型: {response.model_used}")
    
    # 获取统计
    stats = analyzer.llm_client.get_stats()
    print(f"\n📈 LLM统计:")
    print(f"   请求次数: {stats['request_count']}")
    print(f"   提供商: {stats['provider']}")
    print(f"   模型: {stats['model']}")
    
    print("\n" + "="*60)
    print("演示完成！")
    print("="*60 + "\n")


if __name__ == "__main__":
    demo_ai_analysis()
