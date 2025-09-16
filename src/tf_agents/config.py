"""Expose Tracks & Fields domain constants for runtime usage."""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from typing import Any

__all__ = [
    "PROJECT_TYPES",
    "MARGIN_STRUCTURE",
    "CUSTOM_CLIENTS",
    "BRIEF_TYPES",
    "MEMBER_TIERS",
    "PRICE_TIERS",
    "WORKFLOW_STATES",
    "SEARCH_TYPES",
    "INTEGRATIONS",
    "FILE_STORAGE_PLATFORMS",
    "EMAIL_TEMPLATES",
    "KNOWLEDGE_BASE",
    "get_project_type",
    "calculate_payout",
]

_TF_CONTEXT_PATH = Path(__file__).resolve().parents[2] / "TF_docs" / "knowledge_base" / "tf_context.py"


def _load_tf_context() -> ModuleType:
    """Dynamically load the legacy `tf_context.py` module."""
    spec = spec_from_file_location("tf_context", _TF_CONTEXT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load tf_context module from {_TF_CONTEXT_PATH}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[arg-type]
    return module


_tf_context = _load_tf_context()

PROJECT_TYPES: dict[str, Any] = getattr(_tf_context, "PROJECT_TYPES")
MARGIN_STRUCTURE: list[tuple[float, float, float]] = getattr(_tf_context, "MARGIN_STRUCTURE")
CUSTOM_CLIENTS: dict[str, Any] = getattr(_tf_context, "CUSTOM_CLIENTS")
BRIEF_TYPES: dict[str, Any] = getattr(_tf_context, "BRIEF_TYPES")
MEMBER_TIERS: list[str] = getattr(_tf_context, "MEMBER_TIERS")
PRICE_TIERS: dict[str, tuple[float, float]] = getattr(_tf_context, "PRICE_TIERS")
WORKFLOW_STATES: dict[str, str] = getattr(_tf_context, "WORKFLOW_STATES")
SEARCH_TYPES: list[str] = getattr(_tf_context, "SEARCH_TYPES")
INTEGRATIONS: dict[str, Any] = getattr(_tf_context, "INTEGRATIONS")
FILE_STORAGE_PLATFORMS: list[str] = getattr(_tf_context, "FILE_STORAGE_PLATFORMS")
EMAIL_TEMPLATES: dict[str, str] = getattr(_tf_context, "EMAIL_TEMPLATES")
KNOWLEDGE_BASE: dict[str, Any] = getattr(_tf_context, "KNOWLEDGE_BASE")
get_project_type = getattr(_tf_context, "get_project_type")
calculate_payout = getattr(_tf_context, "calculate_payout")
