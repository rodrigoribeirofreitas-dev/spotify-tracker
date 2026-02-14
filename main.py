import requests
import base64

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'

def check_for_updates():
    try:
        # 1. Token com cabeçalhos de navegador
        auth_str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        headers_auth = {
            "Authorization": f"Basic {auth_str}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers=headers_auth,
            data={"grant_type": "client_credentials"}
        )
        token = token_res.json().get('access_token')

        # 2. Acesso à Playlist sem filtros (URL limpa)
        # Se o erro 'Forbidden' persistir aqui, o ID da playlist está bloqueado para APIs
        api_url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=50"
        headers_api = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        res = requests.get(api_url, headers=headers_api)
        
        if res.status_code == 403:
            msg = "ERRO 403: O Spotify bloqueou este ID de playlist para acesso externo via API."
        elif res.status_code == 200:
            total = res.json().get('total', 0)
            msg = f"SUCESSO! Link direto liberado. {total} faixas encontradas. O rastreador está online."
        else:
            msg = f"Falha técnica: Status {res.status_code}"

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro crítico: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
