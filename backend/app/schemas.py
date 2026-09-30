import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator, model_validator

Answer = Literal["A", "B", "C", "D"]
Mode = Literal["60_min", "180_min"]


class Question(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    option_a: str = Field(min_length=1)
    option_b: str = Field(min_length=1)
    option_c: str = Field(min_length=1)
    option_d: str = Field(min_length=1)
    correct_answer: Answer
    category: str = Field(min_length=1)
    subcategory: str = Field(min_length=1)
    difficulty: Literal["easy", "medium", "hard"]
    tags: list[str]

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str]) -> list[str]:
        normalized = []
        for tag in tags:
            if not isinstance(tag, str) or not tag.strip():
                raise ValueError("tags must contain nonempty strings")
            value = re.sub(r"\s+", "-", tag.strip().lower())
            if value not in normalized:
                normalized.append(value)
        return normalized


class PublicQuestion(BaseModel):
    id: str
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    category: str
    subcategory: str
    difficulty: str
    tags: list[str]


class FlashcardQuestion(PublicQuestion):
    check_token: str


class FlashcardRequest(BaseModel):
    categories: list[str] = Field(min_length=1)
    exclude_ids: list[str] = Field(default_factory=list)


class CheckRequest(BaseModel):
    question_id: str = Field(min_length=1)
    check_token: str = Field(min_length=1)
    answer: Answer


class ExamRequest(BaseModel):
    mode: Mode
    category_distribution: dict[str, StrictInt] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_distribution(self):
        if any(not isinstance(v, int) or isinstance(v, bool) or v < 0 or v > 100 for v in self.category_distribution.values()):
            raise ValueError("percentages must be whole numbers from 0 to 100")
        if any(not name.strip() for name in self.category_distribution):
            raise ValueError("category names cannot be empty")
        if sum(self.category_distribution.values()) != 100:
            raise ValueError("category percentages must total 100")
        return self


class SubmitRequest(BaseModel):
    answers: dict[str, Answer]
