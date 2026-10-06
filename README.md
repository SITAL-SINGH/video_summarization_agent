# AI Video Summarizer

An internship-ready AI application that analyzes public YouTube videos or uploaded video files with Gemini,
optionally verifies important claims with Google Search grounding, optionally uses CrewAI agents to review the
briefing, and stores finished summaries in SQLite.

## Project structure

```text
ai-video-summarizer/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── summarize.py
│   │   │   └── history.py
│   │   ├── agents/
│   │   │   ├── video_analyst.py
│   │   │   ├── researcher.py
│   │   │   └── summarizer.py
│   │   ├── services/
│   │   │   ├── gemini_video.py
│   │   │   ├── gemini_search.py
│   │   │   ├── video_service.py
│   │   │   └── history_service.py
│   │   ├── schemas/
│   │   │   ├── request.py
│   │   │   └── response.py
│   │   ├── core/config.py
│   │   ├── db/database.py
│   │   └── utils/validators.py
│   ├── tests/
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── app.py
│   ├── components/
│   │   ├── input_form.py
│   │   └── summary_view.py
│   ├── utils/api_client.py
│   ├── requirements.txt
│   └── Dockerfile
├── docs/architecture.md
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Architecture

```text
Streamlit
   |
   v
FastAPI
   |
   v
VideoService
   |
   +-- Gemini video understanding
   +-- Gemini Google Search grounding (optional)
   +-- CrewAI agents (optional)
   +-- SQLite history
```

Gemini performs the actual video understanding. CrewAI receives the structured output afterwards; it does not
re-read the video. This keeps the system cheaper, easier to debug, and easier to explain.

## 1. Local setup

Python 3.12 is recommended.

```bash
python -m venv .venv
```

Activate it:

```bash
# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install backend and frontend dependencies:

```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

Copy the environment file:

```bash
# macOS/Linux
cp backend/.env.example backend/.env
```

On Windows, copy `backend/.env.example` to `backend/.env` manually.

Then set:

```env
GEMINI_API_KEY=your_real_key_here
```

## 2. Run FastAPI

From the project root:

```bash
uvicorn backend.app.main:app --reload --port 8000
```

Open API docs at:

```text
http://localhost:8000/docs
```

## 3. Run Streamlit

In a second terminal, from the same project root:

```bash
streamlit run frontend/app.py
```

Open:

```text
http://localhost:8501
```

## 4. Run tests

```bash
pytest backend/tests -q
```

The included tests do not call Gemini, so they can run without spending API credits.

## 5. Docker

Create `backend/.env` first, then:

```bash
docker compose up --build
```

Frontend: `http://localhost:8501`  
Backend docs: `http://localhost:8000/docs`

## API endpoints

- `GET /api/v1/health`
- `POST /api/v1/summarize`
- `GET /api/v1/history`
- `GET /api/v1/history/{id}`

## Recommended first test

For the first real API test, disable both Google Search verification and CrewAI polishing in the Streamlit UI.
Test a short public YouTube video first. Once Gemini video analysis works, enable grounding, then enable CrewAI.
This makes integration errors much easier to isolate.
