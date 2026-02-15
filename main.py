import requests
import base64
import time

# CREDENCIAIS RESTAURADAS
CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'

def check_for_updates():
    try:
        # 1. Autenticação
        auth_str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_str}"},
            data={"grant_type": "client_credentials"}
        ).json()
        token = token_res.get('access_token')

        headers = {"Authorization": f"Bearer {token}"}

        # 2. Leitura do Objeto da Playlist (Pega o total e o nome)
        # Usar o endpoint direto da playlist é mais estável que o de tracks
        url_playlist = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}"
        res_playlist = requests.get(url_playlist, headers=headers).json()
        
        total_meta = res_playlist.get('tracks', {}).get('total', 0)
        
        # 3. Varredura de Disponibilidade (Pega as primeiras 100)
        url_tracks = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100"
        res_tracks = requests.get(url_tracks, headers=headers).json()
        items = res_tracks.get('items', [])
        
        tocaveis = []
        for item in items:
            track = item.get('track')
            # Critério: se tem nome e não é local, o robô está vendo
            if track and track.get('name') and not track.get('is_local'):
                artist = track['artists'][0]['name'] if track.get('artists') else "Unknown"
                tocaveis.append(f"{track['name']} - {artist}")

        # 4. Relatório Final
        qtd_tocaveis = len(tocaveis)
        msg = f"📊 Status da Playlist: {res_playlist.get('name', 'N/A')}\n\n"
        msg += f"Total de Itens: {total_meta}\n"
        msg += f"🟢 Tocáveis (Nesta página): {qtd_tocaveis}\n"
        msg += f"🔴 Bloqueadas: {total_meta - qtd_tocaveis}\n"

        if qtd_tocaveis > 0:
            msg += "\n🎵 Primeiras visíveis:\n" + "\n".join(tocaveis[:5])

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"❌ Erro: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
