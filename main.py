import requests
import base64
import time
import random

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'

def check_for_updates():
    try:
        # 1. Autenticação
        auth_str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        token_res = requests.post("https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_str}"},
            data={"grant_type": "client_credentials"}).json()
        token = token_res.get('access_token')
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Tentativa de Leitura com Paciência (Anti-Bloqueio)
        total_meta = 0
        for i in range(3): # Aumentamos para 3 tentativas
            url_meta = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?fields=tracks(total)&cache={random.random()}"
            res_meta = requests.get(url_meta, headers=headers).json()
            total_meta = res_meta.get('tracks', {}).get('total', 0)
            
            if total_meta > 0:
                break
            time.sleep(30) # Se vier 0, espera 30 segundos para o servidor "respirar"

        if total_meta == 0:
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data="⚠️ AVISO: Spotify bloqueou o acesso temporariamente (Total 0). Tentando novamente na próxima rodada.".encode('utf-8'))
            return

        # 3. Varredura de Disponíveis (Sem filtros que causam erro)
        url_tracks = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100&fields=next,items(track(id,name))"
        qtd_disponiveis = 0
        
        while url_tracks:
            res_tracks = requests.get(url_tracks, headers=headers).json()
            items = res_tracks.get('items', [])
            for item in items:
                t = item.get('track')
                if t and t.get('id'): # Se tem ID, a música "existe" na lista
                    qtd_disponiveis += 1
            
            url_tracks = res_tracks.get('next')
            if url_tracks: time.sleep(1)

        # 4. Relatório
        msg = f"📊 PLACAR REAL\nTotal: {total_meta}\n🟢 Disponíveis: {qtd_disponiveis}\n🔴 Indisponíveis: {total_meta - qtd_disponiveis}"
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"❌ Erro: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
