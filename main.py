import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = 'a873df6bb1974db6b963d25c14bf695a'

os.environ['SPOTIPY_CLIENT_ID'] = CLIENT_ID
os.environ['SPOTIPY_CLIENT_SECRET'] = CLIENT_SECRET

PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
REDIRECT_URI = 'http://localhost:8888/callback'
NTFY_TOPIC = 'spotify_tracker' 
MY_MARKET = 'BR'

def check_for_updates():
    try:
        auth_manager = SpotifyClientCredentials(
            client_id=CLIENT_ID, 
            client_secret=CLIENT_SECRET
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)

        found_tracks = []
        total_songs_scanned = 0
        
        results = sp.playlist_items(PLAYLIST_ID, market=MY_MARKET)
        
        while results:
            for item in results['items']:
                track = item['track']
                if track:
                    total_songs_scanned += 1
                    if track.get('is_playable'):
                        found_tracks.append(f"{track['name']} - {track['artists'][0]['name']}")
            
            if results['next']:
                results = sp.next(results)
            else:
                results = None

        if found_tracks:
            title = "Musicas Liberadas!"
            message = f"Encontrei {len(found_tracks)} novas musicas disponiveis:\n" + "\n".join(found_tracks)
            tags = "tada,headphones"
        else:
            title = "Status: Sem Novidades"
            message = f"Escaneadas {total_songs_scanned} faixas. Todas continuam bloqueadas em {MY_MARKET}."
            tags = "white_check_mark"

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=message.encode(encoding='utf-8'),
                      headers={"Title": title, "Tags": tags})

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=f"FAIA: {str(e)}".encode(encoding='utf-8'),
                      headers={"Title": "DEU RUIM AQUI IRMÃO"})

if __name__ == "__main__":
    check_for_updates()
