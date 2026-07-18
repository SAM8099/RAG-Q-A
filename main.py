import requests
import streamlit as st
from src.modules.config import TOPICS, DIFFICULTY_PROMPTS

FASTAPI_URL = "http://localhost:8000"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Current Affairs Q&A Generator",
    page_icon="📰",
    layout="wide",
)

st.title("📰 Current Affairs Q&A Generator")
st.caption("Powered by NewsAPI · BGE-M3 Embeddings · LlamaIndex · BGE Reranker · LLaMA 3 (Groq)")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    topic_label = st.selectbox("📂 Topic", list(TOPICS.keys()))
    difficulty = st.radio("🎯 Difficulty", list(DIFFICULTY_PROMPTS.keys()), index=1)
    num_articles = st.slider("📄 Articles to Fetch", min_value=5, max_value=20, value=10)
    num_questions = st.slider("❓ Questions to Generate", min_value=3, max_value=10, value=5)
    use_cached = st.checkbox("♻️ Use cached index (if available)", value=False)
    st.markdown("---")
    st.markdown("**Stack**")
    st.markdown("LlamaIndex · BGE-M3 · BGE Reranker · LLaMA 3")

# ── Generate ──────────────────────────────────────────────────────────────────
if st.button("🚀 Generate Questions", type="primary", use_container_width=True):
    with st.spinner("Generating questions..."):
        try:
            response = requests.post(
                f"{FASTAPI_URL}/questions/generate",
                json={
                    "category": topic_label,
                    "difficulty": difficulty,
                    "num_articles": num_articles,
                    "num_questions": num_questions,
                    "use_cached_index": use_cached,
                },
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()

        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to FastAPI server. Make sure it is running on port 8000.")
            st.stop()
        except requests.exceptions.Timeout:
            st.error("Request timed out. Try reducing the number of articles.")
            st.stop()
        except requests.exceptions.HTTPError as e:
            st.error(f"API error: {response.json().get('detail', str(e))}")
            st.stop()

    st.success(f"✅ Fetched {data['articles_fetched']} articles · Generated {len(data['questions'])} questions")
    st.subheader(f"🧠 {data['difficulty']} Questions — {data['topic']}")

    for i, qa in enumerate(data["questions"], 1):
        with st.expander(f"Q{i}. {qa['question']}"):
            st.markdown(f"**Answer:** {qa['answer']}")