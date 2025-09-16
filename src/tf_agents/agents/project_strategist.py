"""Tracks & Fields project strategist agent."""

from __future__ import annotations

import json
from typing import Any, Dict

from agency_swarm import Agent, RunContextWrapper, function_tool

from tf_agents.prompts import PROJECT_STRATEGIST_PROMPT
from tf_agents.state import get_brief_analysis, set_project_strategy
from tf_agents.utils import call_json_llm

__all__ = ["create_project_strategist_agent"]


@function_tool()
async def generate_project_strategy(wrapper: RunContextWrapper) -> str:
    """Draft a project strategy using the LLM based on stored brief analysis."""
    context = wrapper.context
    analysis = get_brief_analysis(context)
    if not analysis:
        return "No brief analysis available. Run the brief analyzer first."
    client = get_async_openai_client()
    model = get_model_name()
    response = await client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": PROJECT_STRATEGIST_PROMPT},
            {"role": "user", "content": json.dumps(analysis, indent=2)},
        ],
        response_format={"type": "json_object"},
    )
    content = response.output[0].content[0].text  # type: ignore[index]
    return content

@function_tool()
async def submit_project_strategy(wrapper: RunContextWrapper, strategy_json: str) -> str:
    """Persist the calculated project strategy payload."""
    context = wrapper.context
    if not get_brief_analysis(context):
        return "No brief analysis found. Run the brief analyzer first."

    try:
        strategy: Dict[str, Any] = json.loads(strategy_json)
    except json.JSONDecodeError as exc:
        return f"Invalid JSON payload: {exc}"

    set_project_strategy(context, strategy)
    return "Project strategy stored"


def create_project_strategist_agent(*, name: str = "ProjectStrategist", **agent_kwargs) -> Agent:
    instructions = (
        "You are the Tracks & Fields Project Strategist. Review the structured brief analysis available in context and craft a project strategy summary. "
        "Use the `generate_project_strategy` tool to draft the structured plan, then call `submit_project_strategy` with the final JSON.\n\n"
        + PROJECT_STRATEGIST_PROMPT
    )

    return Agent(
        name=name,
        description="Develops project strategies based on extracted brief information",
        instructions=instructions,
        tools=[generate_project_strategy, submit_project_strategy],
        **agent_kwargs,
    )
