import os
import time
from typing import ClassVar, Literal
from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
import json
from helpers import get_access_token

# Define valid search types as Literal type
SearchType = Literal['all', 'artists', 'tracks', 'albums', 'playlists', 'curators', 'stations', 'cities', 'songwriters']

class GeneralSearch(BaseTool):
    """
    Tool to perform general searches using the Chartmetric API search endpoint.
    Can search across multiple entity types including artists, tracks, albums, playlists,
    curators, stations, cities, and songwriters.
    """

    q: str = Field(
        ...,
        description="The search query (can also search full URLs)."
    )
    type: SearchType = Field(
        default='all',
        description="Type of search to perform. Options: all, artists, tracks, albums, playlists, curators, stations, cities, songwriters"
    )
    limit: int = Field(
        default=10,
        description="The number of results to return. Default is 10."
    )
    offset: int = Field(
        default=0,
        description="The offset for pagination. Default is 0."
    )
    base_url: str = Field(
        default="https://api.chartmetric.com/api",
        description="The base URL for the Chartmetric API."
    )

    last_call_time: ClassVar[float] = 0
    rate_limit_seconds: ClassVar[float] = 2

    def run(self):
        """
        Perform a general search using the Chartmetric API.
        """
        # Check if we need to wait before making the next API call
        current_time = time.time()
        if current_time - self.__class__.last_call_time < self.rate_limit_seconds:
            time.sleep(self.rate_limit_seconds - (current_time - self.__class__.last_call_time))

        access_token = get_access_token()
        url = f"{self.base_url}/search"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        params = {
            "q": self.q,
            "type": self.type,
            "limit": self.limit,
            "offset": self.offset
        }

        response = requests.get(url, headers=headers, params=params)

        # Update the last call time after the request
        self.__class__.last_call_time = time.time()

        if response.status_code == 200:
            try:
                json_response = response.json()
                return json.dumps(json_response, indent=2)
            except json.JSONDecodeError as e:
                return json.dumps({
                    "error": "Failed to parse JSON response",
                    "details": str(e),
                    "response_text": response.text[:1000]  # First 1000 characters of the response
                }, indent=2)
        else:
            return json.dumps({
                "error": f"Failed to perform general search. Status code: {response.status_code}",
                "response_text": response.text[:1000]  # First 1000 characters of the response
            }, indent=2)

if __name__ == "__main__":
    # Test the tool
    search_query = "Taylor Swift"
    tool = GeneralSearch(q=search_query, type="artists", limit=5)
    result = tool.run()
    print(result) 