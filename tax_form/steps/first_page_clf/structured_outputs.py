from typing import Literal
from pydantic import BaseModel, Field


PageTypes = Literal[
    "1040f",
    "f1040sa",
    "f1040sb",
    "f1040sc",
    "f1040sd",
    "f1040se",
    "f1040s1",
    "f1040s2",
    "f1040s3",
    "f8863",
    "f8812",
    "f2441",
    "other",
]


# TODO: add field for reasoning
class ClassificationResult(BaseModel):
    page_type: PageTypes = Field(
        ..., description="The type of the form page classified."
    )
