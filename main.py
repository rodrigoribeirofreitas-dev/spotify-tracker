import requests
import base64

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = 'a873df6bb1974db6b963d25c14bf695a'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'
MY_MARKET = 'BR'

def check_for_updates():
    try:
        # 1. Autenticação (Client Credentials)
        auth_base64 = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_base64}"},
            data={"grant_type": "client_credentials"}
        ).json()
        token = token_res.get('access_token')

        # 2. Varredura Total da Playlist
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100"
        headers = {"Authorization": f"Bearer {token}"}
        
        liberadas = []
        total_analisado = 0
        total_reportado_api = 0

        while url:
            res_raw = requests.get(url, headers=headers)
            res = res_raw.json()
            
            if res_raw.status_code != 200:
                raise Exception(f"Erro API: {res_raw.status_code}")

            total_reportado_api = res.get('total', 0)
            items = res.get('items', [])
            
            if not items:
                break

            for item in items:
                total_analisado += 1
                track = item.get('track')
                if track and isinstance(track, dict):
                    markets = track.get('available_markets', [])
                    if MY_MARKET in markets:
                        artist = track['artists'][0]['name'] if track.get('artists') else "Unknown"
                        liberadas.append(f"{track.get('name', 'S/N')} - {artist}")
            
            url = res.get('next')

        # 3. Notificação de Status
        if total_analisado == 0:
            msg = f"ALERTA: Playlist vazia para a API. Total no Spotify: {total_reportado_api}. Verifique 'Adicionar ao Perfil'."
        elif liberadas:
            msg = f"BOAS NOTICIAS! {len(liberadas)} musicas liberadas:\n\n" + "\n".join(liberadas)
        else:
            msg = f"Scan concluido: {total_analisado} musicas verificadas (Total: {total_reportado_api}). Nada no BR ainda."

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro Script: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
