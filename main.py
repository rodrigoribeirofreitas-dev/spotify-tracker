import requests
import base64

# Credenciais Fixas
CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = 'a873df6bb1974db6b963d25c14bf695a'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'

def check_for_updates():
    try:
        # 1. LINK DIRETO PARA O TOKEN
        # Conforme o manual: POST para /api/token com Basic Auth
        auth_base64 = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_base64}"},
            data={"grant_type": "client_credentials"}
        )
        token = token_res.json().get('access_token')

        if not token:
            raise Exception("Não foi possível gerar o token de acesso.")

        # 2. LINK DIRETO PARA A PLAYLIST
        # Acessando o endpoint de tracks sem parâmetros extras que causam 403
        api_url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(api_url, headers=headers)
        
        # Verificação de status real
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            total = len(items)
            msg = f"SUCESSO! O link direto funcionou. {total} faixas lidas na primeira página."
        elif response.status_code == 403:
            msg = "Erro 403: O Spotify barrou o link direto. O App precisa de um 'Reset' no Dashboard."
        else:
            msg = f"Erro na API: Status {response.status_code}"

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro Script: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
