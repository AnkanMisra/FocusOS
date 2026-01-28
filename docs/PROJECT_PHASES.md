# FocusOS — Project Phases & Execution Plan

This document describes the full lifecycle of FocusOS, from problem framing
to post-hackathon expansion. The phases are intentionally ordered to prioritize
agent correctness, evaluation, and observability before UI polish or feature breadth.

FocusOS is developed as an **evaluation-first agent system**, not a UI-first product.

---

## Progress Overview

| Phase | Name | Status |
|-------|------|--------|
| 0 | Problem Framing & Scope Definition | COMPLETE |
| 1 | System & Agent Design | COMPLETE |
| 2 | Core Agent Implementation | COMPLETE |
| 3 | Evaluation & Observability Integration | COMPLETE |
| 4 | MVP Surface (UI + State Integration) | COMPLETE |
| 5 | Experimentation | COMPLETE |
| 6 | Adaptation & Optimization | NOT STARTED |
| 7 | Validation & Refinement | NOT STARTED |
| 8 | Finalization & Submission | NOT STARTED |
| 9 | Future Expansion | NOT STARTED |

---

## Phase 0: Problem Framing & Scope Definition [COMPLETE]

### Objective
Define a narrow, real-world problem with clear success criteria and measurable outcomes.

### Rationale
Most productivity tools fail because they generate plans without learning
whether those plans actually work. This phase ensures the problem is framed
around *follow-through*, not task generation.

### Activities
- Identified productivity follow-through as the core failure point
- Defined the user as an individual managing daily knowledge-work tasks
- Scoped the solution to single-day planning and execution
- Defined success metrics (completion rate, plan realism, drop-off)

### Outputs
- Clear problem statement
- Defined user workflow
- Explicit MVP boundaries

---

## Phase 1: System & Agent Design [COMPLETE]

### Objective
Design a stateful, goal-driven agent with explicit evaluation and adaptation loops.

### Rationale
A well-defined agent loop prevents the system from degrading into a chatbot.
Evaluation must be designed *before* implementation.

### Activities
- Defined agent loop: Plan → Act → Observe → Evaluate → Adapt
- Designed agent state (goal, time, energy, historical performance)
- Defined evaluation dimensions and behavioral metrics
- Designed experiment variables and strategy identifiers

### Outputs
- Agent design specification (`docs/agent_design.md`)
- System architecture (`docs/architecture.md`)
- Evaluation framework (`docs/evaluation.md`)
- Data model (`docs/data_model.md`)

---

## Phase 2: Core Agent Implementation [COMPLETE]

### Objective
Implement the planning agent as an independent, runnable system.

### Rationale
The agent must exist and function before UI, persistence, or optimization.
This phase proves the system can generate structured plans deterministically.

### Implementation Details

#### Tech Stack
- **Runtime**: Python 3.11+ with `uv` package manager
- **Framework**: FastAPI 0.128+
- **LLM (Plan Generation)**: Gemini 3 Flash Preview (`gemini-3-flash-preview`)
- **LLM (Evaluation)**: Gemini 3 Pro Preview (`gemini-3-pro-preview`)
- **SDK**: `google-genai` (new SDK, replaces deprecated `google-generativeai`)
- **Observability**: Opik (optional, enabled when `OPIK_API_KEY` is set)
- **Testing**: pytest with 18 passing tests

#### Project Structure
```
agent/
├── pyproject.toml           # uv-compatible dependencies
├── README.md                # Setup instructions
├── .env.example             # Environment template
├── src/agent/
│   ├── __init__.py
│   ├── main.py              # FastAPI app (4 endpoints)
│   ├── models.py            # Pydantic schemas
│   ├── planner.py           # Gemini integration + Opik tracing
│   ├── prompts.py           # Prompt templates (v1)
│   └── strategies.py        # 3 strategy configurations
└── tests/
    └── test_planner.py      # Unit tests
```

#### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/strategies` | List available strategies |
| POST | `/agent/plan` | Generate focus plan |
| POST | `/agent/feedback` | Submit feedback (stub) |

#### Strategies Implemented
1. `empathetic_25_light` - Warm tone, 25-min blocks, conservative scheduling
2. `strict_25_aggressive` - Direct tone, 25-min blocks, tight scheduling
3. `empathetic_40_light` - Warm tone, 40-min blocks, conservative scheduling

#### Request/Response Format
```json
// Request
{
  "goal_text": "Finish DSA revision and write README",
  "available_minutes": 120,
  "energy_level": "high",
  "strategy_id": "empathetic_25_light"  // optional
}

// Response
{
  "strategy_id": "empathetic_25_light",
  "prompt_version": "v1",
  "blocks": [
    {"order": 1, "duration_min": 25, "task": "...", "nudge": "..."},
    {"order": 2, "duration_min": 25, "task": "...", "nudge": "..."}
  ],
  "total_minutes": 75
}
```

### Run Commands
```bash
cd agent
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
cp .env.example .env  # Add GEMINI_API_KEY
uvicorn agent.main:app --reload
# Open http://localhost:8000/docs for Swagger UI
```

### Outputs
- Runnable FastAPI agent service
- Gemini-powered focus plan generation
- Strategy-tagged runs with prompt versioning
- Opik tracing integration (optional)
- Interactive API docs at `/docs`

---

## Phase 3: Evaluation & Observability Integration [COMPLETE]

### Objective
Instrument the agent for traceability, evaluation, and debugging.

### Rationale
Without observability, agent behavior cannot be trusted, compared, or improved.
Evaluation is treated as a first-class system component.

