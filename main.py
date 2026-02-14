import requests
import base64

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = 'a873df6bb1974db6b963d25c14bf695a'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm' # Certifique-se de que é só o código!
NTFY_TOPIC = 'spotify_tracker'
MY_MARKET = 'BR'

def check_for_updates():
    try:
        # 1. Autenticação
        auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
        auth_base64 = base64.b64encode(auth_str.encode()).decode()
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_base64}"},
            data={"grant_type": "client_credentials"}
        ).json()
        token = token_res.get('access_token')

        # 2. Teste de Acesso Direto
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(url, headers=headers)
        data = response.json()

        # DIAGNÓSTICO: Se a lista de itens estiver vazia, vamos descobrir o porquê
        items = data.get('items', [])
        total_no_spotify = data.get('total', 'Desconhecido')

        if not items:
            msg = f"ERRO: O Spotify retornou lista VAZIA. Total reportado: {total_no_spotify}. Verifique se a playlist está 'Adicionada ao Perfil'."
        else:
            total_analisado = 0
            liberadas = []
            
            # Varredura (Simplificada para o teste)
            for item in items:
                total_analisado += 1
                track = item.get('track')
                if track and MY_MARKET in track.get('available_markets', []):
                    liberadas.append(f"{track['name']}")

            msg = f"SUCESSO! Li {total_analisado} musicas de um total de {total_no_spotify}. Liberadas: {len(liberadas)}"

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro Script: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
