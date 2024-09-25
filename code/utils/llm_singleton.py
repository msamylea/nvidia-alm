from typing import Optional
from utils.llm_factory import BaseLLM

class LLMHolder:
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