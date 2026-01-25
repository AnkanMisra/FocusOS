# AGENTS.md

## Tech Stack
- Frontend: Next.js + TypeScript
- Agent Service: Python (FastAPI)
- Workers: Rust
- Database: Convex
- LLM: Gemini 3 Flash
- Observability: Opik

## Build/Test Commands
- Agent (Python): `cd agent && uv pip install -e ".[dev]"` to install
  - Run: `uvicorn agent.main:app --reload`
  - Test all: `pytest`
  - Test single: `pytest tests/test_planner.py::TestStrategies::test_all_strategies_exist`
  - Lint: `ruff check src tests` (auto-fix: `ruff check --fix src tests`)
- Frontend: `bun dev`, `bun run build`, `bun test`, `bun test path/to/file.test.ts`

## Code Style
- TypeScript: strict mode, explicit return types, prefer `const`, named exports
- Python: type hints required, snake_case, Google-style docstrings, ruff for linting
- Rust: clippy for lints, snake_case functions, PascalCase types
- Imports: group stdlib, external, internal; sort alphabetically
- Error handling: explicit error types, no silent failures, log all agent decisions
- All agent traces must be instrumented via Opik for observability
