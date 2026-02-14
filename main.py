import requests
import base64

# Credenciais e a NOVA Playlist
CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm' 
NTFY_TOPIC = 'spotify_tracker'
MY_MARKET = 'BR'

def check_for_updates():
    try:
        # 1. Autenticação (Fluxo de Servidor)
        auth_str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_str}"},
            data={"grant_type": "client_credentials"}
        ).json()
        token = token_res.get('access_token')

        # 2. Varredura da Nova Playlist
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100"
        headers = {"Authorization": f"Bearer {token}"}
        
        liberadas = []
        total_analisado = 0

        res = requests.get(url, headers=headers).json()
        items = res.get('items', [])
        total_playlist = res.get('total', 0)

        for item in items:
            track = item.get('track')
            if track:
                total_analisado += 1
                # Verifica se o Brasil está nos mercados disponíveis
                if MY_MARKET in track.get('available_markets', []):
                    artist = track['artists'][0]['name'] if track.get('artists') else "Unknown"
                    liberadas.append(f"{track['name']} - {artist}")

        # 3. Notificação Customizada
        if liberadas:
            msg = f"BOAS NOTÍCIAS! {len(liberadas)} músicas liberadas na nova lista:\n\n" + "\n".join(liberadas)
            title = "⚠️ Novidade!"
        else:
            msg = f"Nova Playlist OK: {total_analisado} de {total_playlist} músicas verificadas. Nada no BR ainda."
            title = "Rastreador Ativo"

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=msg.encode('utf-8'),
                      headers={"Title": title})

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro na nova lista: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
