"""Long-form instructions for TF agents."""

from __future__ import annotations

from pathlib import Path

from tf_agents.prompts import BRIEF_ANALYZER_PROMPT

__all__ = ["ANR_AGENT_INSTRUCTIONS", "BRIEF_ANALYZER_INSTRUCTIONS"]

_ANR_FILE = Path(__file__).resolve().parents[2] / "Previous Agents" / "previous_agent_instructions" / "AnR_Agent_instructions.md"
if not _ANR_FILE.exists():
    raise RuntimeError(f"Missing AnR agent instructions at {_ANR_FILE}")

ANR_AGENT_INSTRUCTIONS = _ANR_FILE.read_text(encoding="utf-8")

BRIEF_ANALYZER_INSTRUCTIONS = (
    "You are the Tracks & Fields Brief Analyzer. Analyze incoming briefs, extract structured data, and call the `submit_brief_analysis` tool with the full JSON payload. "
    "Ensure the JSON matches the schema described below and capture gaps in the `missing_information` field."
    "\n\nExtraction specification:\n"
    + BRIEF_ANALYZER_PROMPT
)
