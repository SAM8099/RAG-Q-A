from fastapi import APIRouter, HTTPException, status
from src.requests.quiz import QuizRequest
from src.responses.news import GenerateQuestionsResponse, HistoryResponse, QAPair
from src.services.news_service import NewsService
from src.services.generator_service import GeneratorService
from src.modules.news_fetcher import format_articles_to_text
from src.modules.rag import chunk_text, build_faiss_index, load_faiss_index, retrieve_relevant_chunks
from src.repositories.history import HistoryRepository

questions_router = APIRouter(prefix="/questions", tags=["Questions"])
history_router = APIRouter(prefix="/history", tags=["History"])


# ── Questions Routes ──────────────────────────────────────────────────────────

@questions_router.post(
    "/generate",
    response_model=GenerateQuestionsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate quiz questions from live news",
)
def generate_questions(request: QuizRequest):
    # Step 1: Fetch news
    articles = NewsService().fetch_headlines(
        topic=request.category,
        page_size=request.num_articles,
    )
    if not articles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No articles found for category '{request.category}'",
        )

    # Step 2: Build or load FAISS index
    if request.use_cached_index:
        vectorstore = load_faiss_index(topic=request.category)

    if not request.use_cached_index or vectorstore is None:
        full_text = format_articles_to_text(articles)
        docs = chunk_text(full_text)
        vectorstore = build_faiss_index(docs, topic=request.category)

    # Step 3: Retrieve relevant chunks
    query = f"current affairs {request.category} news events"
    relevant_docs = retrieve_relevant_chunks(vectorstore, query, k=5)

    # Step 4: Generate questions
    raw_output = GeneratorService().generate_questions(
        docs=relevant_docs,
        difficulty=request.difficulty,
        topic=request.category,
    )

    # Step 5: Parse and save
    questions = GeneratorService().parse_questions(raw_output)
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse generated questions. Please try again.",
        )

    session_id = HistoryRepository.insert_session(
        topic=request.category,
        difficulty=request.difficulty,
        questions=questions,
    )

    return GenerateQuestionsResponse(
        session_id=session_id,
        topic=request.category,
        difficulty=request.difficulty,
        questions=[QAPair(**qa) for qa in questions],
        articles_fetched=len(articles),
    )


# ── History Routes ────────────────────────────────────────────────────────────

@history_router.get(
    "/",
    response_model=HistoryResponse,
    summary="Get all past quiz sessions",
)
def get_history():
    sessions = HistoryRepository.get_all_sessions()
    return HistoryResponse(sessions=sessions, total=len(sessions))


@history_router.get(
    "/{session_id}",
    response_model=HistoryResponse,
    summary="Get a single quiz session by ID",
)
def get_session(session_id: int):
    session = HistoryRepository.get_session_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )
    return HistoryResponse(sessions=[session], total=1)


@history_router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a single quiz session by ID",
)
def delete_session(session_id: int):
    deleted = HistoryRepository.delete_session_by_id(session_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )


@history_router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all quiz sessions",
)
def delete_all_sessions():
    HistoryRepository.delete_all_sessions()