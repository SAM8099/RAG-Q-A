from llama_index.core.postprocessor import SentenceTransformerRerank

from src.modules.config import RERANK_MODEL

class BGEV3Rerank(SentenceTransformerRerank):

    def __init__(self, top_n: int):
        super().__init__(
            top_n=top_n,
            model=RERANK_MODEL
        )