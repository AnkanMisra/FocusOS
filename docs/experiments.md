# FocusOS Experiment Design

FocusOS runs controlled experiments on agent behavior to systematically compare strategies.

## Quick Start

```bash
# Build the experiment runner (from project root)
cd experiments && cargo build --release

# Run experiment (requires agent running on localhost:8000)
./target/release/run-experiment --name baseline

# With custom options
./target/release/run-experiment \
  --name my_experiment \
  --strategies empathetic_25_light,strict_25_aggressive \
  --concurrency 5 \
  --verbose
```

## CLI Options

| Flag | Description | Default |
|------|-------------|---------|
| `-n, --name` | Experiment name | `experiment` |
| `-u, --url` | Agent API URL | `http://localhost:8000` |
| `-s, --strategies` | Comma-separated strategy IDs | All available |
| `-d, --dataset` | Custom goals JSON file | Built-in 12 goals |
| `-o, --output` | Output directory | `results/` |
| `-c, --concurrency` | Max parallel requests | `3` |
| `--verbose` | Print detailed results | `false` |

## Variable Dimensions

Each strategy varies along these dimensions:

| Dimension | Options | Description |
|-----------|---------|-------------|
| Coaching tone | `strict`, `empathetic` | Direct vs warm/encouraging |
| Focus block length | `25`, `40` minutes | Pomodoro vs deep-work |
| Plan density | `light`, `aggressive` | 60-70% vs 85-95% utilization |

### Current Strategies

1. **empathetic_25_light** - Warm tone, 25-min blocks, conservative scheduling
2. **strict_25_aggressive** - Direct tone, 25-min blocks, tight scheduling  
3. **empathetic_40_light** - Warm tone, 40-min blocks, conservative scheduling

## Fixed Inputs (Dataset)

The default dataset includes 12 goals covering:

- **Time availability**: Short (30-60min), Medium (90-120min), Long (180-240min)
- **Energy levels**: Low, Medium, High
- **Work types**: Technical, Creative, Administrative, Learning
- **Complexity**: Single-focus vs multi-task goals

### Custom Dataset Format

```json
[
  {
    "id": "unique_goal_id",
    "goal_text": "Your goal description here",
    "available_minutes": 120,
    "energy_level": "high",
    "category": "technical"
  }
]
```

## Evaluation Criteria

Each plan is evaluated on 4 dimensions (0-10 scale):

| Dimension | Description |
|-----------|-------------|
| Task Clarity | Are tasks specific and actionable? |
| Workload Realism | Is the workload achievable in the time? |
| Goal Alignment | Does the plan address the stated goal? |
| Motivation Quality | Are nudges helpful and encouraging? |

**Overall Score** = Average of all 4 dimensions

## Output Format

Results are saved as JSON in the output directory:

```json
{
  "experiment_name": "baseline_2026_01_28",
  "timestamp": "2026-01-28T10:30:00Z",
  "prompt_version": "v1",
  "num_goals": 12,
  "strategies_tested": ["empathetic_25_light", "strict_25_aggressive", "empathetic_40_light"],
  "trials": [...],
  "strategy_stats": [
    {
      "strategy_id": "empathetic_25_light",
      "trials_run": 12,
      "trials_succeeded": 12,
      "task_clarity": {"mean": 8.2, "std_dev": 0.8, "min": 7, "max": 10, "count": 12},
      "overall": {"mean": 8.1, "std_dev": 0.6, "min": 7.25, "max": 9.0, "count": 12}
    }
  ],
  "best_overall": "empathetic_25_light",
  "dimension_winners": [
    {"dimension": "task_clarity", "winner": "strict_25_aggressive", "score": 8.5},
    {"dimension": "overall", "winner": "empathetic_25_light", "score": 8.1}
  ]
}
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Rust CLI (experiments/)                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  datasets   │  │   runner    │  │      results        │ │
│  │ (12 goals)  │  │ (parallel)  │  │ (stats + JSON)      │ │
│  └─────────────┘  └──────┬──────┘  └─────────────────────┘ │
└──────────────────────────│──────────────────────────────────┘
                           │ HTTP
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                Python Agent (localhost:8000)                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  planner    │  │ evaluators  │  │       Opik          │ │
│  │  (Gemini)   │  │ (LLM judge) │  │    (tracing)        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Running Experiments

### Prerequisites

1. Start the Python agent:
   ```bash
   cd agent && source .venv/bin/activate && uvicorn agent.main:app --reload
   ```

2. Ensure `GEMINI_API_KEY` is set in `agent/.env`

3. (Optional) Set `OPIK_API_KEY` for tracing

### Example Workflow

```bash
# 1. Build the CLI
cd experiments && cargo build --release

# 2. Run baseline experiment
./target/release/run-experiment --name baseline_v1

# 3. View results
cat results/baseline_v1_*.json | jq '.best_overall'

# 4. Compare specific strategies
./target/release/run-experiment \
  --name compare_tones \
  --strategies empathetic_25_light,strict_25_aggressive

# 5. Run with custom goals
./target/release/run-experiment \
  --name custom_test \
  --dataset my_goals.json
```

## Analysis

After running experiments, compare:

1. **Overall scores** - Which strategy wins most often?
2. **Dimension breakdowns** - Are there trade-offs? (e.g., strict = clearer but less motivating)
3. **Failure rates** - Do some strategies fail more often?
4. **Duration** - How long do API calls take per strategy?

Poorly performing strategies should be deprecated or improved in Phase 6 (Adaptation).
