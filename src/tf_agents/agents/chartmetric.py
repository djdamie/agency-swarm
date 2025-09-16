"""Factory for the Chartmetric data analysis agent."""

from __future__ import annotations

from typing import Iterable

from agency_swarm import Agent
from agency_swarm.tools.tool_factory import ToolFactory

from tf_agents.instructions import ANR_AGENT_INSTRUCTIONS
from tf_agents.tools.chartmetric import (
    ArtistCareerHistory,
    ArtistCityListeners,
    ArtistFanMetrics,
    ArtistMetadata,
    ArtistPlaylists,
    ArtistTopTracks,
    GeneralSearch,
    SocialAudienceStats,
)

__all__ = ["create_chartmetric_agent"]


_CHARTMETRIC_TOOL_CLASSES: Iterable[type] = (
    GeneralSearch,
    ArtistMetadata,
    ArtistFanMetrics,
    ArtistCityListeners,
    ArtistTopTracks,
    ArtistPlaylists,
    ArtistCareerHistory,
    SocialAudienceStats,
)


def create_chartmetric_agent(
    *,
    name: str = "ChartmetricAnalyst",
    description: str | None = "Analyzes artists and catalogs using Chartmetric APIs",
    instructions: str = ANR_AGENT_INSTRUCTIONS,
    **agent_kwargs,
) -> Agent:
    """Instantiate an Agency Swarm agent wired with Chartmetric tooling."""

    tools = [ToolFactory.adapt_base_tool(tool_cls) for tool_cls in _CHARTMETRIC_TOOL_CLASSES]
    return Agent(
        name=name,
        description=description,
        instructions=instructions,
        tools=tools,
        **agent_kwargs,
    )
