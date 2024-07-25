# MusicInsightAgency/ChartmetricExpert/tools/GetArtistsWithFilters.py

from agency_swarm.tools import BaseTool
from pydantic import Field
from enum import Enum
import requests
import json
import time
from typing import Optional, List

class SortColumn(str, Enum):
    amazon_ed_playlist_count = "amazon_ed_playlist_count"
    amazon_playlist_count = "amazon_playlist_count"
    boomplay_comments = "boomplay_comments"
    boomplay_favorites = "boomplay_favorites"
    boomplay_plays = "boomplay_plays"
    boomplay_ranking_current = "boomplay_ranking_current"
    boomplay_shares = "boomplay_shares"
    bs_followers = "bs_followers"
    deezer_ed_playlist_count = "deezer_ed_playlist_count"
    deezer_ed_playlist_total_reach = "deezer_ed_playlist_total_reach"
    deezer_fans = "deezer_fans"
    deezer_playlist_count = "deezer_playlist_count"
    deezer_playlist_total_reach = "deezer_playlist_total_reach"
    facebook_followers = "facebook_followers"
    fs_likes = "fs_likes"
    fs_talks = "fs_talks"
    genius_pageviews = "genius_pageviews"
    ins_engagement_rate = "ins_engagement_rate"
    ins_followers = "ins_followers"
    itunes_ed_playlist_count = "itunes_ed_playlist_count"
    itunes_playlist_count = "itunes_playlist_count"
    line_music_artist_likes = "line_music_artist_likes"
    line_music_likes = "line_music_likes"
    line_music_mv_plays = "line_music_mv_plays"
    line_music_plays = "line_music_plays"
    melon_artist_fans = "melon_artist_fans"
    melon_likes = "melon_likes"
    melon_video_likes = "melon_video_likes"
    melon_video_views = "melon_video_views"
    pandora_lifetime_stations_added = "pandora_lifetime_stations_added"
    pandora_lifetime_streams = "pandora_lifetime_streams"
    pandora_listeners_28_day = "pandora_listeners_28_day"
    shazam_count = "shazam_count"
    songkick_fans = "songkick_fans"
    soundcloud_followers = "soundcloud_followers"
    soundcloud_plays = "soundcloud_plays"
    sp_followers = "sp_followers"
    sp_followers_to_listeners_ratio = "sp_followers_to_listeners_ratio"
    sp_listeners_to_followers_ratio = "sp_listeners_to_followers_ratio"
    sp_monthly_listeners = "sp_monthly_listeners"
    sp_popularity = "sp_popularity"
    spotify_ed_playlist_count = "spotify_ed_playlist_count"
    spotify_ed_playlist_total_reach = "spotify_ed_playlist_total_reach"
    spotify_playlist_count = "spotify_playlist_count"
    spotify_playlist_total_reach = "spotify_playlist_total_reach"
    tiktok_followers = "tiktok_followers"
    tiktok_likes = "tiktok_likes"
    tiktok_top_video_views = "tiktok_top_video_views"
    tiktok_track_posts = "tiktok_track_posts"
    ts_followers = "ts_followers"
    twitch_followers = "twitch_followers"
    twitch_monthly_viewer_hours = "twitch_monthly_viewer_hours"
    twitch_views = "twitch_views"
    twitch_weekly_viewer_hours = "twitch_weekly_viewer_hours"
    ws_views = "ws_views"
    ycs_subscribers = "ycs_subscribers"
    ycs_views = "ycs_views"
    youtube_daily_video_views = "youtube_daily_video_views"
    youtube_ed_playlist_count = "youtube_ed_playlist_count"
    youtube_ed_playlist_total_reach = "youtube_ed_playlist_total_reach"
    youtube_monthly_video_views = "youtube_monthly_video_views"
    youtube_playlist_count = "youtube_playlist_count"
    youtube_playlist_total_reach = "youtube_playlist_total_reach"
    ts_retweets = "ts_retweets"
    pandora_stations_added = "pandora_stations_added"
    cm_artist_rank = "cm_artist_rank"
    rank_eg = "rank_eg"
    rank_fb = "rank_fb"
    
