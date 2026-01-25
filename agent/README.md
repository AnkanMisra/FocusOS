# FocusOS Agent Service

FastAPI-based planning agent for FocusOS.

## Setup

```bash
cd agent
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Configuration

Copy `.env.example` to `.env` and set your `GEMINI_API_KEY`.

## Run

```bash
uvicorn agent.main:app --reload
```

## Test

```bash
pytest
```
