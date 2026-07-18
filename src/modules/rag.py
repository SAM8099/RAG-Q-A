import os
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
from llama_index.core.schema import NodeWithScore
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.indices.query.query_transform.base import HyDEQueryTransform
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from src.modules.config import FAISS_INDEX_PATH, EMBEDDING_MODEL, RERANK_MODEL


def configure_settings() -> None:
    """
    Configure LlamaIndex global settings.
    Called once on startup — applies to all retrieval and indexing.
    BGE-M3 chosen for superior multilingual and semantic retrieval over BGE-small.
    """
    Settings.embed_model = HuggingFaceEmbedding(
        model_name=EMBEDDING_MODEL,
        embed_batch_size=32,
    )
    Settings.llm = None  # LLM handled separately via Groq


def chunk_text(nodes: list) -> list:
    """
    Split TextNodes into sentence-aware chunks using SentenceSplitter.
    Metadata (source, title, url) is preserved in each chunk automatically.
    """
    splitter = SentenceSplitter(
        chunk_size=400,
        chunk_overlap=60,
    )
    return splitter.get_nodes_from_documents(nodes)


def build_vector_index(nodes: list, topic: str) -> VectorStoreIndex:
    """
    Build VectorStoreIndex from nodes and persist to disk per topic.
    """
    index = VectorStoreIndex(nodes)
    index_path = f"{FAISS_INDEX_PATH}/{topic or 'general'}"
    os.makedirs(index_path, exist_ok=True)
    index.storage_context.persist(persist_dir=index_path)
    return index


def load_vector_index(topic: str) -> VectorStoreIndex | None:
    """
    Load existing VectorStoreIndex from disk if available.
    Returns None if not found.
    """
    index_path = f"{FAISS_INDEX_PATH}/{topic or 'general'}"
    if os.path.exists(index_path):
        storage_context = StorageContext.from_defaults(persist_dir=index_path)
        return load_index_from_storage(storage_context)
    return None


def retrieve_relevant_chunks(
    index: VectorStoreIndex,
    query: str,
    top_k: int = 5,
) -> tuple[list[str], list[str]]:
    """
    Full three-stage retrieval pipeline:

    Stage 1 — HyDE (Hypothetical Document Embedding):
        Generates a hypothetical answer to the query first.
        Searches using that answer instead of raw query.
        Why: answer-like text matches retrieved chunks better than question-like text.

    Stage 2 — Hybrid Search (BM25 + Vector):
        BM25: keyword matching — good for exact terms like names, dates, places.
        Vector: semantic matching — good for meaning and context.
        Combined via Reciprocal Rank Fusion for best of both.
        Retrieves top_k * 2 candidates to give reranker more to work with.

    Stage 3 — Reranking (BGE Reranker):
        Cross-encoder scores every candidate against the original query.
        More accurate than embedding similarity alone.
        Returns final top_k best chunks.

    Returns:
        chunks: text content to pass to LLM
        sources: unique source names for attribution in response
    """
    all_nodes = list(index.docstore.docs.values())
    if not all_nodes:
        return [], []

    # ── Stage 1: HyDE ────────────────────────────────────────────────────────
    hyde = HyDEQueryTransform(include_original=True)
    transformed_query = hyde(query).query_str

    # ── Stage 2: Hybrid Search ────────────────────────────────────────────────
    vector_retriever = index.as_retriever(similarity_top_k=top_k * 2)

    bm25_retriever = BM25Retriever.from_defaults(
        nodes=all_nodes,
        similarity_top_k=min(top_k * 2, len(all_nodes)),
    )

    hybrid_retriever = QueryFusionRetriever(
        retrievers=[vector_retriever, bm25_retriever],
        similarity_top_k=top_k * 2,
        num_queries=1,           # don't generate extra queries
        mode="reciprocal_rerank",
        use_async=False,
    )

    retrieved_nodes: list[NodeWithScore] = hybrid_retriever.retrieve(transformed_query)

    # ── Stage 3: Reranking ────────────────────────────────────────────────────
    reranker = SentenceTransformerRerank(
        model=RERANK_MODEL,
        top_n=top_k,
    )
    reranked_nodes = reranker.postprocess_nodes(retrieved_nodes, query_str=query)

    # ── Extract content and sources ───────────────────────────────────────────
    chunks = [node.get_content() for node in reranked_nodes]
    sources = list({
        node.metadata.get("source", "Unknown")
        for node in reranked_nodes
        if node.metadata
    })

    return chunks, sources