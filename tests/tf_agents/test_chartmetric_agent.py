from tf_agents.agents import create_chartmetric_agent


def test_chartmetric_agent_exposes_tools():
    agent = create_chartmetric_agent()
    tool_names = {tool.name for tool in agent.tools}
    expected = {
        "GeneralSearch",
        "ArtistMetadata",
        "ArtistFanMetrics",
        "ArtistCityListeners",
        "ArtistTopTracks",
        "ArtistPlaylists",
        "ArtistCareerHistory",
        "SocialAudienceStats",
    }
    assert expected.issubset(tool_names)
    assert agent.instructions
