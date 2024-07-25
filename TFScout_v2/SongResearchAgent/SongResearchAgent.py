from agency_swarm.agents import Agent


class SongResearchAgent(Agent):
    def __init__(self):
        super().__init__(
            name="SongResearchAgent",
            description="Specialized in analyzing songs and finding other similar songs that match a descrition or brief.",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[],
            tools_folder="./tools",
            temperature=0.3,
            max_prompt_tokens=25000,
            model="gpt-4o-mini",
            response_format={"type": "json_object"}
        )
        
    def response_validator(self, message):
        return message
