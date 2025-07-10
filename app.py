import streamlit as st
from langchain_groq import ChatGroq
from newsapi import NewsApiClient
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
import os
from dotenv import load_dotenv
load_dotenv()
# Set your keys
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")


# Init NewsAPI
newsapi = NewsApiClient(api_key=NEWSAPI_KEY)

st.title("📰 Auto News-Based Question Generator")

if st.button("Generate Current Affairs Questions"):
    with st.spinner("Fetching top news..."):
        news = newsapi.get_top_headlines(language='en', page_size=10)

        if not news['articles']:
            st.warning("No news found.")
        else:
            articles = [f"{a['title']}. {a['description']}" for a in news['articles'] if a['description']]
            full_text = "\n\n".join(articles)

            st.subheader("🗞 Headlines:")
            for a in news['articles'][:3]:
                st.markdown(f"- **{a['title']}**")

            # Step 1: Create document chunks
            text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            docs = [Document(page_content=chunk) for chunk in text_splitter.split_text(full_text)]

            # Step 2: Embed and store in FAISS
            embeddings = OllamaEmbeddings(model="mxbai-embed-large")
            vectorstore = FAISS.from_documents(docs, embeddings)

            # Step 3: Retrieve relevant chunks (optional since all are fresh)
            retriever_docs = vectorstore.similarity_search("current events", k=5)

            # Step 4: Use LLM to generate questions
            llm = ChatGroq(temperature=0,model_name="llama3-70b-8192",api_key=groq_api_key)
            chain = load_qa_chain(llm, chain_type="stuff")

            question_prompt = """
            Based on the news content below, generate 5 current affairs quiz questions with their answers.
            The questions should be concise and factual.
            """
            content = "\n".join([doc.page_content for doc in retriever_docs])
            response = chain.run(input_documents=[Document(page_content=content)], question=question_prompt)

            st.subheader("🧠 Auto-Generated Questions:")
            st.markdown(response)
