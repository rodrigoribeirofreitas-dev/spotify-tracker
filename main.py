import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = 'a873df6bb1974db6b963d25c14bf695a'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
MY_MARKET = 'BR'
NTFY_TOPIC = 'spotify_tracker'

def check_for_updates():
    try:
        # Autenticacao direta via Client Credentials
        client_credentials_manager = SpotifyClientCredentials(
            client_id=CLIENT_ID, 
            client_secret=CLIENT_SECRET
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        # Busca simplificada
        results = sp.playlist_items(PLAYLIST_ID, market=MY_MARKET)
        
        found_tracks = []
        total_songs_scanned = 0
        
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
                break

        if found_tracks:
            title = "Musicas Liberadas!"
            message = f"Encontrei {len(found_tracks)} novas musicas disponiveis:\n" + "\n".join(found_tracks)
            tags = "tada,headphones"
        else:
            title = "Status: Sem Novidades"
            message = f"Escaneadas {total_songs_scanned} faixas. Todas continuam bloqueadas."
            tags = "white_check_mark"

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=message.encode('utf-8'),
                      headers={"Title": title, "Tags": tags})

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=f"Erro: {str(e)}".encode('utf-8'),
                      headers={"Title": "Tracker Error Alert"})

if __name__ == "__main__":
    check_for_updates()
