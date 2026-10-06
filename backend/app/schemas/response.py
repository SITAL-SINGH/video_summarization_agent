from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class KeyMoment(BaseModel):
    timestamp: str

    title: str

    description: str


class SegmentAnalysis(BaseModel):
    segment_index: int

    start_seconds: float

    end_seconds: float

    summary: str

    key_points: list[str] = Field(
        default_factory=list
    )

    key_moments: list[
        KeyMoment
    ] = Field(
        default_factory=list
    )

    entities: list[str] = Field(
        default_factory=list
    )

    claims_to_verify: list[
        str
    ] = Field(
        default_factory=list
    )


class Chapter(BaseModel):
    timestamp: str

    title: str

    summary: str


class VideoAnalysis(BaseModel):
    title: str

    detected_language: str

    overview: str

    summary: str

    key_points: list[str] = Field(
        default_factory=list
    )

    chapters: list[
        Chapter
    ] = Field(
        default_factory=list
    )

    action_items: list[
        str
    ] = Field(
        default_factory=list
    )

    entities: list[str] = Field(
        default_factory=list
    )

    claims_to_verify: list[
        str
    ] = Field(
        default_factory=list
    )

    tags: list[str] = Field(
        default_factory=list
    )


class ResearchSource(BaseModel):
    id: int

    title: str

    url: str

    snippet: str = ""


class ClaimVerification(
    BaseModel,
):
    claim: str

    status: Literal[
        "confirmed",
        "contradicted",
        "uncertain",
        "context-dependent",
    ]

    explanation: str

    source_ids: list[
        int
    ] = Field(
        default_factory=list
    )


class GroundedResearch(
    BaseModel,
):
    overview: str

    claims: list[
        ClaimVerification
    ] = Field(
        default_factory=list
    )

    sources: list[
        ResearchSource
    ] = Field(
        default_factory=list
    )


class ModelSelection(BaseModel):
    video_models: list[str]

    reasoning_models: list[str]

    summary_models: list[str]


class SummaryResponse(BaseModel):
    id: int | None = None

    source_type: Literal[
        "youtube",
        "upload",
    ]

    source_name: str

    source_title: str

    duration_seconds: float

    analysis: VideoAnalysis

    research: (
        GroundedResearch
        | None
    ) = None

    models: ModelSelection

    warnings: list[
        str
    ] = Field(
        default_factory=list
    )

    generated_at: datetime


class HistoryListItem(
    BaseModel,
):
    id: int

    source_type: str

    source_name: str

    title: str

    generated_at: datetime