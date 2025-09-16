import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Global variables to cache the token
_access_token = None
_token_expiry = None

def get_access_token():
    """
    Gets an access token from the Chartmetric API.
    Caches the token and reuses it until expiry.
    Returns:
        str: The access token
    """
    global _access_token, _token_expiry
    
    # Check if we have a valid cached token
    if _access_token and _token_expiry and datetime.now() < _token_expiry:
        return _access_token
    
    refresh_token = os.environ.get('CHARTMETRIC_REFRESH_TOKEN')
    url = "https://api.chartmetric.com/api/token"
    response = requests.post(url, data={"refreshtoken": refresh_token})
    
    if response.status_code == 200:
        token_data = response.json()
        _access_token = token_data['token']
        # Token expires in 1 hour, we'll cache it for slightly less
        _token_expiry = datetime.now() + timedelta(minutes=55)
        return _access_token
    else:
        raise Exception(f"Failed to obtain access token. Status code: {response.status_code}, Response: {response.text}")