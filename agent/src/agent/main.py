"""FastAPI application for FocusOS Agent Service."""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agent.models import FeedbackInput, FeedbackResponse, FocusPlan, GoalInput
from agent.planner import generate_plan
from agent.strategies import STRATEGIES


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load environment variables on startup."""
    load_dotenv()
    yield


app = FastAPI(
    title="FocusOS Agent Service",
    description="AI-powered focus planning agent",
    version="0.1.0",
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
    return {"status": "healthy", "service": "focusos-agent"}


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


@app.post("/agent/plan", response_model=FocusPlan)
async def create_plan(goal_input: GoalInput) -> FocusPlan:
    """Generate a focus plan for the given goal.

    Args:
        goal_input: User's goal, available time, energy level, and optional strategy.

    Returns:
        FocusPlan with strategy_id, prompt_version, and ordered focus blocks.
    """
    try:
        plan = generate_plan(goal_input)
        return plan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {e}") from e


@app.post("/agent/feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackInput) -> FeedbackResponse:
    """Submit feedback on a focus plan or block.

    Note: This is a stub endpoint. Feedback will be persisted in Phase 4
    when Convex integration is added.
    """
    # TODO: Persist feedback to Convex in Phase 4
    # For now, just acknowledge receipt
    return FeedbackResponse(
        received=True,
        message=f"Feedback for plan {feedback.plan_id} recorded (stub)",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
