
from tf_agents.agents import create_tf_agency


def test_tf_agency_structure():
    agency = create_tf_agency()
    names = {agent.name for agent in agency.agents.values()}
    assert "BriefAnalyzer" in names
    assert "ProjectStrategist" in names
    assert agency.entry_points[0].name == "BriefAnalyzer"
