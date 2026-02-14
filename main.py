import requests
import base64

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

        # 2. Leitura Direta do Objeto Playlist
        # Aqui pedimos o objeto 'tracks' dentro da playlist de uma vez
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}"
        headers = {"Authorization": f"Bearer {token}"}
        
        res = requests.get(url, headers=headers).json()
        
        # Tentamos pegar o total de várias formas para não vir 0
        tracks_data = res.get('tracks', {})
        items = tracks_data.get('items', [])
        total_no_spotify = tracks_data.get('total', 0)
        
        total_analisado = 0
        liberadas = []

        for item in items:
            track = item.get('track')
            if track:
                total_analisado += 1
                markets = track.get('available_markets', [])
                if MY_MARKET in markets:
                    artist = track['artists'][0]['name'] if track.get('artists') else "Desconhecido"
                    liberadas.append(f"{track['name']} - {artist}")

        # 3. Notificação de Impacto
        if total_no_spotify > 0:
            if liberadas:
                msg = f"🔥 ALERTA! {len(liberadas)} músicas liberadas no BR!\n\n" + "\n".join(liberadas)
            else:
                msg = f"Rastreador OK: Li as primeiras {total_analisado} músicas de {total_no_spotify}. Nada no BR ainda."
        else:
            msg = "O Spotify continua bloqueando a leitura desta playlist específica. Tente o teste da 'Playlist Espelho' com 5 músicas."

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
