import time
from typing import ClassVar, Optional

from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
import json
from tf_agents.utils import get_access_token

class ArtistCareerHistory(BaseTool):
    """
    This tool retrieves an artist's historical career information from the Chartmetric API.
    Understanding an artist's career history is important for assessing their growth and development.
    """

    artist_id: int = Field(..., description="Chartmetric artist ID.")
    since: Optional[str] = Field(None, description="Start of the date range in ISO date format (e.g., '2023-05-12').")
    until: Optional[str] = Field(None, description="End of the date range in ISO date format (e.g., '2025-01-01'). Default is today.")
    limit: int = Field(10, description="The number of entries to be returned. Default is 10.")
    offset: int = Field(0, description="The offset of entries to be returned. Default is 0.")
    base_url: str = Field(
        default="https://api.chartmetric.com/api",
        description="The base URL for the Chartmetric API."
    )

    last_call_time: ClassVar[float] = 0
    rate_limit_seconds: ClassVar[float] = 2  # Rate limit of 1 call every 2 seconds

    def run(self):
        """
        Executes the main functionality of the tool, retrieving artist career history from Chartmetric.
        """
        # Check if we need to wait before making the next API call
        current_time = time.time()
        if current_time - self.__class__.last_call_time < self.rate_limit_seconds:
            time.sleep(self.rate_limit_seconds - (current_time - self.__class__.last_call_time))

        access_token = get_access_token()
        url = f"{self.base_url}/artist/{self.artist_id}/career"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        params = {
            "since": self.since,
            "until": self.until,
            "limit": self.limit,
            "offset": self.offset,
        }

        # Remove None values from params
        params = {k: v for k, v in params.items() if v is not None}

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
                "error": f"Failed to retrieve artist career history. Status code: {response.status_code}",
                "response_text": response.text[:1000]  # First 1000 characters of the response
            }, indent=2)

if __name__ == "__main__":
    # Test the tool
    artist_id = 2762  # Taylor Swift's Chartmetric ID
    tool = ArtistCareerHistory(artist_id=artist_id)
    result = tool.run()
    print(result)