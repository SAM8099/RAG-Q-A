from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.indices.query.query_transform.base import HyDEQueryTransform

from src.modules.retrievers.bm25 import BM25
from src.modules.retrievers.semantic import SemanticRetriever

class HybridRetriever:
    def __init__(self, semantic_retriever: SemanticRetriever, bm25_retriever: BM25):
        self.semantic_retriever = semantic_retriever
        self.bm25_retriever = bm25_retriever
        self.hyde = HyDEQueryTransform(include_original=True)
        self.retriever = QueryFusionRetriever(
            retrievers=[self.semantic_retriever.retriever, self.bm25_retriever],
            similarity_top_k=self.semantic_retriever.top_k,
            num_queries=1,           
            mode="reciprocal_rerank",
            use_async=False,
        )
    
    def _transform_query(self, query: str):
        transformed_query = self.hyde(query).query_str
        return transformed_query

    def retrieve(self, query: str):
        transformed_query = self._transform_query(query)
        return self.retriever.retrieve(transformed_query)