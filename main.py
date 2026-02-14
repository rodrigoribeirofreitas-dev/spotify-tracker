import requests
import base64

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = 'a873df6bb1974db6b963d25c14bf695a'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'

def check_for_updates():
    try:
        # Gerando o Token
        auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
        auth_b64 = base64.b64encode(auth_str.encode()).decode()
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_base64}"},
            data={"grant_type": "client_credentials"}
        )
        token = token_res.json().get('access_token')

        # Chamada SEM o parametro 'market' para evitar o 403
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks"
        res = requests.get(url, headers={"Authorization": f"Bearer {token}"})

        if res.status_code == 200:
            msg = "CONECTADO: O Spotify finalmente liberou o acesso!"
        elif res.status_code == 403:
            msg = "ERRO 403 persistente. O problema esta na visibilidade da playlist no perfil."
        else:
            msg = f"Erro {res.status_code}: Falha inesperada."

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
