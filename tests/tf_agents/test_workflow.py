import json
import pytest

from tf_agents.workflow import process_brief
@pytest.mark.asyncio
async def test_process_brief(monkeypatch):
    responses = iter([
        json.dumps(
            {
                "extraction_status": "complete",
                "brief_quality": "good",
                "business_brief": {"client": "Test Client"},
                "creative_brief": {},
                "contextual_brief": {},
                "technical_brief": {},
                "deliverables": {},
                "competitive_brief": {},
                "missing_information": [],
                "extraction_notes": "",
            }
        ),
        json.dumps(
            {
                "project_type": "Synch A-Type",
                "estimated_payout": 0,
                "margin_percentage": 0.3,
                "workflow_recommendations": [],
                "resource_requirements": [],
                "risk_factors": [],
                "alternative_approaches": [],
                "immediate_actions": [],
            }
        ),
    ])

    async def fake_call_json_llm(system_prompt: str, user_content: str):
        return next(responses)

    monkeypatch.setattr("tf_agents.workflow.call_json_llm", fake_call_json_llm)

    result = await process_brief("dummy brief")

    assert result["analysis"]["business_brief"]["client"] == "Test Client"
    assert result["strategy"]["project_type"] == "Synch A-Type"
    assert result["analysis"].get("missing_information") is not None
    assert result["final_summary"]
