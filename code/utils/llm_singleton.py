from typing import Optional
from utils.llm_factory import BaseLLM

class LLMHolder:
    """
    LLMHolder is a singleton class that holds a single instance of a language model (LLM).

    Attributes:
        _instance (LLMHolder): The singleton instance of the LLMHolder class.
        _llm (Optional[BaseLLM]): The language model instance held by the singleton.

    Methods:
        __new__(cls): Creates a new instance of the LLMHolder class if one does not already exist.
        llm (property): Gets the current language model instance.
        llm (setter): Sets a new language model instance.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMHolder, cls).__new__(cls)
            cls._instance._llm = None
        return cls._instance

    @property
    def llm(self) -> Optional[BaseLLM]:
        return self._llm

    @llm.setter
    def llm(self, new_llm: BaseLLM):
        self._llm = new_llm

llm_holder = LLMHolder()