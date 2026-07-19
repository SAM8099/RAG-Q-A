import os
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core import Settings
from llama_index.core.schema import NodeWithScore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from src.modules.config import FAISS_INDEX_PATH, EMBEDDING_MODEL, CHUNKING_STRATEGY
from src.modules.retrievers.bm25 import BM25
from src.modules.retrievers.semantic import SemanticRetriever
from src.modules.retrievers.hybrid import HybridRetriever
from src.modules.rerankers.bge_v3 import BGEV3Rerank
from src.modules.chunkers.chunker_factory import ChunkerFactory


def configure_settings() -> None:

    Settings.embed_model = HuggingFaceEmbedding(
        model_name=EMBEDDING_MODEL,
        embed_batch_size=32,
    )
    Settings.llm = None  


def chunk_text(nodes: list) -> list:
    
    splitter = ChunkerFactory.get_chunker(strategy=CHUNKING_STRATEGY)
    return splitter.get_nodes_from_documents(nodes)

class VectorIndexManager:
    
    @staticmethod
    def build_vector_index(nodes: list, topic: str) -> VectorStoreIndex:

        index = VectorStoreIndex(nodes)
        index_path = f"{FAISS_INDEX_PATH}/{topic or 'general'}"
        os.makedirs(index_path, exist_ok=True)
        index.storage_context.persist(persist_dir=index_path)
        return index

    @staticmethod
    def load_vector_index(topic: str) -> VectorStoreIndex | None:

        index_path = f"{FAISS_INDEX_PATH}/{topic or 'general'}"
        if os.path.exists(index_path):
            storage_context = StorageContext.from_defaults(persist_dir=index_path)
            return load_index_from_storage(storage_context)
        return None

class Retriever:
    
    @staticmethod
    def retrieve_relevant_chunks(
        index: VectorStoreIndex,
        query: str,
        top_k: int = 5,
    ) -> tuple[list[str], list[str]]:
        
        all_nodes = list(index.docstore.docs.values())
        if not all_nodes:
            return [], []

        vector_retriever = SemanticRetriever(index=index, top_k=top_k)

        bm25_retriever = BM25.from_defaults(
            nodes=all_nodes,
            similarity_top_k=min(top_k * 2, len(all_nodes)),
        )

        hybrid_retriever = HybridRetriever(
            semantic_retriever = vector_retriever,
            bm25_retriever = bm25_retriever,
        ).retriever

        retrieved_nodes: list[NodeWithScore] = hybrid_retriever.retrieve(query)
        reranker = BGEV3Rerank(top_n=top_k)
        reranked_nodes = reranker.postprocess_nodes(retrieved_nodes, query_str=query)


        chunks = [node.get_content() for node in reranked_nodes]
        sources = list({
            node.metadata.get("source", "Unknown")
            for node in reranked_nodes
            if node.metadata
        })

        return chunks, sources