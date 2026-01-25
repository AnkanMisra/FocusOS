# System Architecture

FocusOS is built as a layered agent system.

## Components
1. Frontend (Next.js)
   - Goal input
   - Focus plan view
   - Completion and feedback capture

2. Agent Service (Python)
   - Planning agent
   - Strategy selection
   - Feedback ingestion

3. Evaluation Layer
   - LLM-as-judge evaluators
   - Behavioral metrics

4. Experiment Controller
   - Prompt and strategy variants
   - Performance comparison

5. Observability
   - Traces
   - Metrics
   - Experiment dashboards (Opik)

## Data Flow
User Input → Agent Plan → User Execution → Feedback → Evaluation → Adaptation → Next Run
