# MusicInsightAgency/ChartmetricExpert/tools/GetGenreByID.py

from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
import json
import time

class GetGenreByID(BaseTool):
    """
    This tool retrieves the details of a genre by its ID from the Chartmetric API.
    It handles the API request and manages the access token and rate limiting.

    Parameters:
    genre_id (int): The ID of the genre to retrieve details for.
    """

    genre_id: int = Field(..., description="The ID of the genre to retrieve details for.")

    def run(self):
        """
        Executes the main functionality of the tool, retrieving genre details from Chartmetric.
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
        url = f"https://api.chartmetric.com/api/genres/{self.genre_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)

        # Handle the API response and update last call time
        if response.status_code == 200:
            with open('access_token.json', 'w') as f:
                token_data['last_call_time'] = time.time()
                json.dump(token_data, f)
            return response.json()
        else:
            return {"error": response.text}