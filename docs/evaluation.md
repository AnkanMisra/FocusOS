# Evaluation System

FocusOS uses both LLM-based and behavioral evaluation signals.

## LLM-as-Judge Metrics
Each agent plan is scored on:
- Task clarity (0–10)
- Workload realism (0–10)
- Goal alignment (0–10)
- Motivation quality (0–10)

Each metric has a dedicated evaluation prompt.

## Behavioral Metrics
- Focus block completion rate
- Skip frequency
- Plan abandonment rate

LLM scores and behavioral metrics are analyzed together.
