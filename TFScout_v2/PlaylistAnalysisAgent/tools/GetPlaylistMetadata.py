from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
import json
import time

class GetPlaylistMetadata(BaseTool):
    """
    Retrieves metadata for a specified playlist from the Chartmetric API.
    This call requires a playlist ID, which can be obtained using the GetPlaylistIDs or generalSearch tools.

    Parameters:
    id (str): Chartmetric playlist ID.
    platform (str): Streaming platform type (e.g., spotify, applemusic, deezer, amazon, youtube).
    storefront (str, optional): Apple Music storefront. Required for Apple Music playlists.
    """

    id: str = Field(..., description="Chartmetric playlist ID.")
    platform: str = Field(..., description="Streaming platform type (e.g., spotify, applemusic, deezer, amazon, youtube).")
    storefront: str = Field(None, description="Apple Music storefront. Required for Apple Music playlists.")

    def run(self):
        """
        Executes the main functionality of the tool, retrieving playlist metadata from Chartmetric.
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
        url = f"https://api.chartmetric.com/api/playlist/{self.platform}/{self.id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"storefront": self.storefront} if self.storefront else {}

        response = requests.get(url, headers=headers, params=params)

        # Handle the API response and update last call time
        if response.status_code == 200:
            with open('access_token.json', 'w') as f:
                token_data['last_call_time'] = time.time()
                json.dump(token_data, f)
            return response.json()
        else:
            return {"error": response.text}
        