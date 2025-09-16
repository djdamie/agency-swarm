"""Top-level TF agency factory."""

from __future__ import annotations

from agency_swarm import Agency

from tf_agents.agents.brief_analyzer import create_brief_analyzer_agent
from tf_agents.agents.project_strategist import create_project_strategist_agent

__all__ = ["create_tf_agency"]


def create_tf_agency(name: str = "TF_Supervisor_Agency") -> Agency:
    brief_analyzer = create_brief_analyzer_agent()
    strategist = create_project_strategist_agent()
    return Agency(
        brief_analyzer,
        communication_flows=[brief_analyzer > strategist],
        name=name,
    )
