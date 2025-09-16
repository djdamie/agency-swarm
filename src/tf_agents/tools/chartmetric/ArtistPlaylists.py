import json
from typing import ClassVar, Literal, Optional, List, Dict, Any
import requests
from agency_swarm.tools import BaseTool
from pydantic import Field, validator
from tf_agents.utils import get_access_token
import time

# Define valid platform types and statuses per Chartmetric API spec
PlatformType = Literal['spotify', 'applemusic', 'deezer', 'amazon', 'youtube']
StatusType = Literal['current', 'past']

# Define valid sort columns based on the documentation
VALID_SORT_COLUMNS = {
    'spotify': {
        'current': ['added_at', 'code2', 'fdiff_month', 'followers', 'name', 'peak_position', 'position', 'track'],
        'past': ['added_at', 'code2', 'fdiff_month', 'followers', 'name', 'peak_position', 'position', 'removed_at', 'track']
    },
    'applemusic': {
        'current': ['added_at', 'name', 'peak_position', 'position', 'track'],
        'past': ['added_at', 'name', 'peak_position', 'position', 'removed_at', 'track']
    },
    'deezer': {
        'current': ['added_at', 'fdiff_month', 'followers', 'name', 'peak_position', 'track'],
        'past': ['added_at', 'fdiff_month', 'followers', 'name', 'peak_position', 'removed_at', 'track']
    },
    'amazon': {
        'current': ['added_at', 'countries', 'name', 'peak_position', 'track'],
        'past': []  # Amazon past playlists don't support sorting
    },
    'youtube': {
        'current': ['added_at', 'name', 'peak_position', 'track', 'vdiff_month', 'views'],
        'past': ['added_at', 'name', 'peak_position', 'removed_at', 'track', 'vdiff_month', 'views']
    }
}

# Platform-specific allowed parameters
PLATFORM_PARAMS = {
    'spotify': ['editorial', 'personalized', 'chart', 'thisIs', 'newMusicFriday', 'radio', 
                'fullyPersonalized', 'brand', 'majorCurator', 'popularIndie', 'indie', 'audiobook'],
    'applemusic': ['editorial', 'editorialBrand', 'musicBrand', 'nonMusicBrand', 'personalityArtist', 
                   'chart', 'radio', 'indie'],
    'deezer': ['editorial', 'deezerPartner', 'chart', 'hundredPercent', 'brand', 'majorCurator', 
               'popularIndie', 'indie'],
    'amazon': [],  # No special parameters
    'youtube': []  # No special parameters
}

