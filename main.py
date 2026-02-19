import requests
import base64

# Suas credenciais
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'

def obter_token():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    # URL OFICIAL DO SPOTIFY (Sem proxy)
    res = requests.post("https://accounts.spotify.com/api/token", 
                        headers={"Authorization": f"Basic {auth_str}"},
                        data={"grant_type": "client_credentials"})
    return res.json().get('access_token')

def execucao_definitiva():
    token = obter_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # URL OFICIAL DO SPOTIFY
    url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?market=BR"
    res = requests.get(url, headers=headers).json()
    
    nome = res.get('name', 'Erro: Playlist não localizada')
    total = res.get('tracks', {}).get('total', 0)
    
    bloqueadas = []
    
    # Processa a primeira página
    tracks_obj = res.get('tracks', {})
    items = tracks_obj.get('items', [])
    
    for item in items:
        t = item.get('track')
        if t and t.get('is_playable') is False:
            bloqueadas.append(f"🚫 {t['artists'][0]['name']} - {t['name']}")

    # Loop com a paginação oficial do Spotify
    next_url = tracks_obj.get('next')
    while next_url:
        res_prox = requests.get(next_url, headers=headers).json()
        for item in res_prox.get('items', []):
            t = item.get('track')
            if t and t.get('is_playable') is False:
                bloqueadas.append(f"🚫 {t['artists'][0]['name']} - {t['name']}")
        next_url = res_prox.get('next')

    # Relatório
    status = "⚠️ MÚSICAS BLOQUEADAS" if bloqueadas else "✅ TUDO OK"
    msg = f"🤘 {status}\n\nPlaylist: {nome}\nTotal lido: {total}\nIndisponíveis no Brasil: {len(bloqueadas)}"
    
    if bloqueadas:
        msg += "\n\nPrimeiras da lista:\n" + "\n".join(bloqueadas[:15])
    elif total > 0:
        msg += "\n\nSua coleção está integral no catálogo BR!"

    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    execucao_definitiva()
