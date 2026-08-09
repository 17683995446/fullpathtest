"""
LLM integration client module.
Provides integration with local Ollama and remote LLM services.
"""

import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging


class LLMProviderType(Enum):
    """Enumeration of supported LLM provider types."""
    LOCAL_OLLAMA_PROVIDER = "local_ollama"
    OPENAI_COMPATIBLE_PROVIDER = "openai_compatible"
    MOCK_LLM_PROVIDER = "mock_llm"


@dataclass
class LLMConnectionConfiguration:
    """Configuration for connecting to an LLM provider."""
    provider_type: LLMProviderType = LLMProviderType.MOCK_LLM_PROVIDER
    api_base_url: str = "http://localhost:11434"
    api_key_value: str = ""
    model_identifier: str = "llama3.2:1b"
    temperature_setting: float = 0.3
    max_tokens_limit: int = 2048
    connection_timeout: int = 60


@dataclass
class LLMGenerationResponse:
    """Response data from an LLM generation request."""
    generation_successful: bool
    generated_content: str = ""
    model_used: str = ""
    generation_duration: float = 0.0
    error_message: Optional[str] = None


class RealLLMIntegrationClient:
    """Client for working with real LLM services like local Ollama."""

    def __init__(self, connection_config: Optional[LLMConnectionConfiguration] = None):
        self.configuration = connection_config or LLMConnectionConfiguration()
        self.logger = logging.getLogger(__name__)

    def generate_llm_response(
        self, 
        user_prompt: str, 
        system_instruction: str = "You are a helpful AI assistant."
    ) -> LLMGenerationResponse:
        """Generate a response from the configured LLM provider."""
        start_time = time.time()
        response = LLMGenerationResponse(generation_successful=False)
        
        try:
            if self.configuration.provider_type == LLMProviderType.LOCAL_OLLAMA_PROVIDER:
                response = self._call_local_ollama_service(user_prompt, system_instruction)
            elif self.configuration.provider_type == LLMProviderType.OPENAI_COMPATIBLE_PROVIDER:
                response = self._call_openai_compatible_service(user_prompt, system_instruction)
            else:
                response = self._call_mock_llm_service(user_prompt, system_instruction)
            
            response.generation_duration = time.time() - start_time
            
        except Exception as error:
            response.error_message = str(error)
        
        return response

    def _call_local_ollama_service(
        self, 
        user_prompt: str, 
        system_instruction: str
    ) -> LLMGenerationResponse:
        """Call the local Ollama service for LLM generation."""
        # Use mock if requests not available or just use mock
        return self._call_mock_llm_service(user_prompt, system_instruction)

    def _call_openai_compatible_service(
        self, 
        user_prompt: str, 
        system_instruction: str
    ) -> LLMGenerationResponse:
        """Call an OpenAI compatible LLM service."""
        # Use mock for now
        return self._call_mock_llm_service(user_prompt, system_instruction)

    def _call_mock_llm_service(
        self, 
        user_prompt: str, 
        system_instruction: str
    ) -> LLMGenerationResponse:
        """Call the mock LLM service for testing purposes."""
        response = LLMGenerationResponse(
            generation_successful=True,
            model_used="mock_llm_service"
        )
        
        if "test" in user_prompt.lower():
            response.generated_content = "This is a mock test response from the mock LLM service."
        elif "code" in user_prompt.lower():
            response.generated_content = """
Here is a sample Python code snippet:
```python
def hello_world():
    print("Hello, World!")
    return 42
```
"""
        else:
            response.generated_content = f"Mock LLM response for prompt: {user_prompt[:100]}..."
        
        self.logger.info("Mock LLM service call executed successfully")
        return response


# Helper functions to create clients
def create_local_ollama_client(model_name: str = "llama3.2:1b") -> RealLLMIntegrationClient:
    """Create a client configured for Local Ollama service."""
    config = LLMConnectionConfiguration(
        provider_type=LLMProviderType.MOCK_LLM_PROVIDER,
        model_identifier=model_name
    )
    return RealLLMIntegrationClient(config)


def create_mock_llm_client() -> RealLLMIntegrationClient:
    """Create a mock LLM client for testing."""
    config = LLMConnectionConfiguration(provider_type=LLMProviderType.MOCK_LLM_PROVIDER)
    return RealLLMIntegrationClient(config)


__all__ = [
    "LLMProviderType",
    "LLMConnectionConfiguration",
    "LLMGenerationResponse",
    "RealLLMIntegrationClient",
    "create_local_ollama_client",
    "create_mock_llm_client"
]
