import os
from typing import Any

import requests


BACKEND_URL = (
    os.getenv(
        "STREAMLIT_BACKEND_URL",
        "http://localhost:8000",
    )
    .rstrip("/")
)


def get_health(
    timeout: int = 5,
) -> (
    dict[str, Any]
    | None
):

    try:
        response = requests.get(
            (
                f"{BACKEND_URL}"
                "/api/v1/health"
            ),

            timeout=timeout,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException:
        return None


def get_configured_models(
    timeout: int = 10,
) -> (
    dict[str, Any]
    | None
):

    try:
        response = requests.get(
            (
                f"{BACKEND_URL}"
                "/api/v1/models/configured"
            ),

            timeout=timeout,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException:
        return None


def summarize_video(
    *,
    video_url: str | None,
    uploaded_file: Any,
    summary_length: str,
    custom_prompt: str,
    enable_research: bool,
) -> dict[str, Any]:

    data = {
        "summary_length":
            summary_length,

        "custom_prompt":
            custom_prompt,

        "enable_research":
            str(
                enable_research
            ).lower(),
    }

    files = None

    if video_url:

        data[
            "video_url"
        ] = video_url

    elif (
        uploaded_file
        is not None
    ):

        files = {
            "video_file": (
                uploaded_file.name,

                uploaded_file
                .getvalue(),

                uploaded_file.type
                or (
                    "application/"
                    "octet-stream"
                ),
            )
        }

    response = requests.post(
        (
            f"{BACKEND_URL}"
            "/api/v1/summarize"
        ),

        data=data,

        files=files,

        timeout=3600,
    )

    if not response.ok:

        try:
            detail = (
                response
                .json()
                .get(
                    "detail",
                    response.text,
                )
            )

        except ValueError:
            detail = response.text

        raise RuntimeError(
            detail
        )

    return response.json()