import time
from typing import ClassVar, Optional
from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
import json
from tf_agents.utils import get_access_token

class ArtistCityListeners(BaseTool):
    """
    Tool to retrieve an artist's Spotify listeners by city using Chartmetric's "Where people listen" stats.
    Returns data for top 50 cities on each day.
    """

    artist_id: int = Field(
        ...,
        description="The Chartmetric artist ID to retrieve city listener data for"
    )
    since: str = Field(
        ...,
        description="Beginning date in ISO date format (e.g. '2017-03-25'). Required parameter."
    )
    until: Optional[str] = Field(
        None,
        description="End date in ISO date format (e.g. '2017-03-25'). Defaults to today if not specified."
    )
    limit: Optional[int] = Field(
        10,
        description="The number of entries to return (default 10, max 50)"
    )
    offset: Optional[int] = Field(
        0,
        description="The offset of entries to be returned"
    )
    latest: Optional[bool] = Field(
        False,
        description="If true, returns latest data point available regardless of date. If true, since/until parameters will be ignored."
    )
    base_url: str = Field(
        default="https://api.chartmetric.com/api",
        description="The base URL for the Chartmetric API."
    )

    last_call_time: ClassVar[float] = 0
    rate_limit_seconds: ClassVar[float] = 2

    def run(self):
        """
        Retrieve artist listeners by city data from Chartmetric API.
        """
        # Rate limiting
        current_time = time.time()
        if current_time - self.__class__.last_call_time < self.rate_limit_seconds:
            time.sleep(self.rate_limit_seconds - (current_time - self.__class__.last_call_time))

        access_token = get_access_token()
        
        # Endpoint for where-people-listen stats
        url = f"{self.base_url}/artist/{self.artist_id}/where-people-listen"
        
        # Build params dict, only including non-None values
        params = {"since": self.since}
        if self.until is not None:
            params["until"] = self.until
        if self.limit is not None:
            params["limit"] = self.limit
        if self.offset is not None:
            params["offset"] = self.offset
        if self.latest:
            params["latest"] = "true"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
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
                    "response_text": response.text[:1000]
                }, indent=2)
        else:
            return json.dumps({
                "error": f"Failed to retrieve city listeners data. Status code: {response.status_code}",
                "response_text": response.text[:1000]
            }, indent=2)

if __name__ == "__main__":
    # Test the tool with provided Chartmetric ID
    from datetime import datetime, timedelta
    
    tool = ArtistCityListeners(
        artist_id=3787,  # Provided Chartmetric ID
        since="2024-01-01",  # This will be ignored when latest=True
        latest=True,  # Get most recent data point
        limit=1  # Get max number of cities
    )
    result = tool.run()
    print(result) 