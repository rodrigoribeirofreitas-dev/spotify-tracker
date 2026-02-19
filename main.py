import requests
import base64

# Suas credenciais
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
# Sua chave mestra definitiva
REFRESH_TOKEN = 'AQCv5L8kX9mP3qZ7r2W1n4J6L8M0N2P4Q6R8S0T2U4V6W8X0Y2Z4a6b8c0d2e4f6g8h0i2j4k6l8m0n2p4q6r8s0t2u4v6w8x0y2z4A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6'
# O ID extraído da sua playlist: 7K33pC...
PLAYLIST_ID = '7K33pCw9Dq9o9X6S8W1n4J' 

def obter_token():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    res = requests.post("https://accounts.spotify.com/api/token", 
                        headers={"Authorization": f"Basic {auth_str}"},
                        data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN})
    return res.json().get('access_token')

def monitorar_playlist_especifica():
    token = obter_token()
    headers = {"Authorization": f"Bearer {token}"}
    indisponiveis = []
    total_rastreado = 0
    offset = 0

    while True:
        # Puxando os itens da sua PLAYLIST específica (não mais da biblioteca geral)
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?offset={offset}&limit=100&market=BR"
        res = requests.get(url, headers=headers).json()
        
        items = res.get('items', [])
        if not items:
            break

        for item in items:
            track = item.get('track')
            if not track: continue
            
            total_rastreado += 1
            # Verifica se a música está cinza (indisponível) no Brasil
            if track.get('is_playable') is False:
                indisponiveis.append(f"🚫 {track['artists'][0]['name']} - {track['name']}")
        
        offset += 100
        if len(items) < 100:
            break

    # Relatório com os dados REAIS da sua playlist
    status = "⚠️ FAIXAS BLOQUEADAS" if indisponiveis else "✅ PLAYLIST INTEGRAL"
    msg = f"{status}\n\nTotal na Playlist: {total_rastreado}\nIndisponíveis no Brasil: {len(indisponiveis)}\n\n"
    msg += "\n".join(indisponiveis[:30]) if indisponiveis else "Todas as músicas estão disponíveis para você em Londrina."
    
    if len(indisponiveis) > 30:
        msg += f"\n... e mais {len(indisponiveis) - 30} faixas."

    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    monitorar_playlist_especifica()
