"""Prompt templates reused from the legacy TF supervisor workflow."""

from __future__ import annotations

from pathlib import Path

__all__ = [
    "SUPERVISOR_PROMPT",
    "BRIEF_ANALYZER_PROMPT",
    "PROJECT_STRATEGIST_PROMPT",
]

_LEGACY_PROMPTS = Path(__file__).resolve().parents[2] / "Previous Agents" / "tf_supervisor_workflow" / "prompts.py"

if not _LEGACY_PROMPTS.exists():
    raise RuntimeError(f"Legacy prompts file missing at {_LEGACY_PROMPTS}")

# Execute the legacy prompts file in isolated namespace and expose constants
namespace: dict[str, object] = {}
exec(compile(_LEGACY_PROMPTS.read_text(), str(_LEGACY_PROMPTS), "exec"), namespace)

SUPERVISOR_PROMPT: str = namespace["SUPERVISOR_PROMPT"]  # type: ignore[assignment]
BRIEF_ANALYZER_PROMPT: str = namespace["BRIEF_ANALYZER_PROMPT"]  # type: ignore[assignment]
PROJECT_STRATEGIST_PROMPT: str = namespace["PROJECT_STRATEGIST_PROMPT"]  # type: ignore[assignment]
