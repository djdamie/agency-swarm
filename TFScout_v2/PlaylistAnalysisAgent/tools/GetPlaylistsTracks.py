from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
import json
import time
from typing import Optional, List

class GetPlaylistsTracks(BaseTool):


    """
    This tool retrieves tracks from a specific playlist on various streaming platforms using the Chartmetric API.
    It can fetch both current and past tracks from the playlist.
    """

    id: str = Field(..., description="Chartmetric playlist ID")
    platform: str = Field(..., description="Streaming platform type (spotify, applemusic, deezer, amazon)")
    span: str = Field(..., description="Time span (current, past)")
    storefront: Optional[str] = Field(None, description="Apple Music storefront. Required for Apple Music playlists (e.g., us, ca, br, de, gb)")
    limit: Optional[int] = Field(100, description="Limit of number of matched tracks. Default is 100.")
    offset: Optional[int] = Field(0, description="Offset for pagination. Default is 0.")
    withDetails: Optional[bool] = Field(True, description="Whether the response includes Artists, Album, and audio features information. Default is true.")
    since: Optional[str] = Field(None, description="Only return tracks with removed_at after this date. Only applies to span = past")
    until: Optional[str] = Field(None, description="Only return tracks with added_at before this date. Only applies to span = past")

    def run(self):
        # Load the access token
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
        url = f"https://api.chartmetric.com/api/playlist/{self.platform}/{self.id}/{self.span}/tracks"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "storefront": self.storefront,
            "limit": self.limit,
            "offset": self.offset,
            "withDetails": self.withDetails,
            "since": self.since,
            "until": self.until
        }

        # Remove None values from params
        params = {k: v for k, v in params.items() if v is not None}

        response = requests.get(url, headers=headers, params=params)
        # process_response = self.process_response
        # process_response(response)
        
        # Update last call time
        with open('access_token.json', 'w') as f:
            token_data['last_call_time'] = time.time()
            json.dump(token_data, f)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text}
        
        
    # def process_response(self, response):
    #     """
    #     Process the API response to extract relevant information.
    #     This method can be customized based on specific needs.
    #     """
    #     if 'obj' in response and isinstance(response['obj'], list):
    #         tracks = response['obj']
    #         processed_tracks = []
    #         for track in tracks:
    #             processed_track = {
    #                 "name": track.get('name'),
    #                 "isrc": track.get('isrc'),
    #                 "added_at": track.get('added_at'),
    #                 "position": track.get('position'),
    #                 "spotify_popularity": track.get('spotify_popularity'),
    #                 "artists": track.get('artist_names', []),
    #                 "album": track.get('album_names', []),
    #                 "release_date": track.get('release_dates', []),
    #                 "spotify_uri": f"spotify:track:{track.get('spotify_track_ids', [''])[0]}" if track.get('spotify_track_ids') else None
    #             }
    #             processed_tracks.append(processed_track)
    #         return processed_tracks
    #     else:
    #         return response  # Return the original response if it's not in the expected format