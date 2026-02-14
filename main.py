import requests
import base64

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = 'a873df6bb1974db6b963d25c14bf695a'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'

def check_for_updates():
    try:
        # 1. Obtendo o Token
        auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
        auth_base64 = base64.b64encode(auth_str.encode()).decode()
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_base64}"},
            data={"grant_type": "client_credentials"}
        )
        token = token_res.json().get('access_token')

        # 2. Acessando a Playlist
        url = f"http://open.spotify.com/playlist/{PLAYLIST_ID}"
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get(url, headers=headers)

        if res.status_code == 200:
            tracks = res.json().get('items', [])
            msg = f"Sucesso! Scan concluido em {len(tracks)} musicas."
        else:
            msg = f"Erro {res.status_code}: Verifique se salvou as alteracoes no Dashboard."

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro Script: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
