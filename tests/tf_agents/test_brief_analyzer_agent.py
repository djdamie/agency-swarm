import pytest

from tf_agents.agents import create_brief_analyzer_agent


@pytest.fixture
def brief_agent():
    return create_brief_analyzer_agent()


def test_brief_analyzer_agent_tools(brief_agent):
    tool_names = {tool.name for tool in brief_agent.tools}
    assert tool_names == {
        "generate_brief_analysis",
        "submit_brief_analysis",
        "merge_additional_info",
        "show_missing_info",
    }
