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
    """
    Configuration class for Large Language Model (LLM) providers.
    Attributes:
        provider (str): The name of the LLM provider (e.g., 'huggingface-openai', 'gemini', 'nvidia').
        model (str): The specific model to use from the provider.
        base_url (Optional[str]): The base URL for the API endpoint, if applicable.
        params (dict): Additional parameters for the LLM configuration.
        api_key (str): The API key for accessing the LLM provider's services.
    Methods:
        __init__(provider: str, model: str, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs):
            Initializes the LLMConfig instance with the given provider, model, and optional parameters.
        _get_api_key(provided_key: Optional[str]) -> str:
            Retrieves the API key for the specified provider. If a key is provided, it is used directly.
            Otherwise, the method attempts to fetch the key from environment variables based on the provider.
            Raises a ValueError if the API key is not set.
    """
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
    """
    BaseLLM is an abstract base class for language model clients.

    Attributes:
        config (LLMConfig): Configuration object for the language model.
        client: The client instance created by the `_create_client` method.

    Methods:
        _create_client():
            Abstract method to create and return a client instance.
        
        get_response(prompt: str) -> Any:
            Abstract method to get a response from the language model synchronously.
        
        get_aresponse(prompt: str) -> Any:
            Abstract method to get a response from the language model asynchronously.
        
        get_model_info() -> Dict[str, Any]:
            Returns a dictionary containing information about the model, including the provider, model name, and parameters.
    """
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
    """
    A class to interact with NVIDIA's language model API.
    Attributes:
        provider (str): The provider name, set to "NVIDIA".
        config (object): Configuration object containing API key, model, and other parameters.
        sync_client (OpenAI): Synchronous client for making API requests.
        async_client (AsyncOpenAI): Asynchronous client for making API requests.
    Methods:
        __init__(config):
            Initializes the NVIDIALLM instance with the given configuration.
        _create_client():
            Creates both synchronous and asynchronous clients for interacting with the NVIDIA API.
        get_response(prompt: str) -> str:
            Sends a prompt to the NVIDIA API and returns the response as a string.
        async get_aresponse(prompt: str):
            Sends a prompt to the NVIDIA API and yields the response asynchronously.
    """
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
    """
    GeminiLLM is a class that interfaces with the Google Generative AI model.
    Attributes:
        provider (str): The provider of the LLM, set to "Google".
        config (object): Configuration object containing API key, model name, and other parameters.
        client (object): The client instance for interacting with the generative model.
    Methods:
        __init__(config):
            Initializes the GeminiLLM instance with the provided configuration.
        _create_client():
            Configures and creates the generative model client.
        _prepare_content(prompt: Union[str, List[Union[str, Image.Image]]]) -> Union[str, List[Union[str, Image.Image]]]:
            Prepares the content to be sent to the generative model based on the type of the prompt.
        get_response(prompt: Union[str, List[Union[str, Image.Image]]]) -> str:
            Generates a response from the generative model based on the provided prompt.
        async get_aresponse(prompt: Union[str, List[Union[str, Image.Image]]]):
            Asynchronously generates a response from the generative model based on the provided prompt, yielding chunks of text.
    """
    def __init__(self, config):
        self.provider = "Google"
        self.config = config
        self.client = self._create_client()  
        
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
    """
    A class to interact with HuggingFace's OpenAI API for language model completions.
    Attributes:
        provider (str): The provider name, set to "HuggingFace".
        config (object): Configuration object containing model and API key information.
        sync_client (OpenAI): Synchronous client for API interactions.
        async_client (AsyncOpenAI): Asynchronous client for API interactions.
    Methods:
        __init__(config):
            Initializes the HFOpenAIAPILLM instance with the given configuration.
        _create_client():
            Creates synchronous and asynchronous clients for API interactions.
        get_response(prompt: str) -> str:
            Gets a response from the language model for the given prompt using the synchronous client.
        async get_aresponse(prompt: str):
            Asynchronously gets a response from the language model for the given prompt using the asynchronous client.
    """
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
    """
    Factory class for creating instances of different LLM (Large Language Model) providers.

    Methods
    -------
    create_llm(config: LLMConfig) -> BaseLLM
        Creates an instance of a specified LLM provider based on the given configuration.

    Raises
    ------
    ValueError
        If the specified provider in the configuration is not supported.
    """
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
    """
    Process a batch of prompts and return their responses.

    Args:
        llm (BaseLLM): An instance of a language model that has a `get_response` method.
        prompts (List[str]): A list of prompt strings to be processed by the language model.

    Returns:
        List[str]: A list of responses generated by the language model for each prompt.
    """
    return [llm.get_response(prompt) for prompt in prompts]

