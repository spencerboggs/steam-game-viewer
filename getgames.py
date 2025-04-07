import os
import json
import requests
import dotenv

dotenv.load_dotenv()
STEAM_API_KEY = os.getenv('STEAM_API_KEY')
STEAM_ID64 = os.getenv('STEAM_ID64')

def get_owned_games(steam_id, api_key): 
    url = f'https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={api_key}&steamid={steam_id}&include_appinfo=true&include_played_free_games=true&include_free_sub=true&skip_unvetted_apps=true&include_extended_appinfo=true'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching owned games: {response.status_code}")
        return None
    
def save_owned_games(data):
    with open('owned_games.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        print("Owned games saved to owned_games.json")
        return True
