import json

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from backend.app.schemas.request import (
    SummaryLength,
)

from backend.app.schemas.response import (
    SegmentAnalysis,
    VideoAnalysis,
)

from backend.app.services.llm_service import (
    LLMService,
)


STYLE = {
    SummaryLength.short:
        (
            "Concise: essential overview, "
            "5-7 key points, major chapters only."
        ),

    SummaryLength.standard:
        (
            "Balanced detail: enough to "
            "understand the full video clearly."
        ),

    SummaryLength.detailed:
        (
            "Comprehensive: retain major arguments, "
            "examples, caveats, and useful detail."
        ),
}


class SynthesisService:

    def __init__(
        self,
        llm: LLMService | None = None,
    ) -> None:

        self.llm = (
            llm
            or LLMService()
        )

    def synthesize(
        self,
        source_title: str,
        duration_seconds: float,
        segments: list[
            SegmentAnalysis
        ],
        summary_length: SummaryLength,
        custom_prompt: str | None,
    ) -> tuple[
        VideoAnalysis,
        str,
    ]:

        segment_json = json.dumps(
            [
                segment.model_dump()
                for segment
                in segments
            ],

            ensure_ascii=False,
        )

        messages = [
            SystemMessage(
                content=(
                    "You are a senior editor combining "
                    "chronologically ordered multimodal "
                    "segment analyses into one faithful "
                    "video briefing. Never claim the video "
                    "said something unless it appears in "
                    "the supplied segment analyses."
                )
            ),

            HumanMessage(
                content=f"""
Video title/source label: {source_title}
Duration: {duration_seconds:.2f} seconds

Requested style:
{STYLE[summary_length]}

User instruction:
{custom_prompt or 'None'}

Combine the segment analyses below into one coherent result.

Remove duplicates.

Keep chapters chronological.

Preserve absolute timestamps.

Action items should only be included when genuinely
implied by the content.

claims_to_verify should be specific factual/current
claims suitable for web research.

SEGMENT ANALYSES:

{segment_json}
""".strip()
            ),
        ]

        return (
            self.llm
            .invoke_structured(
                "summary",
                messages,
                VideoAnalysis,
            )
        )