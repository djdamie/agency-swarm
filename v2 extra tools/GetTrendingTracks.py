from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
import json
import time
from datetime import datetime, timedelta

class GetTrendingTracks(BaseTool):
    """
    This tool identifies trending tracks from emerging artists based on specific criteria including genre, region, and play count.
    """

    genres: list = Field(..., description="List of genres to filter tracks by (e.g., ['electronic', 'hip hop']).")
    regions: list = Field(..., description="List of regions to check popularity in (e.g., ['DE', 'FR', 'UK']).")
    min_play_count: int = Field(..., description="Minimum Spotify play count.")
    max_play_count: int = Field(..., description="Maximum Spotify play count.")
    days_since_release: int = Field(90, description="Maximum number of days since track release.")
    limit: int = Field(50, description="Number of tracks to return.")

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

        headers = {"Authorization": f"Bearer {access_token}"}

        # Step 1: Get genre IDs
        genre_ids = self.get_genre_ids(headers)

        # Step 2: Get tracks with filters
        tracks = self.get_filtered_tracks(headers, genre_ids)

        # Step 3: Filter tracks by play count and check regional popularity
        trending_tracks = self.filter_and_check_regional_popularity(headers, tracks)

        # Update last call time
        with open('access_token.json', 'w') as f:
            token_data['last_call_time'] = time.time()
            json.dump(token_data, f)

        return trending_tracks

    def get_genre_ids(self, headers):
        genre_ids = []
        for genre in self.genres:
            response = requests.get(f"https://api.chartmetric.com/api/genres?name={genre}", headers=headers)
            if response.status_code == 200:
                genres = response.json().get('obj', [])
                if genres:
                    genre_ids.append(str(genres[0]['id']))
        return genre_ids

    def get_filtered_tracks(self, headers, genre_ids):
        url = "https://api.chartmetric.com/api/track/list/filter"
        params = {
            "genres[]": genre_ids,
            "min_release_date": (datetime.now() - timedelta(days=self.days_since_release)).strftime('%Y-%m-%d'),
            "limit": self.limit,
            "sortColumn": "latest.spotify_plays",
            "sortOrderDesc": True
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get('obj', [])
        return []

    def filter_and_check_regional_popularity(self, headers, tracks):
        trending_tracks = []
        for track in tracks:
            spotify_plays = track.get('latest', {}).get('spotify_plays', 0)
            if self.min_play_count <= spotify_plays <= self.max_play_count:
                # Check regional popularity
                artist_id = track.get('artist_chart_id')
                if self.check_regional_popularity(headers, artist_id):
                    trending_tracks.append({
                        "track_name": track.get('name'),
                        "artist_name": track.get('artist_name'),
                        "release_date": track.get('release_date'),
                        "spotify_plays": spotify_plays,
                        "spotify_uri": track.get('spotify_uri')
                    })
            if len(trending_tracks) >= self.limit:
                break
        return trending_tracks

    def check_regional_popularity(self, headers, artist_id):
        url = f"https://api.chartmetric.com/api/artist/{artist_id}/where-people-listen"
        params = {"since": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            cities = response.json().get('obj', [])
            for city in cities:
                if any(region in city.get('country_code', '') for region in self.regions):
                    return True
        return False