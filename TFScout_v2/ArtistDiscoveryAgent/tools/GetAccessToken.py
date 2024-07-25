from agency_swarm.tools import BaseTool                                                                                                                                                                                        
from pydantic import BaseModel, Field                                                                                                                                                                                          
import requests                                                                                                                                                                                                                
import json
import os

                                                                                                                                                                                                                                
class RefreshTokenRequest(BaseModel):                                                                                                                                                                                          
    refreshtoken: str = Field(..., description="The refresh token required to obtain an access token.")                                                                                                                       
                                                                                                                                                                                                                                
class GetAccessToken(BaseTool):                                                                                                                                                                                                
    """Obtain an access token using a refresh token."""                                                                                                                                                                        
    refreshtoken: str = Field(default= os.getenv("CHARTMETRIC_REFRESH_TOKEN"), description="Refresh token for obtaining access token")                                                

    def run(self):                                                                                                                                                                                                             
        # Construct the request body from the refresh token attribute                                                                                                                                                          
        data = RefreshTokenRequest(refreshtoken=self.refreshtoken).dict()                                                                                                                                                                                                                                                                                                                                                                                   
        url = "https://api.chartmetric.com/api/token"                                                                                                                                                                                  
                                                                                                                                                                                                                                
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=data)

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['token']
            token_expiry = token_data['expires_in']
            with open('access_token.json', 'w') as f:
                json.dump({'access_token': access_token, 'token_expiry': token_expiry, 'last_call_time': None}, f)
            return {"access_token": access_token, "token_expiry": token_expiry}
        else:
            return {"error": f"Error: {response.status_code} - {response.reason}"}