class ArtistPlaylists(BaseTool):
    """
    Retrieves playlists that feature a specific artist using the Chartmetric API.
    Supports Spotify, Apple Music, Deezer, Amazon Music, and YouTube.
    Returns detailed playlist and track information with platform-specific filtering options.
    """
    
    artist_id: int = Field(..., description="Chartmetric artist ID (from GeneralSearch)")
    platform: PlatformType = Field(..., description="Platform source: spotify, applemusic, deezer, amazon, or youtube")
    status: StatusType = Field(..., description="Playlist status: current or past")
    
    # Date filters
    since: Optional[str] = Field(None, description="ISO date YYYY-MM-DD. Return playlists added on or after this date.")
    until: Optional[str] = Field(None, description="ISO date YYYY-MM-DD. Return playlists added on or before this date.")
    
    # Platform-specific filters
    indie: Optional[bool] = Field(None, description="If true, playlist was curated by major labels")
    editorial: Optional[bool] = Field(None, description="If true, includes playlists curated by the platform")
    majorCurator: Optional[bool] = Field(None, description="If true, includes playlists curated by major curators")
    newMusicFriday: Optional[bool] = Field(None, description="Spotify only: Curated selection of new tracks")
    editorialBrand: Optional[bool] = Field(None, description="Apple Music only: Playlists under editorial brands")
    personalized: Optional[bool] = Field(None, description="If true, includes personalized playlists")
    deezerPartner: Optional[bool] = Field(None, description="Deezer only: Playlists by Deezer partners")
    chart: Optional[bool] = Field(None, description="If true, includes playlists based on music charts")
    thisIs: Optional[bool] = Field(None, description="Spotify only: 'This Is' playlists")
    hundredPercent: Optional[bool] = Field(None, description="Deezer only: '100%' playlists")
    radio: Optional[bool] = Field(None, description="If true, includes playlists from radio stations")
    fullyPersonalized: Optional[bool] = Field(None, description="Spotify only: Fully personalized playlists")
    brand: Optional[bool] = Field(None, description="If true, includes playlists related to brands")
    musicBrand: Optional[bool] = Field(None, description="Apple Music only: Music brand playlists")
    nonMusicBrand: Optional[bool] = Field(None, description="Apple Music only: Non-music brand playlists")
    popularIndie: Optional[bool] = Field(None, description="If true, includes popular indie playlists")
    audiobook: Optional[bool] = Field(None, description="Spotify only: Audiobook playlists")
    personalityArtist: Optional[bool] = Field(None, description="Apple Music only: Personality artist playlists")
    
    # Sorting and pagination
    sortColumn: Optional[str] = Field(None, description="Column to sort by (platform/status specific)")
    sortOrderDesc: Optional[bool] = Field(None, description="Sort in descending order (only with sortColumn)")
    limit: Optional[int] = Field(10, description="Number of results (default: 10)")
    offset: Optional[int] = Field(0, description="Offset for pagination (default: 0)")
    
    # Base URL
    base_url: ClassVar[str] = "https://api.chartmetric.com/api"
    
    # Rate limiting
    last_call_time: ClassVar[float] = 0
    rate_limit_seconds: ClassVar[float] = 2

    @validator('sortColumn')
    def validate_sort_column(cls, v, values):
        if v is None:
            return v
        
        platform = values.get('platform')
        status = values.get('status')
        
        if platform and status:
            valid_columns = VALID_SORT_COLUMNS.get(platform, {}).get(status, [])
            if v not in valid_columns:
                raise ValueError(f"Invalid sortColumn '{v}' for {platform}/{status}. Valid options: {valid_columns}")
        
        return v
    
    @validator('sortOrderDesc')
    def validate_sort_order(cls, v, values):
        if v is not None and values.get('sortColumn') is None:
            raise ValueError("sortOrderDesc can only be set when sortColumn is specified")
        return v

    def run(self) -> str:
        """Execute the API request to get artist playlists"""
        # Rate limiting
        current_time = time.time()
        elapsed_time = current_time - self.__class__.last_call_time
        if elapsed_time < self.rate_limit_seconds:
            time.sleep(self.rate_limit_seconds - elapsed_time)
        
        try:
            # Get access token
            token = get_access_token()
            
            # Build URL
            url = f"{self.base_url}/artist/{self.artist_id}/{self.platform}/{self.status}/playlists"
            
            # Build headers
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Build params - only include platform-specific parameters
            params = {
                "limit": self.limit,
                "offset": self.offset
            }
            
            # Add date filters if provided
            if self.since:
                params["since"] = self.since
            if self.until:
                params["until"] = self.until
            
            # Add sorting if provided
            if self.sortColumn:
                params["sortColumn"] = self.sortColumn
                if self.sortOrderDesc is not None:
                    params["sortOrderDesc"] = str(self.sortOrderDesc).lower()
            
            # Add platform-specific parameters
            allowed_params = PLATFORM_PARAMS.get(self.platform, [])
            
            # Map field names to API parameter names
            field_mapping = {
                'indie': 'indie',
                'editorial': 'editorial',
                'majorCurator': 'majorCurator',
                'newMusicFriday': 'newMusicFriday',
                'editorialBrand': 'editorialBrand',
                'personalized': 'personalized',
                'deezerPartner': 'deezerPartner',
                'chart': 'chart',
                'thisIs': 'thisIs',
                'hundredPercent': 'hundredPercent',
                'radio': 'radio',
                'fullyPersonalized': 'fullyPersonalized',
                'brand': 'brand',
                'musicBrand': 'musicBrand',
                'nonMusicBrand': 'nonMusicBrand',
                'popularIndie': 'popularIndie',
                'audiobook': 'audiobook',
                'personalityArtist': 'personalityArtist'
            }
            
            # Add only allowed parameters for this platform
            for field_name, api_param in field_mapping.items():
                value = getattr(self, field_name)
                if value is not None and api_param in allowed_params:
                    params[api_param] = str(value).lower()
            
            # Make request
            response = requests.get(url, headers=headers, params=params)
            
            # Update rate limit timer
            self.__class__.last_call_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract the playlist data
                playlists = data.get('obj', [])
                
                # Create a summary with key information
                summary = {
                    "artist_id": self.artist_id,
                    "platform": self.platform,
                    "status": self.status,
                    "total_playlists": len(playlists),
                    "parameters_used": {k: v for k, v in params.items() if k not in ['limit', 'offset']},
                    "playlists": []
                }
                
                # Extract key fields from each playlist
                for item in playlists:
                    playlist_data = {
                        'playlist_id': item.get('playlist_id') or item.get('id'),
                        'name': item.get('name'),
                        'followers': item.get('followers'),
                        'track_name': item.get('track_name') or item.get('track', {}).get('name'),
                        'track_id': item.get('track_id') or item.get('track', {}).get('id'),
                        'added_at': item.get('added_at'),
                        'position': item.get('position'),
                        'peak_position': item.get('peak_position')
                    }
                    
                    # Add platform-specific fields
                    if self.platform == 'spotify':
                        playlist_data['code2'] = item.get('code2')
                        playlist_data['followers_diff_month'] = item.get('fdiff_month')
                    elif self.platform == 'youtube':
                        playlist_data['views'] = item.get('views')
                        playlist_data['views_diff_month'] = item.get('vdiff_month')
                    elif self.status == 'past':
                        playlist_data['removed_at'] = item.get('removed_at')
                    
                    # Add playlist type indicators
                    if item.get('editorial'):
                        playlist_data['type'] = 'editorial'
                    elif item.get('majorCurator'):
                        playlist_data['type'] = 'major_curator'
                    elif item.get('personalized'):
                        playlist_data['type'] = 'personalized'
                    else:
                        playlist_data['type'] = 'user_created'
                    
                    summary['playlists'].append(playlist_data)
                
                return json.dumps(summary, indent=2)
                
            else:
                error_msg = {
                    "error": f"API request failed with status {response.status_code}",
                    "details": response.text[:1000]
                }
                return json.dumps(error_msg, indent=2)
                
        except Exception as e:
            error_response = {
                "error": "Failed to retrieve playlist data",
                "error_type": type(e).__name__,
                "details": str(e)
            }
            return json.dumps(error_response, indent=2)

if __name__ == "__main__":
    # Test with various parameter combinations
    
    # Test 1: Basic Spotify current playlists
    tool = ArtistPlaylists(
        artist_id=3787,
        platform="spotify",
        status="current",
        editorial=True,
        limit=5
    )
    print("Test 1 - Spotify Editorial:")
    print(tool.run())
    print("\n" + "="*50 + "\n")
    
    # Test 2: Apple Music with sorting
    tool2 = ArtistPlaylists(
        artist_id=3787,
        platform="applemusic", 
        status="current",
        sortColumn="position",
        sortOrderDesc=False,
        limit=5
    )
    print("Test 2 - Apple Music Sorted:")
    print(tool2.run())