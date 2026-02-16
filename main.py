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
        # 1. Autenticação (Mantida)
        auth_str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        token_res = requests.post("https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_str}"},
            data={"grant_type": "client_credentials"}).json()
        token = token_res.get('access_token')
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Leitura do Total (Âncora de 1699)
        url_meta = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?fields=tracks(total)&cache={random.random()}"
        res_meta = requests.get(url_meta, headers=headers).json()
        total_meta = res_meta.get('tracks', {}).get('total', 0)

        # 3. Varredura de Disponibilidade (Lógica de Identificação Mínima)
        # IMPORTANTE: Removido market e adicionado campos específicos
        url_tracks = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100&fields=next,items(track(id,name,is_playable,restrictions))"
        qtd_disponiveis = 0
        
        while url_tracks:
            res_tracks = requests.get(url_tracks, headers=headers).json()
            items = res_tracks.get('items', [])
            
            for item in items:
                track = item.get('track')
                if not track: continue
                
                # Se o Spotify retornou o nome ou se a faixa NÃO possui restrições explícitas
                # Muitas vezes o 'id' aparece mas o 'name' some no bloqueio total
                if track.get('name') or track.get('id'):
                    # Se não houver a tag de restrição 'market', consideramos visível
                    restrictions = track.get('restrictions', {})
                    if 'reason' not in restrictions:
                        qtd_disponiveis += 1
            
            url_tracks = res_tracks.get('next')
            if url_tracks: time.sleep(0.5)

        # 4. Relatório Final
        qtd_indisponiveis = total_meta - qtd_disponiveis
        
        # Se mesmo assim der 0, o script enviará um aviso de "Modo de Segurança"
        msg = f"📊 STATUS DA PLAYLIST\n\n"
        msg += f"Total: {total_meta}\n"
        msg += f"🟢 Disponíveis: {qtd_disponiveis}\n"
        msg += f"🔴 Indisponíveis: {qtd_indisponiveis}\n"

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"❌ Erro: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
