import requests
import base64

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

        # 2. Chamada com FILTRO DE CAMPOS (O segredo para listas bloqueadas)
        # Pedimos apenas o essencial para 'furar' o bloqueio de privacidade
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?fields=total,items(track(name,artists,available_markets))&limit=100"
        headers = {"Authorization": f"Bearer {token}"}
        
        res = requests.get(url, headers=headers).json()
        
        total_playlist = res.get('total', 0)
        items = res.get('items', [])
        
        liberadas = []
        for item in items:
            track = item.get('track')
            if track and MY_MARKET in track.get('available_markets', []):
                liberadas.append(f"{track['name']} - {track['artists'][0]['name']}")

        # 3. Notificação
        if total_playlist > 0:
            if items:
                msg = f"SUCESSO! Li as primeiras {len(items)} de {total_playlist} músicas."
                if liberadas:
                    msg += f"\n\n🔥 DISPONÍVEIS: " + "\n".join(liberadas)
            else:
                msg = f"O Spotify diz que há {total_playlist} músicas, mas o acesso aos itens foi NEGADO. Verifique se a playlist é PÚBLICA e está no seu PERFIL."
        else:
            msg = "A lista continua vindo zerada. O Spotify bloqueou este ID para aplicativos externos."

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
