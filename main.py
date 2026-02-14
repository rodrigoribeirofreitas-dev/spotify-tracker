import requests
import base64

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'

def check_for_updates():
    try:
        # 1. Autenticação Básica
        auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
        auth_base64 = base64.b64encode(auth_str.encode()).decode()
        
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_base64}"},
            data={"grant_type": "client_credentials"}
        )
        token = token_res.json().get('access_token')

        # 2. CHAMADA DE IMPACTO: Usando o endpoint de 'playlists' em vez de 'tracks'
        # Isso força o Spotify a entregar os metadados que ele está escondendo
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}"
        headers = {"Authorization": f"Bearer {token}"}
        
        res = requests.get(url, headers=headers).json()
        
        # O Spotify estrutura o JSON de playlist diferente do de tracks
        tracks_obj = res.get('tracks', {})
        items = tracks_obj.get('items', [])
        total_real = tracks_obj.get('total', 0)
        
        liberadas = []
        for item in items:
            track = item.get('track')
            if track and 'BR' in track.get('available_markets', []):
                liberadas.append(f"{track['name']} - {track['artists'][0]['name']}")

        # 3. Notificação
        if total_real > 0:
            if items:
                msg = f"VITÓRIA! O rastreador finalmente leu {len(items)} de {total_real} músicas."
                if liberadas:
                    msg += f"\n\n🔥 DISPONÍVEIS: " + ", ".join(liberadas)
            else:
                msg = f"Bloqueio de Conteúdo: A playlist tem {total_real} músicas, mas o Spotify as escondeu do robô. Ação: Mude a playlist para 'Pública' no seu Perfil."
        else:
            msg = "Falha Crítica: O Spotify não reconhece este ID de playlist como válido."

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
