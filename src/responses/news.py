from pydantic import BaseModel


class QAPair(BaseModel):
    question: str
    answer: str


class QuizResponse(BaseModel):
    topic: str
    difficulty: str
    articles_fetched: int
    questions: list[QAPair]