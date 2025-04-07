import os
import json
import datetime
from flask import Flask, render_template, send_from_directory
from getcover import download_cover
from getgames import get_owned_games, save_owned_games

app = Flask(__name__)

@app.route('/')
def index():
    if not os.path.exists('owned_games.json'):
        owned_games = get_owned_games(os.getenv('STEAM_ID64'), os.getenv('STEAM_API_KEY'))
        if owned_games:
            save_owned_games(owned_games)
        else:
            return "Failed to fetch owned games."
    else:
        with open('owned_games.json', 'r', encoding='utf-8') as f:
            owned_games = json.load(f)
            if 'response' not in owned_games or 'games' not in owned_games['response']:
                owned_games = get_owned_games(os.getenv('STEAM_ID64'), os.getenv('STEAM_API_KEY'))
                if owned_games:
                    save_owned_games(owned_games)
                else:
                    return "Failed to fetch owned games."
        
    # TODO: Add ability to paste in Steam ID and Key and refresh the page

    with open('owned_games.json', 'r', encoding='utf-8') as f:
        games = json.load(f)['response']['games']
    
    for game in games:
        appid = game['appid']
        download_cover(appid)
        game['cover_path'] = f'/covers/{appid}.jpg'

        game['playtime_hours'] = round(game['playtime_forever'] / 60, 1)
        game['last_played'] = (
            datetime.datetime.utcfromtimestamp(game['rtime_last_played']).strftime('%Y-%m-%d %H:%M:%S')
            if game.get('rtime_last_played') else 'Never'
        )

    return render_template('index.html', games=games)

@app.route('/covers/<filename>')
def serve_cover(filename):
    return send_from_directory('covers', filename)

if __name__ == '__main__':
    app.run(debug=True)
