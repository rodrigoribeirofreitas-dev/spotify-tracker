import requests
import base64

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'

def check_for_updates():
    try:
        # 1. Autenticação Direta (Sem Redirect URI)
        auth_str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_str}"},
            data={"grant_type": "client_credentials"}
        ).json()
        token = token_res.get('access_token')

        # 2. Acesso ao Objeto da Playlist (Não apenas às tracks)
        # Pedimos o objeto completo para furar o bloqueio de lista vazia
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?market=BR"
        
        res = requests.get(url, headers=headers).json()
        
        # Tentamos extrair o total de duas fontes diferentes no JSON
        total_meta = res.get('tracks', {}).get('total', 0)
        items = res.get('tracks', {}).get('items', [])
        
        if total_meta > 0:
            msg = f"CONECTADO! A playlist '{res.get('name')}' foi encontrada.\nTotal de músicas: {total_meta}."
            if not items:
                msg += "\n(Nota: Os itens ainda estão ocultos, mas o contador foi liberado.)"
        else:
            msg = "O Spotify ainda reporta 0 músicas. Ação: No App do celular, remova a playlist do perfil e adicione-a novamente como PÚBLICA."

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro Técnico: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
