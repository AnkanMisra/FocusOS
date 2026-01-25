"""Strategy configurations for FocusOS Agent."""

from dataclasses import dataclass
from enum import Enum


class CoachingTone(str, Enum):
    """Coaching tone for plan generation."""

    EMPATHETIC = "empathetic"
    STRICT = "strict"


class PlanDensity(str, Enum):
    """Plan density - how aggressively to pack the schedule."""

    LIGHT = "light"
    AGGRESSIVE = "aggressive"


@dataclass(frozen=True)
class Strategy:
    """Configuration for a planning strategy."""

    id: str
    tone: CoachingTone
    block_length_min: int
    density: PlanDensity
    description: str

    def get_tone_instruction(self) -> str:
        """Get the tone instruction for the prompt."""
        if self.tone == CoachingTone.EMPATHETIC:
            return (
                "Use a warm, encouraging, and understanding tone. "
                "Acknowledge that focus is hard and celebrate small wins. "
                "Be supportive and gentle with nudges."
            )
        return (
            "Use a direct, no-nonsense, accountability-focused tone. "
            "Be clear about expectations and push the user to stay on track. "
            "Nudges should be firm but not harsh."
        )

    def get_density_instruction(self) -> str:
        """Get the density instruction for the prompt."""
        if self.density == PlanDensity.LIGHT:
            return (
                "Schedule conservatively with buffer time between blocks. "
                "Aim for 60-70% utilization of available time. "
                "Leave room for breaks and context switching."
            )
        return (
            "Schedule ambitiously to maximize productivity. "
            "Aim for 85-95% utilization of available time. "
            "Pack blocks tightly with minimal gaps."
        )


# The 3 initial strategies as specified
STRATEGIES: dict[str, Strategy] = {
    "empathetic_25_light": Strategy(
        id="empathetic_25_light",
        tone=CoachingTone.EMPATHETIC,
        block_length_min=25,
        density=PlanDensity.LIGHT,
        description="Gentle coaching with short Pomodoro-style blocks and conservative scheduling",
    ),
    "strict_25_aggressive": Strategy(
        id="strict_25_aggressive",
        tone=CoachingTone.STRICT,
        block_length_min=25,
        density=PlanDensity.AGGRESSIVE,
        description="Accountability-focused with short blocks and tight scheduling",
    ),
    "empathetic_40_light": Strategy(
        id="empathetic_40_light",
        tone=CoachingTone.EMPATHETIC,
        block_length_min=40,
        density=PlanDensity.LIGHT,
        description="Gentle coaching with longer deep-work blocks and conservative scheduling",
    ),
}

DEFAULT_STRATEGY_ID = "empathetic_25_light"


def get_strategy(strategy_id: str | None = None) -> Strategy:
    """Get a strategy by ID, falling back to default."""
    if strategy_id is None:
        return STRATEGIES[DEFAULT_STRATEGY_ID]
    if strategy_id not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {strategy_id}. Available: {list(STRATEGIES.keys())}")
    return STRATEGIES[strategy_id]
