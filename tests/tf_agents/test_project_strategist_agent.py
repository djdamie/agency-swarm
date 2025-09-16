from tf_agents.agents import create_project_strategist_agent


def test_project_strategist_agent_tools():
    agent = create_project_strategist_agent()
    tool_names = {tool.name for tool in agent.tools}
    assert "submit_project_strategy" in tool_names
    assert "submit_project_strategy" in agent.instructions
