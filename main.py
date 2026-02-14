import requests
import base64

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = 'a873df6bb1974db6b963d25c14bf695a'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'
MY_MARKET = 'BR'

def check_for_updates():
    try:
        # 1. Autenticação por Link Direto (Client Credentials)
        # Este fluxo não usa Redirect URI, por isso é mais seguro agora
        auth_bytes = f"{CLIENT_ID}:{CLIENT_SECRET}".encode('utf-8')
        auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
        
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_base64}"},
            data={"grant_type": "client_credentials"}
        ).json()
        token = token_res.get('access_token')

        # 2. Acesso ao Endpoint de Faixas
        # Usamos o link direto da API para evitar bloqueios de interface
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100"
        headers = {"Authorization": f"Bearer {token}"}
        
        res = requests.get(url, headers=headers)
        
        if res.status_code == 403:
            msg = "ERRO 403: O Spotify ainda bloqueia seu App. Verifique se o seu e-mail esta no User Management."
        elif res.status_code == 200:
            data = res.json()
            total = data.get('total', 0)
            items = data.get('items', [])
            
            total_analisado = 0
            liberadas = []
            
            for item in items:
                total_analisado += 1
                track = item.get('track')
                if track and MY_MARKET in track.get('available_markets', []):
                    liberadas.append(f"{track['name']} - {track['artists'][0]['name']}")
            
            if total_analisado > 0:
                msg = f"SUCESSO! Li {total_analisado} musicas de um total de {total}. Novas no BR: {len(liberadas)}"
            else:
                msg = f"CONECTADO: Mas a lista de musicas veio vazia. Verifique se a playlist e publica."
        else:
            msg = f"Erro inesperado: Status {res.status_code}"

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro Script: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
