import os
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List, Union
import requests
import google.generativeai as genai
from openai import AsyncOpenAI, OpenAI
from PIL import Image
import logging

class LLMConfig:
    def __init__(self, provider: str, model: str, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs):
        self.provider = provider.lower()
        self.model = model
        self.base_url = base_url
        self.params = kwargs
        self.api_key = self._get_api_key(api_key)

    def _get_api_key(self, provided_key: Optional[str]) -> str:
        logging.debug(f"Getting API key for provider: {self.provider}")
        
        if provided_key:
            logging.debug("Using provided API key.")
            return provided_key

        env_var_map = {
            "huggingface-openai": "HF_TOKEN",
            "gemini": "GENAI_API_KEY",
            "nvidia": "NVIDIA_API_KEY",
               }
        
        env_var = env_var_map.get(self.provider)
        logging.debug(f"Environment variable for provider {self.provider}: {env_var}")
        
        api_key = os.environ.get(env_var) if env_var else None
        logging.debug(f"API key from environment: {api_key}")
        
        if not api_key:
            raise ValueError(f"API key for {self.provider} is not set. Please set the appropriate environment variable or provide it directly.")
        
        return api_key

class BaseLLM(ABC):
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = self._create_client()

    @abstractmethod
    def _create_client(self):
        pass

    @abstractmethod
    def get_response(self, prompt: str) -> Any:
        pass

    @abstractmethod
    async def get_aresponse(self, prompt: str) -> Any:
        pass

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": self.config.provider,
            "model": self.config.model,
            "parameters": self.config.params
        }
 
class NVIDIALLM(BaseLLM):
    def __init__(self, config):
        self.provider = "NVIDIA"
        self.config = config
        self._create_client()
        
    def _create_client(self):
        base_url = "https://integrate.api.nvidia.com/v1"
        self.sync_client = OpenAI(base_url=base_url, api_key=self.config.api_key)
        self.async_client = AsyncOpenAI(base_url=base_url, api_key=self.config.api_key)

    def get_response(self, prompt: str) -> str:
        response = self.sync_client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            **self.config.params
        )
        return response.choices[0].message.content

    async def get_aresponse(self, prompt: str):
        stream = await self.async_client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            **self.config.params
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

class GeminiLLM(BaseLLM):
    def __init__(self, config):
        self.provider = "Google"
        self.config = config
        self._create_client()
        
    def _create_client(self):
        genai.configure(api_key=self.config.api_key)
        return genai.GenerativeModel(model_name=self.config.model)

    def _prepare_content(self, prompt: Union[str, List[Union[str, Image.Image]]]) -> Union[str, List[Union[str, Image.Image]]]:
        if isinstance(prompt, str):
            return prompt
        elif isinstance(prompt, list):
            return [item if isinstance(item, (str, Image.Image)) else str(item) for item in prompt]
        else:
            return str(prompt)

    def get_response(self, prompt: Union[str, List[Union[str, Image.Image]]]) -> str:
        generation_config = genai.GenerationConfig(**{k: v for k, v in self.config.params.items() if k in ['temperature', 'max_output_tokens', 'top_p', 'top_k']})
        content = self._prepare_content(prompt)
        response = self.client.generate_content(content, generation_config=generation_config)
        response.resolve()
        return response.text

    async def get_aresponse(self, prompt: Union[str, List[Union[str, Image.Image]]]):
        generation_config = genai.GenerationConfig(**{k: v for k, v in self.config.params.items() if k in ['temperature', 'max_output_tokens', 'top_p', 'top_k']})
        content = self._prepare_content(prompt)
        response = self.client.generate_content(content, generation_config=generation_config, stream=True)
        for chunk in response:
            yield chunk.text
            await asyncio.sleep(0.01)

class HFOpenAIAPILLM(BaseLLM):
    def __init__(self, config):
        self.provider = "HuggingFace"
        self.config = config
        self._create_client()
        
    def _create_client(self):
        base_url = f"https://api-inference.huggingface.co/models/{self.config.model}/v1/"
        self.sync_client = OpenAI(base_url=base_url, api_key=self.config.api_key)
        self.async_client = AsyncOpenAI(base_url=base_url, api_key=self.config.api_key)

    def get_response(self, prompt: str) -> str:
        try:
            response = self.sync_client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                **self.config.params
            )
            return response.choices[0].message.content
        except Exception as e:
            return str(e)

    async def get_aresponse(self, prompt: str):
        stream = await self.async_client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            **self.config.params
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content


class LLMFactory:
    @staticmethod
    def create_llm(config: LLMConfig) -> BaseLLM:
        llm_classes = {
            "gemini": GeminiLLM,
            "huggingface-openai": HFOpenAIAPILLM,
            "nvidia": NVIDIALLM        
        }
        if config.provider not in llm_classes:
            raise ValueError(f"Unsupported provider: {config.provider}")
        return llm_classes[config.provider](config)


def batch_process(llm: BaseLLM, prompts: List[str]) -> List[str]:
    """Process a batch of prompts and return their responses."""
    return [llm.get_response(prompt) for prompt in prompts]

async def batch_process_async(llm: BaseLLM, prompts: List[str]) -> List[str]:
    """Process a batch of prompts asynchronously and return their responses."""
    async def process_prompt(prompt):
        result = ""
        async for chunk in llm.get_aresponse(prompt):
            result += chunk
        return result
    
    return await asyncio.gather(*[process_prompt(prompt) for prompt in prompts])

def compare_responses(llms: List[BaseLLM], prompt: str) -> Dict[str, str]:
    """Compare responses from multiple LLMs for the same prompt."""
    return {llm.get_model_info()['model']: llm.get_response(prompt) for llm in llms}

async def stream_to_file(llm: BaseLLM, prompt: str, filename: str):
    """Stream the LLM response to a file."""
    with open(filename, 'w') as f:
        async for chunk in llm.get_aresponse(prompt):
            f.write(chunk)
            f.flush()
            
def validate_api_key(provider: str, api_key: str) -> bool:
    try:
        if provider == "huggingface-openai":
            response = requests.get(
                "https://huggingface.co/api/whoami-v2",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            return response.status_code == 200
        
        elif provider == "nvidia":
            client = OpenAI(api_key=api_key, base_url="https://integrate.api.nvidia.com/v1")
            models = client.models.list()
            return len(models.data) > 0
        
        elif provider == "gemini":
            genai.configure(api_key=api_key)
            models = genai.list_models()
            return len(list(models)) > 0
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    except Exception as e:
        print(f"API key validation failed: {str(e)}")
        return False

def get_llm(provider: str, model: str, api_key: Optional[str] = None, **kwargs) -> BaseLLM:
    if not validate_api_key(provider, api_key):
        raise ValueError(f"Invalid API key for provider: {provider}")
    
    config = LLMConfig(provider, model, api_key=api_key, **kwargs)
    return LLMFactory.create_llm(config)