"""FastAPI application for FocusOS Agent Service."""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from agent.evaluators import evaluate_plan
from agent.models import (
    EvaluationScoreResponse,
    FeedbackInput,
    FeedbackResponse,
    FocusPlan,
    GoalInput,
    PlanEvaluationResponse,
    PlanWithEvaluation,
)
from agent.planner import generate_plan
from agent.strategies import STRATEGIES

# Try to import Opik for logging evaluations
_opik_enabled = False
try:
    import opik  # noqa: F401

    if os.getenv("OPIK_API_KEY"):
        _opik_enabled = True
except ImportError:
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load environment variables on startup."""
    load_dotenv()
    yield


app = FastAPI(
    title="FocusOS Agent Service",
    description="AI-powered focus planning agent with LLM-as-judge evaluation",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "focusos-agent",
        "opik_enabled": _opik_enabled,
    }


@app.get("/strategies")
async def list_strategies() -> dict:
    """List available planning strategies."""
    return {
        "strategies": [
            {
                "id": s.id,
                "description": s.description,
                "tone": s.tone.value,
                "block_length_min": s.block_length_min,
                "density": s.density.value,
            }
            for s in STRATEGIES.values()
        ]
    }


def _create_plan_impl(goal_input: GoalInput, evaluate: bool) -> PlanWithEvaluation:
    """Implementation of create_plan logic."""
    plan = generate_plan(goal_input)

    evaluation_response = None
    if evaluate:
        evaluation = evaluate_plan(goal_input, plan)

        # Convert to response model
        evaluation_response = PlanEvaluationResponse(
            task_clarity=EvaluationScoreResponse(
                score=evaluation.task_clarity.score,
                reasoning=evaluation.task_clarity.reasoning,
            ),
            workload_realism=EvaluationScoreResponse(
                score=evaluation.workload_realism.score,
                reasoning=evaluation.workload_realism.reasoning,
            ),
            goal_alignment=EvaluationScoreResponse(
                score=evaluation.goal_alignment.score,
                reasoning=evaluation.goal_alignment.reasoning,
            ),
            motivation_quality=EvaluationScoreResponse(
                score=evaluation.motivation_quality.score,
                reasoning=evaluation.motivation_quality.reasoning,
            ),
            overall_score=evaluation.overall_score,
        )

        # Log to Opik if enabled
        if _opik_enabled:
            _log_evaluation_to_opik(plan, evaluation)

    return PlanWithEvaluation(
        strategy_id=plan.strategy_id,
        prompt_version=plan.prompt_version,
        blocks=plan.blocks,
        total_minutes=plan.total_minutes,
        evaluation=evaluation_response,
    )


@app.post("/agent/plan", response_model=PlanWithEvaluation)
async def create_plan(
    goal_input: GoalInput,
    evaluate: bool = Query(default=False, description="Run LLM-as-judge evaluation"),
) -> PlanWithEvaluation:
    """Generate a focus plan for the given goal.

    Args:
        goal_input: User's goal, available time, energy level, and optional strategy.
        evaluate: If True, also run LLM-as-judge evaluation on the plan.

    Returns:
        PlanWithEvaluation containing the plan and optional evaluation scores.
    """
    try:
        if _opik_enabled:
            import opik

            # Track the request
            @opik.track(name="create_plan_endpoint")
            def tracked_create(gi: GoalInput, eval_flag: bool):
                return _create_plan_impl(gi, eval_flag)

            return tracked_create(goal_input, evaluate)
        else:
            return _create_plan_impl(goal_input, evaluate)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {e}") from e


@app.post("/agent/evaluate", response_model=PlanEvaluationResponse)
async def evaluate_existing_plan(
    goal_input: GoalInput,
    plan: FocusPlan,
) -> PlanEvaluationResponse:
    """Evaluate an existing focus plan using LLM-as-judge.

    Args:
        goal_input: The original user input that generated the plan.
        plan: The focus plan to evaluate.

    Returns:
        PlanEvaluationResponse with scores for all 4 dimensions.
    """
    try:
        evaluation = evaluate_plan(goal_input, plan)

        return PlanEvaluationResponse(
            task_clarity=EvaluationScoreResponse(
                score=evaluation.task_clarity.score,
                reasoning=evaluation.task_clarity.reasoning,
            ),
            workload_realism=EvaluationScoreResponse(
                score=evaluation.workload_realism.score,
                reasoning=evaluation.workload_realism.reasoning,
            ),
            goal_alignment=EvaluationScoreResponse(
                score=evaluation.goal_alignment.score,
                reasoning=evaluation.goal_alignment.reasoning,
            ),
            motivation_quality=EvaluationScoreResponse(
                score=evaluation.motivation_quality.score,
                reasoning=evaluation.motivation_quality.reasoning,
            ),
            overall_score=evaluation.overall_score,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {e}") from e


@app.post("/agent/feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackInput) -> FeedbackResponse:
    """Submit feedback on a focus plan or block.

    Note: This is a stub endpoint. Feedback will be persisted in Phase 4
    when Convex integration is added.
    """
    return FeedbackResponse(
        received=True,
        message=f"Feedback for plan {feedback.plan_id} recorded (stub)",
    )


def _log_evaluation_to_opik(plan: FocusPlan, evaluation) -> None:
    """Log evaluation scores to Opik for tracking."""
    try:
        import opik

        # Log scores as metadata on the current trace
        opik.opik_context.update_current_trace(
            metadata={
                "eval_task_clarity": evaluation.task_clarity.score,
                "eval_workload_realism": evaluation.workload_realism.score,
                "eval_goal_alignment": evaluation.goal_alignment.score,
                "eval_motivation_quality": evaluation.motivation_quality.score,
                "eval_overall_score": evaluation.overall_score,
            }
        )
    except Exception:
        # Don't fail the request if Opik logging fails
        pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
