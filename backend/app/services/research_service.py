import json

from ddgs import DDGS

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from pydantic import (
    BaseModel,
    Field,
)

from backend.app.core.config import (
    settings,
)

from backend.app.schemas.response import (
    ClaimVerification,
    GroundedResearch,
    ResearchSource,
    VideoAnalysis,
)

from backend.app.services.llm_service import (
    LLMService,
)


class ResearchDraft(BaseModel):
    overview: str

    claims: list[
        ClaimVerification
    ] = Field(
        default_factory=list
    )


class ResearchService:

    def __init__(
        self,
        llm: LLMService | None = None,
    ) -> None:

        self.llm = (
            llm
            or LLMService()
        )

    def research(
        self,
        analysis: VideoAnalysis,
    ) -> tuple[
        GroundedResearch,
        str,
    ]:

        claims = (
            analysis
            .claims_to_verify[
                :settings
                .search_max_claims
            ]
        )

        if not claims:

            return (
                GroundedResearch(
                    overview=(
                        "No specific claims "
                        "were selected for "
                        "web verification."
                    ),

                    claims=[],

                    sources=[],
                ),
                "",
            )

        sources: list[
            ResearchSource
        ] = []

        seen_urls: set[str] = set()

        with DDGS() as ddgs:

            for claim in claims:

                try:
                    results = ddgs.text(
                        claim,

                        max_results=(
                            settings
                            .search_results_per_claim
                        ),
                    )

                except Exception:
                    results = []

                for result in (
                    results or []
                ):

                    url = str(
                        result.get(
                            "href"
                        )
                        or result.get(
                            "url"
                        )
                        or ""
                    ).strip()

                    if (
                        not url
                        or url
                        in seen_urls
                    ):
                        continue

                    seen_urls.add(
                        url
                    )

                    sources.append(
                        ResearchSource(
                            id=(
                                len(sources)
                                + 1
                            ),

                            title=str(
                                result.get(
                                    "title"
                                )
                                or url
                            ),

                            url=url,

                            snippet=str(
                                result.get(
                                    "body"
                                )
                                or result.get(
                                    "snippet"
                                )
                                or ""
                            ),
                        )
                    )

        if not sources:

            return (
                GroundedResearch(
                    overview=(
                        "Search returned no "
                        "usable public results "
                        "for the selected claims."
                    ),

                    claims=[],

                    sources=[],
                ),
                "",
            )

        evidence = json.dumps(
            [
                source.model_dump()
                for source
                in sources
            ],

            ensure_ascii=False,
        )

        claim_text = json.dumps(
            claims,
            ensure_ascii=False,
        )

        messages = [
            SystemMessage(
                content=(
                    "You are a cautious "
                    "fact-checking analyst. "
                    "Use only the supplied "
                    "search results. Never "
                    "invent source IDs or URLs. "
                    "A search snippet can be "
                    "incomplete, so use "
                    "'uncertain' when evidence "
                    "is not strong enough."
                )
            ),

            HumanMessage(
                content=f"""
Verify these claims from a video:

{claim_text}

Available sources, each with a fixed integer id:

{evidence}

For every claim, classify it as exactly one of:

confirmed
contradicted
uncertain
context-dependent

Use only source_ids that exist in the supplied
source list.

The overview should summarize the overall
verification outcome.
""".strip()
            ),
        ]

        draft, model_id = (
            self.llm
            .invoke_structured(
                "reasoning",
                messages,
                ResearchDraft,
            )
        )

        valid_ids = {
            source.id
            for source
            in sources
        }

        for item in (
            draft.claims
        ):

            item.source_ids = [
                source_id

                for source_id
                in item.source_ids

                if source_id
                in valid_ids
            ]

        return (
            GroundedResearch(
                overview=(
                    draft.overview
                ),

                claims=(
                    draft.claims
                ),

                sources=sources,
            ),
            model_id,
        )