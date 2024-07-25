# MusicInsightAgency/ChartmetricExpert/tools/GetNeighboringArtists.py

from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
import json
import time

class GetNeighboringArtists(BaseTool):
    """
    This tool retrieves neighboring artists for a given artist from the Chartmetric API.
    It handles the API request and manages the access token and rate limiting.

    """

    artist_id: int = Field(..., description="The ID of the artist for whom to retrieve neighboring artists.")
    metric: str = Field(None, description="The metric to determine similarity. Default value is 'cm_artist_rank'.")
    limit: int = Field(10, description="The number of entries to be returned. Default value is 10, max value is 100.")
    type: str = Field(None, description="Should be set to 'genre' if genre-clustering should be applied.")

    def run(self):
        """
        Executes the main functionality of the tool, retrieving neighboring artists from Chartmetric.
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
        url = f"https://api.chartmetric.com/api/artist/{self.artist_id}/neighboring-artists"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "metric": self.metric,
            "limit": self.limit,
            "type": self.type
        }
        response = requests.get(url, headers=headers, params={k: v for k, v in params.items() if v is not None})

        # Handle the API response and update last call time
        if response.status_code == 200:
            with open('access_token.json', 'w') as f:
                token_data['last_call_time'] = time.time()
                json.dump(token_data, f)
            return response.json()
        else:
            return {"error": response.text}