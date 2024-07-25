# MusicInsightAgency/ChartmetricExpert/tools/GetArtistFanMetrics.py
from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
import json
import time

class GetArtistFanMetrics(BaseTool):
    """
    This tool retrieves the fan metrics of a given artist from the Chartmetric API.
    Gets an artist's fan metrics for various services.
    
    There are two ways to get fan metrics from each source:
    1. Return all fields (by default).
    2. Return only selected field (by adding `field` parameter).

    Return all fields by default.

    Return only selected field (by adding `field` parameter).
    """
    artist_id: int = Field(..., description="The ID of the artist for whom to retrieve fan metrics.")
    source: str = Field(..., description="Data source. Options are 'spotify', 'deezer', 'facebook', 'twitter', 'instagram', 'youtube_channel', 'youtube_artist', 'wikipedia', 'bandsintown', 'soundcloud', 'tiktok', 'twitch'.")
    since: str = Field(None, description="Start date, in ISO date format (e.g., '2017-03-25').")
    until: str = Field(None, description="End date, in ISO date format (e.g., '2017-03-25'). Default is today.")
    field: str = Field(None, description="Specific stat from source (e.g., 'followers', 'popularity', 'listeners', 'talks', 'subscribers', etc.).")
    latest: bool = Field(False, description="If true, returns latest data point available regardless of date.")
    interpolated: bool = Field(False, description="Returns interpolated data for missing data.")
    isDomainId: bool = Field(False, description="If true, the id passed in the request parameter will be considered the domain ID.")
    code2: str = Field(None, description="ISO code for certain metrics.")
    city_id: int = Field(None, description="Chartmetric city ID for certain metrics.")

    def run(self):
        """
        Executes the main functionality of the tool, retrieving artist fan metrics from Chartmetric.
        """
        print("Executing GetArtistFanMetrics Tool...")
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
        url = f"https://api.chartmetric.com/api/artist/{self.artist_id}/stat/{self.source}"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        params = {
            "since": self.since,
            "until": self.until,
            "field": self.field,
            "latest": self.latest,
            "interpolated": self.interpolated,
            "isDomainId": self.isDomainId,
            "code2": self.code2,
            "city_id": self.city_id
        }

        response = requests.get(url, headers=headers, params={k: v for k, v in params.items() if v is not None})

        # Update the token call time
        with open('access_token.json', 'w') as f:
            token_data['last_call_time'] = time.time()
            json.dump(token_data, f)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text}