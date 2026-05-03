import os
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from src.modules.config import FAISS_INDEX_PATH
from src.services.embedding_service import EmbeddingService


def chunk_text(text: str) -> list[Document]:
    """
    Split text into overlapping chunks using RecursiveCharacterTextSplitter.
    Smarter than CharacterTextSplitter — respects paragraph and sentence boundaries.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=60,
        separators=["\n\n", "\n", ".", " "],
    )
    return [Document(page_content=chunk) for chunk in splitter.split_text(text)]


def build_faiss_index(docs: list[Document], topic: str) -> FAISS:
    """
    Build FAISS index and persist to disk per topic.
    Uses EmbeddingService singleton — no re-initialization.
    """
    embeddings = EmbeddingService().get_embeddings()
    vectorstore = FAISS.from_documents(docs, embeddings)
    index_path = f"{FAISS_INDEX_PATH}/{topic or 'general'}"
    os.makedirs(index_path, exist_ok=True)
    vectorstore.save_local(index_path)
    return vectorstore


def load_faiss_index(topic: str) -> FAISS | None:
    """
    Load existing FAISS index from disk if available.
    """
    embeddings = EmbeddingService().get_embeddings()
    index_path = f"{FAISS_INDEX_PATH}/{topic or 'general'}"
    if os.path.exists(index_path):
        return FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    return None


def retrieve_relevant_chunks(vectorstore: FAISS, query: str, k: int = 5) -> list[Document]:
    """
    Retrieve top-k relevant chunks with similarity score filtering.
    """
    results = vectorstore.similarity_search_with_score(query, k=k)
    filtered = [doc for doc, score in results if score < 1.2]
    return filtered if filtered else [doc for doc, _ in results]