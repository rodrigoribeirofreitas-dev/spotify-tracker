import requests
import base64

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

        # 2. Varredura com Parâmetro de Mercado Obrigatório
        # O segredo é manter o market=BR em todas as chamadas
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100&market={MY_MARKET}"
        headers = {"Authorization": f"Bearer {token}"}
        
        liberadas = []
        total_analisado = 0
        total_meta = 0

        while url:
            # Garante que o market=BR seja anexado se a URL 'next' não o tiver
            if 'market=' not in url:
                url += f"&market={MY_MARKET}"
                
            res = requests.get(url, headers=headers).json()
            
            if total_meta == 0:
                total_meta = res.get('total', 0)
            
            items = res.get('items', [])
            if not items:
                break

            for item in items:
                track = item.get('track')
                if track:
                    total_analisado += 1
                    # Se a música está disponível no BR, ela terá o nome visível aqui
                    if track.get('name'):
                        artist = track['artists'][0]['name'] if track.get('artists') else "Unknown"
                        liberadas.append(f"{track['name']} - {artist}")
            
            url = res.get('next')

        # 3. Notificação Inteligente
        if total_analisado > 0:
            if liberadas:
                msg = f"🔥 VITÓRIA! {len(liberadas)} músicas detectadas no BR!\n\n" + "\n".join(liberadas[:20])
            else:
                msg = f"Rastreador OK: {total_analisado} de {total_meta} músicas verificadas. Nada no BR ainda."
        else:
            msg = f"ALERTA: O Spotify ocultou as músicas novamente (Total meta: {total_meta}). Tentando contornar..."

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro Técnico: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
