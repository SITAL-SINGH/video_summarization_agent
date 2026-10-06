import base64
import math
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import imageio_ffmpeg

from yt_dlp import YoutubeDL

from backend.app.core.config import (
    settings,
)


@dataclass
class MediaSource:
    path: Path

    title: str

    source_name: str

    duration_seconds: float


@dataclass
class MediaSegment:
    index: int

    start_seconds: float

    end_seconds: float

    frame_data_urls: list[str]

    audio_base64: str | None


class MediaService:

    def __init__(
        self,
    ) -> None:

        self.ffmpeg = (
            imageio_ffmpeg
            .get_ffmpeg_exe()
        )

    def download_youtube(
        self,
        url: str,
        workdir: Path,
    ) -> MediaSource:

        output_template = str(
            workdir
            / "source.%(ext)s"
        )

        options = {
            "format": (
                "best[ext=mp4][height<=720]/"
                "best[height<=720]/"
                "best"
            ),

            "outtmpl":
                output_template,

            "noplaylist":
                True,

            "quiet":
                True,

            "no_warnings":
                True,
        }

        with YoutubeDL(
            options
        ) as ydl:

            info = (
                ydl.extract_info(
                    url,
                    download=True,
                )
            )

            path = Path(
                ydl.prepare_filename(
                    info
                )
            )

            title = str(
                info.get("title")
                or path.stem
            )

            duration = float(
                info.get("duration")
                or 0
            )

        if not path.exists():

            matches = list(
                workdir.glob(
                    "source.*"
                )
            )

            if not matches:
                raise RuntimeError(
                    "yt-dlp finished but "
                    "no video file was created."
                )

            path = matches[0]

        if duration <= 0:
            duration = (
                self.probe_duration(
                    path
                )
            )

        self._validate_duration(
            duration
        )

        return MediaSource(
            path=path,

            title=title,

            source_name=url,

            duration_seconds=duration,
        )

    def uploaded_source(
        self,
        path: Path,
        filename: str,
    ) -> MediaSource:

        duration = (
            self.probe_duration(
                path
            )
        )

        self._validate_duration(
            duration
        )

        return MediaSource(
            path=path,

            title=(
                Path(filename)
                .stem
            ),

            source_name=filename,

            duration_seconds=duration,
        )

    def _validate_duration(
        self,
        duration: float,
    ) -> None:

        if duration <= 0:
            raise ValueError(
                "Could not determine "
                "the video's duration."
            )

        if (
            duration
            > settings.max_video_minutes
            * 60
        ):
            raise ValueError(
                f"Video is "
                f"{duration / 60:.1f} minutes. "
                "Current MAX_VIDEO_MINUTES "
                f"is {settings.max_video_minutes}."
            )

    def probe_duration(
        self,
        path: Path,
    ) -> float:

        proc = subprocess.run(
            [
                self.ffmpeg,

                "-hide_banner",

                "-i",
                str(path),
            ],

            stdout=subprocess.DEVNULL,

            stderr=subprocess.PIPE,

            check=False,
        )

        stderr = proc.stderr.decode(
            "utf-8",
            errors="ignore",
        )

        match = re.search(
            (
                r"Duration:\s*"
                r"(\d+):"
                r"(\d+):"
                r"(\d+(?:\.\d+)?)"
            ),
            stderr,
        )

        if not match:
            return 0.0

        hours, minutes, seconds = (
            match.groups()
        )

        return (
            int(hours) * 3600
            + int(minutes) * 60
            + float(seconds)
        )

    def segment_windows(
        self,
        duration: float,
    ) -> list[
        tuple[float, float]
    ]:

        chunk = max(
            60,
            settings
            .video_chunk_seconds,
        )

        count = max(
            1,
            math.ceil(
                duration
                / chunk
            ),
        )

        return [
            (
                index * chunk,

                min(
                    duration,
                    (index + 1)
                    * chunk,
                ),
            )

            for index
            in range(count)
        ]

    def build_segment(
        self,
        source: MediaSource,
        index: int,
        start_seconds: float,
        end_seconds: float,
        include_images: bool,
        include_audio: bool,
    ) -> MediaSegment:

        frames = (
            self._extract_frames(
                source.path,
                start_seconds,
                end_seconds,
            )
            if include_images
            else []
        )

        audio = (
            self._extract_audio(
                source.path,
                start_seconds,
                end_seconds,
            )
            if include_audio
            else None
        )

        return MediaSegment(
            index=index,

            start_seconds=(
                start_seconds
            ),

            end_seconds=(
                end_seconds
            ),

            frame_data_urls=frames,

            audio_base64=audio,
        )

    def _extract_frames(
        self,
        path: Path,
        start: float,
        end: float,
    ) -> list[str]:

        count = max(
            1,
            settings
            .frames_per_chunk,
        )

        span = max(
            0.1,
            end - start,
        )

        offsets = [
            start
            + span
            * (
                (i + 1)
                / (count + 1)
            )

            for i
            in range(count)
        ]

        frames: list[str] = []

        for timestamp in offsets:

            proc = subprocess.run(
                [
                    self.ffmpeg,

                    "-loglevel",
                    "error",

                    "-ss",
                    f"{timestamp:.3f}",

                    "-i",
                    str(path),

                    "-frames:v",
                    "1",

                    "-vf",
                    (
                        "scale="
                        "'min(960,iw)':-2"
                    ),

                    "-q:v",
                    "5",

                    "-f",
                    "image2pipe",

                    "-vcodec",
                    "mjpeg",

                    "pipe:1",
                ],

                stdout=subprocess.PIPE,

                stderr=subprocess.PIPE,

                check=False,
            )

            if (
                proc.returncode == 0
                and proc.stdout
            ):

                encoded = (
                    base64
                    .b64encode(
                        proc.stdout
                    )
                    .decode(
                        "ascii"
                    )
                )

                frames.append(
                    "data:image/jpeg;base64,"
                    + encoded
                )

        return frames

    def _extract_audio(
        self,
        path: Path,
        start: float,
        end: float,
    ) -> str | None:

        duration = max(
            0.1,
            end - start,
        )

        proc = subprocess.run(
            [
                self.ffmpeg,

                "-loglevel",
                "error",

                "-ss",
                f"{start:.3f}",

                "-t",
                f"{duration:.3f}",

                "-i",
                str(path),

                "-vn",

                "-ac",
                "1",

                "-ar",
                "16000",

                "-b:a",
                (
                    f"{settings.audio_bitrate_kbps}"
                    "k"
                ),

                "-f",
                "mp3",

                "pipe:1",
            ],

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            check=False,
        )

        if (
            proc.returncode != 0
            or not proc.stdout
        ):
            return None

        return (
            base64
            .b64encode(
                proc.stdout
            )
            .decode(
                "ascii"
            )
        )