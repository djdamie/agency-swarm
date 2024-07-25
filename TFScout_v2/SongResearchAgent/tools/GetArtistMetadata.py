from agency_swarm.tools import BaseTool                                                                                                                                                                                        
from pydantic import BaseModel, Field                                                                                                                                                                                          
import requests      
import json
import time

class GetArtistMetadata(BaseTool):                                                                                                                                                           
    """Retrieve the artist's metadata and Chartmetric stats."""                                                                                                                              
    artist_id: int = Field(..., description="Chartmetric artist ID")                                                                                                                         
                                                                                                                                                                                            
    def run(self):
        # Read the access token and last call time from the access_token.json file
        with open('access_token.json', 'r') as f:
            data = json.load(f)
            access_token = data['access_token']
            last_call_time = data.get('last_call_time')

        # Enforce rate limit
        rate_limit_interval = 2  # seconds
        if last_call_time is not None:
            elapsed = time.time() - last_call_time
            if elapsed < rate_limit_interval:
                time.sleep(rate_limit_interval - elapsed)
                
        url = f"https://api.chartmetric.com/api/artist/{self.artist_id}"                                                                                                                     
        headers = {'Authorization': f'Bearer {access_token}'}                                                                                                                                
                                                                                                                                                                                            
        response = requests.get(url, headers=headers)                                                                                                                                        
        
         # Update the last call time in the access_token.json file
        with open('access_token.json', 'w') as f:
            data['last_call_time'] = time.time()
            json.dump(data, f)
                                                                                                                                                                                                
        if response.status_code == 200:                                                                                                                                                      
            artist_metadata = response.json()                                                                                                                                                
            return artist_metadata                                                                                                                                                           
        else:                                                                                                                                                                                
            return f"Error: {response.status_code} - {response.reason}"  