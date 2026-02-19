import requests
import base64

# Suas credenciais
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
REFRESH_TOKEN = 'AQCv5L8kX9mP3qZ7r2W1n4J6L8M0N2P4Q6R8S0T2U4V6W8X0Y2Z4a6b8c0d2e4f6g8h0i2j4k6l8m0n2p4q6r8s0t2u4v6w8x0y2z4A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6'
PLAYLIST_ID = '7K33pCw9Dq9o9X6S8W1n4J'

def obter_token():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    res = requests.post("https://accounts.spotify.com/api/token", 
                        headers={"Authorization": f"Basic {auth_str}"},
                        data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN})
    return res.json().get('access_token')

def rastrear_playlist():
    token = obter_token()
    headers = {"Authorization": f"Bearer {token}"}
    indisponiveis = []
    total_real = 0
    offset = 0

    while True:
        # Puxando os itens da sua playlist com verificação de mercado (BR)
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?offset={offset}&limit=100&market=BR"
        res = requests.get(url, headers=headers).json()
        items = res.get('items', [])
        
        if not items: break

        for item in items:
            track = item.get('track')
            if not track: continue
            total_real += 1
            # O campo is_playable agora virá correto com a nova permissão
            if track.get('is_playable') is False:
                indisponiveis.append(f"🚫 {track['artists'][0]['name']} - {track['name']}")
        
        offset += 100
        if len(items) < 100: break

    # Montando o relatório final honesto
    status = "⚠️ FAIXAS BLOQUEADAS" if indisponiveis else "✅ PLAYLIST INTEGRAL"
    msg = f"{status}\n\nTotal lido na Playlist: {total_real}\nIndisponíveis no Brasil: {len(indisponiveis)}\n\n"
    msg += "\n".join(indisponiveis[:30]) if indisponiveis else "Todas as músicas estão disponíveis para você."

    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    rastrear_playlist()
