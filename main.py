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

        # 2. Tentativa de Leitura do Total
        total_meta = 0
        for tentativa in range(2):
            url_meta = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?fields=tracks(total)&cache={random.random()}"
            res_meta = requests.get(url_meta, headers=headers).json()
            total_meta = res_meta.get('tracks', {}).get('total', 0)
            
            if total_meta > 0:
                break
            time.sleep(10)

        if total_meta == 0:
            # AGORA ENVIA ALERTA DE BLOQUEIO
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                          data=f"⚠️ BLOQUEIO: O Spotify retornou 0 músicas. Tentarei novamente em 3h.".encode('utf-8'))
            return

        # 3. Verificação de Músicas (Paginação)
        url_tracks = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100&market={MY_MARKET}"
        liberadas = []
        total_lido = 0

        while url_tracks:
            res_tracks = requests.get(url_tracks, headers=headers).json()
            items = res_tracks.get('items', [])
            
            for item in items:
                track = item.get('track')
                if track and track.get('name'):
                    total_lido += 1
                    artist = track['artists'][0]['name'] if track.get('artists') else "Unknown"
                    liberadas.append(f"{track['name']} - {artist}")
            
            url_tracks = res_tracks.get('next')
            if url_tracks: time.sleep(1)

        # 4. Notificações de Status (Sempre enviadas)
        if liberadas:
            msg = f"🔥 NOVIDADE! {len(liberadas)} músicas voltaram ao BR:\n\n" + "\n".join(liberadas[:10])
        else:
            msg = f"✅ Rastreador OK: {total_meta} músicas monitoradas. Nenhuma novidade no BR."

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        # AGORA ENVIA ERROS TÉCNICOS
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=f"❌ ERRO TÉCNICO: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
