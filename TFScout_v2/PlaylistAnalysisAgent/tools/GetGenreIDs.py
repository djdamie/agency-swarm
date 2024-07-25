from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
import json
import time

class GetGenreIDs(BaseTool):
    """
    This tool retrieves a list of genre IDs from the Chartmetric API.
    It handles the API request and manages the access token and rate limiting.

    Parameters:
    name (str, optional): Genre name. If no name is passed, it returns all available genres.
    """

    name: str = Field(None, description="Genre name. If no name is passed, it returns all available genres.")

    def run(self):
        """
        Executes the main functionality of the tool, retrieving genre IDs from Chartmetric.
        """

        # Load the access token from file
        with open('access_token.json', 'r') as f:
            token_data = json.load(f)
        
        access_token = token_data['access_token']
        last_call_time = token_data.get('last_call_time')

        # Enforce rate limiting
        if last_call_time:
            elapsed_time = time.time() - last_call_time
            if elapsed_time < 2:
                time.sleep(2 - elapsed_time)

        # Construct the API request
        url = "https://api.chartmetric.com/api/genres"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"name": self.name}
        response = requests.get(url, headers=headers, params={k: v for k, v in params.items() if v is not None})

        # Handle the API response and update last call time
        if response.status_code == 200:
            with open('access_token.json', 'w') as f:
                token_data['last_call_time'] = time.time()
                json.dump(token_data, f)
            return response.json()
        else:
            return {"error": response.text}