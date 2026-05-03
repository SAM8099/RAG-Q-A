from langchain_groq import ChatGroq
from src.modules.config import GROQ_API_KEY, LLM_MODEL
from src.utils.singleton import Singleton


class LLMService(metaclass=Singleton):

    def __init__(self) -> None:
        self._llm = ChatGroq(
            temperature=0.3,
            model_name=LLM_MODEL,
            api_key=GROQ_API_KEY,
        )

    def get_llm(self) -> ChatGroq:
        return self._llm