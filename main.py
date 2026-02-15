import requests
import base64
import time

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'
MY_MARKET = 'BR'

def get_token():
    auth_str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    res = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {auth_str}"},
        data={"grant_type": "client_credentials"}
    ).json()
    return res.get('access_token')

def check_for_updates():
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # TENTATIVA 1: Pegar o total real da playlist
        url_meta = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?fields=tracks(total)"
        meta = requests.get(url_meta, headers=headers).json()
        total_meta = meta.get('tracks', {}).get('total', 0)

        # Se vier 0, espera 5 segundos e tenta uma última vez
        if total_meta == 0:
            time.sleep(5)
            meta = requests.get(url_meta, headers=headers).json()
            total_meta = meta.get('tracks', {}).get('total', 0)

        if total_meta == 0:
            msg = "ALERTA: O Spotify bloqueou a leitura novamente. Tentaremos na próxima rodada (daqui a 3h)."
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))
            return

        # VARREDURA: Se temos o total, vamos ler as músicas
        liberadas = []
        url_tracks = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100&market={MY_MARKET}"
        
        while url_tracks:
            res = requests.get(url_tracks, headers=headers).json()
            items = res.get('items', [])
            
            for item in items:
                track = item.get('track')
                if track and track.get('name'):
                    # Se o objeto track vier preenchido com market=BR, ela está disponível
                    artist = track['artists'][0]['name'] if track.get('artists') else "Unknown"
                    liberadas.append(f"{track['name']} - {artist}")
            
            url_tracks = res.get('next')
            if url_tracks: time.sleep(1) # Pausa curta para não ser bloqueado no loop

        # NOTIFICAÇÃO
        if liberadas:
            msg = f"🔥 NOVIDADE! {len(liberadas)} músicas voltaram ao BR:\n\n" + "\n".join(liberadas[:15])
        else:
            msg = f"Rastreador OK: {total_meta} músicas monitoradas. Tudo segue indisponível no BR."

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro Técnico: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
