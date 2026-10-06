from contextlib import (
    asynccontextmanager,
)

from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from backend.app.api.history import (
    router as history_router,
)

from backend.app.api.models import (
    router as models_router,
)

from backend.app.api.summarize import (
    router as summarize_router,
)

from backend.app.core.config import (
    settings,
)

from backend.app.db.database import (
    init_db,
)


@asynccontextmanager
async def lifespan(
    _: FastAPI,
):

    init_db()

    yield


app = FastAPI(
    title=settings.app_name,

    version=settings.app_version,

    description=(
        "Model-agnostic AI video "
        "summarizer using "
        "OpenRouter + LangChain."
    ),

    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
)


app.include_router(
    summarize_router
)

app.include_router(
    history_router
)

app.include_router(
    models_router
)


@app.get("/")
def root() -> dict:

    return {
        "message":
            settings.app_name,

        "docs":
            "/docs",

        "health":
            "/api/v1/health",
    }


@app.get(
    "/api/v1/health",

    tags=[
        "system"
    ],
)
def health() -> dict:

    return {
        "status":
            "ok",

        "app":
            settings.app_name,

        "version":
            settings.app_version,

        "openrouter_key_configured":
            bool(
                settings
                .openrouter_api_key
                .strip()
            ),

        "video_models":
            settings
            .video_model_list,

        "reasoning_models":
            settings
            .reasoning_model_list,

        "summary_models":
            settings
            .summary_model_list,
    }