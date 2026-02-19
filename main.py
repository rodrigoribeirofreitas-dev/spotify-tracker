import requests
import base64

CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'

def obter_token():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    res = requests.post("https://accounts.spotify.com/api/token", 
                        headers={"Authorization": f"Basic {auth_str}"},
                        data={"grant_type": "client_credentials"})
    return res.json().get('access_token')

def varredura_total():
    token = obter_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    indisponiveis = []
    total_acumulado = 0
    offset = 0
    limit = 100
    
    while True:
        # URL específica para buscar os itens (tracks) da playlist
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?offset={offset}&limit={limit}&market=BR"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            break
            
        dados = response.json()
        items = dados.get('items', [])
        
        if not items:
            break
            
        for item in items:
            track = item.get('track')
            if not track: continue
            
            total_acumulado += 1
            # Se is_playable for False, a música sumiu do catálogo BR
            if track.get('is_playable') is False:
                indisponiveis.append(f"🚫 {track['artists'][0]['name']} - {track['name']}")
        
        offset += limit
        # Se trouxe menos de 100, significa que chegamos na última página
        if len(items) < limit:
            break

    # Relatório Final para o seu celular
    status = "⚠️ MÚSICAS BLOQUEADAS" if indisponiveis else "✅ TUDO OK"
    msg = f"📊 {status}\n\nTotal lido na Playlist: {total_acumulado}\nIndisponíveis no Brasil: {len(indisponiveis)}\n\n"
    
    if indisponiveis:
        msg += "Algumas das faixas fora:\n" + "\n".join(indisponiveis[:15])

    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    varredura_total()
