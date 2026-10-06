import json
from typing import Any

import streamlit as st


def render_summary(
    result: dict[str, Any],
) -> None:

    analysis = (
        result["analysis"]
    )

    st.success(
        "Summary complete · "
        f"History ID #{result.get('id')}"
    )

    for warning in (
        result.get(
            "warnings",
            [],
        )
    ):
        st.warning(
            warning
        )

    st.header(
        analysis["title"]
    )

    st.caption(
        f"Source: {result['source_title']} · "
        f"Duration: "
        f"{result['duration_seconds'] / 60:.1f} min · "
        f"Language: "
        f"{analysis['detected_language']}"
    )

    (
        overview_tab,
        chapters_tab,
        actions_tab,
        research_tab,
        models_tab,
        raw_tab,
    ) = st.tabs(
        [
            "Overview",
            "Chapters",
            "Action items",
            "Research",
            "Models",
            "Raw JSON",
        ]
    )

    with overview_tab:

        st.subheader(
            "Executive overview"
        )

        st.write(
            analysis["overview"]
        )

        st.subheader(
            "Detailed summary"
        )

        st.markdown(
            analysis["summary"]
        )

        st.subheader(
            "Key points"
        )

        for point in (
            analysis.get(
                "key_points",
                [],
            )
        ):
            st.markdown(
                f"- {point}"
            )

        if analysis.get(
            "entities"
        ):

            st.subheader(
                "Important entities"
            )

            st.write(
                ", ".join(
                    analysis[
                        "entities"
                    ]
                )
            )

        if analysis.get(
            "tags"
        ):

            st.subheader(
                "Tags"
            )

            st.write(
                " · ".join(
                    f"`{tag}`"

                    for tag
                    in analysis["tags"]
                )
            )

    with chapters_tab:

        chapters = (
            analysis.get(
                "chapters",
                [],
            )
        )

        if not chapters:

            st.info(
                "No reliable chapters "
                "were extracted."
            )

        for chapter in chapters:

            st.markdown(
                "### "
                f"{chapter['timestamp']} "
                "— "
                f"{chapter['title']}"
            )

            st.write(
                chapter[
                    "summary"
                ]
            )

    with actions_tab:

        actions = (
            analysis.get(
                "action_items",
                [],
            )
        )

        if actions:

            for (
                index,
                action,
            ) in enumerate(
                actions,
                start=1,
            ):

                st.markdown(
                    f"{index}. {action}"
                )

        else:

            st.info(
                "No meaningful action "
                "items were found."
            )

        claims = (
            analysis.get(
                "claims_to_verify",
                [],
            )
        )

        if claims:

            st.subheader(
                "Claims selected "
                "for verification"
            )

            for claim in claims:

                st.markdown(
                    f"- {claim}"
                )

    with research_tab:

        research = (
            result.get(
                "research"
            )
        )

        if not research:

            st.info(
                "Research was disabled "
                "or unavailable."
            )

        else:

            st.write(
                research.get(
                    "overview",
                    "",
                )
            )

            for item in (
                research.get(
                    "claims",
                    [],
                )
            ):

                st.markdown(
                    "#### "
                    f"{item['status'].title()}: "
                    f"{item['claim']}"
                )

                st.write(
                    item[
                        "explanation"
                    ]
                )

                if item.get(
                    "source_ids"
                ):

                    st.caption(
                        "Sources: "
                        + ", ".join(
                            f"#{x}"
                            for x
                            in item[
                                "source_ids"
                            ]
                        )
                    )

            if research.get(
                "sources"
            ):

                st.subheader(
                    "Sources"
                )

                for source in (
                    research[
                        "sources"
                    ]
                ):

                    st.markdown(
                        f"**#{source['id']}** "
                        f"[{source['title']}]"
                        f"({source['url']})"
                    )

                    if source.get(
                        "snippet"
                    ):
                        st.caption(
                            source[
                                "snippet"
                            ]
                        )

    with models_tab:

        st.json(
            result.get(
                "models",
                {},
            )
        )

        st.caption(
            "Change model slugs in the "
            "root .env; application code "
            "does not change."
        )

    with raw_tab:

        st.json(
            result
        )

        st.download_button(
            "Download JSON",

            data=json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            ),

            file_name=(
                "video_summary_"
                f"{result.get('id', 'result')}"
                ".json"
            ),

            mime="application/json",
        )