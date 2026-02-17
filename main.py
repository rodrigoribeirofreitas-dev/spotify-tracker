import requests
import base64
import time

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'
MY_MARKET = 'BR'

def check_for_updates():
    try:
        # 1. Autenticação (Resgatando o acesso)
        auth_str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        token_res = requests.post("https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_str}"},
            data={"grant_type": "client_credentials"}).json()
        token = token_res.get('access_token')
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Leitura Robusta (Pegando o Objeto Pai da Playlist)
        # Este endpoint é o que confirmou as 1698 músicas anteriormente
        url_playlist = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?market={MY_MARKET}"
        res_playlist = requests.get(url_playlist, headers=headers).json()
        
        total_meta = res_playlist.get('tracks', {}).get('total', 0)
        
        # 3. Varredura com Lógica de Disponibilidade Real
        url_tracks = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100&market={MY_MARKET}"
        qtd_disponiveis = 0
        
        while url_tracks:
            res_tracks = requests.get(url_tracks, headers=headers).json()
            items = res_tracks.get('items', [])
            
            for item in items:
                track = item.get('track')
                if track and track.get('id'):
                    # No Spotify, se 'is_playable' for False, a música está bloqueada no BR
                    # Se o campo não existir, ela é considerada disponível
                    if track.get('is_playable', True):
                        qtd_disponiveis += 1
            
            url_tracks = res_tracks.get('next')
            if url_tracks: time.sleep(1) # Pausa para evitar novo bloqueio

        # 4. Relatório
        qtd_indisponiveis = total_meta - qtd_disponiveis
        
        msg = f"📊 STATUS DA PLAYLIST\n\n"
        msg += f"Total: {total_meta}\n"
        msg += f"🟢 Disponíveis: {qtd_disponiveis}\n"
        msg += f"🔴 Indisponíveis: {qtd_indisponiveis}\n"

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"❌ Erro de Conexão: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
