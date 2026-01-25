"""Prompt templates for FocusOS Agent."""

from agent.strategies import Strategy

PROMPT_VERSION = "v1"

SYSTEM_PROMPT = """You are FocusOS, an AI focus coach that creates personalized daily work plans.

Your job is to:
1. Break down the user's goal into actionable focus blocks
2. Assign realistic time estimates to each block
3. Provide a short motivational nudge for each block

Rules:
- Each focus block should be a single, concrete task
- Nudges should be 1-2 sentences max
- Be realistic about what can be accomplished
- Consider the user's energy level when ordering tasks
{tone_instruction}
{density_instruction}

Output your plan as valid JSON matching this exact schema:
{{
  "blocks": [
    {{
      "order": 1,
      "duration_min": {block_length},
      "task": "Specific task description",
      "nudge": "Short motivational message"
    }}
  ]
}}

IMPORTANT:
- Return ONLY the JSON object, no markdown code fences, no explanations
- Each block duration should be approximately {block_length} minutes
- Total time across all blocks must not exceed {available_minutes} minutes
- Order tasks intelligently based on energy level: {energy_guidance}
"""

PLAN_REQUEST_TEMPLATE = """User's goal for today: {goal_text}

Available time: {available_minutes} minutes
Energy level: {energy_level}

Generate a focus plan with {block_length}-minute blocks."""


def get_energy_guidance(energy_level: str) -> str:
    """Get task ordering guidance based on energy level."""
    guidance = {
        "high": "Start with the most challenging/creative tasks while energy is high",
        "medium": "Mix challenging and routine tasks, save very hard tasks for mid-session",
        "low": "Start with easier tasks to build momentum, save hardest for when warmed up",
    }
    return guidance.get(energy_level, guidance["medium"])


def build_system_prompt(
    strategy: Strategy,
    available_minutes: int,
    energy_level: str,
) -> str:
    """Build the system prompt with strategy-specific instructions."""
    return SYSTEM_PROMPT.format(
        tone_instruction=strategy.get_tone_instruction(),
        density_instruction=strategy.get_density_instruction(),
        block_length=strategy.block_length_min,
        available_minutes=available_minutes,
        energy_guidance=get_energy_guidance(energy_level),
    )


def build_user_prompt(
    goal_text: str,
    available_minutes: int,
    energy_level: str,
    block_length: int,
) -> str:
    """Build the user prompt with goal details."""
    return PLAN_REQUEST_TEMPLATE.format(
        goal_text=goal_text,
        available_minutes=available_minutes,
        energy_level=energy_level,
        block_length=block_length,
    )
