from fastapi import APIRouter, HTTPException, status
from src.requests.quiz import QuizRequest
from src.responses.news import QuizResponse, QAPair
from src.services.news_service import NewsService
from src.services.generator_service import GeneratorService
from src.modules.news_fetcher import format_articles_to_nodes
from src.modules.rag import chunk_text, build_vector_index, load_vector_index, retrieve_relevant_chunks

questions_router = APIRouter(prefix="/questions", tags=["Questions"])


@questions_router.post(
    "/generate",
    response_model=QuizResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate quiz questions from live news",
)
async def generate_questions(request: QuizRequest):

    # Step 1: Fetch news
    try:
        articles = NewsService().fetch_headlines(
            topic=request.category if request.category != "General" else "",
            page_size=request.num_articles,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    if not articles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No articles found for category '{request.category}'",
        )

    # Step 2: Build or load vector index
    index = None
    if request.use_cached_index:
        index = load_vector_index(topic=request.category)

    if index is None:
        nodes = format_articles_to_nodes(articles)
        chunked_nodes = chunk_text(nodes)
        index = build_vector_index(chunked_nodes, topic=request.category)

    # Step 3: Hybrid search + HyDE + reranking
    query = f"current affairs {request.category} news events"
    chunks, sources = retrieve_relevant_chunks(index, query, top_k=5)

    # Step 4: Generate and parse questions
    try:
        raw_output = GeneratorService().generate_questions(
            chunks=chunks,
            difficulty=request.difficulty,
            topic=request.category,
            sources=sources,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    questions = GeneratorService().parse_questions(raw_output)
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse generated questions. Please try again.",
        )

    return QuizResponse(
        topic=request.category,
        difficulty=request.difficulty,
        articles_fetched=len(articles),
        sources_used=sources,
        questions=[QAPair(**qa) for qa in questions],
    )