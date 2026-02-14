import requests
import base64

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = 'a873df6bb1974db6b963d25c14bf695a'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'
MY_MARKET = 'BR'

def check_for_updates():
    try:
        # 1. Gerar Token
        auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
        auth_base64 = base64.b64encode(auth_str.encode()).decode()
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_base64}"},
            data={"grant_type": "client_credentials"}
        ).json()
        token = token_res.get('access_token')

        # 2. Rastrear Faixas (Loop para pegar todas as 1.698)
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?market={MY_MARKET}&limit=100"
        headers = {"Authorization": f"Bearer {token}"}
        
        liberadas = []
        total_analisado = 0

        while url:
            res = requests.get(url, headers=headers).json()
            items = res.get('items', [])
            
            for item in items:
                track = item.get('track')
                if track:
                    total_analisado += 1
                    # Verifica se a música pode ser reproduzida no Brasil
                    if track.get('is_playable'):
                        liberadas.append(f"{track['name']} - {track['artists'][0]['name']}")
            
            # Pega o link da próxima página de músicas
            url = res.get('next')

        # 3. Enviar Resultado para o ntfy
        if liberadas:
            msg = f"BOAS NOTICIAS! {len(liberadas)} musicas liberadas:\n\n" + "\n".join(liberadas)
            title = "Musicas Disponiveis!"
            priority = "high"
            tags = "tada,headphones"
        else:
            msg = f"Scan concluido: {total_analisado} musicas verificadas na playlist. Nenhuma novidade no momento."
            title = "Status do Rastreador"
            priority = "default"
            tags = "mag"

        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=msg.encode('utf-8'),
            headers={"Title": title, "Priority": priority, "Tags": tags}
        )

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro no Script: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
