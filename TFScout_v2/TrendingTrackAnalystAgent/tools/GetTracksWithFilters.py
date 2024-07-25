from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
import json
import time
from typing import Optional, List

class GetTracksWithFilters(BaseTool):
    """
    This tool retrieves a list of tracks from the Chartmetric API based on various filters.
    """

    limit: Optional[int] = Field(None, description="The number of tracks to return. Maximum 100. Default is 50.")
    offset: Optional[int] = Field(None, description="The offset of entries to be returned. Default is 0.")
    range_period: Optional[str] = Field(None, description="The stat's period used to apply range filters. Default value: 'latest'. Allowed values: 'latest', 'monthly_diff', 'weekly_diff'.")
    sortColumn: Optional[str] = Field(None, description="Column to sort results by. sortColumn must be one of [score, release_date, latest.spotify_playlist_count, latest.spotify_playlist_total_reach, latest.spotify_plays, latest.spotify_popularity, latest.tiktok_posts, latest.tiktok_top_videos_likes, latest.tiktok_top_videos_views, latest.youtube_likes]")
    sortOrderDesc: Optional[bool] = Field(None, description="Whether to sort in descending order. Default is True.")
    genres: Optional[List[int]] = Field(None, description="Chartmetric genre IDs to filter tracks by.")
    artists: Optional[List[int]] = Field(None, description="Chartmetric artist IDs to filter tracks by.")
    shortlistIds: Optional[List[int]] = Field(None, description="Array of shortlist IDs to filter by.")
    min_score: Optional[float] = Field(None, description="Value used to filter tracks by minimum score.")
    max_score: Optional[float] = Field(None, description="Value used to filter tracks by maximum score.")
    min_release_date: Optional[str] = Field(None, description="Value used to filter tracks by minimum release date in YYYY-MM-DD format.")
    max_release_date: Optional[str] = Field(None, description="Value used to filter tracks by maximum release date in YYYY-MM-DD format.")
    max_spotify_plays: Optional[int] = Field(None, description="Value used to filter tracks by maximum spotify_plays. The range_period parameter is applied to this stat.")
    min_spotify_plays: Optional[int] = Field(None, description="Value used to filter tracks by minimum spotify_plays. The range_period parameter is applied to this stat.")
    max_spotify_popularity: Optional[int] = Field(None, description="Value used to filter tracks by maximum spotify_popularity. The range_period parameter is applied to this stat.")
    min_spotify_popularity: Optional[int] = Field(None, description="Value used to filter tracks by minimum spotify_popularity. The range_period parameter is applied to this stat.")
    
    # Add other fields as necessary based on the API documentation

    def run(self):
        """
        Executes the main functionality of the tool, retrieving tracks from Chartmetric.
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
        url = "https://api.chartmetric.com/api/track/list/filter"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "limit": self.limit,
            "offset": self.offset,
            "sortOrderDesc": self.sortOrderDesc,
            "sortColumn": self.sortColumn,
            "range_period": self.range_period,
            "min_score": self.min_score,
            "max_score": self.max_score,
            "min_release_date": self.min_release_date,
            "max_release_date": self.max_release_date,
            "min_spotify_plays": self.min_spotify_plays,
            "max_spotify_plays": self.max_spotify_plays,
            "min_spotify_popularity": self.min_spotify_popularity,
            "max_spotify_popularity": self.max_spotify_popularity,
            # Add other params as necessary based on the API documentation
        }
        
        # Handle list parameters correctly
        if self.genres:
            params["genres[]"] = self.genres
        if self.artists:
            params["artists[]"] = self.artists
        if self.shortlistIds:
            params["shortlistIds[]"] = self.shortlistIds

        # Remove keys with None values to avoid sending them as parameters
        params = {k: v for k, v in params.items() if v is not None}

        response = requests.get(url, headers=headers, params=params)

        # Handle the API response and update last call time
        if response.status_code == 200:
            with open('access_token.json', 'w') as f:
                token_data['last_call_time'] = time.time()
                json.dump(token_data, f)
            return response.json()
        else:
            return {"error": response.text}

# Example usage
if __name__ == "__main__":
    tool = GetTracksWithFilters(
        artists=[209150],
        limit=10,
        offset=0,
        sortColumn="latest.spotify_plays",  # Using the correct format from allowed values
        sortOrderDesc=False,
    )
    result = tool.run()
    print(json.dumps(result, indent=2))