import requests
import base64

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'
MY_MARKET = 'BR'

def check_for_updates():
    try:
        # 1. Autenticação (Corrigida)
        auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
        auth_base64 = base64.b64encode(auth_str.encode()).decode()
        
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_base64}"},
            data={"grant_type": "client_credentials"}
        )
        token = token_res.json().get('access_token')

        # 2. Busca das Músicas (Com Paginação para ler as ~1700)
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100&market={MY_MARKET}"
        headers = {"Authorization": f"Bearer {token}"}
        
        liberadas = []
        total_analisado = 0
        total_no_spotify = 0

        while url:
            res = requests.get(url, headers=headers).json()
            
            # Pega o total real na primeira resposta
            if total_no_spotify == 0:
                total_no_spotify = res.get('total', 0)
            
            items = res.get('items', [])
            if not items:
                break

            for item in items:
                track = item.get('track')
                if track and track.get('name'):
                    total_analisado += 1
                    # Como passamos 'market=BR' na URL, as faixas que 
                    # retornarem aqui são as que estão disponíveis.
                    artist = track['artists'][0]['name'] if track.get('artists') else "Unknown"
                    liberadas.append(f"{track['name']} - {artist}")
            
            # Vai para a próxima página
            url = res.get('next')

        # 3. Notificação
        if total_analisado > 0:
            if liberadas:
                msg = f"🔥 SUCESSO! {len(liberadas)} músicas disponíveis no BR:\n\n" + "\n".join(liberadas[:20])
                if len(liberadas) > 20: msg += "\n... e outras."
            else:
                msg = f"Rastreador OK: {total_analisado} de {total_no_spotify} músicas lidas. Nenhuma liberada no BR ainda."
        else:
            msg = f"A API conectou, mas a lista veio vazia. Playlist ID: {PLAYLIST_ID}"

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro Técnico: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
