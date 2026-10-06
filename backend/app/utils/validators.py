from pathlib import Path
from urllib.parse import urlparse


ALLOWED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".webm",
    ".mpeg",
    ".mpg",
    ".m4v",
    ".mkv",
}


def is_youtube_url(
    url: str,
) -> bool:

    try:
        parsed = urlparse(
            url.strip()
        )

    except ValueError:
        return False

    host = (
        parsed.hostname
        or ""
    ).lower()

    return (
        parsed.scheme
        in {
            "http",
            "https",
        }
        and (
            host == "youtu.be"
            or host.endswith(
                "youtube.com"
            )
            or host.endswith(
                "youtube-nocookie.com"
            )
        )
    )


def validate_video_extension(
    filename: str,
) -> str:

    suffix = (
        Path(filename)
        .suffix
        .lower()
    )

    if (
        suffix
        not in ALLOWED_VIDEO_EXTENSIONS
    ):

        allowed = ", ".join(
            sorted(
                ALLOWED_VIDEO_EXTENSIONS
            )
        )

        raise ValueError(
            "Unsupported video extension. "
            f"Allowed: {allowed}"
        )

    return suffix