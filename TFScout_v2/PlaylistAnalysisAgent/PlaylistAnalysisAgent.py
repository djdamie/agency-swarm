from agency_swarm.agents import Agent


class PlaylistAnalysisAgent(Agent):
    def __init__(self):
        super().__init__(
            name="PlaylistAnalysisAgent",
            description="Specialized in analyzing playlists and track performance within them across various platforms.",
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
