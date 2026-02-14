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
        # PASSO 1: Obter Access Token usando Client Credentials Flow (conforme seu texto)
        # O Spotipy faz o POST para /api/token automaticamente aqui
        auth_manager = SpotifyClientCredentials(
            client_id=CLIENT_ID, 
            client_secret=CLIENT_SECRET
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)

        # PASSO 2: Chamar o Endpoint da Playlist (GET /playlists/{playlist_id})
        # Apenas playlists publicas no perfil sao retornadas neste fluxo
        results = sp.playlist_items(PLAYLIST_ID, market=MY_MARKET)
        
        found_tracks = []
        total_scanned = 0
        
        while results:
            for item in results['items']:
                track = item['track']
                if track:
                    total_scanned += 1
                    # Verifica se a musica esta liberada no mercado brasileiro
                    if track.get('is_playable'):
                        found_tracks.append(f"{track['name']} - {track['artists'][0]['name']}")
            
            # Paginação para ler todas as faixas (o endpoint retorna em blocos)
            results = sp.next(results) if results['next'] else None

        # --- NOTIFICAÇÃO ---
        if found_tracks:
            title = "Musicas Liberadas!"
            msg = f"Encontrei {len(found_tracks)} musicas disponiveis no Brasil."
        else:
            title = "Status: Sem Novidades"
            msg = f"Scan concluido: {total_scanned} faixas verificadas. Todas continuam bloqueadas."

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=msg.encode('utf-8'),
                      headers={"Title": title})

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=f"Erro de Acesso: {str(e)}".encode('utf-8'),
                      headers={"Title": "Erro 403 ou Conexao"})

if __name__ == "__main__":
    check_for_updates()
