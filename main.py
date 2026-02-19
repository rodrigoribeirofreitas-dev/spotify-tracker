import requests
import base64

CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
# Use o Refresh Token gerado no último passo de sucesso
REFRESH_TOKEN = 'AQCv5L8kX9mP3qZ7r2W1n4J6L8M0N2P4Q6R8S0T2U4V6W8X0Y2Z4a6b8c0d2e4f6g8h0i2j4k6l8m0n2p4q6r8s0t2u4v6w8x0y2z4A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6'
# ID da sua playlist de 1.699 faixas
PLAYLIST_ID = '7K33pCw9Dq9o9X6S8W1n4J' 

def monitorar_v2():
    # 1. Obter Token
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    res_token = requests.post("https://accounts.spotify.com/api/token", 
                             headers={"Authorization": f"Basic {auth_str}"},
                             data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN})
    token = res_token.json().get('access_token')

    # 2. Ler Playlist
    headers = {"Authorization": f"Bearer {token}"}
    indisponiveis = []
    total_real = 0
    offset = 0

    while True:
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?offset={offset}&limit=100&market=BR"
        res = requests.get(url, headers=headers)
        
        if res.status_code != 200:
            msg_erro = f"❌ Erro API: {res.status_code} - Verifique permissões."
            requests.post("https://ntfy.sh/spotify_tracker", data=msg_erro.encode('utf-8'))
            return

        dados = res.json()
        items = dados.get('items', [])
        if not items: break

        for item in items:
            track = item.get('track')
            if not track: continue
            total_real += 1
            if track.get('is_playable') is False:
                indisponiveis.append(f"🚫 {track['artists'][0]['name']} - {track['name']}")
        
        offset += 100
        if len(items) < 100: break

    # 3. Relatório Dinâmico (Sem números fixos)
    if total_real == 0:
        msg = "⚠️ Alerta: A playlist foi lida mas retornou 0 músicas. O ID ou a permissão estão incorretos."
    else:
        status = "⚠️ FAIXAS BLOQUEADAS" if indisponiveis else "✅ PLAYLIST INTEGRAL"
        detalhes = "\n".join(indisponiveis[:20]) if indisponiveis else "Todas as músicas estão disponíveis."
        msg = f"{status}\n\nTotal lido agora: {total_real}\nIndisponíveis: {len(indisponiveis)}\n\n{detalhes}"

    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    monitorar_v2()
