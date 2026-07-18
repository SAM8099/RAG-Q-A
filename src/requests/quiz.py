from pydantic import BaseModel, Field, field_validator


class QuizRequest(BaseModel):
    category: str = Field(
        default="General",
        description="News category to fetch headlines for",
        examples=["Technology", "Sports", "Health"],
    )
    difficulty: str = Field(
        default="Medium",
        description="Difficulty level of generated questions",
        examples=["Easy", "Medium", "Hard"],
    )
    num_articles: int = Field(
        default=10,
        ge=5,
        le=20,
        description="Number of news articles to fetch (5–20)",
    )
    num_questions: int = Field(
        default=5,
        ge=3,
        le=10,
        description="Number of questions to generate (3–10)",
    )
    use_cached_index: bool = Field(
        default=False,
        description="Use persisted FAISS index if available instead of rebuilding",
    )

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        allowed = {"Easy", "Medium", "Hard"}
        if v not in allowed:
            raise ValueError(f"difficulty must be one of {allowed}")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        allowed = {"General", "Technology", "Business", "Science", "Health", "Sports", "Entertainment"}
        if v not in allowed:
            raise ValueError(f"category must be one of {allowed}")
        return v