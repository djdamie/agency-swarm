import time
from typing import ClassVar
from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
import json
from tf_agents.utils import get_access_token

class ArtistMetadata(BaseTool):
    """
    Tool to retrieve comprehensive artist metadata from Chartmetric API.
    Provides detailed information about an artist including platform performance,
    social media metrics, audience demographics, and more.
    """

    artist_id: int = Field(
        ...,
        description="The Chartmetric artist ID to retrieve metadata for."
    )
    base_url: str = Field(
        default="https://api.chartmetric.com/api",
        description="The base URL for the Chartmetric API."
    )

    last_call_time: ClassVar[float] = 0
    rate_limit_seconds: ClassVar[float] = 2

    def run(self):
        """
        Retrieve artist metadata from Chartmetric API.
        """
        # Check if we need to wait before making the next API call
        current_time = time.time()
        if current_time - self.__class__.last_call_time < self.rate_limit_seconds:
            time.sleep(self.rate_limit_seconds - (current_time - self.__class__.last_call_time))

        access_token = get_access_token()
        url = f"{self.base_url}/artist/{self.artist_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)

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
                "error": f"Failed to retrieve artist metadata. Status code: {response.status_code}",
                "response_text": response.text[:1000]  # First 1000 characters of the response
            }, indent=2)

if __name__ == "__main__":
    # Test the tool with Taylor Swift's Chartmetric ID
    tool = ArtistMetadata(artist_id=3281) # Taylor Swift's Chartmetric ID
    result = tool.run()
    print(result) 