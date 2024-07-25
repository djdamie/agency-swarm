from agency_swarm import BaseTool
from pydantic import BaseModel, Field, validator
import requests
import json
import time

allowed_types = ["all", "artists", "tracks", "albums", "playlists", "curators", "stations", "cities", "songwriters"]
class generalSearch(BaseTool):
    """A general search across various entities like artists, tracks, albums, etc.
        This call can also be used to obtain IDs for cities, artists, playlists, tracks, albums, stations, etc.
    """
    q: str = Field(..., description="The search query (can also search full urls).")
    type: str = Field(default="all", description="The type of search for the query. type must be one of:" + ",".join(allowed_types))
    limit: int = Field(10, description="The number of results to return. Default is 10.")
    offset: int = Field(0, description="The offset for pagination. Default is 0.")

    @validator('type')
    def check_type(cls, v):
        if v not in allowed_types:
            raise ValueError(f"type must be one of {allowed_types}")
        return v

    def run(self):
        with open('access_token.json', 'r') as f:
            token_data = json.load(f)

        access_token = token_data['access_token']
        last_call_time = token_data.get('last_call_time')

        if last_call_time:
            elapsed_time = time.time() - last_call_time
            if elapsed_time < 2:
                time.sleep(2 - elapsed_time)

        url = "https://api.chartmetric.com/api/search"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"q": self.q, "type": self.type, "limit": self.limit, "offset": self.offset}
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            with open('access_token.json', 'w') as f:
                token_data['last_call_time'] = time.time()
                json.dump(token_data, f)
            return response.json()
        else:
            return {"error": response.text}
