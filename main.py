import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests

# Suas credenciais validadas
CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = 'a873df6bb1974db6b963d25c14bf695a'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'
MY_MARKET = 'BR'

def check_for_updates():
    try:
        # Este gerenciador NAO usa Redirect URI e NAO abre navegador
        auth_manager = SpotifyClientCredentials(
            client_id=CLIENT_ID, 
            client_secret=CLIENT_SECRET
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)

        # Realiza a busca na playlist
        results = sp.playlist_items(PLAYLIST_ID, market=MY_MARKET)
        
        found_tracks = []
        total_scanned = 0
        
        while results:
            for item in results['items']:
                track = item['track']
                if track:
                    total_scanned += 1
                    if track.get('is_playable'):
                        found_tracks.append(f"{track['name']} - {track['artists'][0]['name']}")
            
            # Navega por todas as paginas da playlist
            results = sp.next(results) if results['next'] else None

        # Prepara a mensagem para o ntfy
        if found_tracks:
            title = "Musicas Liberadas!"
            msg = f"Encontrei {len(found_tracks)} musicas disponiveis no Brasil."
        else:
            title = "Status: Sem Novidades"
            msg = f"Scan concluido: {total_scanned} faixas verificadas e bloqueadas em {MY_MARKET}."

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=msg.encode('utf-8'),
                      headers={"Title": title})

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=f"Erro de Conexao: {str(e)}".encode('utf-8'),
                      headers={"Title": "Erro no Rastreador"})

if __name__ == "__main__":
    check_for_updates()
