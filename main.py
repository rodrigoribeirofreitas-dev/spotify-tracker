import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests

# 1. Configuração (Mantenha seus IDs aqui)
CLIENT_ID = 'ea5f9e4831d2429d90564b630c921666'
CLIENT_SECRET = 'c5fa223490da45fcafbdcea1ac47623e'
PLAYLIST_ID = '3cKE9Q2sTLoETiwnSktln9'
NTFY_TOPIC = 'spotify_tracker' 
MY_MARKET = 'BR'

def check_for_updates():
    try:
        # Criamos o gerenciador de autenticação de forma mais robusta
        client_credentials_manager = SpotifyClientCredentials(
            client_id=CLIENT_ID, 
            client_secret=CLIENT_SECRET
        )
        
        # O segredo está aqui: forçar o sp a usar o token explicitamente
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        # 2. Lógica para buscar TODAS as faixas
        found_tracks = []
        total_songs_scanned = 0
        
        # Teste de conexão simples antes de baixar a playlist
        print("Tentando conexão...")
        results = sp.playlist_items(PLAYLIST_ID, market=MY_MARKET)
        
        while results:
            for item in results['items']:
                track = item['track']
                if track:
                    total_songs_scanned += 1
                    # Verifica se a música está disponível no Brasil
                    if track.get('is_playable'):
                        found_tracks.append(f"{track['name']} - {track['artists'][0]['name']}")
            
            # Se houver mais de 100, ele busca o próximo lote
            if results['next']:
                results = sp.next(results)
            else:
                results = None

        # 3. Notificação
        if found_tracks:
            title = "New Songs Available"
            message = f"Found {len(found_tracks)} new songs!\n" + "\n".join(found_tracks)
            tags = "tada,headphones"
        else:
            title = "Status: No Updates"
            message = f"Scanned {total_songs_scanned} tracks. All are still locked in {MY_MARKET}."
            tags = "white_check_mark"

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=message.encode(encoding='utf-8'),
                      headers={"Title": title, "Tags": tags})

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=error_msg.encode(encoding='utf-8'),
                      headers={"Title": "Tracker Error Alert"})

if __name__ == "__main__":
    check_for_updates()
