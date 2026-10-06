# Architecture

## Request flow

```text
Streamlit UI
    |
    v
FastAPI API
    |
    v
VideoService (orchestration)
    |
    +--> GeminiVideoService
    |       - YouTube URL or uploaded file
    |       - audio + visual understanding
    |       - structured VideoAnalysis
    |
    +--> GeminiSearchService (optional)
    |       - Google Search grounding
    |       - current claim verification
    |       - citations
    |
    +--> CrewAI agents (optional)
    |       - Video Analysis Reviewer
    |       - Grounded Research Reviewer
    |       - Video Briefing Editor
    |
    +--> HistoryService
            - SQLite persistence
```

## Responsibilities

- `api/`: HTTP validation and transport only.
- `agents/`: CrewAI role definitions and behavioral instructions.
- `services/`: Gemini integrations and application orchestration.
- `schemas/`: typed request/response contracts.
- `core/`: configuration.
- `db/`: low-level database connection and initialization.
- `utils/`: reusable validation helpers.
- `frontend/components/`: Streamlit presentation components.
- `frontend/utils/`: API client code.

## Important design rule

Gemini reads the actual video. CrewAI works on the structured analysis after video understanding.
This avoids paying multiple agents to process the same video and keeps the video layer independently testable.

Grounded web research is also kept separate from the video's own content so external facts are not
misrepresented as statements made in the source video.