### Activities Completed
- Implemented LLM-as-judge evaluators (`agent/evaluators.py`):
  - Task clarity (0-10)
  - Workload realism (0-10)
  - Goal alignment (0-10)
  - Motivation quality (0-10)
- Integrated evaluation into `/agent/plan` via `?evaluate=true` query param
- Added standalone `/agent/evaluate` endpoint
- Connected Opik logging for evaluation scores (as trace metadata)
- Verified with unit tests (`tests/test_evaluators.py`)

### Outputs
- Full agent traces with evaluation metadata in Opik
- Evaluation score datasets available via API
- Observability integration verified

---

## Phase 4: MVP Surface (UI + State Integration) [COMPLETE]

### Objective
Expose the agent through a minimal user-facing interface.

### Rationale
UI is built only after the agent and evaluation loop are stable, ensuring
the frontend consumes a validated system rather than shaping it.

### Activities Completed
- Built Next.js (App Router) + Tailwind CSS frontend (`web/`)
- Implemented Convex schema and backend logic (`web/convex/`)
  - `createGoal`, `savePlan`, `updateBlockStatus`, `getLatestGoal`
- Integrated Agent API in frontend (`web/lib/agent.ts`)
- Created main UI flow (`web/app/page.tsx`):
  - Goal input form -> Loading -> Plan display
  - Interactive checkboxes for task completion
  - Evaluation score visualization

### Outputs
- Functional end-to-end MVP accessible at `http://localhost:3000`
- Persisted goals, plans, and feedback in Convex database
- Real-time updates and optimistic UI for task completion

---

## Phase 5: Experimentation [COMPLETE]

### Objective
Systematically compare agent strategies under controlled conditions.

### Rationale
Improvement must be proven through experiments, not anecdotal behavior.

### Implementation Details

#### Tech Stack
- **Experiment Runner**: Rust CLI with parallel HTTP execution
- **Dependencies**: tokio, reqwest, clap, serde, indicatif, statrs

#### Project Structure
```
experiments/
├── Cargo.toml           # Rust dependencies
├── src/
│   ├── main.rs          # CLI entrypoint with clap
│   ├── client.rs        # HTTP client for Python agent API
│   ├── datasets.rs      # 12 built-in test goals
│   ├── runner.rs        # Parallel experiment execution
│   └── results.rs       # Statistics and JSON output
└── results/             # JSON output directory
```

#### CLI Usage
```bash
# Build
cd experiments && cargo build --release

# Run experiment (requires agent on localhost:8000)
./target/release/run-experiment --name baseline

# Options
./target/release/run-experiment \
  --name my_experiment \
  --strategies empathetic_25_light,strict_25_aggressive \
  --concurrency 5 \
  --verbose
```

#### Dataset (12 Goals)
- **Time Coverage**: Short (30-60min), Medium (90-120min), Long (180-240min)
- **Energy Levels**: Low, Medium, High
- **Work Types**: Technical, Creative, Administrative, Learning
- **Complexity**: Single-focus and multi-task goals

#### Evaluation Dimensions
| Dimension | Description |
|-----------|-------------|
| Task Clarity | Are tasks specific and actionable? |
| Workload Realism | Is workload achievable in time? |
| Goal Alignment | Does plan address stated goal? |
| Motivation Quality | Are nudges helpful? |

### Outputs
- Rust CLI tool for running experiments
- 12-goal built-in test dataset
- Parallel execution with progress bars
- JSON results with per-strategy statistics
- Dimension-by-dimension winner analysis

---

## Phase 6: Adaptation & Optimization [NOT STARTED]

### Objective
Use evaluation results to improve agent behavior over time.

### Rationale
Adaptation is meaningless without reliable evaluation data.
This phase demonstrates learning, not just experimentation.

### Planned Activities
- Implement score-weighted strategy selection
- Deprecate consistently underperforming strategies
- Promote high-performing variants
- Validate improvements across multiple runs

### Expected Outputs
- Improved completion rates
- Upward evaluation score trends
- Demonstrable agent learning

---

## Phase 7: Validation & Refinement [NOT STARTED]

### Objective
Validate real-world usefulness and system robustness.

### Rationale
A system can score well internally but fail users.
This phase ensures practical relevance.

### Planned Activities
- Test with real users
- Analyze plan abandonment and drop-offs
- Refine prompts, heuristics, and defaults
- Improve failure handling and edge cases

### Expected Outputs
- Qualitative user feedback
- Stability and reliability improvements
- Refined agent configurations

---

## Phase 8: Finalization & Submission [NOT STARTED]

### Objective
Prepare the system for judging and demonstration.

### Rationale
Judges evaluate clarity, not raw complexity.
This phase focuses on presentation and proof.

### Planned Activities
- Feature freeze
- Documentation finalization
- Dashboard and experiment review
- Submission content preparation

### Expected Outputs
- Final build
- Complete documentation set
- Submission-ready materials

---

## Phase 9: Future Expansion (Post-Hackathon) [NOT STARTED]

### Objective
Outline scalable growth beyond the hackathon.

### Planned Activities
- Multi-day planning horizons
- Cross-user learning
- Personalized evaluation weighting
- Deeper automation and optimization

### Expected Outputs
- Product roadmap
- Technical extension plan

---

## Summary

FocusOS follows an **agent-first, evaluation-driven development process**
where observability and experimentation precede UI expansion.
Each phase builds on measurable agent behavior, ensuring continuous,
data-driven improvement rather than static functionality.

### Current Status
- **Phases 0-5 Complete**: Full MVP + Experimentation tooling ready
- **Next Up**: Phase 6 (Adaptation & Optimization) to improve agent behavior based on experiment results
