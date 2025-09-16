import os
import sys
import time
from typing import Optional, Literal, ClassVar

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
import json
from helpers import get_access_token

class SocialAudienceStats(BaseTool):
    """
    Tool to fetch social audience stats for an artist from Chartmetric API.
    Supports platforms like Instagram, YouTube, and TikTok.
    """

    artist_id: int = Field(
        ..., 
        description="Artist's Chartmetric ID."
    )
    domain: Literal['instagram', 'youtube', 'tiktok'] = Field(
        ..., 
        description="Social platform to fetch data from."
    )
    since: Optional[str] = Field(
        None, 
        description="Beginning date in ISO date format. Defaults to today."
    )
    until: Optional[str] = Field(
        None, 
        description="End date in ISO date format. Defaults to today."
    )
    audienceType: Literal['followers', 'likes', 'commenters'] = Field(
        ..., 
        description="Specific audience type from source."
    )
    statsType: Literal['country', 'city', 'interest', 'brand', 'language', 'stat', 'demographic'] = Field(
        ..., 
        description="Specific stat type from source."
    )
    offset: Optional[int] = Field(
        0, 
        description="The offset of entries to be returned."
    )
    limit: Optional[int] = Field(
        50, 
        description="The number of entries to be returned."
    )

    # Rate limiting variables
    last_call_time: ClassVar[float] = 0
    rate_limit_seconds: ClassVar[float] = 2  # Rate limit of 1 call every 2 seconds

    def run(self):
        """
        Executes an API call to Chartmetric to fetch social audience stats.

        Returns:
            dict: JSON response containing the social audience stats, or an error message.
        """
        try:
            # Check if we need to wait before making the next API call
            current_time = time.time()
            if current_time - self.__class__.last_call_time < self.rate_limit_seconds:
                time.sleep(self.rate_limit_seconds - (current_time - self.__class__.last_call_time))

            access_token = get_access_token()
            if not access_token:
                return json.dumps({"error": "Unable to get access token. Please check your credentials."})
            
            url = f"https://api.chartmetric.com/api/artist/{self.artist_id}/social-audience-stats"
            headers = {"Authorization": f"Bearer {access_token}"}
            params = {
                "domain": self.domain,
                "since": self.since,
                "until": self.until,
                "audienceType": self.audienceType,
                "statsType": self.statsType,
                "offset": self.offset,
                "limit": self.limit
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
                    "error": f"Failed to fetch social audience stats. Status code: {response.status_code}",
                    "response_text": response.text[:1000]  # First 1000 characters of the response
                }, indent=2)
        
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)

if __name__ == "__main__":
    tool = SocialAudienceStats(
        artist_id=3787, 
        domain='instagram', 
        audienceType='followers', 
        statsType='stat'
    )
    print(tool.run()) 