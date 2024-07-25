from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import Optional, Literal
import requests
import json
import time

class GetTracksPlaylistHistory(BaseTool):
    """
    This tool retrieves a list of playlists featuring a specific track, filtering by different parameters from the Chartmetric API.
    """

    id: int = Field(..., description="Chartmetric track ID")
    platform: Literal["spotify", "applemusic", "deezer", "amazon"] = Field(..., description="Streaming platform type")
    status: Literal["current", "past"] = Field(..., description="Playlist status")
    since: Optional[str] = Field(None, description="Start date of the added/removed date, in ISO date format (e.g. '2017-03-25'). Default value is 'today'")
    until: Optional[str] = Field(None, description="End date of the added/removed date, in ISO date format (e.g. '2017-03-25'). Default value is 'today'")
    indie: Optional[bool] = Field(None, description="If the playlist was curated by major labels")
    editorial: Optional[bool] = Field(True, description="If true, the response includes playlists curated by the platform (e.g., Spotify Editorial Playlists, Apple Music Editorial Playlists, Deezer Editorial Playlists). Default value is True.")
    majorCurator: Optional[bool] = Field(None, description="If true, the response includes playlists curated by major curators (e.g., Filtr Colombia, Digster, Deezer MENA editor).")
    newMusicFriday: Optional[bool] = Field(None, description="A curated selection of Spotify's most anticipated new tracks of the week.")
    editorialBrand: Optional[bool] = Field(None, description="If true, includes playlists curated under specific editorial brands or themes by Apple Music's editorial team.")
    personalized: Optional[bool] = Field(None, description="If true, the response includes personalized playlists created based on user's listening habits and preferences.")
    deezerPartner: Optional[bool] = Field(None, description="If true, includes playlists curated by Deezer partners.")
    chart: Optional[bool] = Field(None, description="If true, the response includes playlists based on music charts.")
    thisIs: Optional[bool] = Field(None, description="If true, includes 'This Is' playlists curated by Spotify.")
    hundredPercent: Optional[bool] = Field(None, description="If true, includes '100%' playlists curated by Deezer.")
    radio: Optional[bool] = Field(None, description="If true, the response includes playlists from radio stations.")
    fullyPersonalized: Optional[bool] = Field(None, description="If true, includes fully personalized playlists curated by Spotify based on the user's listening behavior and preferences.")
    brand: Optional[bool] = Field(None, description="If true, the response includes playlists related to brands.")
    musicBrand: Optional[bool] = Field(None, description="If true, includes playlists curated under specific music brands by Apple Music's editorial team.")
    nonMusicBrand: Optional[bool] = Field(None, description="If true, includes playlists curated under specific non-music brands by Apple Music's editorial team.")
    popularIndie: Optional[bool] = Field(None, description="If true, the response includes playlists featuring popular indie tracks.")
    audiobook: Optional[bool] = Field(None, description="If true, includes audiobook playlists curated by Spotify. These playlists feature audiobook content.")
    personalityArtist: Optional[bool] = Field(None, description="If true, includes playlists curated under specific personality artists by Apple Music's editorial team.")
    sortColumn: Optional[str] = Field(None, description="Sort by column")
    sortOrderDesc: Optional[bool] = Field(None, description="Whether to sort in descending order. Can only be defined when sortColumn is defined. Default value is True.")
    limit: Optional[int] = Field(None, description="The number of entries to be returned. Default value is 10, max 100.")
    offset: Optional[int] = Field(None, description="The offset of entries to be returned. Default value is 0.")

    def run(self):
        """
        Executes the main functionality of the tool, retrieving playlists by track from Chartmetric.
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
        url = f"https://api.chartmetric.com/api/track/{self.id}/{self.platform}/{self.status}/playlists"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "since": self.since,
            "until": self.until,
            "indie": self.indie,
            "editorial": self.editorial,
            "majorCurator": self.majorCurator,
            "newMusicFriday": self.newMusicFriday,
            "editorialBrand": self.editorialBrand,
            "personalized": self.personalized,
            "deezerPartner": self.deezerPartner,
            "chart": self.chart,
            "thisIs": self.thisIs,
            "hundredPercent": self.hundredPercent,
            "radio": self.radio,
            "fullyPersonalized": self.fullyPersonalized,
            "brand": self.brand,
            "musicBrand": self.musicBrand,
            "nonMusicBrand": self.nonMusicBrand,
            "popularIndie": self.popularIndie,
            "audiobook": self.audiobook,
            "personalityArtist": self.personalityArtist,
            "sortColumn": self.sortColumn,
            "sortOrderDesc": self.sortOrderDesc,
            "limit": self.limit,
            "offset": self.offset
        }

        # Filter out None values from params
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