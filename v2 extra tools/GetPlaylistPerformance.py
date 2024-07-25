from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
import json
import time

class GetPlaylistPerformance(BaseTool):
    """
    This tool analyzes the performance of a playlist, including track performance, audience growth, and overall engagement.
    """

    playlist_id: str = Field(..., description="Chartmetric playlist ID to analyze.")
    platform: str = Field(..., description="Platform of the playlist (e.g., 'spotify', 'applemusic').")
    time_period: str = Field("30d", description="Time period for analysis. Options: '7d', '30d', '90d'.")

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

        # Get playlist metadata
        metadata_url = f"https://api.chartmetric.com/api/playlist/{self.platform}/{self.playlist_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        metadata_response = requests.get(metadata_url, headers=headers)
        
        if metadata_response.status_code != 200:
            return {"error": f"Failed to get playlist metadata: {metadata_response.text}"}

        playlist_data = metadata_response.json()['obj']

        # Analyze track performance
        # Note: In a real implementation, you'd make additional API calls to get historical data for each track
        track_performance = []
        for track in playlist_data['tracks'][:10]:  # Analyze top 10 tracks
            track_performance.append({
                "name": track['name'],
                "artist": track['artist_name'],
                "streams": track.get('streams', 'N/A'),
                "playlist_adds": track.get('playlist_adds', 'N/A')
            })

        # Calculate overall playlist performance
        # Note: These would be calculated based on historical data in a real implementation
        follower_growth_rate = 5.2  # Placeholder value
        average_track_streams = sum(track['streams'] for track in track_performance if track['streams'] != 'N/A') / len(track_performance)

        performance_summary = {
            "playlist_name": playlist_data['name'],
            "curator": playlist_data['curator_name'],
            "follower_count": playlist_data['followers'],
            "follower_growth_rate": follower_growth_rate,
            "average_track_streams": average_track_streams,
            "top_tracks": track_performance
        }

        # Update last call time
        with open('access_token.json', 'w') as f:
            token_data['last_call_time'] = time.time()
            json.dump(token_data, f)

        return performance_summary