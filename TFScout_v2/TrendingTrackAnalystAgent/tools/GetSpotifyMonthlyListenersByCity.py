from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
import json
import time

class GetSpotifyMonthlyListenersByCity(BaseTool):
    """
    This tool retrieves Spotify's "Where people listen" stats, showing cities on each day for a given artist.
    
    """

    id: int = Field(..., description="Chartmetric artist ID.")
    since: str = Field(..., description="Beginning date in ISO date format (e.g., '2017-03-25'). This parameter is required.")
    until: str = Field(None, description="End date in ISO date format (e.g., '2017-03-25'). Default is today.")
    limit: int = Field(10, description="The number of entries to be returned. Default is 10, max 50.")
    offset: int = Field(0, description="The offset of entries to be returned. Default value: 0.")
    latest: bool = Field(False, description="If true, returns latest data point available regardless of date. If this is true, since/until parameters will be ignored.")

    def run(self):
        """
        Executes the main functionality of the tool, retrieving Spotify Monthly Listeners by City data from Chartmetric.
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
        url = f"https://api.chartmetric.com/api/artist/{self.id}/where-people-listen"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "since": self.since,
            "until": self.until,
            "limit": self.limit,
            "offset": self.offset,
            "latest": self.latest
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