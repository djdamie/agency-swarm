import json
import time

def get_chartmetric_access_token():
    with open('access_token.json', 'r') as f:
        token_data = json.load(f)
    
    access_token = token_data['access_token']
    last_call_time = token_data.get('last_call_time')

    if last_call_time:
        elapsed_time = time.time() - last_call_time
        if elapsed_time < 2:
            time.sleep(2 - elapsed_time)

    return access_token

def update_last_call_time():
    with open('access_token.json', 'r') as f:
        token_data = json.load(f)
    
    token_data['last_call_time'] = time.time()
    
    with open('access_token.json', 'w') as f:
        json.dump(token_data, f)

# Usage in your API calls:
# access_token = get_chartmetric_access_token()
# ... make API call ...
# update_last_call_time()