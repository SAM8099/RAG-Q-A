from fastapi import APIRouter, HTTPException, status
from src.requests.quiz import QuizRequest
from src.responses.news import QuizResponse
from src.modules.question_generator import QuestionGenerator

questions_router = APIRouter(prefix="/questions", tags=["Questions"])


@questions_router.post(
    "/generate",
    response_model=QuizResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate quiz questions from live news",
)
async def generate_questions(request: QuizRequest):

    try:
        response = await QuestionGenerator.generate_questions(request)
        return response

    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))