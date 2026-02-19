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
    
    # 1. Primeiro, pega o nome e confirma o total oficial
    url_pl = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?fields=name,tracks.total"
    res_pl = requests.get(url_pl, headers=headers).json()
    nome_pl = res_pl.get('name', 'Playlist não encontrada')
    total_esperado = res_pl.get('tracks', {}).get('total', 0)

    indisponiveis = []
    total_processado = 0
    offset = 0
    limit = 100

    # 2. Loop para ler TODAS as faixas (100 por vez)
    while offset < total_esperado:
        url_tracks = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?offset={offset}&limit={limit}&market=BR"
        res_tracks = requests.get(url_tracks, headers=headers).json()
        items = res_tracks.get('items', [])
        
        if not items:
            break

        for item in items:
            track = item.get('track')
            if not track: continue
            
            total_processado += 1
            # Se is_playable for False, ela sumiu do catálogo brasileiro
            if track.get('is_playable') is False:
                indisponiveis.append(f"🚫 {track['artists'][0]['name']} - {track['name']}")
        
        offset += limit

    # Relatório Final
    status = "⚠️ MÚSICAS BLOQUEADAS" if indisponiveis else "✅ TUDO OK"
    msg = f"🤘 {status}\n\nPlaylist: {nome_pl}\nTotal Lido: {total_processado}/{total_esperado}\nIndisponíveis no Brasil: {len(indisponiveis)}"
    
    if indisponiveis:
        msg += "\n\nExemplos sumidos:\n" + "\n".join(indisponiveis[:15])

    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    varredura_total()
