"""Pydantic models for FocusOS Agent Service."""

from enum import Enum

from pydantic import BaseModel, Field


class EnergyLevel(str, Enum):
    """User energy level for the day."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class GoalInput(BaseModel):
    """Input for generating a focus plan."""

    goal_text: str = Field(..., description="User's daily goal(s)", min_length=1)
    available_minutes: int = Field(..., description="Available time in minutes", ge=15, le=720)
    energy_level: EnergyLevel = Field(..., description="User's current energy level")
    strategy_id: str | None = Field(default=None, description="Optional strategy override")


class FocusBlock(BaseModel):
    """A single focus block in the plan."""

    order: int = Field(..., description="Block sequence number", ge=1)
    duration_min: int = Field(..., description="Block duration in minutes", ge=5, le=60)
    task: str = Field(..., description="Task description for this block")
    nudge: str = Field(..., description="Motivational nudge for this block")


class FocusPlan(BaseModel):
    """Generated focus plan response."""

    strategy_id: str = Field(..., description="Strategy used for generation")
    prompt_version: str = Field(..., description="Prompt template version")
    blocks: list[FocusBlock] = Field(..., description="Ordered list of focus blocks")
    total_minutes: int = Field(..., description="Total planned time in minutes")


class FeedbackInput(BaseModel):
    """User feedback on a focus plan or block."""

    plan_id: str = Field(..., description="ID of the plan being rated")
    block_order: int | None = Field(
        default=None, description="Specific block order (if rating a block)"
    )
    completed: bool = Field(..., description="Whether the block/plan was completed")
    perceived_difficulty: int = Field(..., description="Difficulty rating 1-5", ge=1, le=5)
    usefulness_score: int = Field(..., description="Usefulness rating 1-5", ge=1, le=5)
    free_text: str | None = Field(default=None, description="Optional feedback text")


class FeedbackResponse(BaseModel):
    """Response after receiving feedback."""

    received: bool = Field(default=True)
    message: str = Field(default="Feedback recorded")


class EvaluationScoreResponse(BaseModel):
    """Single evaluation dimension score."""

    score: int = Field(..., description="Score from 0-10", ge=0, le=10)
    reasoning: str = Field(..., description="Explanation for the score")


class PlanEvaluationResponse(BaseModel):
    """Complete evaluation of a focus plan."""

    task_clarity: EvaluationScoreResponse
    workload_realism: EvaluationScoreResponse
    goal_alignment: EvaluationScoreResponse
    motivation_quality: EvaluationScoreResponse
    overall_score: float = Field(..., description="Average of all dimensions")


class PlanWithEvaluation(BaseModel):
    """Focus plan with optional evaluation scores."""

    strategy_id: str = Field(..., description="Strategy used for generation")
    prompt_version: str = Field(..., description="Prompt template version")
    blocks: list[FocusBlock] = Field(..., description="Ordered list of focus blocks")
    total_minutes: int = Field(..., description="Total planned time in minutes")
    evaluation: PlanEvaluationResponse | None = Field(
        default=None, description="LLM-as-judge evaluation scores"
    )
