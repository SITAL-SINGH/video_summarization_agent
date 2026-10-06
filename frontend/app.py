import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


if (
    str(PROJECT_ROOT)
    not in sys.path
):

    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from frontend.components.input_form import (  # noqa: E402
    render_input_form,
)

from frontend.components.summary_view import (  # noqa: E402
    render_summary,
)

from frontend.utils.api_client import (  # noqa: E402
    BACKEND_URL,
    get_configured_models,
    get_health,
    summarize_video,
)


st.set_page_config(
    page_title=(
        "AI Video Summarizer"
    ),

    page_icon="🎬",

    layout="wide",
)


st.title(
    "🎬 AI Video Summarizer"
)


st.write(
    "Model-agnostic video summarization "
    "using OpenRouter + LangChain. "
    "You can swap the video, reasoning, "
    "or final-summary model from `.env`."
)


with st.sidebar:

    st.header(
        "System"
    )

    health = (
        get_health()
    )

    if health:

        st.success(
            "Backend connected"
        )

        if not health.get(
            "openrouter_key_configured"
        ):

            st.error(
                "OPENROUTER_API_KEY "
                "is missing in the "
                "root .env file."
            )

        st.caption(
            f"API: {BACKEND_URL}"
        )

        models = (
            get_configured_models()
        )

        if models:

            with st.expander(
                "Configured model capabilities"
            ):

                st.json(
                    models
                )

    else:

        st.error(
            "Backend is not reachable. "
            "Start FastAPI on port 8000."
        )


form = (
    render_input_form()
)


if st.button(
    "Summarize video",

    type="primary",

    use_container_width=True,
):

    youtube_url = (
        form[
            "youtube_url"
        ]
        .strip()
    )

    uploaded_file = (
        form[
            "uploaded_file"
        ]
    )

    has_url = bool(
        youtube_url
    )

    has_file = (
        uploaded_file
        is not None
    )

    if (
        has_url
        == has_file
    ):

        st.error(
            "Use exactly one input: "
            "either a YouTube URL "
            "or an uploaded video."
        )

    elif not health:

        st.error(
            "The FastAPI backend "
            "is not running."
        )

    else:

        try:

            with st.status(
                "Processing video…",

                expanded=True,
            ) as status:

                st.write(
                    "1. Downloading/normalizing "
                    "the media locally."
                )

                st.write(
                    "2. Splitting into time chunks "
                    "and extracting compressed "
                    "audio + sampled frames."
                )

                st.write(
                    "3. Running multimodal segment "
                    "analysis through the configured "
                    "OpenRouter video model."
                )

                st.write(
                    "4. Combining segment analyses "
                    "with the configured summary model."
                )

                if form[
                    "enable_research"
                ]:

                    st.write(
                        "5. Searching public web "
                        "results and verifying "
                        "selected claims."
                    )

                result = (
                    summarize_video(
                        video_url=(
                            youtube_url
                            if has_url
                            else None
                        ),

                        uploaded_file=(
                            uploaded_file
                            if has_file
                            else None
                        ),

                        summary_length=(
                            form[
                                "summary_length"
                            ]
                        ),

                        custom_prompt=(
                            form[
                                "custom_prompt"
                            ]
                        ),

                        enable_research=(
                            form[
                                "enable_research"
                            ]
                        ),
                    )
                )

                status.update(
                    label="Finished",

                    state="complete",

                    expanded=False,
                )

            st.session_state[
                "last_result"
            ] = result

        except Exception as exc:

            st.error(
                "Summarization failed: "
                f"{exc}"
            )


if (
    "last_result"
    in st.session_state
):

    st.divider()

    render_summary(
        st.session_state[
            "last_result"
        ]
    )