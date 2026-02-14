import requests
import base64

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'

def check_for_updates():
    try:
        # 1. Gerar Token com identidade protegida
        auth_str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        
        # Headers de um navegador real para evitar o bloqueio
        headers_comuns = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }

        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={**headers_comuns, "Authorization": f"Basic {auth_str}"},
            data={"grant_type": "client_credentials"}
        )
        token = token_res.json().get('access_token')

        # 2. Acesso à Playlist (Apenas os primeiros itens para teste)
        # Se o Forbidden persistir aqui, o Spotify bloqueou esse ID de playlist para APIs
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=10"
        
        res = requests.get(url, headers={**headers_comuns, "Authorization": f"Bearer {token}"})

        if res.status_code == 200:
            total = res.json().get('total', 0)
            msg = f"VITÓRIA! O modo camuflagem funcionou. {total} faixas detectadas. O rastreador está oficialmente vivo!"
        elif res.status_code == 403:
            msg = "ERRO 403: O Spotify bloqueou permanentemente o acesso via API a esta playlist específica."
        else:
            msg = f"Falha: Status {res.status_code}. O Spotify está instável."

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro Crítico: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
