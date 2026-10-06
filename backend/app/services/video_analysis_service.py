import json

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from backend.app.schemas.response import (
    SegmentAnalysis,
)

from backend.app.services.llm_service import (
    LLMService,
)

from backend.app.services.media_service import (
    MediaSegment,
    MediaSource,
)

from backend.app.services.model_catalog import (
    ModelCatalogService,
)


class VideoAnalysisService:

    def __init__(
        self,
        llm: LLMService | None = None,
        catalog: (
            ModelCatalogService
            | None
        ) = None,
    ) -> None:

        self.catalog = (
            catalog
            or ModelCatalogService()
        )

        self.llm = (
            llm
            or LLMService(
                self.catalog
            )
        )

    def analyze_segment(
        self,
        source: MediaSource,
        segment: MediaSegment,
        custom_prompt: (
            str | None
        ) = None,
    ) -> tuple[
        SegmentAnalysis,
        str,
    ]:

        errors: list[str] = []

        for model_id in (
            self.llm.models_for(
                "video"
            )
        ):

            try:
                caps = (
                    self.catalog.get(
                        model_id
                    )
                )

                supports_images = (
                    "image"
                    in caps
                    .input_modalities
                )

                supports_audio = (
                    "audio"
                    in caps
                    .input_modalities
                )

                if (
                    not supports_images
                    and not supports_audio
                ):
                    raise ValueError(
                        "Selected video model "
                        "accepts neither image "
                        "nor audio input."
                    )

                content: list[
                    dict
                ] = [
                    {
                        "type":
                            "text",

                        "text":
                            self._prompt(
                                source,
                                segment,
                                custom_prompt,
                            ),
                    }
                ]

                if supports_images:

                    for data_url in (
                        segment
                        .frame_data_urls
                    ):

                        content.append(
                            {
                                "type":
                                    "image_url",

                                "image_url": {
                                    "url":
                                        data_url
                                },
                            }
                        )

                if (
                    supports_audio
                    and segment.audio_base64
                ):

                    content.append(
                        {
                            "type":
                                "input_audio",

                            "input_audio": {
                                "data":
                                    segment
                                    .audio_base64,

                                "format":
                                    "mp3",
                            },
                        }
                    )

                messages = [
                    SystemMessage(
                        content=(
                            "You are a precise "
                            "multimodal video analyst. "
                            "Use only the supplied "
                            "audio and sampled frames. "
                            "Do not invent missing "
                            "content."
                        )
                    ),

                    HumanMessage(
                        content=content
                    ),
                ]

                result = (
                    self.llm
                    .invoke_structured_model(
                        model_id,
                        messages,
                        SegmentAnalysis,
                    )
                )

                result.segment_index = (
                    segment.index
                )

                result.start_seconds = (
                    segment
                    .start_seconds
                )

                result.end_seconds = (
                    segment
                    .end_seconds
                )

                return (
                    result,
                    model_id,
                )

            except Exception as exc:

                errors.append(
                    f"{model_id}: {exc}"
                )

        raise RuntimeError(
            "All video models failed. "
            + " | ".join(
                errors
            )
        )

    @staticmethod
    def _prompt(
        source: MediaSource,
        segment: MediaSegment,
        custom_prompt: (
            str | None
        ),
    ) -> str:

        schema = json.dumps(
            SegmentAnalysis
            .model_json_schema(),

            ensure_ascii=False,
        )

        return f"""
Analyze this segment from the video "{source.title}".

Absolute segment time range:
- start: {segment.start_seconds:.2f} seconds
- end: {segment.end_seconds:.2f} seconds

The images are sparse samples, not every frame.
The audio covers the segment when available.

Use ABSOLUTE video timestamps for key moments,
for example 00:12:31.

Extract concrete externally verifiable claims
into claims_to_verify.

Keep summaries faithful to what is actually
observable or heard.

Additional user instruction:
{custom_prompt or 'None'}

Return only JSON matching this schema:
{schema}
""".strip()