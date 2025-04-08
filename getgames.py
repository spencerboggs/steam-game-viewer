import os
import json
import requests
import dotenv

dotenv.load_dotenv()

def get_owned_games(steam_id, api_key): 
    url = f'https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={api_key}&steamid={steam_id}&include_appinfo=true&include_played_free_games=true&include_free_sub=true&skip_unvetted_apps=true&include_extended_appinfo=true'
    try:
        response = requests.get(url, timeout=10)
        print("Steam API response:", response.text)

        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None
    
def save_owned_games(data):
    with open('owned_games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        return True