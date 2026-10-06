from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "AI Video Summarizer"
    app_version: str = "2.0.0"

    openrouter_api_key: str = ""

    openrouter_app_name: str = (
        "AI Video Summarizer"
    )

    openrouter_app_url: str = (
        "http://localhost:8501"
    )

    video_models: str = (
        "nvidia/"
        "nemotron-3-nano-omni-30b-a3b-reasoning:free"
    )

    reasoning_models: str = (
        "nvidia/"
        "nemotron-3-ultra-550b-a55b:free,"
        "inclusionai/ling-3.1-flash"
    )

    summary_models: str = (
        "google/gemma-4-26b-a4b-it:free,"
        "google/gemma-4-31b-it:free"
    )

    model_temperature: float = 0.1

    model_max_retries: int = 2

    video_chunk_seconds: int = 480

    frames_per_chunk: int = 4

    audio_bitrate_kbps: int = 32

    max_video_minutes: int = 90

    max_upload_mb: int = 500

    search_max_claims: int = 5

    search_results_per_claim: int = 3

    database_path: str = (
        "data/summaries.db"
    )

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",

        env_file_encoding="utf-8",

        case_sensitive=False,

        extra="ignore",
    )

    @staticmethod
    def _csv(
        value: str,
    ) -> list[str]:

        return [
            item.strip()
            for item
            in value.split(",")
            if item.strip()
        ]

    @property
    def video_model_list(
        self,
    ) -> list[str]:

        return self._csv(
            self.video_models
        )

    @property
    def reasoning_model_list(
        self,
    ) -> list[str]:

        return self._csv(
            self.reasoning_models
        )

    @property
    def summary_model_list(
        self,
    ) -> list[str]:

        return self._csv(
            self.summary_models
        )

    @property
    def resolved_database_path(
        self,
    ) -> Path:

        path = Path(
            self.database_path
        )

        if not path.is_absolute():
            path = (
                PROJECT_ROOT
                / path
            )

        return path

    def require_openrouter_key(
        self,
    ) -> str:

        key = (
            self.openrouter_api_key
            .strip()
        )

        if not key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is missing. "
                "Copy .env.example to .env "
                "and add your key."
            )

        return key


@lru_cache
def get_settings(
) -> Settings:

    return Settings()


settings = get_settings()