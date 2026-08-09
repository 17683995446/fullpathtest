"""
真实LLM集成 - 支持本地Ollama和云端OpenAI

站在巨人的肩膀上！
"""

import requests
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging


class LLMProvider(Enum):
    """LLM提供商"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    MOCK = "mock"


@dataclass
class LLMConfig:
    """LLM配置"""
    provider: LLMProvider = LLMProvider.OLLAMA
    api_base: str = "http://localhost:11434"
    api_key: str = ""
    model: str = "llama3.2:1b"
    temperature: float = 0.3
    max_tokens: int = 2048
    timeout: int = 60


@dataclass
class LLMResponse:
    """LLM响应"""
    success: bool
    content: str = ""
    model: str = ""
    duration: float = 0.0
    error: Optional[str] = None


class RealLLMClient:
    """真实LLM客户端"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self.logger = logging.getLogger(__name__)
    
    def generate(self, prompt: str, system_prompt: str = "") -> LLMResponse:
        """生成文本"""
        start = time.time()
        result = LLMResponse(success=False)
        
        try:
            if self.config.provider == LLMProvider.OLLAMA:
                result = self._call_ollama(prompt, system_prompt)
            elif self.config.provider == LLMProvider.OPENAI:
                result = self._call_openai(prompt, system_prompt)
            else:
                result = self._call_mock(prompt, system_prompt)
            
            result.duration = time.time() - start
            
        except Exception as e:
            result.error = str(e)
        
        return result
    
    def _call_ollama(self, prompt: str, system_prompt: str) -> LLMResponse:
        """调用本地Ollama"""
        result = LLMResponse(success=False)
        result.model = self.config.model
        
        try:
            url = f"{self.config.api_base}/api/generate"
            
            payload = {
                "model": self.config.model,
                "prompt": prompt,
                "system": system_prompt if system_prompt else "You are a helpful AI assistant.",
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens
                }
            }
            
            response = requests.post(url, json=payload, timeout=self.config.timeout)
            
            if response.status_code == 200:
                data = response.json()
                result.content = data.get("response", "")
                result.success = True
                self.logger.info(f"Ollama call successful for model {self.config.model}")
            else:
                result.error = f"Ollama API error: {response.status_code} {response.text}"
        
        except requests.exceptions.ConnectionError:
            result.error = "Cannot connect to Ollama. Is Ollama running at " + self.config.api_base + " ?"
            self.logger.warning(result.error)
        
        except Exception as e:
            result.error = f"Ollama call failed: {e}"
        
        return result
    
    def _call_openai(self, prompt: str, system_prompt: str) -> LLMResponse:
        """调用OpenAI API"""
        result = LLMResponse(success=False)
        result.model = self.config.model
        
        try:
            url = f"{self.config.api_base}/chat/completions" if not self.config.api_base.endswith('/chat/completions') else self.config.api_base
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}"
            }
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.config.model,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=self.config.timeout)
            
            if response.status_code == 200:
                data = response.json()
                result.content = data["choices"][0]["message"]["content"]
                result.success = True
                self.logger.info("OpenAI call successful")
            else:
                result.error = f"OpenAI API error: {response.status_code} {response.text}"
        
        except Exception as e:
            result.error = f"OpenAI call failed: {e}"
        
        return result
    
    def _call_mock(self, prompt: str, system_prompt: str) -> LLMResponse:
        """Mock LLM响应（用于测试）"""
        result = LLMResponse(success=True)
        result.model = "mock-llm"
        
        if "test" in prompt.lower():
            result.content = "This is a mock test response."
        elif "code" in prompt.lower():
            result.content = """
            Here is some Python code:
            
            def hello_world():
                print("Hello, World!")
            
            return 42
            """
        else:
            result.content = f"Mock response to: {prompt[:100]}..."
        
        self.logger.info("Mock LLM call")
        return result


class TestDataGenerator:
    """测试数据生成器 - 使用真实LLM"""
    
    def __init__(self, llm_client: Optional[RealLLMClient] = None):
        self.llm_client = llm_client or RealLLMClient()
    
    def generate_test_data(self, function_code: str, function_name: str) -> Dict[str, Any]:
        """生成测试数据"""
        prompt = f"""
        Generate test data for this Python function:
        
        {function_code}
        
        Function name: {function_name}
        
        Please provide:
        1. Normal test cases
        2. Edge cases
        3. Error cases
        4. Input-output examples
        
        Return JSON format:
        {{
            "normal_cases": [...],
            "edge_cases": [...],
            "error_cases": [...]
        }}
        """
        
        system_prompt = "You are a senior software engineer specialized in writing high-quality test cases."
        
        response = self.llm_client.generate(prompt, system_prompt)
        
        result = {
            "success": response.success,
            "content": response.content
        }
        
        if response.success:
            try:
                json_start = response.content.find('{')
                json_end = response.content.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = response.content[json_start:json_end]
                    result.update(json.loads(json_str))
            except Exception as e:
                result["parse_error"] = str(e)
        
        return result


# 快捷函数
def get_ollama_client(model: str = "llama3.2:1b") -> RealLLMClient:
    """获取Ollama客户端"""
    config = LLMConfig(
        provider=LLMProvider.OLLAMA,
        model=model
    )
    return RealLLMClient(config)


def get_mock_client() -> RealLLMClient:
    """获取Mock客户端"""
    config = LLMConfig(provider=LLMProvider.MOCK)
    return RealLLMClient(config)
