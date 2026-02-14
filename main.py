import requests
import base64

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = 'a873df6bb1974db6b963d25c14bf695a'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'

def check_for_updates():
    try:
        # 1. Obter Token via Client Credentials (Manual)
        auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
        auth_base64 = base64.b64encode(auth_str.encode()).decode()
        
        token_url = "https://accounts.spotify.com/api/token"
        headers_token = {"Authorization": f"Basic {auth_base64}"}
        data_token = {"grant_type": "client_credentials"}
        
        token_res = requests.post(token_url, headers=headers_token, data=data_token)
        token = token_res.json().get('access_token')

        if not token:
            raise Exception("Nao foi possivel gerar o token. Verifique Client ID/Secret.")

        # 2. Acessar a Playlist diretamente
        api_url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks"
        headers_api = {"Authorization": f"Bearer {token}"}
        
        res = requests.get(api_url, headers=headers_api)
        
        if res.status_code == 403:
            msg = "Erro 403: O Spotify ainda recusa o acesso deste App. Verifique o User Management e clique em SAVE."
        elif res.status_code == 200:
            tracks = res.json().get('items', [])
            msg = f"Sucesso! Conectado. {len(tracks)} faixas encontradas na primeira pagina."
        else:
            msg = f"Erro inesperado: Status {res.status_code}"

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro Script: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
