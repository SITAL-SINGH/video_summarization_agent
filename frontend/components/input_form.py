from typing import Any

import streamlit as st


def render_input_form(
) -> dict[str, Any]:

    (
        youtube_tab,
        upload_tab,
    ) = st.tabs(
        [
            "YouTube URL",
            "Upload video",
        ]
    )

    with youtube_tab:

        youtube_url = (
            st.text_input(
                "Public YouTube URL",

                placeholder=(
                    "https://www.youtube.com/"
                    "watch?v=..."
                ),
            )
        )

    with upload_tab:

        uploaded_file = (
            st.file_uploader(
                "Upload video",

                type=[
                    "mp4",
                    "mov",
                    "webm",
                    "mpeg",
                    "mpg",
                    "m4v",
                    "mkv",
                ],
            )
        )

    left, right = (
        st.columns(2)
    )

    with left:

        summary_length = (
            st.selectbox(
                "Summary detail",

                options=[
                    "short",
                    "standard",
                    "detailed",
                ],

                index=1,
            )
        )

        enable_research = (
            st.checkbox(
                "Verify selected claims "
                "with web search",

                value=True,
            )
        )

    with right:

        custom_prompt = (
            st.text_area(
                "Optional custom instruction",

                placeholder=(
                    "Example: Focus on "
                    "concepts useful for "
                    "exam revision."
                ),

                max_chars=4000,
            )
        )

    return {
        "youtube_url":
            youtube_url,

        "uploaded_file":
            uploaded_file,

        "summary_length":
            summary_length,

        "enable_research":
            enable_research,

        "custom_prompt":
            custom_prompt,
    }