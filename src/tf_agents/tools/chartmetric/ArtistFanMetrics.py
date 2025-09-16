import time
from typing import Optional, ClassVar
from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
import json
from tf_agents.utils import get_access_token

class ArtistFanMetrics(BaseTool):
    """
    Tool to retrieve fan metrics for an artist from Chartmetric API.
    Fetches detailed fan engagement and growth metrics for specific platforms/sources.
    Uses the /artist/:id/stat/:source endpoint for each requested platform.
    """

    artist_id: int = Field(
        ...,
        description="The Chartmetric artist ID to retrieve fan metrics for."
    )
    since: str = Field(
        ...,
        description="Start date for the metrics in YYYY-MM-DD format."
    )
    until: str = Field(
        ...,
        description="End date for the metrics in YYYY-MM-DD format."
    )
    sources: Optional[str] = Field(
        "spotify",
        description="Comma-separated list of sources: spotify, deezer, facebook, twitter, instagram, youtube_channel, youtube_artist, wikipedia, bandsintown, soundcloud, tiktok, twitch"
    )
    base_url: str = Field(
        default="https://api.chartmetric.com/api",
        description="The base URL for the Chartmetric API."
    )

    last_call_time: ClassVar[float] = 0
    rate_limit_seconds: ClassVar[float] = 2

    def run(self):
        """
        Retrieve fan metrics from Chartmetric API for each specified source.
        """
        # Check if we need to wait before making the next API call
        current_time = time.time()
        if current_time - self.__class__.last_call_time < self.rate_limit_seconds:
            time.sleep(self.rate_limit_seconds - (current_time - self.__class__.last_call_time))

        access_token = get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Parse sources
        source_list = [s.strip() for s in self.sources.split(',')]
        
        # Collect metrics from all sources
        all_metrics = {}
        errors = []
        
        for source in source_list:
            url = f"{self.base_url}/artist/{self.artist_id}/stat/{source}"
            params = {
                "since": self.since,
                "until": self.until,
            }

            response = requests.get(url, headers=headers, params=params)
            
            # Update the last call time after each request
            self.__class__.last_call_time = time.time()
            
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    all_metrics[source] = json_response
                except json.JSONDecodeError as e:
                    errors.append({
                        "source": source,
                        "error": "Failed to parse JSON response",
                        "details": str(e)
                    })
            else:
                errors.append({
                    "source": source,
                    "status_code": response.status_code,
                    "error": response.text[:500]
                })
            
            # Rate limit between requests
            if source != source_list[-1]:  # Don't sleep after last request
                time.sleep(self.rate_limit_seconds)
        
        # Return combined results
        result = {
            "artist_id": self.artist_id,
            "date_range": {
                "since": self.since,
                "until": self.until
            },
            "sources_requested": source_list,
            "sources_retrieved": list(all_metrics.keys()),
            "data": all_metrics
        }
        
        if errors:
            result["errors"] = errors
            
        return json.dumps(result, indent=2)

if __name__ == "__main__":
    # Test the tool with Taylor Swift's Chartmetric ID
    from datetime import datetime, timedelta
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    tool = ArtistFanMetrics(
        artist_id=2762,  # Taylor Swift's Chartmetric ID
        since=start_date,
        until=end_date,
        sources="spotify,youtube_channel,instagram"
    )
    result = tool.run()
    print(result) 