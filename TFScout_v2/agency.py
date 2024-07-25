import os
from agency_swarm import Agency, set_openai_key
from ArtistDiscoveryAgent import ArtistDiscoveryAgent
from TrendingTrackAnalystAgent import TrendingTrackAnalystAgent
from PlaylistAnalysisAgent import PlaylistAnalysisAgent
from SongResearchAgent import SongResearchAgent
from TFScoutCEO import TFScoutCEO
from dotenv import load_dotenv

load_dotenv()

set_openai_key(os.environ["OPENAI_API_KEY"])

tfScoutCEO = TFScoutCEO()
#briefAgent = BriefAgent()
#spotifyAgent = SpotifyAgent()
#chartmetricExpert = ChartmetricExpert()
trendingTrackAnalyst = TrendingTrackAnalystAgent()
playlistAnalysisAgent = PlaylistAnalysisAgent()
artistDiscoveryAgent = ArtistDiscoveryAgent()
songResearchAgent = SongResearchAgent()

agency = Agency([
    tfScoutCEO,
    [tfScoutCEO, trendingTrackAnalyst],
    [tfScoutCEO, artistDiscoveryAgent],
    [tfScoutCEO, playlistAnalysisAgent],
    [tfScoutCEO, songResearchAgent],
    [trendingTrackAnalyst, artistDiscoveryAgent, playlistAnalysisAgent, songResearchAgent],
],
    shared_instructions='./agency_manifesto.md', # shared instructions for all agents
    max_prompt_tokens=50000, # default tokens in conversation for all agents
    temperature=0.3, # default temperature for all agents
    #async_mode= 'threading',
    )
                
if __name__ == '__main__':
    agency.demo_gradio()
