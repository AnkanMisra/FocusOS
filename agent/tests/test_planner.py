"""Tests for the FocusOS planner."""

import pytest

from agent.models import EnergyLevel, GoalInput
from agent.prompts import PROMPT_VERSION, build_system_prompt, build_user_prompt
from agent.strategies import (
    DEFAULT_STRATEGY_ID,
    STRATEGIES,
    CoachingTone,
    PlanDensity,
    get_strategy,
)


class TestStrategies:
    """Tests for strategy configuration."""

    def test_all_strategies_exist(self):
        """Verify all 3 required strategies are defined."""
        assert "empathetic_25_light" in STRATEGIES
        assert "strict_25_aggressive" in STRATEGIES
        assert "empathetic_40_light" in STRATEGIES

    def test_default_strategy(self):
        """Verify default strategy is set correctly."""
        assert DEFAULT_STRATEGY_ID == "empathetic_25_light"

    def test_get_strategy_default(self):
        """Test getting default strategy."""
        strategy = get_strategy(None)
        assert strategy.id == "empathetic_25_light"

    def test_get_strategy_by_id(self):
        """Test getting strategy by ID."""
        strategy = get_strategy("strict_25_aggressive")
        assert strategy.id == "strict_25_aggressive"
        assert strategy.tone == CoachingTone.STRICT
        assert strategy.block_length_min == 25
        assert strategy.density == PlanDensity.AGGRESSIVE

    def test_get_strategy_invalid(self):
        """Test error on invalid strategy ID."""
        with pytest.raises(ValueError, match="Unknown strategy"):
            get_strategy("nonexistent_strategy")

    def test_strategy_tone_instructions(self):
        """Test that tone instructions differ between strategies."""
        empathetic = get_strategy("empathetic_25_light")
        strict = get_strategy("strict_25_aggressive")

        empathetic_tone = empathetic.get_tone_instruction()
        strict_tone = strict.get_tone_instruction()

        assert "warm" in empathetic_tone.lower() or "encouraging" in empathetic_tone.lower()
        assert "direct" in strict_tone.lower() or "accountability" in strict_tone.lower()
        assert empathetic_tone != strict_tone


class TestPrompts:
    """Tests for prompt generation."""

    def test_prompt_version_exists(self):
        """Verify prompt version is set."""
        assert PROMPT_VERSION == "v1"

    def test_build_system_prompt_contains_strategy_elements(self):
        """Test system prompt includes strategy-specific elements."""
        strategy = get_strategy("empathetic_25_light")
        prompt = build_system_prompt(
            strategy=strategy,
            available_minutes=120,
            energy_level="high",
        )

        assert "25" in prompt  # block length
        assert "120" in prompt  # available minutes
        assert "JSON" in prompt  # output format

    def test_build_user_prompt_contains_goal(self):
        """Test user prompt includes goal text."""
        prompt = build_user_prompt(
            goal_text="Write unit tests",
            available_minutes=60,
            energy_level="medium",
            block_length=25,
        )

        assert "Write unit tests" in prompt
        assert "60" in prompt
        assert "medium" in prompt


class TestModels:
    """Tests for Pydantic models."""

    def test_goal_input_valid(self):
        """Test valid GoalInput creation."""
        goal = GoalInput(
            goal_text="Complete project",
            available_minutes=120,
            energy_level=EnergyLevel.HIGH,
        )
        assert goal.goal_text == "Complete project"
        assert goal.available_minutes == 120
        assert goal.energy_level == EnergyLevel.HIGH
        assert goal.strategy_id is None

    def test_goal_input_with_strategy(self):
        """Test GoalInput with strategy override."""
        goal = GoalInput(
            goal_text="Complete project",
            available_minutes=120,
            energy_level=EnergyLevel.LOW,
            strategy_id="strict_25_aggressive",
        )
        assert goal.strategy_id == "strict_25_aggressive"

    def test_goal_input_minimum_time(self):
        """Test minimum available time validation."""
        with pytest.raises(ValueError):
            GoalInput(
                goal_text="Too short",
                available_minutes=10,  # Below minimum of 15
                energy_level=EnergyLevel.MEDIUM,
            )

    def test_goal_input_empty_goal(self):
        """Test empty goal text validation."""
        with pytest.raises(ValueError):
            GoalInput(
                goal_text="",
                available_minutes=60,
                energy_level=EnergyLevel.MEDIUM,
            )
