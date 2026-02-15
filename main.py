import requests
import base64
import time
import random

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'

def check_for_updates():
    try:
        # 1. Autenticação
        auth_str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        token_res = requests.post("https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_str}"},
            data={"grant_type": "client_credentials"}).json()
        token = token_res.get('access_token')
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Captura o Total Real (Meta)
        url_meta = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?fields=tracks(total)&cache={random.random()}"
        res_meta = requests.get(url_meta, headers=headers).json()
        total_meta = res_meta.get('tracks', {}).get('total', 0)

        # 3. Varredura e Separação (Paginação)
        url_tracks = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100"
        qtd_disponiveis = 0
        
        while url_tracks:
            res_tracks = requests.get(url_tracks, headers=headers).json()
            items = res_tracks.get('items', [])
            
            for item in items:
                track = item.get('track')
                # Se o Spotify retorna ID e Nome, a música está disponível/visível
                if track and track.get('id') and track.get('name'):
                    qtd_disponiveis += 1
            
            url_tracks = res_tracks.get('next')
            if url_tracks: time.sleep(0.5)

        # 4. Cálculo e Relatório
        qtd_indisponiveis = total_meta - qtd_disponiveis

        msg = f"📊 PLACAR DE DISPONIBILIDADE\n\n"
        msg += f"Total na Playlist: {total_meta}\n"
        msg += f"🟢 Disponíveis: {qtd_disponiveis}\n"
        msg += f"🔴 Indisponíveis: {qtd_indisponiveis}\n"

        # Notificação via ntfy
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"❌ Erro: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
