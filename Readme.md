# FocusOS

FocusOS is an adaptive AI focus and work-habit coach built as a stateful agent system.
It plans daily focus blocks, observes user behavior, evaluates its own decisions,
and improves over time using structured experiments and observability.

The system emphasizes agent evaluation, experimentation, and continuous improvement
using Opik, rather than static task planning or chat-based assistance.

## Tech Stack

- **Frontend:** Next.js 15, TypeScript, Tailwind CSS
- **Backend/Agent:** Python (FastAPI), Google Gemini 3 Flash
- **Database/State:** Convex
- **Observability:** Opik
- **Tooling:** Bun, uv

## Quick Start

### Prerequisites
- [Bun](https://bun.sh)
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- Python 3.11+

### 1. Setup Environment

Create `.env` in `agent/` with your API keys:

```bash
cp agent/.env.example agent/.env
# Edit agent/.env to add GEMINI_API_KEY (Required) and OPIK_API_KEY (Optional)
```

### 2. Initialize Dependencies

```bash
# Install root dependencies
bun install

# Install web dependencies
cd web && bun install

# Install agent dependencies
cd ../agent && uv venv && source .venv/bin/activate && uv pip install -e ".[dev]"
```

### 3. Initialize Convex (One-time)

You need to link the project to your Convex account:

```bash
cd web
npx convex dev
# Follow the login prompt. This generates web/.env.local
# You can stop it (Ctrl+C) once "convex dev is running" appears.
```

### 4. Run Everything

From the root directory:

```bash
bun run dev
```

This runs:
- **Agent API** on [http://localhost:8000](http://localhost:8000)
- **Web App** on [http://localhost:3000](http://localhost:3000)
- **Convex** sync service

## Architecture

- **`agent/`**: FastAPI service containing the "Brain".
    - `planner.py`: Generates focus plans using Gemini.
    - `evaluators.py`: LLM-as-judge scoring logic.
    - `strategies.py`: Configurable planning strategies.
- **`web/`**: Next.js frontend.
    - `convex/`: Backend logic (mutations/queries) and schema.
    - `app/`: UI pages.
    - `lib/agent.ts`: Bridge to the Python agent.

## Evaluation & Observability

FocusOS uses [Opik](https://comet.com/opik) to trace every agent decision.
To enable:
1. Get an API Key from Opik.
2. Add it to `agent/.env` as `OPIK_API_KEY`.
3. Run the app. All plans and evaluations will be logged.
