from pydantic import BaseModel, Field


class LLMWorkSuggestion(BaseModel):
    """Одно предложение регламентной работы от LLM."""
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    reason: str = Field(..., min_length=10)
    estimated_hours: float = Field(..., gt=0, le=24)


class LLMResponse(BaseModel):
    """Ответ LLM: список предложений."""
    suggestions: list[LLMWorkSuggestion]