import requests
import base64

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'

def check_for_updates():
    try:
        # 1. Autenticação Reforçada
        auth_str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        
        # Tentamos o acesso via conta de desenvolvedor (Whitelist)
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_str}"},
            data={"grant_type": "client_credentials"}
        ).json()
        token = token_res.get('access_token')

        # 2. Chamada Direta ao Endpoint de Playlist (Modo Verboso)
        # Se o 404 persistir, o Spotify exige login de usuário (OAuth2)
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}"
        headers = {"Authorization": f"Bearer {token}"}
        
        res = requests.get(url, headers=headers)
        
        if res.status_code == 200:
            data = res.json()
            total = data.get('tracks', {}).get('total', 0)
            msg = f"VITÓRIA! Conectado como Desenvolvedor. {total} músicas encontradas na lista principal."
        elif res.status_code == 404:
            msg = "BLOQUEIO DE PRIVACIDADE: O Spotify escondeu a lista. Solução: No Dashboard, vá em 'User Management' e adicione seu e-mail do Spotify."
        else:
            msg = f"Erro {res.status_code}: O Spotify recusou a conexão automática."

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
