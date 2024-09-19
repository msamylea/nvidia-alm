from utils.llm_singleton import llm_holder
from .llm_factory import get_llm


from .llm_singleton import llm_holder
from pathlib import Path

cache_dir = Path(__file__).resolve().parent / "cache"
cache_dir.mkdir(exist_ok=True)

llm = get_llm("huggingface-openai", "meta-llama/Meta-Llama-3.1-8B-Instruct", max_tokens=2048)

def get_llm():
    llm = llm_holder.llm
    if llm is None:
        raise ValueError("LLM is not set. Please configure the LLM before using it.")
    return llm

app_config = {
    'DEBUG': True,
    'HOST': '0.0.0.0',
    'PORT': 8050,
    'MAX_CACHE_FILES': 10,
    'CACHE_DIR': 'cache-directory'
}

LOGO_ICON = 'assets/logo.jpg'
MAX_CACHE_FILES = 10 

DATETIME_FORMATS = ['datetime64[s]', 'datetime64[ms]', 'datetime64[us]', 'datetime64[ns]']
CATEGORICAL_DTYPES = ['string', 'object']
NUMERIC_DTYPES = ['int8', 'int16', 'int32', 'int64', 'float16', 'float32', 'float64']

LLM_PROVIDERS = {
    "HuggingFace": "huggingface-openai",
    "NVIDIA": "nvidia",
    "Google Gemini": "gemini",
}

LLM_PROVIDER_OPTIONS = [{"label": key, "value": value} for key, value in LLM_PROVIDERS.items()]