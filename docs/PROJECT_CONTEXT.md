# FocusOS — Project Context & System Design

## 1. What is FocusOS?

FocusOS is an adaptive AI focus and work-habit coach designed to help users
consistently follow through on daily productivity goals.

Unlike traditional task managers or chatbots, FocusOS is built as a
**stateful, goal-driven agent system** that:
- plans daily work
- observes real user behavior
- evaluates its own decisions
- improves over time using structured experiments

The core philosophy of FocusOS is that productivity tools should not just assist,
but **learn what actually works** for a user through measurable feedback.

---

## 2. The Problem FocusOS Solves

Most productivity tools fail because:
- plans are unrealistic
- tasks are too vague
- motivation is generic
- systems do not learn from failure

Users abandon tools not because they lack discipline, but because tools do not
adapt to their real constraints.

FocusOS addresses this by treating productivity as an **iterative optimization
problem**, not a one-time plan generation task.

---

## 3. Core Idea

> If an AI agent can measure whether its plans are realistic and effective,
> it can continuously improve how it helps users work.

FocusOS operationalizes this idea by tightly coupling:
- agent planning
- user behavior
- evaluation
- experimentation
- adaptation

---

## 4. Unique Selling Proposition (USP)

FocusOS is not differentiated by UI or features.
It is differentiated by **measurable improvement**.

### Key USPs
- Agent behavior is evaluated on every run
- Multiple strategies are tested systematically
- Poor strategies are discarded over time
- Improvement is visible through metrics and dashboards

This makes FocusOS:
- transparent
- debuggable
- evidence-driven

---

## 5. User Workflow

### Step 1: Goal Definition
User provides:
- daily goal(s)
- available time
- energy level

Example:
> "Finish DSA revision and write project README"

---

### Step 2: Planning
The agent generates:
- time-boxed focus blocks
- task breakdowns
- short motivational nudges

Each plan is tagged with:
- strategy ID
- prompt version
- experiment group

---

### Step 3: Execution
User interacts with the plan by:
- starting focus blocks
- completing or skipping them

This produces **behavioral signals**, not just chat logs.

---

### Step 4: Feedback
User provides lightweight feedback:
- perceived difficulty
- usefulness
- realism

This feedback is treated as ground truth.

---

### Step 5: Evaluation
Each agent run is evaluated using:
- LLM-as-judge scoring
- behavioral metrics

Evaluation results are logged and aggregated.

---

### Step 6: Adaptation
The system updates:
- strategy selection probabilities
- prompt preferences

Higher-performing strategies are favored in future runs.

---

## 6. Agent Design

### Agent Characteristics
- Stateful
- Goal-oriented
- Evaluated
- Adaptive

### Agent State
The agent maintains:
- current user goal
- time constraints
- energy level
- historical completion rates
- previous strategy performance

---

### Agent Loop

1. Plan  
2. Act  
3. Observe  
4. Evaluate  
5. Adapt  

This loop runs once per day per user.

---

## 7. Evaluation System

Evaluation is a first-class component, not an afterthought.

### LLM-as-Judge Dimensions
Each plan is scored on:
- Task clarity
- Workload realism
- Goal alignment
- Motivation quality

Scores are numeric and comparable across runs.

---

### Behavioral Metrics
- Focus block completion rate
- Skip frequency
- Plan abandonment

LLM scores are always interpreted alongside behavioral data.

---

## 8. Experimentation Framework

FocusOS runs controlled experiments rather than ad-hoc testing.

### Variable Dimensions
- Coaching tone (strict vs empathetic)
- Focus block length (25 vs 40 minutes)
- Plan density (light vs aggressive)

### Fixed Inputs
- Same user goal
- Same availability
- Same constraints

### Outcome Comparison
- Evaluation score trends
- Completion rate deltas
- Drop-off analysis

---

## 9. Observability & Instrumentation

FocusOS uses :contentReference[oaicite:0]{index=0} as the
central observability and evaluation layer.

Tracked data includes:
- full agent traces
- prompt versions
- experiment identifiers
- evaluation scores
- behavioral outcomes

This enables:
- regression detection
- failure analysis
- proof of improvement

---

## 10. MVP Scope

### Included in MVP
- Daily goal input
- Focus plan generation
- Execution tracking
- Feedback collection
- Evaluation + experiments
- Observability dashboards

### Explicitly Excluded
- Social features
- Gamification
- Long-term analytics UI
- Notifications beyond basics

The MVP prioritizes **agent quality**, not feature breadth.

---

## 11. System Architecture (High Level)

User  
→ Frontend (Next.js)  
→ Agent Service (Python)  
→ Evaluation + Experiments  
→ Observability (Opik)  
→ Strategy Update  
→ Next Agent Run  

Each step is instrumented.

---

## 12. Tech Stack Summary

- Next.js + TypeScript (frontend)
- Python (agent orchestration)
- Rust (performance-critical workers)
- Convex (database)
- Gemini 3 Flash (LLM)
- Opik (evaluation & observability)
- Docker (containerization)

---

## 13. Design Philosophy

- Prefer simple systems with strong instrumentation
- Optimize for clarity over complexity
- Treat failures as data
- Make improvement visible

---

## 14. What This Project Demonstrates

- How to build a real AI agent, not a chatbot
- How to evaluate agent behavior systematically
- How observability improves AI system quality
- How experimentation drives measurable outcomes

---

## 15. One-Line Summary

FocusOS is a productivity-focused AI agent system that uses continuous evaluation,
experimentation, and observability to measurably improve how it helps users work.
