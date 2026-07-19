from llama_index.core import VectorStoreIndex

class SemanticRetriever:
    def __init__(self, index: VectorStoreIndex, top_k: int):
        self.index = index
        self.top_k = top_k*2
        self.retriever = self.index.as_retriever(similarity_top_k=self.top_k)
