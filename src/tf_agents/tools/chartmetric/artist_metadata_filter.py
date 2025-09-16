"""
Artist Metadata Filter - Token-Efficient Data Processing

This module contains the filtering logic extracted from the n8n workflow
"Refined Artist Metadata" to reduce token usage by selecting only essential
fields from Chartmetric API responses.

Original n8n workflow filters the full artist metadata response to include
only the most relevant fields for A&R analysis and decision making.
"""

def filter_artist_metadata(api_response):
    """
    Filter Chartmetric artist metadata to essential fields only.
    
    This function mimics the JavaScript filtering logic from the n8n workflow
    to reduce token consumption while preserving key artist data.
    
    Args:
        api_response (dict): Raw response from Chartmetric API /api/artist/{id}
        
    Returns:
        dict: Filtered artist metadata with only essential fields
    """
    d = api_response
    
    return {
        "name": d.get("name"),
        "id": d.get("id"),
        "hometown_city": d.get("hometown_city"),
        "current_city": d.get("current_city"),
        "record_label": d.get("record_label"),
        "associatedLabels": d.get("associatedLabels"),
        "description": d.get("description"),
        
        # genres: keep only name/type/source (remove IDs)
        "genres": {
            "primary": {
                "name": d.get("genres", {}).get("primary", {}).get("name"),
                "type": d.get("genres", {}).get("primary", {}).get("type"),
                "source": d.get("genres", {}).get("primary", {}).get("source"),
            },
            "secondary": [
                {
                    "name": g.get("name"),
                    "type": g.get("type"),
                    "source": g.get("source"),
                }
                for g in d.get("genres", {}).get("secondary", [])
            ],
            "sub": [
                {
                    "name": g.get("name"),
                    "type": g.get("type"),
                    "source": g.get("source"),
                }
                for g in d.get("genres", {}).get("sub", [])
            ],
        },
        
        "topSongwriterId": d.get("topSongwriterId"),
        "career_status": d.get("career_status"),
        
        # Extract only names from moods and activities
        "moods": [m.get("name") for m in d.get("moods", [])],
        "activities": [a.get("name") for a in d.get("activities", [])],
        
        "topSongwriterCollaborators": d.get("topSongwriterCollaborators"),
        
        "cm_statistics": {
            "sp_followers": d.get("cm_statistics", {}).get("sp_followers"),
            "countryRank": d.get("cm_statistics", {}).get("countryRank"),
            
            # Remove ID from genreRank
            "genreRank": {
                "name": d.get("cm_statistics", {}).get("genreRank", {}).get("name"),
                "rank": d.get("cm_statistics", {}).get("genreRank", {}).get("rank"),
            },
            
            # Strip ID from each secondary genre rank
            "secondaryGenreRanks": [
                {
                    "name": r.get("name"),
                    "rank": r.get("rank"),
                }
                for r in d.get("cm_statistics", {}).get("secondaryGenreRanks", [])
            ],
            
            "sp_where_people_listen": d.get("cm_statistics", {}).get("sp_where_people_listen"),
            "sp_monthly_listeners": d.get("cm_statistics", {}).get("sp_monthly_listeners"),
            "sp_popularity": d.get("cm_statistics", {}).get("sp_popularity"),
            "num_sp_editorial_playlists": d.get("cm_statistics", {}).get("num_sp_editorial_playlists"),
            "twitter_followers": d.get("cm_statistics", {}).get("twitter_followers"),
            "ins_followers": d.get("cm_statistics", {}).get("ins_followers"),
            "ycs_subscribers": d.get("cm_statistics", {}).get("ycs_subscribers"),
            "ycs_views": d.get("cm_statistics", {}).get("ycs_views"),
            "tiktok_followers": d.get("cm_statistics", {}).get("tiktok_followers"),
            "tiktok_likes": d.get("cm_statistics", {}).get("tiktok_likes"),
            "tiktok_top_video_views": d.get("cm_statistics", {}).get("tiktok_top_video_views"),
            "youtube_daily_video_views": d.get("cm_statistics", {}).get("youtube_daily_video_views"),
            "youtube_monthly_video_views": d.get("cm_statistics", {}).get("youtube_monthly_video_views"),
            "twitch_followers": d.get("cm_statistics", {}).get("twitch_followers"),
            "twitch_views": d.get("cm_statistics", {}).get("twitch_views"),
            "twitch_monthly_viewer_hours": d.get("cm_statistics", {}).get("twitch_monthly_viewer_hours"),
            "sp_editorial_playlist_total_reach": d.get("cm_statistics", {}).get("sp_editorial_playlist_total_reach"),
            "cm_artist_rank": d.get("cm_statistics", {}).get("cm_artist_rank"),
            
            "latest": {
                "itunes_ed_playlist_count": d.get("cm_statistics", {}).get("latest", {}).get("itunes_ed_playlist_count"),
                "latest_album_release_date": d.get("cm_statistics", {}).get("latest", {}).get("latest_album_release_date"),
                "latest_album_upc": d.get("cm_statistics", {}).get("latest", {}).get("latest_album_upc"),
            }
        }
    }