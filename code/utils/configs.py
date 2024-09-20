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

