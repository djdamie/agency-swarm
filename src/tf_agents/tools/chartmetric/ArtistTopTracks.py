import json
from typing import ClassVar, Optional, List, Dict, Any, Literal
import requests
from agency_swarm.tools import BaseTool
from pydantic import Field
from tf_agents.utils import get_access_token

# Define valid artist types per Chartmetric API spec
ArtistType = Literal[
    'main',     # tracks where the artist is primary
    'featured'  # tracks where the artist is featured
]

# Define fields to sort by for top tracks
SortBy = Literal[
    'streams',    # sort by sp_streams
    'popularity'  # sort by sp_popularity
]

class ArtistTopTracks(BaseTool):
    """
    Retrieves key track statistics for a given artist using the Chartmetric API.
    Supports filtering by artist role (main or featured), basic pagination,
    and optional auto-paging with sorting to find top tracks by streams or popularity.
    Returns a minimal summary of selected fields to conserve context tokens.
    """
    artist_id: int = Field(..., description="Chartmetric artist ID (from GeneralSearch)")
    artist_type: Optional[ArtistType] = Field(
        None,
        description="Filter by artist role on track: 'main' or 'featured' (omit for both)"
    )
    limit: Optional[int] = Field(
        10,
        description="Number of top tracks to return when sorting, or max entries when not sorting (default: 10)"
    )
    offset: Optional[int] = Field(
        0,
        description="Offset for pagination (default: 0)"
    )
    sort_by: Optional[SortBy] = Field(
        None,
        description="If set, auto-pages through all tracks and returns top N by 'streams' or 'popularity' desc"
    )

    # Base URL for Chartmetric API
    base_url: ClassVar[str] = "https://api.chartmetric.com"
    # Chartmetric max page size for tracks endpoint
    max_page_size: ClassVar[int] = 100

    def run(self) -> str:
        # Authenticate
        try:
            token = get_access_token()
        except Exception as e:
            return json.dumps({"error": "Auth error", "details": str(e)}, indent=2)

        # Helper to fetch a page and return list of summaries
        def fetch_page(page_limit: int, page_offset: int) -> List[Dict[str, Any]]:
            path = f"/api/artist/{self.artist_id}/tracks"
            params = [f"limit={page_limit}", f"offset={page_offset}"]
            if self.artist_type:
                params.append(f"artist_type={self.artist_type}")
            url = f"{self.base_url}{path}?{'&'.join(params)}"
            headers = {"Authorization": f"Bearer {token}"}
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            payload = resp.json()
            entries = payload.get('obj', payload.get('data', []))
            result = []
            for item in entries:
                stats = item.get('cm_statistics', {})
                summary = {
                    'id': item.get('id'),
                    'isrc': item.get('isrc'),
                    'artist_type': item.get('artist_type'),
                    'cm_artist': item.get('cm_artist'),
                    'artist_names': item.get('artist_names'),
                    'spotify_track_ids': item.get('spotify_track_ids'),
                    'album_label': item.get('album_label'),
                    'release_dates': item.get('release_dates'),
                    'name': item.get('name'),
                    'cm_track': stats.get('cm_track'),
                    'num_sp_editorial_playlists': stats.get('num_sp_editorial_playlists'),
                    'num_sp_playlists': stats.get('num_sp_playlists'),
                    'sp_popularity': stats.get('sp_popularity'),
                    'sp_streams': stats.get('sp_streams'),
                    'tags': item.get('tags')
                }
                result.append(summary)
            return result

        # If sorting requested, auto-page through all tracks
        if self.sort_by:
            all_tracks: List[Dict[str, Any]] = []
            curr_offset = self.offset or 0
            
            # Fetch all tracks with pagination
            while True:
                try:
                    batch = fetch_page(self.max_page_size, curr_offset)
                except requests.RequestException as e:
                    return json.dumps({"error": "HTTP request error", "details": str(e)}, indent=2)
                if not batch:
                    break
                all_tracks.extend(batch)
                if len(batch) < self.max_page_size:
                    break
                curr_offset += self.max_page_size
            
            # Sort by the requested field
            if self.sort_by == 'streams':
                all_tracks.sort(key=lambda x: x.get('sp_streams') or 0, reverse=True)
            else:  # popularity
                all_tracks.sort(key=lambda x: x.get('sp_popularity') or 0, reverse=True)
            
            # Return top N
            summary = all_tracks[:self.limit]
        else:
            # Single-page fetch with user-specified limit/offset
            try:
                summary = fetch_page(self.limit, self.offset or 0)
            except requests.RequestException as e:
                return json.dumps({"error": "HTTP request error", "details": str(e)}, indent=2)

        return json.dumps(summary, indent=2)

if __name__ == "__main__":
    # Example: Top 10 most streamed tracks
    tool = ArtistTopTracks(
        artist_id=3787,
        artist_type='main',
        limit=10,
        sort_by='streams'
    )
    print(tool.run())
