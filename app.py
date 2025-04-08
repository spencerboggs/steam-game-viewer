import os
import json
import datetime
import dotenv
from flask import request, redirect, url_for
from flask import Flask, render_template, send_from_directory
from getcover import download_cover
from getgames import get_owned_games, save_owned_games

from flask import Flask, session
app = Flask(__name__)
app.secret_key = os.urandom(32)

dotenv.load_dotenv()

initial_load = False

def check_env_credentials():
    steam_id64 = os.getenv('STEAM_ID64')
    steam_api_key = os.getenv('STEAM_API_KEY')
    if not steam_id64 or not steam_api_key:
        return False
    test_data = get_owned_games(steam_id64, steam_api_key)
    return bool(test_data and 'response' in test_data)

@app.route('/')
def index():
    global initial_load
    steam_id64 = session.get('steam_id64') or os.getenv('STEAM_ID64')
    steam_api_key = session.get('steam_api_key') or os.getenv('STEAM_API_KEY')

    if not steam_id64 or not steam_api_key:
        return redirect(url_for('credentials'))

    if (request.args.get('steam_id64') or request.args.get('steam_api_key')) and os.path.exists('owned_games.json'):
        os.remove('owned_games.json')
        if os.path.exists('covers'):
            for file in os.listdir('covers'):
                os.remove(os.path.join('covers', file))
        initial_load = False

    if not os.path.exists('owned_games.json'):
        owned_games = get_owned_games(steam_id64, steam_api_key)
        if not owned_games:
            return redirect(url_for('credentials', error='Invalid Steam ID or API Key'))
        save_owned_games(owned_games)

    with open('owned_games.json', 'r', encoding='utf-8') as f:
        games = json.load(f)['response']['games']
    
    for game in games:
        appid = game['appid']
        if not initial_load:
            download_cover(appid)
        game['cover_path'] = f'/covers/{appid}.jpg'
        game['playtime_hours'] = round(game['playtime_forever'] / 60, 1)
        game['last_played'] = (
            datetime.datetime.utcfromtimestamp(game['rtime_last_played']).strftime('%Y-%m-%d %H:%M:%S')
            if game.get('rtime_last_played') else 'Never'
        )

    initial_load = True
    return render_template('index.html', games=games, steam_id64=steam_id64, steam_api_key=steam_api_key)

@app.route('/credentials', methods=['GET', 'POST'])
def credentials():
    global initial_load
    if request.method == 'POST':
        steam_id64 = request.form['steam_id64']
        steam_api_key = request.form['steam_api_key']
        test_data = get_owned_games(steam_id64, steam_api_key)
        if not test_data or 'response' not in test_data:
            return render_template('credentials.html', error='Invalid Steam ID or API Key')
        session['steam_id64'] = steam_id64
        session['steam_api_key'] = steam_api_key
        save_owned_games(test_data)

        initial_load = False
        return redirect(url_for('index'))

    return render_template('credentials.html', error=request.args.get('error'))

@app.route('/refresh-game-data')
def refresh_game_data():
    steam_id64 = request.args.get('steam_id64', os.getenv('STEAM_ID64'))
    steam_api_key = request.args.get('steam_api_key', os.getenv('STEAM_API_KEY'))
    owned_games = get_owned_games(steam_id64, steam_api_key)
    if owned_games:
        save_owned_games(owned_games)
        with open('owned_games.json', 'r', encoding='utf-8') as f:
            games = json.load(f)['response']['games']
        for game in games:
            download_cover(game['appid'])
        return "Game data refreshed."
    return "Failed to refresh game data."

@app.route('/refresh-covers')
def refresh_covers():
    with open('owned_games.json', 'r', encoding='utf-8') as f:
        games = json.load(f)['response']['games']
    for game in games:
        download_cover(game['appid'], True)
    return "Covers refreshed."

@app.route('/covers/<filename>')
def serve_cover(filename):
    return send_from_directory('covers', filename)

if __name__ == '__main__':
    if not check_env_credentials():
        print("Warning: Invalid or missing .env credentials")
    app.run(debug=True)