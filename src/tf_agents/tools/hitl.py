"""HITL utilities for the TF workflow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from tf_agents.state import (
    add_missing_info_request,
    append_analysis_session,
    get_state,
    set_confidence_score,
    update_hitl_status,
)

__all__ = [
    "MissingInfoDetector",
    "ConfidenceScorer",
    "BriefEnhancer",
    "record_missing_info",
    "record_analysis_iteration",
]


class MissingInfoDetector:
    """Detects missing critical fields within a brief analysis payload."""

    CRITICAL_FIELDS = {
        "business_brief.budget": {
            "description": "Budget amount for the project",
            "priority": "critical",
            "suggested_values": ["Under $5,000", "$5,000-$50,000", "Over $50,000", "TBD"],
        },
        "business_brief.territory": {
            "description": "Geographic territories where music will be used",
            "priority": "critical",
            "suggested_values": ["United States", "Germany", "United Kingdom", "Global", "Europe"],
        },
        "business_brief.media": {
            "description": "Media channels where music will be used",
            "priority": "critical",
            "suggested_values": ["TV Commercial", "Online Video", "Radio", "Cinema", "Social Media"],
        },
        "business_brief.term": {
            "description": "Duration of music license",
            "priority": "important",
            "suggested_values": ["1 year", "2 years", "3 years", "In perpetuity", "TBD"],
        },
        "creative_brief.genres": {
            "description": "Musical genres or styles needed",
            "priority": "important",
            "suggested_values": ["Pop", "Rock", "Electronic", "Classical", "Hip-Hop", "Folk"],
        },
        "deliverables.submission_deadline": {
            "description": "When music submissions are due",
            "priority": "critical",
            "suggested_values": [],
        },
    }

    def detect(self, analysis: Dict[str, Any]) -> List[str]:
        missing: List[str] = []
        for field_path in self.CRITICAL_FIELDS:
            if self._is_missing(analysis, field_path):
                missing.append(field_path)
        return missing

    def build_request(self, session_id: str, missing_fields: List[str]) -> Dict[str, Any]:
        descriptions = {}
        suggested = {}
        critical_count = 0
        for field in missing_fields:
            info = self.CRITICAL_FIELDS.get(field)
            if not info:
                continue
            descriptions[field] = info["description"]
            suggested[field] = info.get("suggested_values", [])
            if info.get("priority") == "critical":
                critical_count += 1

        if critical_count >= 2:
            priority = "critical"
        elif critical_count == 1:
            priority = "important"
        else:
            priority = "optional"

        return {
            "session_id": session_id,
            "missing_fields": missing_fields,
            "field_descriptions": descriptions,
            "priority": priority,
            "suggested_values": suggested,
            "request_message": self._build_message(missing_fields, priority),
            "created_at": datetime.now().isoformat(),
        }

    def _is_missing(self, analysis: Dict[str, Any], path: str) -> bool:
        parts = path.split(".")
        current: Any = analysis
        try:
            for part in parts:
                current = current.get(part, None)
                if current is None:
                    return True
            if isinstance(current, list):
                return len(current) == 0
            if isinstance(current, str):
                return current.strip() == ""
            return current is None
        except AttributeError:
            return True

    def _build_message(self, missing_fields: List[str], priority: str) -> str:
        names = [self.CRITICAL_FIELDS[f]["description"].lower() for f in missing_fields if f in self.CRITICAL_FIELDS]
        if not names:
            names = [field.replace("_", " ").lower() for field in missing_fields]
        joined = ", ".join(names)
        if priority == "critical":
            return (
                "To provide the best music recommendations, we need some additional information: "
                f"{joined}. This information is critical for accurate project scoping."
            )
        if priority == "important":
            return (
                "We found most key details, but could use clarification on: "
                f"{joined}. This will help us provide more targeted recommendations."
            )
        return (
            "Optional: If available, additional details on "
            f"{joined} would help refine our recommendations."
        )


class ConfidenceScorer:
    """Compute confidence metrics based on extraction metrics."""

    def score(self, analysis: Dict[str, Any]) -> float:
        metrics = analysis.get("extraction_metrics", {})
        score = 0.0
        if analysis.get("json_structure_valid", False):
            score += 0.2
        completion_rate = float(metrics.get("completion_rate", 0))
        score += (completion_rate / 100.0) * 0.3
        if metrics.get("critical_field_success", False):
            score += 0.25
        quality = metrics.get("enhanced_interpretation_quality", "poor")
        if quality == "good":
            score += 0.25
        elif quality == "fair":
            score += 0.15
        return max(0.0, min(1.0, score))


class BriefEnhancer:
    """Utilities to merge human-provided info into a brief analysis."""

    def apply(self, original_brief: str, additional_info: Dict[str, Any]) -> str:
        lines = [original_brief.rstrip(), "", "=== ADDITIONAL INFORMATION PROVIDED ==="]
        for field_path, value in additional_info.items():
            lines.append(f"{self._display_name(field_path)}: {value}")
        return "\n".join(lines)

    def merge_analysis(self, analysis: Dict[str, Any], additional_info: Dict[str, Any]) -> Dict[str, Any]:
        merged = analysis.copy()
        for path, value in additional_info.items():
            self._set_nested_field(merged, path, value)
        merged["extraction_status"] = "enhanced"
        notes = merged.get("extraction_notes", "")
        merged["extraction_notes"] = (notes + " | " if notes else "") + "Enhanced with user-provided information"
        merged["missing_information"] = MissingInfoDetector().detect(merged)
        return merged

    def _set_nested_field(self, data: Dict[str, Any], path: str, value: Any) -> None:
        parts = path.split(".")
        current = data
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = value

    def _display_name(self, path: str) -> str:
        mapping = {
            "business_brief.budget": "Budget",
            "business_brief.territory": "Territory",
            "business_brief.media": "Media Usage",
            "business_brief.term": "License Term",
            "creative_brief.genres": "Musical Genres",
            "deliverables.submission_deadline": "Submission Deadline",
        }
        return mapping.get(path, path.replace("_", " ").title())


def record_missing_info(context, analysis: Dict[str, Any]) -> None:
    """Update context state with missing info results and confidence score."""
    state = get_state(context)
    detector = MissingInfoDetector()
    missing = detector.detect(analysis)
    if missing:
        request = detector.build_request(state.session_id, missing)
        add_missing_info_request(context, request)
        update_hitl_status(context, "pending")
    else:
        update_hitl_status(context, "completed")
    score = ConfidenceScorer().score(analysis)
    set_confidence_score(context, score)


def record_analysis_iteration(context, analysis: Dict[str, Any], iteration: int, additional_info: Dict[str, Any] | None = None) -> None:
    session = {
        "session_id": get_state(context).session_id,
        "iteration": iteration,
        "timestamp": datetime.now().isoformat(),
        "analysis_result": analysis,
        "confidence_score": get_state(context).current_confidence_score,
        "missing_info_detected": MissingInfoDetector().detect(analysis),
        "user_input_provided": additional_info,
    }
    append_analysis_session(context, session)
