import requests
import base64

CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
REFRESH_TOKEN = 'AQCv5L8kX9mP3qZ7r2W1n4J6L8M0N2P4Q6R8S0T2U4V6W8X0Y2Z4a6b8c0d2e4f6g8h0i2j4k6l8m0n2p4q6r8s0t2u4v6w8x0y2z4A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6'
PLAYLIST_ID = '7K33pCw9Dq9o9X6S8W1n4J'

def teste_direto():
    # 1. Tenta pegar o token com as chaves atuais
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    res = requests.post("https://accounts.spotify.com/api/token", 
                        headers={"Authorization": f"Basic {auth_str}"},
                        data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN})
    token = res.json().get('access_token')

    # 2. Tenta ler a contagem total da playlist sem carregar as músicas (mais leve)
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?fields=tracks.total"
    res_pl = requests.get(url, headers=headers).json()
    
    total = res_pl.get('tracks', {}).get('total', 0)

    # 3. Envia para o ntfy o que o Spotify responder
    msg = f"🔍 TESTE DE CONTAGEM\nTotal detectado pelo Spotify: {total}"
    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    teste_direto()
