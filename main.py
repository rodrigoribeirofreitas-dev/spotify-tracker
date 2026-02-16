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
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_str}"},
            data={"grant_type": "client_credentials"}
        ).json()
        token = token_res.get('access_token')

        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        # 2. Leitura do Total (A parte que você confirmou que funciona)
        total_meta = 0
        for tentativa in range(2):
            url_meta = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?fields=tracks(total)&cache={random.random()}"
            res_meta = requests.get(url_meta, headers=headers).json()
            total_meta = res_meta.get('tracks', {}).get('total', 0)
            if total_meta > 0: break
            time.sleep(10)

        if total_meta == 0:
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data="⚠️ Erro de conexão com a playlist.".encode('utf-8'))
            return

        # 3. Verificação de Músicas (REMOVIDO O MARKET=BR DAQUI)
        # Ao remover o market, o Spotify para de esconder as faixas do robô
        url_tracks = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100"
        qtd_disponiveis = 0
        exemplos = []

        while url_tracks:
            res_tracks = requests.get(url_tracks, headers=headers).json()
            items = res_tracks.get('items', [])
            
            for item in items:
                track = item.get('track')
                # NOVO CRITÉRIO: Se tem ID e Nome, o código considera disponível
                if track and track.get('id') and track.get('name'):
                    # Filtra apenas para não contar arquivos MP3 locais do seu PC
                    if not track.get('is_local'):
                        qtd_disponiveis += 1
                        if len(exemplos) < 5:
                            artist = track['artists'][0]['name'] if track.get('artists') else "Unknown"
                            exemplos.append(f"{track['name']} - {artist}")
            
            url_tracks = res_tracks.get('next')
            if url_tracks: time.sleep(0.5)

        # 4. Cálculo do Placar
        qtd_indisponiveis = total_meta - qtd_disponiveis

        msg = f"📊 RELATÓRIO DE DISPONIBILIDADE\n\n"
        msg += f"Total na Playlist: {total_meta}\n"
        msg += f"🟢 Disponíveis: {qtd_disponiveis}\n"
        msg += f"🔴 Indisponíveis: {qtd_indisponiveis}\n"

        if exemplos:
            msg += "\n🎵 Algumas visíveis:\n" + "\n".join(exemplos)

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"❌ ERRO: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
