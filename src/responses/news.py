from pydantic import BaseModel


class QAPair(BaseModel):
    question: str
    answer: str


class GenerateQuestionsResponse(BaseModel):
    session_id: int
    topic: str
    difficulty: str
    questions: list[QAPair]
    articles_fetched: int


class HistoryEntry(BaseModel):
    id: int
    timestamp: str
    topic: str
    difficulty: str
    questions: list[QAPair]


class HistoryResponse(BaseModel):
    sessions: list[HistoryEntry]
    total: int