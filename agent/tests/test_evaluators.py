"""Tests for the FocusOS evaluators."""

from unittest.mock import patch

import pytest

from agent.evaluators import (
    EvaluationScore,
    evaluate_goal_alignment,
    evaluate_motivation_quality,
    evaluate_plan,
    evaluate_task_clarity,
    evaluate_workload_realism,
)
from agent.models import EnergyLevel, FocusBlock, FocusPlan, GoalInput


@pytest.fixture
def mock_goal_input():
    return GoalInput(
        goal_text="Test goal",
        available_minutes=60,
        energy_level=EnergyLevel.MEDIUM,
    )


@pytest.fixture
def mock_focus_plan():
    return FocusPlan(
        strategy_id="test_strategy",
        prompt_version="v1",
        blocks=[
            FocusBlock(order=1, duration_min=25, task="Task 1", nudge="Nudge 1"),
            FocusBlock(order=2, duration_min=25, task="Task 2", nudge="Nudge 2"),
        ],
        total_minutes=50,
    )


@patch("agent.evaluators._call_evaluator")
def test_evaluate_task_clarity(mock_call, mock_goal_input, mock_focus_plan):
    """Test task clarity evaluator."""
    mock_call.return_value = {"score": 8, "reasoning": "Clear tasks."}

    score = evaluate_task_clarity(mock_goal_input, mock_focus_plan)

    assert isinstance(score, EvaluationScore)
    assert score.dimension == "task_clarity"
    assert score.score == 8
    assert score.reasoning == "Clear tasks."


@patch("agent.evaluators._call_evaluator")
def test_evaluate_workload_realism(mock_call, mock_goal_input, mock_focus_plan):
    """Test workload realism evaluator."""
    mock_call.return_value = {"score": 9, "reasoning": "Realistic workload."}

    score = evaluate_workload_realism(mock_goal_input, mock_focus_plan)

    assert score.dimension == "workload_realism"
    assert score.score == 9


@patch("agent.evaluators._call_evaluator")
def test_evaluate_goal_alignment(mock_call, mock_goal_input, mock_focus_plan):
    """Test goal alignment evaluator."""
    mock_call.return_value = {"score": 7, "reasoning": "Aligned well."}

    score = evaluate_goal_alignment(mock_goal_input, mock_focus_plan)

    assert score.dimension == "goal_alignment"
    assert score.score == 7


@patch("agent.evaluators._call_evaluator")
def test_evaluate_motivation_quality(mock_call, mock_goal_input, mock_focus_plan):
    """Test motivation quality evaluator."""
    mock_call.return_value = {"score": 10, "reasoning": "Great nudges."}

    score = evaluate_motivation_quality(mock_goal_input, mock_focus_plan)

    assert score.dimension == "motivation_quality"
    assert score.score == 10


@patch("agent.evaluators.evaluate_task_clarity")
@patch("agent.evaluators.evaluate_workload_realism")
@patch("agent.evaluators.evaluate_goal_alignment")
@patch("agent.evaluators.evaluate_motivation_quality")
def test_evaluate_plan(
    mock_motivation, mock_alignment, mock_workload, mock_clarity, mock_goal_input, mock_focus_plan
):
    """Test aggregate evaluate_plan function."""
    mock_clarity.return_value = EvaluationScore("task_clarity", 8, "Good")
    mock_workload.return_value = EvaluationScore("workload_realism", 8, "Good")
    mock_alignment.return_value = EvaluationScore("goal_alignment", 8, "Good")
    mock_motivation.return_value = EvaluationScore("motivation_quality", 8, "Good")

    evaluation = evaluate_plan(mock_goal_input, mock_focus_plan)

    assert evaluation.overall_score == 8.0
    assert evaluation.task_clarity.score == 8
    assert evaluation.workload_realism.score == 8
    assert evaluation.goal_alignment.score == 8
    assert evaluation.motivation_quality.score == 8
