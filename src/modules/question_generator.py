from src.requests.quiz import QuizRequest
from src.requests.generation_records import GenerationRecordRequest
from src.responses.news import QuizResponse, QAPair
from src.services.news_service import NewsService
from src.services.generator_service import GeneratorService
from src.modules.news_fetcher import format_articles_to_nodes
from src.modules.rag import chunk_text, VectorIndexManager, Retriever
from src.repositories.records import RecordRepository
from src.modules.records import GenerationRecord
from src.modules.config import LLM_MODEL, CHUNKING_STRATEGY


class QuestionGenerator:

    @staticmethod
    async def generate_questions(request: QuizRequest):

        try:
            articles = NewsService().fetch_headlines(
                topic=request.category if request.category != "General" else "",
                page_size=request.num_articles,
            )
        except RuntimeError as e:
            raise e

        if not articles:
            raise RuntimeError(f"No articles found for category '{request.category}'")
        
        index = None
        if request.use_cached_index:
            index = VectorIndexManager.load_vector_index(topic=request.category)

        if index is None:
            nodes = format_articles_to_nodes(articles)
            chunked_nodes = chunk_text(nodes)
            index = VectorIndexManager.build_vector_index(chunked_nodes, topic=request.category)

        query = f"current affairs {request.category} news events"
        chunks, sources = Retriever.retrieve_relevant_chunks(index, query, top_k=5)

        try:
            raw_output = GeneratorService().generate_questions(
                chunks=chunks,
                difficulty=request.difficulty,
                topic=request.category,
                sources=sources,
            )
        except RuntimeError as e:
            raise e

        questions = GeneratorService().parse_questions(raw_output)
        if not questions:
            raise RuntimeError("Failed to parse generated questions. Please try again.")

        try:
            
            repo = RecordRepository()
            record_request = GenerationRecordRequest(
                category=request.category,
                difficulty=request.difficulty,
                num_articles=len(articles),
                num_questions=request.num_questions,
                chunking_strategy=CHUNKING_STRATEGY,
                model_used=LLM_MODEL,
                questions_data=questions
            )
            record = GenerationRecord.from_module(record_request)
            repo.add_record(record)
            
        except Exception as db_err:
            import logging
            logging.error(f"Failed to log run to database: {db_err}")

        return QuizResponse(
            topic=request.category,
            difficulty=request.difficulty,
            articles_fetched=len(articles),
            sources_used=sources,
            questions=[QAPair(**qa) for qa in questions],
        )