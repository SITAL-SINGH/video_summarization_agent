import tempfile
from datetime import (
    datetime,
    timezone,
)
from pathlib import Path

from backend.app.core.config import (
    settings,
)

from backend.app.schemas.request import (
    SummaryLength,
)

from backend.app.schemas.response import (
    ModelSelection,
    SummaryResponse,
)

from backend.app.services.history_service import (
    HistoryService,
)

from backend.app.services.llm_service import (
    LLMService,
)

from backend.app.services.media_service import (
    MediaService,
    MediaSource,
)

from backend.app.services.model_catalog import (
    ModelCatalogService,
)

from backend.app.services.research_service import (
    ResearchService,
)

from backend.app.services.synthesis_service import (
    SynthesisService,
)

from backend.app.services.video_analysis_service import (
    VideoAnalysisService,
)


class VideoPipeline:

    def __init__(
        self,
    ) -> None:

        self.catalog = (
            ModelCatalogService()
        )

        self.llm = LLMService(
            self.catalog
        )

        self.media = (
            MediaService()
        )

        self.video = (
            VideoAnalysisService(
                self.llm,
                self.catalog,
            )
        )

        self.synthesis = (
            SynthesisService(
                self.llm
            )
        )

        self.researcher = (
            ResearchService(
                self.llm
            )
        )

        self.history = (
            HistoryService()
        )

    def summarize_youtube(
        self,
        url: str,
        summary_length: SummaryLength,
        custom_prompt: str | None,
        enable_research: bool,
    ) -> SummaryResponse:

        with tempfile.TemporaryDirectory(
            prefix="ai-video-"
        ) as temp:

            source = (
                self.media
                .download_youtube(
                    url,
                    Path(temp),
                )
            )

            return (
                self._summarize_source(
                    source=source,

                    source_type="youtube",

                    summary_length=(
                        summary_length
                    ),

                    custom_prompt=(
                        custom_prompt
                    ),

                    enable_research=(
                        enable_research
                    ),
                )
            )

    def summarize_upload(
        self,
        path: Path,
        filename: str,
        summary_length: SummaryLength,
        custom_prompt: str | None,
        enable_research: bool,
    ) -> SummaryResponse:

        source = (
            self.media
            .uploaded_source(
                path,
                filename,
            )
        )

        return (
            self._summarize_source(
                source=source,

                source_type="upload",

                summary_length=(
                    summary_length
                ),

                custom_prompt=(
                    custom_prompt
                ),

                enable_research=(
                    enable_research
                ),
            )
        )

    def _summarize_source(
        self,
        source: MediaSource,
        source_type: str,
        summary_length: SummaryLength,
        custom_prompt: str | None,
        enable_research: bool,
    ) -> SummaryResponse:

        warnings: list[
            str
        ] = []

        segment_analyses = []

        used_video_models: list[
            str
        ] = []

        for (
            index,
            (
                start,
                end,
            ),
        ) in enumerate(
            self.media
            .segment_windows(
                source
                .duration_seconds
            )
        ):

            # Extract both once.
            # Individual models receive only
            # modalities they support.
            segment = (
                self.media
                .build_segment(
                    source,

                    index=index,

                    start_seconds=start,

                    end_seconds=end,

                    include_images=True,

                    include_audio=True,
                )
            )

            analysis, model_id = (
                self.video
                .analyze_segment(
                    source,
                    segment,

                    custom_prompt=(
                        custom_prompt
                    ),
                )
            )

            segment_analyses.append(
                analysis
            )

            if (
                model_id
                not in used_video_models
            ):
                used_video_models.append(
                    model_id
                )

        (
            analysis,
            used_summary_model,
        ) = (
            self.synthesis
            .synthesize(
                source_title=(
                    source.title
                ),

                duration_seconds=(
                    source
                    .duration_seconds
                ),

                segments=(
                    segment_analyses
                ),

                summary_length=(
                    summary_length
                ),

                custom_prompt=(
                    custom_prompt
                ),
            )
        )

        research = None

        used_reasoning_model = ""

        if enable_research:

            try:
                (
                    research,
                    used_reasoning_model,
                ) = (
                    self.researcher
                    .research(
                        analysis
                    )
                )

            except Exception as exc:

                warnings.append(
                    "Research step was "
                    "skipped because it "
                    f"failed: {exc}"
                )

        response = SummaryResponse(
            source_type=source_type,

            source_name=(
                source.source_name
            ),

            source_title=(
                source.title
            ),

            duration_seconds=(
                source.duration_seconds
            ),

            analysis=analysis,

            research=research,

            models=ModelSelection(
                video_models=(
                    used_video_models
                    or settings
                    .video_model_list
                ),

                reasoning_models=(
                    [
                        used_reasoning_model
                    ]
                    if used_reasoning_model
                    else settings
                    .reasoning_model_list
                ),

                summary_models=[
                    used_summary_model
                ],
            ),

            warnings=warnings,

            generated_at=(
                datetime.now(
                    timezone.utc
                )
            ),
        )

        self.history.save(
            response
        )

        return response