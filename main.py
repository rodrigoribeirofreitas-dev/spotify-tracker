import requests
import base64

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'
MY_MARKET = 'BR'

def check_for_updates():
    try:
        # 1. Autenticação (O que funcionou)
        auth_str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_str}"},
            data={"grant_type": "client_credentials"}
        ).json()
        token = token_res.get('access_token')

        # 2. Varredura Completa (Paginação)
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100&market={MY_MARKET}"
        headers = {"Authorization": f"Bearer {token}"}
        
        liberadas = []
        total_analisado = 0
        total_meta = 0

        while url:
            res = requests.get(url, headers=headers).json()
            
            if total_meta == 0:
                total_meta = res.get('total', 0)
            
            items = res.get('items', [])
            if not items:
                break

            for item in items:
                track = item.get('track')
                if track and track.get('name'):
                    total_analisado += 1
                    # Se a música aparece aqui com market=BR, ela está disponível
                    # Músicas indisponíveis (cinzas) não retornam o objeto 'track' completo ou são filtradas
                    artist = track['artists'][0]['name'] if track.get('artists') else "Unknown"
                    liberadas.append(f"{track['name']} - {artist}")
            
            url = res.get('next') # Pega a próxima página de 100

        # 3. Notificação Final
        if liberadas:
            # Envia apenas as primeiras 20 para não travar o ntfy, mas avisa o total
            lista_str = "\n".join(liberadas[:20])
            msg = f"🔥 VITÓRIA! {len(liberadas)} músicas detectadas no BR!\n\n{lista_str}"
            if len(liberadas) > 20:
                msg += f"\n... e mais {len(liberadas)-20} faixas."
        else:
            msg = f"Rastreador OK: {total_analisado} de {total_meta} músicas verificadas. Tudo segue indisponível no BR."

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro no Loop: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