class GetArtistsWithFilters(BaseTool):
    """
    This tool retrieves a snapshot of sample artists based on given filters from the Chartmetric API.
    Given different filters and score range, get a list of artist IDs and all relevant metrics for the given range of the respective metric.
    This endpoint is useful for artist profiling based on specific filters such as Spotify performance, YouTube performance, and social media performance.
    
    """

    tagId: Optional[int] = Field(None, description="Filter by Genre Id.")
    subTagId: Optional[int] = Field(None, description="Filter by Subgenre Id.")
    code2: Optional[str] = Field(None, description="Filtering by artist's country.")
    firstReleaseDaysAgo: Optional[int] = Field(None, description="Filter based on artist's first release in number of days ago from the current date.")
    band: Optional[bool] = Field(False, description="Filtering bands or solo artists only. Default value is False.")
    pronoun: Optional[str] = Field(None, description="Filtering by artist's pronoun.")
    sortColumn: Optional[SortColumn] = Field(None, description="The sorting order of the artist list based on filters.")
    sortOrderDesc: Optional[bool] = Field(True, description="Whether to sort in descending order. Default value is True.")
    sp_p: Optional[List[int]] = Field(None, description="Max and min filter threshold for Spotify popularity.")
    sp_f: Optional[List[int]] = Field(None, description="Max and min filter threshold for Spotify followers.")
    dz_fans: Optional[List[int]] = Field(None, description="Max and min filter threshold for Deezer fans.")
    sp_ml: Optional[List[int]] = Field(None, description="Max and min filter threshold for Spotify monthly listeners.")
    sp_ratio: Optional[List[int]] = Field(None, description="Max and min filter threshold for Spotify listeners/fans ratio.")
    sp_fl_ratio: Optional[List[int]] = Field(None, description="Max and min filter threshold for Spotify fans/listeners ratio.")
    tt_f: Optional[List[int]] = Field(None, description="Max and min filter threshold for TikTok followers.")
    tt_l: Optional[List[int]] = Field(None, description="Max and min filter threshold for TikTok likes.")
    fb_f: Optional[List[int]] = Field(None, description="Max and min filter threshold for Facebook followers.")
    fb_l: Optional[List[int]] = Field(None, description="Max and min filter threshold for Facebook likes.")
    fb_t: Optional[List[int]] = Field(None, description="Max and min filter threshold for Facebook talks.")
    tw_f: Optional[List[int]] = Field(None, description="Max and min filter threshold for Twitter followers.")
    tw_r: Optional[List[int]] = Field(None, description="Max and min filter threshold for Twitter retweets.")
    ig_f: Optional[List[int]] = Field(None, description="Max and min filter threshold for Instagram followers.")
    ytc_v: Optional[List[int]] = Field(None, description="Max and min filter threshold for YouTube channel views.")
    ytc_s: Optional[List[int]] = Field(None, description="Max and min filter threshold for YouTube channel subscribers.")
    ytd_vv: Optional[List[int]] = Field(None, description="Max and min filter threshold for YouTube daily video views.")
    ytm_vv: Optional[List[int]] = Field(None, description="Max and min filter threshold for YouTube monthly video views.")
    sc_f: Optional[List[int]] = Field(None, description="Max and min filter threshold for Soundcloud followers.")
    bit_f: Optional[List[int]] = Field(None, description="Max and min filter threshold for Bandsintown followers.")
    cpp: Optional[List[int]] = Field(None, description="Max and min filter threshold for CPP (Ranking).")
    t_f: Optional[List[int]] = Field(None, description="Max and min filter threshold for Twitch followers.")
    t_v: Optional[List[int]] = Field(None, description="Max and min filter threshold for Twitch views.")
    t_mvh: Optional[List[int]] = Field(None, description="Max and min filter threshold for Twitch monthly viewer hours.")
    t_wwh: Optional[List[int]] = Field(None, description="Max and min filter threshold for Twitch weekly viewer hours.")
    career_stage: Optional[str] = Field(None, description="Filter by the artist's career stage.")
    career_stage_score: Optional[List[int]] = Field(None, description="Max and min filter threshold for career stage score.")
    career_trend: Optional[str] = Field(None, description="Filter by the artist's career trend category.")
    career_trend_score: Optional[List[int]] = Field(None, description="Max and min filter threshold for career trend score.")
    limit: Optional[int] = Field(50, description="Number of entries to be returned. Default is 50.")
    offset: Optional[int] = Field(0, description="Offset of entries to be returned. Default is 0.")

    def run(self):
        """
        Executes the main functionality of the tool, retrieving filtered artists from Chartmetric.
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
        url = "https://api.chartmetric.com/api/artist/list/filter"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "tagId": self.tagId,
            "subTagId": self.subTagId,
            "code2": self.code2,
            "firstReleaseDaysAgo": self.firstReleaseDaysAgo,
            "band": self.band,
            "pronoun": self.pronoun,
            "sortColumn": self.sortColumn,
            "sortOrderDesc": self.sortOrderDesc,
            "sp_p": self.sp_p,
            "sp_f": self.sp_f,
            "dz_fans": self.dz_fans,
            "sp_ml": self.sp_ml,
            "sp_ratio": self.sp_ratio,
            "sp_fl_ratio": self.sp_fl_ratio,
            "tt_f": self.tt_f,
            "tt_l": self.tt_l,
            "fb_f": self.fb_f,
            "fb_l": self.fb_l,
            "fb_t": self.fb_t,
            "tw_f": self.tw_f,
            "tw_r": self.tw_r,
            "ig_f": self.ig_f,
            "ytc_v": self.ytc_v,
            "ytc_s": self.ytc_s,
            "ytd_vv": self.ytd_vv,
            "ytm_vv": self.ytm_vv,
            "sc_f": self.sc_f,
            "bit_f": self.bit_f,
            "cpp": self.cpp,
            "t_f": self.t_f,
            "t_v": self.t_v,
            "t_mvh": self.t_mvh,
            "t_wwh": self.t_wwh,
            "career_stage": self.career_stage,
            "career_stage_score": self.career_stage_score,
            "career_trend": self.career_trend,
            "career_trend_score": self.career_trend_score,
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
        
