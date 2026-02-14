import requests
import base64

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'
MY_MARKET = 'BR'

def check_for_updates():
    try:
        # 1. Autenticação Direta
        auth_str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_base64}"}, # Se der erro aqui, use auth_str
            data={"grant_type": "client_credentials"}
        ).json()
        token = token_res.get('access_token')

        # 2. O Pulo do Gato: Forçar a leitura da primeira página com Market
        # Usamos 'market=BR' para que o Spotify seja obrigado a filtrar os itens
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100&market={MY_MARKET}"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(url, headers=headers)
        
        # Se ele retornar 0 aqui, vamos tentar um 'offset' de 1 para forçar o cache
        if response.json().get('total', 0) == 0:
            url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100&offset=1&market={MY_MARKET}"
            response = requests.get(url, headers=headers)

        data = response.json()
        total_real = data.get('total', 0)
        items = data.get('items', [])
        
        liberadas = []
        total_lido = 0

        for item in items:
            track = item.get('track')
            if track and track.get('name'):
                total_lido += 1
                # Se a música aparecer aqui, é porque ela está disponível para o Market BR
                artist = track['artists'][0]['name'] if track.get('artists') else "Unknown"
                liberadas.append(f"{track['name']} - {artist}")

        # 3. Notificação Realista
        if total_real > 0:
            if liberadas:
                msg = f"🔥 SUCESSO! {len(liberadas)} músicas detectadas como ONLINE no BR!\n\n" + "\n".join(liberadas)
            else:
                msg = f"Rastreador Conectado: Li {total_lido} de {total_real} músicas. Nenhuma liberada no BR ainda."
        else:
            msg = "A API do Spotify continua reportando 0 músicas. Isso indica que o seu Client ID não tem permissão de leitura para este conteúdo."

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro Técnico: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
