import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON

from src.repositories.config import Base
from src.requests.generation_records import GenerationRecordRequest

class GenerationRecord(Base):
    __tablename__ = "generation_records"  

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    difficulty = Column(String)
    num_articles = Column(Integer)
    num_questions = Column(Integer)
    chunking_strategy = Column(String)
    model_used = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    questions_data = Column(JSON, nullable=True)  

    @classmethod
    def from_module(
        cls,
        generation_record_request: GenerationRecordRequest
    ):
        return cls(
            category=generation_record_request.category,
            difficulty=generation_record_request.difficulty,
            num_articles=generation_record_request.num_articles,
            num_questions=generation_record_request.num_questions,
            chunking_strategy=generation_record_request.chunking_strategy,
            model_used=generation_record_request.model_used,
            questions_data=generation_record_request.questions_data
        )