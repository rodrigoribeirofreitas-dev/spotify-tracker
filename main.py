import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests

# --- CONFIGURAÇÃO ---
# Mantenha os códigos entre aspas para evitar erros de comunicação com o GitHub
CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = 'a873df6bb1974db6b963d25c14bf695a'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker' 
MY_MARKET = 'US'

def check_for_updates():
    try:
        # Autenticação robusta
        auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        sp = spotipy.Spotify(auth_manager=auth_manager)

        found_tracks = []
        total_songs_scanned = 0
        
        # 1. Busca inicial (Pega as primeiras 100 músicas)
        results = sp.playlist_items(PLAYLIST_ID, market=MY_MARKET)
        
        # 2. Loop de Paginação (Escaneia TODAS as faixas da playlist)
        while results:
            for item in results['items']:
                track = item['track']
                if track:
                    total_songs_scanned += 1
                    # Verifica se a música pode ser reproduzida no Brasil
                    if track.get('is_playable'):
                        found_tracks.append(f"{track['name']} - {track['artists'][0]['name']}")
            
            # Se houver uma próxima página de músicas, ele continua
            if results['next']:
                results = sp.next(results)
            else:
                results = None

        # --- LÓGICA DE NOTIFICAÇÃO ---
        if found_tracks:
            title = "Músicas Liberadas!"
            message = f"Encontrei {len(found_tracks)} novas músicas disponíveis:\n" + "\n".join(found_tracks)
            tags = "tada,headphones"
        else:
            title = "Status: Sem Novidades"
            message = f"Escaneadas {total_songs_scanned} faixas. Todas continuam bloqueadas em {MY_MARKET}."
            tags = "white_check_mark"

        # Envia para o ntfy.sh
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=message.encode(encoding='utf-8'),
                      headers={
                          "Title": title,
                          "Tags": tags
                      })

    except Exception as e:
        # Alerta de erro detalhado para debug
        error_str = str(e)
        print(f"Erro detectado: {error_str}")
        
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=f"Erro: {error_str}".encode(encoding='utf-8'),
                      headers={"Title": "Tracker Error Alert"})

if __name__ == "__main__":
    check_for_updates()
