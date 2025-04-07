import os
import requests

def download_cover(appid, folder='covers'):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f'{appid}.jpg')

    if os.path.exists(filepath):
        print(f'Skipped: {filepath} already exists.')
        return

    url = f'https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/library_600x900.jpg'
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f'Saved cover for appid {appid} to {filepath}')
    else:
        print(f'Failed to fetch cover for appid {appid} (status {response.status_code})')
        open(filepath, 'w').close()
        print(f'Created placeholder for appid {appid} at {filepath}')
