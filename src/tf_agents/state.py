"""Context helpers for storing TF workflow state in Agency Swarm."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agency_swarm.context import MasterContext

__all__ = [
    "STATE_KEY",
    "TFWorkflowState",
    "initialize_state",
    "get_state",
    "set_brief_analysis",
    "get_brief_analysis",
    "set_project_strategy",
    "get_project_strategy",
    "add_missing_info_request",
    "clear_missing_info_requests",
    "update_hitl_status",
    "get_hitl_status",
    "set_confidence_score",
    "get_confidence_score",
    "append_analysis_session",
]

STATE_KEY = "tf_workflow"


@dataclass
class TFWorkflowState:
    """In-memory representation of the workflow state stored in `MasterContext`."""

    brief_analysis: Optional[Dict[str, Any]] = None
    project_strategy: Optional[Dict[str, Any]] = None
    missing_info_requests: List[Dict[str, Any]] = field(default_factory=list)
    analysis_sessions: List[Dict[str, Any]] = field(default_factory=list)
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hitl_status: str = "pending"
    current_confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "brief_analysis": self.brief_analysis,
            "project_strategy": self.project_strategy,
            "missing_info_requests": self.missing_info_requests,
            "analysis_sessions": self.analysis_sessions,
            "session_id": self.session_id,
            "hitl_status": self.hitl_status,
            "current_confidence_score": self.current_confidence_score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TFWorkflowState":
        return cls(
            brief_analysis=data.get("brief_analysis"),
            project_strategy=data.get("project_strategy"),
            missing_info_requests=list(data.get("missing_info_requests", [])),
            analysis_sessions=list(data.get("analysis_sessions", [])),
            session_id=data.get("session_id") or str(uuid.uuid4()),
            hitl_status=data.get("hitl_status", "pending"),
            current_confidence_score=float(data.get("current_confidence_score", 0.0)),
        )


def initialize_state(context: MasterContext, *, session_id: Optional[str] = None) -> TFWorkflowState:
    """Ensure the TF workflow state exists in the given context."""

    existing = context.user_context.get(STATE_KEY)
    if isinstance(existing, dict):
        state = TFWorkflowState.from_dict(existing)
        if session_id and state.session_id != session_id:
            state.session_id = session_id
    else:
        state = TFWorkflowState(session_id=session_id or str(uuid.uuid4()))

    context.user_context[STATE_KEY] = state.to_dict()
    return state


def get_state(context: MasterContext) -> TFWorkflowState:
    """Retrieve the TF workflow state, creating defaults if needed."""

    return initialize_state(context)


def _write_state(context: MasterContext, state: TFWorkflowState) -> None:
    context.user_context[STATE_KEY] = state.to_dict()


def set_brief_analysis(context: MasterContext, analysis: Dict[str, Any]) -> None:
    state = get_state(context)
    state.brief_analysis = analysis
    _write_state(context, state)


def get_brief_analysis(context: MasterContext) -> Optional[Dict[str, Any]]:
    return get_state(context).brief_analysis


def set_project_strategy(context: MasterContext, strategy: Dict[str, Any]) -> None:
    state = get_state(context)
    state.project_strategy = strategy
    _write_state(context, state)


def get_project_strategy(context: MasterContext) -> Optional[Dict[str, Any]]:
    return get_state(context).project_strategy


def add_missing_info_request(context: MasterContext, request: Dict[str, Any]) -> None:
    state = get_state(context)
    state.missing_info_requests.append(request)
    _write_state(context, state)


def clear_missing_info_requests(context: MasterContext) -> None:
    state = get_state(context)
    state.missing_info_requests.clear()
    _write_state(context, state)


def update_hitl_status(context: MasterContext, status: str) -> None:
    state = get_state(context)
    state.hitl_status = status
    _write_state(context, state)


def get_hitl_status(context: MasterContext) -> str:
    return get_state(context).hitl_status


def set_confidence_score(context: MasterContext, score: float) -> None:
    state = get_state(context)
    state.current_confidence_score = score
    _write_state(context, state)


def get_confidence_score(context: MasterContext) -> float:
    return get_state(context).current_confidence_score



def append_analysis_session(context: MasterContext, session_record: Dict[str, Any]) -> None:
    state = get_state(context)
    state.analysis_sessions.append(session_record)
    _write_state(context, state)
