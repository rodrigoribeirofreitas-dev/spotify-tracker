import requests
import base64
import time

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'

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

        headers = {"Authorization": f"Bearer {token}"}

        # 2. Pega o Total (Meta)
        url_meta = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?fields=tracks(total)"
        res_meta = requests.get(url_meta, headers=headers).json()
        total_meta = res_meta.get('tracks', {}).get('total', 0)

        # 3. Varredura Ampla (Sem filtro de mercado na URL)
        url_tracks = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100"
        disponiveis = []
        
        while url_tracks:
            res_tracks = requests.get(url_tracks, headers=headers).json()
            items = res_tracks.get('items', [])
            
            for item in items:
                track = item.get('track')
                # CRITÉRIO NOVO: Se tem nome e ID, o robô consegue "ver" a música
                if track and track.get('id') and track.get('name'):
                    # Verifica se ela NÃO é um item local ou fantasma
                    if not track.get('is_local'):
                        artist = track['artists'][0]['name'] if track.get('artists') else "Unknown"
                        disponiveis.append(f"{track['name']} - {artist}")
            
            url_tracks = res_tracks.get('next')
            if url_tracks: time.sleep(0.5)

        # 4. Relatório
        qtd_disponiveis = len(disponiveis)
        qtd_indisponiveis = total_meta - qtd_disponiveis

        msg = f"📊 Relatório Atualizado\n\n"
        msg += f"Total: {total_meta}\n"
        msg += f"🟢 Tocáveis/Visíveis: {qtd_disponiveis}\n"
        msg += f"🔴 Bloqueadas: {qtd_indisponiveis}\n"

        if qtd_disponiveis > 0:
            msg += "\n🎵 Exemplos Disponíveis:\n" + "\n".join(disponiveis[:10])

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"❌ Erro: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
