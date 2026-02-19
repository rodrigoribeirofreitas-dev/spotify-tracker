import requests
import base64

CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
# Chave que geramos às 16:11
REFRESH_TOKEN = 'AQCv5L8kX9mP3qZ7r2W1n4J6L8M0N2P4Q6R8S0T2U4V6W8X0Y2Z4a6b8c0d2e4f6g8h0i2j4k6l8m0n2p4q6r8s0t2u4v6w8x0y2z4A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6'
# ID da sua playlist
PLAYLIST_ID = '7K33pCw9Dq9o9X6S8W1n4J'

def rodar():
    # 1. Pega o Token de Acesso (resolve o erro 'No token provided')
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    res = requests.post("https://accounts.spotify.com/api/token", 
                        headers={"Authorization": f"Basic {auth_str}"},
                        data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN})
    token = res.json().get('access_token')

    # 2. Busca as músicas na sua playlist
    headers = {"Authorization": f"Bearer {token}"}
    indisponiveis = []
    total = 0
    url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?market=BR"
    
    res_playlist = requests.get(url, headers=headers).json()
    items = res_playlist.get('items', [])

    for item in items:
        track = item.get('track')
        if track:
            total += 1
            if track.get('is_playable') is False:
                indisponiveis.append(f"🚫 {track['artists'][0]['name']} - {track['name']}")

    # 3. Envia o resultado REAL para o seu celular
    status = "⚠️ MÚSICAS SUMIRAM" if indisponiveis else "✅ TUDO OK"
    msg = f"{status}\nTotal na Playlist: {total}\nBloqueadas: {len(indisponiveis)}"
    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    rodar()
