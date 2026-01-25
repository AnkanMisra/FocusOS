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
| 3 | Evaluation & Observability Integration | NOT STARTED |
| 4 | MVP Surface (UI + State Integration) | NOT STARTED |
| 5 | Experimentation | NOT STARTED |
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
- **LLM**: Gemini 3 Flash Preview (`gemini-3-flash-preview`)
- **SDK**: `google-genai` (new SDK, replaces deprecated `google-generativeai`)
- **Observability**: Opik (optional, enabled when `OPIK_API_KEY` is set)
- **Testing**: pytest with 13 passing tests

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

## Phase 3: Evaluation & Observability Integration [NOT STARTED]

### Objective
Instrument the agent for traceability, evaluation, and debugging.

### Rationale
Without observability, agent behavior cannot be trusted, compared, or improved.
Evaluation is treated as a first-class system component.

### Planned Activities
- Implement LLM-as-judge evaluators for:
  - Task clarity (0-10)
  - Workload realism (0-10)
  - Goal alignment (0-10)
  - Motivation quality (0-10)
- Log behavioral metrics (completion, skips, abandonment)
- Connect evaluations to strategy identifiers
- Build Opik experiment dashboards

### Expected Outputs
- Full agent traces in Opik
- Evaluation score datasets
- Observability dashboards

---

## Phase 4: MVP Surface (UI + State Integration) [NOT STARTED]

### Objective
Expose the agent through a minimal user-facing interface.

### Rationale
UI is built only after the agent and evaluation loop are stable, ensuring
the frontend consumes a validated system rather than shaping it.

### Planned Activities
- Build goal input and focus plan UI using Next.js + TypeScript + Bun
- Integrate Convex for user state, goals, and feedback storage
- Connect UI → agent → evaluation pipeline end-to-end
- Implement start/complete/skip interactions

### Expected Outputs
- Functional end-to-end MVP
- Persisted feedback and experiment data
- Real user interaction signals

---

## Phase 5: Experimentation [NOT STARTED]

### Objective
Systematically compare agent strategies under controlled conditions.

### Rationale
Improvement must be proven through experiments, not anecdotal behavior.

### Planned Activities
- Define controlled variables (coaching tone, block length, plan density)
- Fix inputs for fair comparisons
- Run Opik experiments across strategies
- Analyze evaluation trends and behavioral deltas

### Expected Outputs
- Strategy performance comparisons
- Identified failure modes
- Evidence of superior strategies

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
- **Phases 0-2 Complete**: Core agent service is live and generating focus plans
- **Next Up**: Phase 3 (Evaluation & Observability) to add LLM-as-judge scoring
