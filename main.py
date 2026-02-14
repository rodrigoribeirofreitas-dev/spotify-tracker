import requests
import base64

# Suas novas credenciais atualizadas
CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'
MY_MARKET = 'BR'

def check_for_updates():
    try:
        # 1. Autenticação (Fluxo de Servidor)
        auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
        auth_base64 = base64.b64encode(auth_str.encode()).decode()
        
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_base64}"},
            data={"grant_type": "client_credentials"}
        )
        
        if token_res.status_code != 200:
            raise Exception(f"Erro na Autenticação: {token_res.status_code}")
            
        token = token_res.json().get('access_token')

        # 2. Varredura da Playlist (Sem filtros na URL para evitar 403)
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100"
        headers = {"Authorization": f"Bearer {token}"}
        
        liberadas = []
        total_analisado = 0
        total_playlist = 0

        while url:
            res_raw = requests.get(url, headers=headers)
            
            if res_raw.status_code == 403:
                raise Exception("Erro 403: O novo App ainda não tem permissão para ler esta playlist.")
                
            res_data = res_raw.json()
            total_playlist = res_data.get('total', 0)
            items = res_data.get('items', [])
            
            if not items:
                break

            for item in items:
                total_analisado += 1
                track = item.get('track')
                if track and isinstance(track, dict):
                    # Checagem manual de disponibilidade no Brasil
                    markets = track.get('available_markets', [])
                    if MY_MARKET in markets:
                        artist = track['artists'][0]['name'] if track.get('artists') else "Unknown"
                        liberadas.append(f"{track.get('name', 'S/N')} - {artist}")
            
            url = res_data.get('next')

        # 3. Notificação Final
        if liberadas:
            msg = f"BOAS NOTICIAS! {len(liberadas)} musicas liberadas no BR:\n\n" + "\n".join(liberadas)
            title = "⚠️ Musicas Disponiveis!"
        else:
            msg = f"Scan concluido: {total_analisado} musicas verificadas de {total_playlist}. Nada liberado no BR ainda."
            title = "Status do Rastreador"

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=msg.encode('utf-8'),
                      headers={"Title": title})

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro Script: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
