import shutil
import tempfile
from pathlib import Path

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from starlette.concurrency import (
    run_in_threadpool,
)

from backend.app.core.config import (
    settings,
)

from backend.app.schemas.request import (
    SummaryLength,
)

from backend.app.schemas.response import (
    SummaryResponse,
)

from backend.app.services.pipeline import (
    VideoPipeline,
)

from backend.app.utils.validators import (
    is_youtube_url,
    validate_video_extension,
)


router = APIRouter(
    prefix="/api/v1",

    tags=[
        "summarization"
    ],
)


pipeline = VideoPipeline()


@router.post(
    "/summarize",

    response_model=(
        SummaryResponse
    ),
)
async def summarize_video(

    video_url: str | None = Form(
        default=None
    ),

    summary_length: str = Form(
        default="standard"
    ),

    custom_prompt: str | None = Form(
        default=None
    ),

    enable_research: bool = Form(
        default=True
    ),

    video_file: (
        UploadFile
        | None
    ) = File(
        default=None
    ),

) -> SummaryResponse:

    video_url = (
        (video_url or "")
        .strip()
        or None
    )

    if (
        bool(video_url)
        == bool(video_file)
    ):
        raise HTTPException(
            status_code=400,

            detail=(
                "Provide exactly one input: "
                "a YouTube URL or a video file."
            ),
        )

    try:
        length = SummaryLength(
            summary_length
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,

            detail=(
                "summary_length must be "
                "short, standard, or detailed."
            ),

        ) from exc

    if (
        custom_prompt
        and len(custom_prompt) > 4000
    ):
        raise HTTPException(
            status_code=400,

            detail=(
                "custom_prompt is too long "
                "(max 4000 chars)."
            ),
        )

    if video_url:

        if not is_youtube_url(
            video_url
        ):
            raise HTTPException(
                status_code=400,

                detail=(
                    "URL input currently "
                    "supports public "
                    "YouTube URLs only."
                ),
            )

        try:
            return (
                await run_in_threadpool(
                    pipeline
                    .summarize_youtube,

                    video_url,

                    length,

                    custom_prompt,

                    enable_research,
                )
            )

        except Exception as exc:

            raise HTTPException(
                status_code=500,
                detail=str(exc),

            ) from exc

    assert (
        video_file
        is not None
    )

    filename = (
        video_file.filename
        or "uploaded_video.mp4"
    )

    try:
        suffix = (
            validate_video_extension(
                filename
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),

        ) from exc

    temp_path: (
        Path
        | None
    ) = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as tmp:

            shutil.copyfileobj(
                video_file.file,
                tmp,
            )

            temp_path = Path(
                tmp.name
            )

        size_mb = (
            temp_path
            .stat()
            .st_size
            / (
                1024
                * 1024
            )
        )

        if (
            size_mb
            > settings.max_upload_mb
        ):
            raise HTTPException(
                status_code=413,

                detail=(
                    f"File is {size_mb:.1f} MB; "
                    "max allowed is "
                    f"{settings.max_upload_mb} MB."
                ),
            )

        return (
            await run_in_threadpool(
                pipeline
                .summarize_upload,

                temp_path,

                filename,

                length,

                custom_prompt,

                enable_research,
            )
        )

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),

        ) from exc

    finally:

        if (
            temp_path
            and temp_path.exists()
        ):
            temp_path.unlink(
                missing_ok=True
            )

        await video_file.close()