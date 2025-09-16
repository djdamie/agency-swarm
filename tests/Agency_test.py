import asyncio
from pathlib import Path
import json

from tf_agents.agents import create_tf_agency
from tf_agents.prompts import BRIEF_ANALYZER_PROMPT
from tf_agents.utils import call_json_llm

BRIEF_PATH = Path("TF_docs/knowledge_base/email_briefs_txt/aldi_gutes_fuer_alle_email.txt")

async def run_analysis():
    agency = create_tf_agency()
    brief_text = BRIEF_PATH.read_text(encoding="utf-8")

    # 1) Call Groq/OpenAI yourself to generate the structured JSON.
    analysis_json = await call_json_llm(BRIEF_ANALYZER_PROMPT, brief_text)

    # 2) Submit that JSON via the analyzer tool.
    result = await agency.get_response(
        message="Submit analysis",
        tool_choice="submit_brief_analysis",
        inputs={"analysis_json": analysis_json},
    )

    print("Brief analyzer final output:", result.final_output)
    print("Structured JSON:", json.loads(analysis_json))

if __name__ == "__main__":
    asyncio.run(run_analysis())
