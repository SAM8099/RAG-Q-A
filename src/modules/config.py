import os
from dotenv import load_dotenv

load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Upgraded from BGE-small to BGE-M3 for better multilingual and retrieval quality
CHUNKING_STRATEGY = "semantic"
EMBEDDING_MODEL = "BAAI/bge-m3"

# BGE Reranker — cross-encoder, more accurate than embedding similarity alone
RERANK_MODEL = "BAAI/bge-reranker-base"

LLM_MODEL = "llama-3.3-70b-versatile"
FAISS_INDEX_PATH = "data/faiss_index"

TOPICS = {
    "General": "",
    "Technology": "technology",
    "Business": "business",
    "Science": "science",
    "Health": "health",
    "Sports": "sports",
    "Entertainment": "entertainment",
}

DIFFICULTY_PROMPTS = {
    "Easy": "Generate simple, factual questions suitable for beginners. Keep questions short and answers straightforward.",
    "Medium": "Generate moderate-difficulty questions that require some background knowledge. Include context-based reasoning.",
    "Hard": "Generate challenging questions that require deep understanding and analytical thinking. Include inference-based questions.",
}