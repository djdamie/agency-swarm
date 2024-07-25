from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
import json
import time
from typing import Optional
from enum import Enum

class SpotifySortColumn(str, Enum):
    active_ratio = "active_ratio"
    last_updated = "last_updated"
    num_track = "num_track"
    fdiff_week = "fdiff_week"
    fdiff_percent_week = "fdiff_percent_week"
    fdiff_month = "fdiff_month"
    fdiff_percent_month = "fdiff_percent_month"
    followers = "followers"
    playlist_updated = "playlist_updated"

class GetPlaylistIDs(BaseTool):
    """
    This tool retrieves a list of playlists from various platforms. The retrieved playlist IDs are required for other playlist-related calls. Playlist IDs can also be obtained using the generalSearch tool.
    """

    platform: str = Field(..., description="The streaming platform to get playlists for (allowed values: spotify, itunes, deezer, amazon, youtube).")
    sortColumn: Optional[SpotifySortColumn] = Field(None, description="Column to sort by for Spotify playlists. Each platform supports different sort columns.")
    sortOrderDesc: Optional[bool] = Field(None, description="Whether to sort in descending order. Default is true.")
    code2: Optional[str] = Field(None, description="Country code.")
    tagIds: Optional[str] = Field(None, description="Playlist tag IDs.")
    curatorIds: Optional[str] = Field(None, description="Spotify's user IDs.")
    limit: Optional[int] = Field(None, description="The number of entries to be returned. Maximum 100. Default is 10.")
    offset: Optional[int] = Field(None, description="The offset of entries to be returned. Default value is 0.")
    indie: Optional[bool] = Field(None, description="If the playlist was curated by indie. Set to false to exclude these results.")
    majorCurator: Optional[bool] = Field(None, description="If the playlist was curated by major labels. Set to false to exclude these results.")
    editorial: Optional[bool] = Field(None, description="If the playlist was curated by editorials. Set to false to exclude these results.")
    newMusicFriday: Optional[bool] = Field(None, description="A curated selection of Spotify's most anticipated new tracks of the week. Set to false to exclude these results.")

    def run(self):
        """
        Executes the main functionality of the tool, retrieving playlist IDs from Chartmetric.
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
        url = f"https://api.chartmetric.com/api/playlist/{self.platform}/lists"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "sortColumn": self.sortColumn.value if self.sortColumn else None,
            "sortOrderDesc": self.sortOrderDesc,
            "code2": self.code2,
            "tagIds": self.tagIds,
            "curatorIds": self.curatorIds,
            "limit": self.limit,
            "offset": self.offset,
            "indie": self.indie,
            "majorCurator": self.majorCurator,
            "editorial": self.editorial,
            "newMusicFriday": self.newMusicFriday
        }
        
        # Remove None values from params
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