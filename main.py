import requests
import base64

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = 'a873df6bb1974db6b963d25c14bf695a'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
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

        # 2. Varredura Total
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=2000"
        headers = {"Authorization": f"Bearer {token}"}
        
        liberadas = []
        total_analisado = 0

        while url:
            res = requests.get(url, headers=headers).json()
            items = res.get('items', [])
            
            if not items:
                break

            for item in items:
                # Contamos o item assim que ele aparece na lista, antes de filtrar
                total_analisado += 1
                
                track = item.get('track')
                if track and isinstance(track, dict):
                    markets = track.get('available_markets', [])
                    # Se o Brasil estiver liberado, adicionamos à lista de boas notícias
                    if MY_MARKET in markets:
                        artist = track['artists'][0]['name'] if track.get('artists') else "Unknown"
                        liberadas.append(f"{track.get('name', 'S/N')} - {artist}")
            
            # Pega o link para os próximos 100 itens
            url = res.get('next')

        # 3. Notificação para o ntfy
        if liberadas:
            msg = f"BOAS NOTICIAS! {len(liberadas)} musicas liberadas no BR:\n\n" + "\n".join(liberadas)
            title = "⚠️ Novidade na Playlist!"
        else:
            # Aqui garantimos que o 'total_analisado' apareça na mensagem
            msg = f"Scan concluido: {total_analisado} musicas verificadas. Nada liberado para {MY_MARKET} ainda."
            title = "Status do Rastreador"

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=msg.encode('utf-8'),
                      headers={"Title": title})

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro Script: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
