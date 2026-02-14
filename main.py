import requests
import base64

# Credenciais e IDs
CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = 'a873df6bb1974db6b963d25c14bf695a'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'
MY_MARKET = 'BR'

def check_for_updates():
    try:
        # 1. Obter Token (Fluxo de Credenciais de Cliente)
        auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
        auth_base64 = base64.b64encode(auth_str.encode()).decode()
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_base64}"},
            data={"grant_type": "client_credentials"}
        ).json()
        token = token_res.get('access_token')

        # 2. Rastrear a Playlist (Sem filtro de mercado na URL para contar tudo)
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100"
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
                    # Verificação manual de disponibilidade no Brasil
                    markets = track.get('available_markets', [])
                    if MY_MARKET in markets:
                        liberadas.append(f"{track['name']} - {track['artists'][0]['name']}")
            
            # Navega para a próxima página de 100 músicas
            url = res.get('next')

        # 3. Enviar Notificação
        if liberadas:
            msg = f"BOAS NOTÍCIAS! {len(liberadas)} músicas foram liberadas no BR:\n\n" + "\n".join(liberadas)
            title = "⚠️ Músicas Disponíveis!"
            priority = "high"
        else:
            msg = f"Scan concluído: {total_analisado} itens verificados na tua playlist. Nenhuma novidade para o Brasil ainda."
            title = "Status do Rastreador"
            priority = "default"

        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=msg.encode('utf-8'),
            headers={"Title": title, "Priority": priority}
        )

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro no Script: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
