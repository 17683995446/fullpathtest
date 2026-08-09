"""
第5层：LLM全局能力适配层

统一封装本地离线LLM引擎与云端LLM接口。
"""

from typing import Optional, Dict, Any
from fullpathtest.types.core import LLMRequest, LLMResponse, LLMMode, LLMConfig
import httpx
import asyncio


class LLMAdapter:
    """LLM适配器"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """生成LLM响应"""
        if self.config.mode == LLMMode.LOCAL_ONLY:
            return await self._call_local(request)
        elif self.config.mode == LLMMode.CLOUD_ONLY:
            return await self._call_cloud(request)
        else:
            try:
                return await self._call_local(request)
            except Exception:
                return await self._call_cloud(request)
    
    async def _call_local(self, request: LLMRequest) -> LLMResponse:
        """调用本地LLM"""
        if not self._client:
            self._client = httpx.AsyncClient(timeout=self.config.timeout)
        
        prompt = request.prompt
        if request.system_prompt:
            prompt = f"{request.system_prompt}\n\n{request.prompt}"
        
        payload = {
            "model": request.model or self.config.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": request.temperature or self.config.temperature,
                "num_predict": request.max_tokens or self.config.max_tokens
            }
        }
        
        try:
            response = await self._client.post(
                self.config.local_endpoint,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                content=data.get('response', ''),
                model=payload['model'],
                finish_reason='stop',
                usage={'prompt_tokens': 0, 'completion_tokens': 0}
            )
        except Exception as e:
            return LLMResponse(
                content='',
                model=payload['model'],
                finish_reason='error',
                error=str(e)
            )
    
    async def _call_cloud(self, request: LLMRequest) -> LLMResponse:
        """调用云端LLM"""
        if not self._client:
            self._client = httpx.AsyncClient(timeout=self.config.timeout)
        
        headers = {
            'Authorization': f'Bearer {self.config.cloud_endpoint}',
            'Content-Type': 'application/json'
        }
        
        messages = []
        if request.system_prompt:
            messages.append({'role': 'system', 'content': request.system_prompt})
        messages.append({'role': 'user', 'content': request.prompt})
        
        payload = {
            'model': request.model or self.config.model_name,
            'messages': messages,
            'temperature': request.temperature or self.config.temperature,
            'max_tokens': request.max_tokens or self.config.max_tokens
        }
        
        try:
            response = await self._client.post(
                self.config.cloud_endpoint,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            content = data['choices'][0]['message']['content']
            usage = data.get('usage', {})
            
            return LLMResponse(
                content=content,
                model=payload['model'],
                finish_reason=data['choices'][0].get('finish_reason', 'stop'),
                usage={
                    'prompt_tokens': usage.get('prompt_tokens', 0),
                    'completion_tokens': usage.get('completion_tokens', 0)
                }
            )
        except Exception as e:
            return LLMResponse(
                content='',
                model=payload['model'],
                finish_reason='error',
                error=str(e)
            )
    
    async def close(self):
        """关闭客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None


class LLMFactory:
    """LLM工厂"""
    
    @staticmethod
    def create_adapter(mode: LLMMode, config: Optional[LLMConfig] = None) -> LLMAdapter:
        """创建LLM适配器"""
        if config is None:
            config = LLMConfig(mode=mode)
        return LLMAdapter(config)
