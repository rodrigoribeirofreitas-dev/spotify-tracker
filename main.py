import requests
import base64

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = 'a873df6bb1974db6b963d25c14bf695a'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'

def check_for_updates():
    try:
        # 1. Gerar Token (Client Credentials Flow)
        auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
        auth_bytes = auth_str.encode('utf-8')
        auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
        
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_base64}"},
            data={"grant_type": "client_credentials"}
        )
        token = token_res.json().get('access_token')

        # 2. Acessar Playlist (Sem filtros extras para evitar 403)
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks"
        res = requests.get(url, headers={"Authorization": f"Bearer {token}"})

        if res.status_code == 200:
            total = len(res.json().get('items', []))
            msg = f"SUCESSO: Conectado! {total} faixas lidas da playlist."
        elif res.status_code == 403:
            msg = "ERRO 403: O Spotify ainda bloqueia este App. Tente criar um NOVO App no Dashboard."
        else:
            msg = f"Erro {res.status_code}: Falha na comunicacao."

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro Script: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
