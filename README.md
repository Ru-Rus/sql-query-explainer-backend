# AI SQL Query Explainer — Backend

A FastAPI backend that validates SQL queries and returns AI-powered analysis via Google Gemini.

## Tech Stack

- **Python 3.13**
- **FastAPI** — API framework
- **Uvicorn** — ASGI server
- **Google Gemini** (`google-genai`, model `gemini-3.8-flash`) — AI analysis
- **slowapi** — rate limiting (10 requests/day per IP, file-backed persistent storage)
- **python-dotenv** — env var loading

## Endpoints

### `POST /api/explain`
Accepts a SQL query and returns structured analysis.

Request:
```json
{ "query": "SELECT * FROM Orders WHERE Status = 'Pending';" }
```

Response:
```json
{
  "explanation": "...",
  "performance_issues": ["..."],
  "erd_description": "...",
  "optimizations": ["..."]
}
```

Errors:
- `400` — failed SQL validation (no keyword, multi-statement, too long)
- `429` — rate limit exceeded (10/day per IP)
- `502` — Gemini call failed or returned invalid JSON

### `GET /health`
Returns `{"status": "ok"}`.

### `GET /`
Returns API running confirmation.

## Project Structure

## Setup

```bash
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in your GEMINI_API_KEY in .env
```

## Running

```bash
uvicorn app.main:app --reload --port 8000
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Gemini API key from https://aistudio.google.com/ |
| `ALLOWED_ORIGINS` | No | Comma-separated frontend URLs. Defaults to `http://localhost:5173` |

## Running Tests

```bash
python -m pytest -v