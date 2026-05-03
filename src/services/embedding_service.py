from langchain_huggingface import HuggingFaceEmbeddings
from src.modules.config import EMBEDDING_MODEL
from src.utils.singleton import Singleton


class EmbeddingService(metaclass=Singleton):

    def __init__(self) -> None:
        self._embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

    def get_embeddings(self) -> HuggingFaceEmbeddings:
        return self._embeddings