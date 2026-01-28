"""LLM-as-judge evaluators for FocusOS plan quality assessment.

Each evaluator scores a specific dimension of plan quality on a 0-10 scale.
Evaluations are logged to Opik for tracking and experimentation.
"""

import json
import os
from dataclasses import dataclass

from google import genai
from google.genai import types

from agent.models import FocusPlan, GoalInput


@dataclass
class EvaluationScore:
    """Score from a single evaluation dimension."""

    dimension: str
    score: int  # 0-10
    reasoning: str


@dataclass
class PlanEvaluation:
    """Complete evaluation of a focus plan across all dimensions."""

    task_clarity: EvaluationScore
    workload_realism: EvaluationScore
    goal_alignment: EvaluationScore
    motivation_quality: EvaluationScore
    overall_score: float  # Average of all dimensions

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "task_clarity": {
                "score": self.task_clarity.score,
                "reasoning": self.task_clarity.reasoning,
            },
            "workload_realism": {
                "score": self.workload_realism.score,
                "reasoning": self.workload_realism.reasoning,
            },
            "goal_alignment": {
                "score": self.goal_alignment.score,
                "reasoning": self.goal_alignment.reasoning,
            },
            "motivation_quality": {
                "score": self.motivation_quality.score,
                "reasoning": self.motivation_quality.reasoning,
            },
            "overall_score": self.overall_score,
        }


def _get_gemini_client() -> genai.Client:
    """Get configured Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    return genai.Client(api_key=api_key)


def _call_evaluator(prompt: str) -> dict:
    """Call Gemini to evaluate and return parsed JSON response."""
    client = _get_gemini_client()
    response = client.models.generate_content(
        model="gemini-3-pro-preview",
        contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
        config=types.GenerateContentConfig(
            temperature=0.1,  # Very low temperature for consistent scoring
            max_output_tokens=512,
        ),
    )

    # Parse JSON response
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        return {"score": 5, "reasoning": "Unable to parse evaluation response"}


def _format_plan_for_eval(goal_input: GoalInput, plan: FocusPlan) -> str:
    """Format the goal and plan for evaluation prompts."""
    blocks_text = "\n".join(
        f"  {b.order}. [{b.duration_min} min] {b.task} | Nudge: {b.nudge}" for b in plan.blocks
    )
    return f"""USER GOAL: {goal_input.goal_text}
AVAILABLE TIME: {goal_input.available_minutes} minutes
ENERGY LEVEL: {goal_input.energy_level.value}

GENERATED PLAN (Strategy: {plan.strategy_id}, Total: {plan.total_minutes} min):
{blocks_text}"""


# === Individual Evaluators ===


def evaluate_task_clarity(goal_input: GoalInput, plan: FocusPlan) -> EvaluationScore:
    """Evaluate how clear and actionable the tasks are (0-10)."""
    plan_text = _format_plan_for_eval(goal_input, plan)
    prompt = f"""You are an expert productivity coach evaluating a focus plan.

{plan_text}

EVALUATE: Task Clarity (0-10)
- Are tasks specific and actionable?
- Is it clear what the user should do in each block?
- Are tasks broken down appropriately (not too vague, not too granular)?

Respond with ONLY valid JSON:
{{"score": <0-10>, "reasoning": "<1-2 sentences>"}}"""

    result = _call_evaluator(prompt)
    return EvaluationScore(
        dimension="task_clarity",
        score=min(10, max(0, int(result.get("score", 5)))),
        reasoning=result.get("reasoning", ""),
    )


def evaluate_workload_realism(goal_input: GoalInput, plan: FocusPlan) -> EvaluationScore:
    """Evaluate if the workload is realistic for the given time/energy (0-10)."""
    plan_text = _format_plan_for_eval(goal_input, plan)
    prompt = f"""You are an expert productivity coach evaluating a focus plan.

{plan_text}

EVALUATE: Workload Realism (0-10)
- Is the total work realistic for the available time?
- Does it account for the user's energy level?
- Are individual block durations reasonable for the tasks?
- Is there appropriate buffer/break time?

Respond with ONLY valid JSON:
{{"score": <0-10>, "reasoning": "<1-2 sentences>"}}"""

    result = _call_evaluator(prompt)
    return EvaluationScore(
        dimension="workload_realism",
        score=min(10, max(0, int(result.get("score", 5)))),
        reasoning=result.get("reasoning", ""),
    )


def evaluate_goal_alignment(goal_input: GoalInput, plan: FocusPlan) -> EvaluationScore:
    """Evaluate how well the plan addresses the user's stated goal (0-10)."""
    plan_text = _format_plan_for_eval(goal_input, plan)
    prompt = f"""You are an expert productivity coach evaluating a focus plan.

{plan_text}

EVALUATE: Goal Alignment (0-10)
- Does the plan directly address the user's stated goal?
- Are all tasks relevant to achieving the goal?
- Will completing these tasks make meaningful progress?
- Are any critical steps missing?

Respond with ONLY valid JSON:
{{"score": <0-10>, "reasoning": "<1-2 sentences>"}}"""

    result = _call_evaluator(prompt)
    return EvaluationScore(
        dimension="goal_alignment",
        score=min(10, max(0, int(result.get("score", 5)))),
        reasoning=result.get("reasoning", ""),
    )


def evaluate_motivation_quality(goal_input: GoalInput, plan: FocusPlan) -> EvaluationScore:
    """Evaluate the quality of motivational nudges (0-10)."""
    plan_text = _format_plan_for_eval(goal_input, plan)
    prompt = f"""You are an expert productivity coach evaluating a focus plan.

{plan_text}

EVALUATE: Motivation Quality (0-10)
- Are the nudges encouraging and supportive?
- Do they provide genuine motivation (not generic platitudes)?
- Are they appropriate for the task difficulty?
- Do they maintain a consistent, helpful tone?

Respond with ONLY valid JSON:
{{"score": <0-10>, "reasoning": "<1-2 sentences>"}}"""

    result = _call_evaluator(prompt)
    return EvaluationScore(
        dimension="motivation_quality",
        score=min(10, max(0, int(result.get("score", 5)))),
        reasoning=result.get("reasoning", ""),
    )


# === Main Evaluation Function ===


def evaluate_plan(goal_input: GoalInput, plan: FocusPlan) -> PlanEvaluation:
    """Run all evaluators on a plan and return complete evaluation.

    Args:
        goal_input: The original user input
        plan: The generated focus plan

    Returns:
        PlanEvaluation with scores for all 4 dimensions plus overall score
    """
    task_clarity = evaluate_task_clarity(goal_input, plan)
    workload_realism = evaluate_workload_realism(goal_input, plan)
    goal_alignment = evaluate_goal_alignment(goal_input, plan)
    motivation_quality = evaluate_motivation_quality(goal_input, plan)

    # Calculate overall score (average)
    overall = (
        task_clarity.score
        + workload_realism.score
        + goal_alignment.score
        + motivation_quality.score
    ) / 4.0

    return PlanEvaluation(
        task_clarity=task_clarity,
        workload_realism=workload_realism,
        goal_alignment=goal_alignment,
        motivation_quality=motivation_quality,
        overall_score=round(overall, 2),
    )
