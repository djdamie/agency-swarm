"""End-to-end helpers for running the TF workflow."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict

from tf_agents.agents import create_tf_agency
from tf_agents.prompts import BRIEF_ANALYZER_PROMPT, PROJECT_STRATEGIST_PROMPT
from tf_agents.utils import call_json_llm

__all__ = ["process_brief", "run_brief_workflow"]


async def process_brief(brief_text: str) -> Dict[str, Any]:
    """Run the brief analysis and strategy submission pipeline for a single brief."""

    agency = create_tf_agency()

    analysis_json = await call_json_llm(BRIEF_ANALYZER_PROMPT, brief_text)
    analysis = json.loads(analysis_json)

    await agency.get_response(
        message="Submit analysis",
        tool_choice="submit_brief_analysis",
        inputs={"analysis_json": analysis_json},
        recipient_agent="BriefAnalyzer",
    )

    strategy_json = await call_json_llm(
        PROJECT_STRATEGIST_PROMPT,
        json.dumps(analysis, indent=2),
    )
    strategy = json.loads(strategy_json)

    submission = await agency.get_response(
        message="Submit strategy",
        tool_choice="submit_project_strategy",
        inputs={"strategy_json": strategy_json},
        recipient_agent="ProjectStrategist",
    )

    return {
        "analysis": analysis,
        "strategy": strategy,
        "final_summary": submission.final_output,
    }


def run_brief_workflow(brief_text: str) -> Dict[str, Any]:
    """Synchronous wrapper around :func:`process_brief`."""

    return asyncio.run(process_brief(brief_text))
