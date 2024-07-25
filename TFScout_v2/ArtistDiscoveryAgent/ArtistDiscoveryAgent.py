from agency_swarm.agents import Agent


class ArtistDiscoveryAgent(Agent):
    def __init__(self):
        super().__init__(
            name="ArtistDiscoveryAgent",
            description="This agent discovers emerging artists, potentially utilizing social media APIs to gather relevant data on new and upcoming artists.",
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
