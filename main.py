import requests
import base64
import time
import random

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'
MY_MARKET = 'BR'

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

        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        # 2. Leitura do Total Real (Meta)
        total_meta = 0
        for tentativa in range(2):
            url_meta = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?fields=tracks(total)&cache={random.random()}"
            res_meta = requests.get(url_meta, headers=headers).json()
            total_meta = res_meta.get('tracks', {}).get('total', 0)
            if total_meta > 0: break
            time.sleep(10)

        if total_meta == 0:
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data="⚠️ BLOQUEIO: Spotify retornou 0 músicas.".encode('utf-8'))
            return

        # 3. Varredura de Disponibilidade
        url_tracks = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100&market={MY_MARKET}"
        disponiveis = []
        
        while url_tracks:
            res_tracks = requests.get(url_tracks, headers=headers).json()
            items = res_tracks.get('items', [])
            for item in items:
                track = item.get('track')
                if track and track.get('name'):
                    artist = track['artists'][0]['name'] if track.get('artists') else "Unknown"
                    disponiveis.append(f"{track['name']} - {artist}")
            url_tracks = res_tracks.get('next')
            if url_tracks: time.sleep(1)

        # 4. Cálculo do Placar
        qtd_disponiveis = len(disponiveis)
        qtd_indisponiveis = total_meta - qtd_disponiveis

        # 5. Notificação Detalhada
        status_icon = "🔥" if qtd_disponiveis > 0 else "✅"
        msg = f"{status_icon} Relatório de Disponibilidade (BR)\n\n"
        msg += f"📊 Total na Playlist: {total_meta}\n"
        msg += f"🟢 Disponíveis: {qtd_disponiveis}\n"
        msg += f"🔴 Indisponíveis: {qtd_indisponiveis}\n"

        if qtd_disponiveis > 0:
            msg += "\n🎵 Músicas Online:\n" + "\n".join(disponiveis[:10])
            if qtd_disponiveis > 10: msg += "\n... e outras."

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"❌ ERRO: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
