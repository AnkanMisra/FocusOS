"""Focus plan generation using Gemini."""

import json
import os

from google import genai
from google.genai import types

from agent.models import FocusBlock, FocusPlan, GoalInput
from agent.prompts import PROMPT_VERSION, build_system_prompt, build_user_prompt
from agent.strategies import Strategy, get_strategy

# Try to initialize Opik for tracing (optional - won't fail if no API key)
_opik_enabled = False
try:
    import opik

    opik_api_key = os.getenv("OPIK_API_KEY")
    if opik_api_key:
        opik.configure(use_local=False)
        _opik_enabled = True
except Exception:
    pass


def _get_gemini_client() -> genai.Client:
    """Get configured Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    return genai.Client(api_key=api_key)


def _parse_plan_response(response_text: str, strategy: Strategy) -> list[FocusBlock]:
    """Parse the LLM response into FocusBlock objects."""
    # Clean up response - remove markdown code fences if present
    text = response_text.strip()
    if text.startswith("```"):
        # Remove opening fence
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM response as JSON: {e}") from e

    blocks_data = data.get("blocks", [])
    if not blocks_data:
        raise ValueError("LLM response contained no blocks")

    blocks = []
    for block_data in blocks_data:
        blocks.append(
            FocusBlock(
                order=block_data["order"],
                duration_min=block_data.get("duration_min", strategy.block_length_min),
                task=block_data["task"],
                nudge=block_data["nudge"],
            )
        )
    return blocks


def _generate_plan_impl(goal_input: GoalInput) -> FocusPlan:
    """Internal implementation of plan generation."""
    # Get strategy
    strategy = get_strategy(goal_input.strategy_id)

    # Build prompts
    system_prompt = build_system_prompt(
        strategy=strategy,
        available_minutes=goal_input.available_minutes,
        energy_level=goal_input.energy_level.value,
    )
    user_prompt = build_user_prompt(
        goal_text=goal_input.goal_text,
        available_minutes=goal_input.available_minutes,
        energy_level=goal_input.energy_level.value,
        block_length=strategy.block_length_min,
    )

    # Call Gemini
    client = _get_gemini_client()
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[
            types.Content(role="user", parts=[types.Part(text=system_prompt)]),
            types.Content(
                role="model",
                parts=[types.Part(text="I understand. I will generate focus plans as JSON.")],
            ),
            types.Content(role="user", parts=[types.Part(text=user_prompt)]),
        ],
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=2048,
        ),
    )

    # Parse response
    response_text = response.text
    blocks = _parse_plan_response(response_text, strategy)

    # Calculate total time
    total_minutes = sum(block.duration_min for block in blocks)

    return FocusPlan(
        strategy_id=strategy.id,
        prompt_version=PROMPT_VERSION,
        blocks=blocks,
        total_minutes=total_minutes,
    )


def generate_plan(goal_input: GoalInput) -> FocusPlan:
    """Generate a focus plan for the given goal input.

    Args:
        goal_input: User's goal, available time, energy level, and optional strategy.

    Returns:
        FocusPlan with strategy_id, prompt_version, and ordered blocks.
    """
    if _opik_enabled:
        # Use Opik tracking decorator dynamically
        import opik

        @opik.track(name="generate_focus_plan")
        def tracked_generate(gi: GoalInput) -> FocusPlan:
            strategy = get_strategy(gi.strategy_id)
            opik.set_trace_attribute("strategy_id", strategy.id)
            opik.set_trace_attribute("prompt_version", PROMPT_VERSION)
            opik.set_trace_attribute("goal_text", gi.goal_text)
            opik.set_trace_attribute("available_minutes", gi.available_minutes)
            opik.set_trace_attribute("energy_level", gi.energy_level.value)
            return _generate_plan_impl(gi)

        return tracked_generate(goal_input)
    else:
        return _generate_plan_impl(goal_input)
