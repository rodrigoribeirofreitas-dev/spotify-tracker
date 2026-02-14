import requests
import base64

# Credenciais e Playlist Principal
CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm' 
NTFY_TOPIC = 'spotify_tracker'
MY_MARKET = 'BR'

def check_for_updates():
    try:
        # 1. Autenticação
        auth_str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_str}"},
            data={"grant_type": "client_credentials"}
        ).json()
        token = token_res.get('access_token')

        # 2. Varredura Completa com Paginação
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100"
        headers = {"Authorization": f"Bearer {token}"}
        
        liberadas = []
        total_analisado = 0
        total_no_spotify = 0

        while url:
            res = requests.get(url, headers=headers).json()
            
            # Pega o total real na primeira passada
            if total_no_spotify == 0:
                total_no_spotify = res.get('total', 0)
            
            items = res.get('items', [])
            if not items:
                break

            for item in items:
                track = item.get('track')
                if track:
                    total_analisado += 1
                    # Verifica disponibilidade no mercado brasileiro
                    markets = track.get('available_markets', [])
                    if MY_MARKET in markets:
                        artist = track['artists'][0]['name'] if track.get('artists') else "Unknown"
                        liberadas.append(f"{track['name']} - {artist}")
            
            # Vai para a próxima página de 100 músicas
            url = res.get('next')

        # 3. Notificação Customizada
        if liberadas:
            msg = f"🔥 BOAS NOTÍCIAS! {len(liberadas)} músicas liberadas no BR:\n\n" + "\n".join(liberadas)
            title = "⚠️ Novidade na Playlist!"
        else:
            msg = f"Scan concluído: {total_analisado} de {total_no_spotify} músicas verificadas. Nenhuma novidade no BR."
            title = "Rastreador OK"

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=msg.encode('utf-8'),
                      headers={"Title": title})

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro na playlist principal: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
