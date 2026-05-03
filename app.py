import streamlit as st
from src.modules.news_fetcher import fetch_news, format_articles_to_text
from src.modules.rag import load_embeddings, chunk_text, build_faiss_index, retrieve_relevant_chunks
from src.modules.generator import generate_questions, parse_questions
from src.repositories.history import save_to_history, get_history, clear_history
from src.modules.config import TOPICS, DIFFICULTY_PROMPTS

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Current Affairs Q&A Generator",
    page_icon="📰",
    layout="wide",
)

st.title("📰 Current Affairs Q&A Generator")
st.caption("Powered by NewsAPI · BGE Embeddings · FAISS · LLaMA 3 (Groq)")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    topic_label = st.selectbox("📂 Topic", list(TOPICS.keys()))
    topic = TOPICS[topic_label]

    difficulty = st.radio("🎯 Difficulty", list(DIFFICULTY_PROMPTS.keys()), index=1)

    num_articles = st.slider("📄 Number of Articles to Fetch", min_value=5, max_value=20, value=10)

    use_cached = st.checkbox("♻️ Use cached FAISS index (if available)", value=False)

    st.markdown("---")
    st.markdown("**About**")
    st.markdown("This app fetches live news, embeds them into a FAISS vector store, and uses LLaMA 3 to generate quiz questions.")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🧠 Generate Questions", "📜 History"])

# ── Tab 1: Generate ───────────────────────────────────────────────────────────
with tab1:
    if st.button("🚀 Generate Questions", type="primary", use_container_width=True):

        # Step 1: Fetch news
        with st.spinner("📡 Fetching latest news..."):
            articles = fetch_news(topic=topic, page_size=num_articles)

        if not articles:
            st.warning("No articles found. Try a different topic.")
            st.stop()

        # Show headlines
        with st.expander(f"🗞 {len(articles)} Headlines Fetched", expanded=False):
            for a in articles:
                st.markdown(f"- **{a['title']}** — *{a['source']}*")
                st.caption(a["url"])

        # Step 2: Embed and index
        with st.spinner("🔍 Building knowledge base..."):
            embeddings = load_embeddings()
            full_text = format_articles_to_text(articles)
            docs = chunk_text(full_text)
            vectorstore = build_faiss_index(docs, embeddings, topic)

        st.success(f"✅ Indexed {len(docs)} chunks from {len(articles)} articles.")

        # Step 3: Retrieve relevant chunks
        with st.spinner("🔎 Retrieving relevant context..."):
            query = f"current affairs {topic_label} news events"
            relevant_docs = retrieve_relevant_chunks(vectorstore, query, k=5)

        # Step 4: Generate questions
        with st.spinner("🤖 Generating questions with LLaMA 3..."):
            raw_output = generate_questions(relevant_docs, difficulty, topic_label)

        if not raw_output:
            st.error("Failed to generate questions. Please try again.")
            st.stop()

        # Step 5: Parse and display
        questions = parse_questions(raw_output)

        if questions:
            st.subheader(f"🧠 {difficulty} Questions — {topic_label}")
            for i, qa in enumerate(questions, 1):
                with st.expander(f"Q{i}. {qa['question']}"):
                    st.markdown(f"**Answer:** {qa['answer']}")

            # Save to history
            save_to_history(topic_label, difficulty, questions)
            st.info("💾 Session saved to history.")
        else:
            # Fallback: show raw output if parsing fails
            st.subheader("🧠 Generated Questions")
            st.markdown(raw_output)

# ── Tab 2: History ────────────────────────────────────────────────────────────
with tab2:
    st.subheader("📜 Past Sessions")

    history = get_history()

    if not history:
        st.info("No history yet. Generate some questions first!")
    else:
        if st.button("🗑️ Clear History", type="secondary"):
            clear_history()
            st.rerun()

        for session in history:
            with st.expander(f"🕐 {session['timestamp']} — {session['topic']} ({session['difficulty']})"):
                for i, qa in enumerate(session["questions"], 1):
                    st.markdown(f"**Q{i}.** {qa['question']}")
                    st.markdown(f"**A{i}.** {qa['answer']}")
                    st.markdown("---")