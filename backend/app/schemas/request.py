from enum import Enum

from pydantic import BaseModel, Field


class SummaryLength(
    str,
    Enum,
):
    short = "short"
    standard = "standard"
    detailed = "detailed"


class SummaryOptions(
    BaseModel,
):
    summary_length: SummaryLength = (
        SummaryLength.standard
    )

    custom_prompt: str | None = Field(
        default=None,
        max_length=4000,
    )

    enable_research: bool = True