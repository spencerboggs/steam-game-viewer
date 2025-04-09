import os
import json
import requests

def get_game_store_data(appid):
    url = f'https://store.steampowered.com/api/appdetails?appids={appid}'

    if os.path.exists(f'gamedata/{appid}.json'):
        with open(f'gamedata/{appid}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(f'gamedata/{appid}.json', 'w', encoding='utf-8') as f:
                json.dump(response.json(), f, indent=4)
                return response.json()
        return None
    except requests.exceptions.RequestException:
        return None
    except json.JSONDecodeError:
        return None
