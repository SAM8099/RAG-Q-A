import datetime
from dataclasses import dataclass, field

@dataclass
class GenerationRecordRequest:
    category: str
    difficulty: str
    num_articles: int
    num_questions: int
    chunking_strategy: str
    model_used: str
    questions_data: list = field(default_factory=list)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
