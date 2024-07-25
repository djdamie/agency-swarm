# MusicInsightAgency/ChartmetricExpert/tools/GetArtistCareerHistory.py

from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
import json
import time

class GetArtistCareerHistory(BaseTool):
    """
    This tool retrieves an artist's historical career information from the Chartmetric API.
    Understanding an artist's career history is important for assessing their growth and development.

    Parameters:
    id (int): Chartmetric artist ID.
    since (str, optional): Start of the date range in ISO date format (e.g., "2023-05-12").
    until (str, optional): End of the date range in ISO date format (e.g., "2023-07-29"). Default is today.
    limit (int, optional): The number of entries to be returned. Default is 10.
    offset (int, optional): The offset of entries to be returned. Default is 0.
    """

    id: int = Field(..., description="Chartmetric artist ID.")
    since: str = Field(None, description="Start of the date range in ISO date format (e.g., '2023-05-12').")
    until: str = Field(None, description="End of the date range in ISO date format (e.g., '2023-07-29'). Default is today.")
    limit: int = Field(10, description="The number of entries to be returned. Default is 10.")
    offset: int = Field(0, description="The offset of entries to be returned. Default is 0.")

    def run(self):
        """
        Executes the main functionality of the tool, retrieving artist career history from Chartmetric.
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
        url = f"https://api.chartmetric.com/api/artist/{self.id}/career"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "since": self.since,
            "until": self.until,
            "limit": self.limit,
            "offset": self.offset,
        }
        response = requests.get(url, headers=headers, params=params)

        # Handle the API response and update last call time
        if response.status_code == 200:
            with open('access_token.json', 'w') as f:
                token_data['last_call_time'] = time.time()
                json.dump(token_data, f)
            return response.json()
        else:
            return {"error": response.text}