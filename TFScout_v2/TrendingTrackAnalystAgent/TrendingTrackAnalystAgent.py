from agency_swarm.agents import Agent


class TrendingTrackAnalystAgent(Agent):
    def __init__(self):
        super().__init__(
            name="TrendingTrackAnalystAgent",
            description="This agent identifies and analyzes trending music tracks, utilizing APIs like Spotify Web API for real-time music trend data.",
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
