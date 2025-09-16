"""Tracks & Fields brief analyzer agent."""

from __future__ import annotations

import json
from typing import Any, Dict

from agency_swarm import Agent, RunContextWrapper, function_tool

from tf_agents.instructions import BRIEF_ANALYZER_INSTRUCTIONS
from tf_agents.prompts import BRIEF_ANALYZER_PROMPT
from tf_agents.state import get_state, set_brief_analysis
from tf_agents.tools.hitl import BriefEnhancer, record_analysis_iteration, record_missing_info
from tf_agents.utils import call_json_llm

__all__ = ["create_brief_analyzer_agent"]




@function_tool()
async def generate_brief_analysis(wrapper: RunContextWrapper, brief_text: str) -> str:
    """Run the LLM to extract the structured brief JSON."""
    client = get_async_openai_client()
    model = get_model_name()
    system_prompt = BRIEF_ANALYZER_PROMPT
    response = await client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": brief_text},
        ],
        response_format={"type": "json_object"},
    )
    content = response.output[0].content[0].text  # type: ignore[index]
    return content

@function_tool()
async def submit_brief_analysis(wrapper: RunContextWrapper, analysis_json: str) -> str:
    """Persist the structured brief analysis JSON and update HITL state."""
    context = wrapper.context
    try:
        analysis: Dict[str, Any] = json.loads(analysis_json)
    except json.JSONDecodeError as exc:
        return f"Invalid JSON payload: {exc}"

    set_brief_analysis(context, analysis)
    record_missing_info(context, analysis)
    iteration = len(get_state(context).analysis_sessions) + 1
    record_analysis_iteration(context, analysis, iteration)
    return "Brief analysis stored"


@function_tool()
async def merge_additional_info(wrapper: RunContextWrapper, additional_info_json: str) -> str:
    """Merge human-provided info into the analysis to keep context in sync."""
    context = wrapper.context
    state = get_state(context)
    if not state.brief_analysis:
        return "No existing analysis to enhance. Call submit_brief_analysis first."

    try:
        additional_info: Dict[str, Any] = json.loads(additional_info_json)
    except json.JSONDecodeError as exc:
        return f"Invalid JSON payload: {exc}"

    enhancer = BriefEnhancer()
    enhanced = enhancer.merge_analysis(state.brief_analysis, additional_info)
    set_brief_analysis(context, enhanced)
    record_missing_info(context, enhanced)
    iteration = len(state.analysis_sessions) + 1
    record_analysis_iteration(context, enhanced, iteration, additional_info)
    return "Analysis updated with additional information"


def create_brief_analyzer_agent(*, name: str = "BriefAnalyzer", **agent_kwargs) -> Agent:
    instructions = (
        BRIEF_ANALYZER_INSTRUCTIONS
        + "\n\nUse the `generate_brief_analysis` tool to create a structured extraction."
        + " Once validated, call `submit_brief_analysis`. If follow-up information is provided, use"
        + " `merge_additional_info` to keep the analysis current."
    )
    return Agent(
        name=name,
        description="Analyzes client briefs and captures structured project data",
        instructions=instructions,
        tools=[generate_brief_analysis, submit_brief_analysis, merge_additional_info],
        **agent_kwargs,
    )
