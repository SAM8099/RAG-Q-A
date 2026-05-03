import os
from dotenv import load_dotenv

load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")  # e.g. postgresql://user:pass@host:5432/dbname

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
LLM_MODEL = "llama3-70b-8192"
FAISS_INDEX_PATH = "data/faiss_index"
HISTORY_FILE = "data/history.json"

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
    "Easy": "Generate 5 simple, factual current affairs questions suitable for beginners. Keep questions short and answers straightforward.",
    "Medium": "Generate 5 moderate-difficulty current affairs questions that require some background knowledge. Include context-based reasoning questions.",
    "Hard": "Generate 5 challenging current affairs questions that require deep understanding and analytical thinking. Include inference-based questions.",
}