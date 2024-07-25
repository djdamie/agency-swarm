from agency_swarm.agents import Agent
from agency_swarm.tools import FileSearch, Retrieval, CodeInterpreter

class TFScoutCEO(Agent):
    def __init__(self):
        super().__init__(
            name="TFScoutCEO",
            description="Central coordinator for the TFScout_v2 agency, specializing in music industry analytics and insights. Responsible for interpreting user requests, delegating tasks to specialized agents for trend analysis, artist discovery, and playlist performance evaluation. Ensures cohesive and data-driven music research outcomes.",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[],
            tools_folder="./tools",
            temperature=0.3,
            max_prompt_tokens=25000,
            model="gpt-4o-mini",
            #response_format={"type": "json_object"}
        )
        
    def response_validator(self, message):
        try:
            # Validate the response structure and content
            if "completed" not in message.lower():
                raise ValueError("Response does not indicate task completion.")
            if "error" in message.lower():
                raise ValueError("Response indicates an error occurred.")
        except Exception as e:
            return f"Error: {e}\nRemember, you must continue sending messages to agents until the task is fully completed."
        return message