async def batch_process_async(llm: BaseLLM, prompts: List[str]) -> List[str]:
    """
    Asynchronously processes a batch of prompts using a language model.
    Args:
        llm (BaseLLM): An instance of a language model that provides an asynchronous method `get_aresponse`.
        prompts (List[str]): A list of prompt strings to be processed by the language model.
    Returns:
        List[str]: A list of responses from the language model corresponding to each prompt.
    """
    async def process_prompt(prompt):
        result = ""
        async for chunk in llm.get_aresponse(prompt):
            result += chunk
        return result
    
    return await asyncio.gather(*[process_prompt(prompt) for prompt in prompts])

def compare_responses(llms: List[BaseLLM], prompt: str) -> Dict[str, str]:
    """
    Compares responses from multiple language models (LLMs) to a given prompt.

    Args:
        llms (List[BaseLLM]): A list of language model instances that implement the BaseLLM interface.
        prompt (str): The input prompt to which the LLMs will generate responses.

    Returns:
        Dict[str, str]: A dictionary where the keys are the model names and the values are the responses from the respective models.
    """
    return {llm.get_model_info()['model']: llm.get_response(prompt) for llm in llms}

async def stream_to_file(llm: BaseLLM, prompt: str, filename: str):
    """
    Asynchronously streams the response from a language model to a file.

    Args:
        llm (BaseLLM): An instance of a language model that provides an asynchronous response method.
        prompt (str): The input prompt to send to the language model.
        filename (str): The name of the file where the response will be written.

    Returns:
        None
    """
    with open(filename, 'w') as f:
        async for chunk in llm.get_aresponse(prompt):
            f.write(chunk)
            f.flush()
            
def validate_api_key(provider: str, api_key: str) -> bool:
    """
    Validates the provided API key for the specified provider.
    Args:
        provider (str): The name of the API provider. Supported providers are "huggingface-openai", "nvidia", and "gemini".
        api_key (str): The API key to be validated.
    Returns:
        bool: True if the API key is valid, False otherwise.
    Raises:
        ValueError: If the provider is not supported.
    Notes:
        - For "huggingface-openai", the function sends a GET request to the Hugging Face API to check the validity of the API key.
        - For "nvidia", the function uses the OpenAI client to list available models and checks if the list is non-empty.
        - For "gemini", the function configures the genai client with the API key and lists available models to check if the list is non-empty.
        - If any exception occurs during the validation process, the function prints an error message and returns False.
    """
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
    """
    Retrieve a language model instance based on the specified provider and model.
    Args:
        provider (str): The name of the language model provider (e.g., 'OpenAI', 'Google').
        model (str): The specific model to use (e.g., 'gpt-3', 'bert').
        api_key (Optional[str]): The API key for authenticating with the provider. Default is None.
        **kwargs: Additional keyword arguments to configure the language model.
    Returns:
        BaseLLM: An instance of the language model.
    Raises:
        ValueError: If the provided API key is invalid for the specified provider.
    """
    if not validate_api_key(provider, api_key):
        raise ValueError(f"Invalid API key for provider: {provider}")
    
    config = LLMConfig(provider, model, api_key=api_key, **kwargs)
    return LLMFactory.create_llm(config)