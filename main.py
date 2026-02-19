import requests
import base64

# Suas credenciais validadas
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'

def obter_token():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    res = requests.post("https://accounts.spotify.com/api/token", 
                        headers={"Authorization": f"Basic {auth_str}"},
                        data={"grant_type": "client_credentials"})
    return res.json().get('access_token')

def varredura_completa():
    token = obter_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    indisponiveis = []
    total_lido = 0
    offset = 0
    limit = 100
    
    # Loop para ler todas as 1.697 músicas (em blocos de 100)
    while True:
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?offset={offset}&limit={limit}&market=BR"
        res = requests.get(url, headers=headers).json()
        
        items = res.get('items', [])
        if not items:
            break
            
        for item in items:
            track = item.get('track')
            if not track: continue
            
            total_lido += 1
            # Verifica se a música está bloqueada no Brasil
            if track.get('is_playable') is False:
                indisponiveis.append(f"🚫 {track['artists'][0]['name']} - {track['name']}")
        
        offset += limit
        if len(items) < limit:
            break

    # Montagem do relatório final para o ntfy
    status = "⚠️ MÚSICAS BLOQUEADAS" if indisponiveis else "✅ TUDO OK"
    msg = f"🤘 {status}\n\n"
    msg += f"Total lido na Playlist: {total_lido}\n"
    msg += f"Indisponíveis no Brasil: {len(indisponiveis)}\n\n"
    
    if indisponiveis:
        msg += "Últimas detectadas:\n" + "\n".join(indisponiveis[-15:]) # Mostra as 15 últimas encontradas

    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    varredura_completa()
