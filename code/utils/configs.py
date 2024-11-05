from utils.llm_singleton import llm_holder


from .llm_singleton import llm_holder
from pathlib import Path

cache_dir = Path(__file__).resolve().parent / "cache"
cache_dir.mkdir(exist_ok=True)



def get_llm():
    """
    Retrieve the Language Learning Model (LLM) instance from the holder.

    Returns:
        The LLM instance if it is set.

    Raises:
        ValueError: If the LLM instance is not set.
    """
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

