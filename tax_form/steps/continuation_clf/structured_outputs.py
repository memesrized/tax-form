from pydantic import BaseModel, Field


class ClassificationResult(BaseModel):
    is_continuation: bool = Field(
        ..., description="Whether the page is a continuation page."
    )
