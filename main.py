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
    
    # 1. Busca o TOTAL real primeiro de forma isolada
    url_meta = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?fields=total"
    res_meta = requests.get(url_meta, headers=headers).json()
    total_esperado = res_meta.get('total', 0)

    indisponiveis = []
    total_lido = 0
    offset = 0
    limit = 100

    # 2. Varre a playlist inteira
    while total_lido < total_esperado:
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?offset={offset}&limit={limit}&market=BR"
        res = requests.get(url, headers=headers).json()
        items = res.get('items', [])
        
        if not items:
            break

        for item in items:
            track = item.get('track')
            if not track: continue
            total_lido += 1
            if track.get('is_playable') is False:
                indisponiveis.append(f"🚫 {track['artists'][0]['name']} - {track['name']}")
        
        offset += limit

    # 3. Relatório para o ntfy
    status = "⚠️ MÚSICAS BLOQUEADAS" if indisponiveis else "✅ TUDO OK"
    msg = f"🤘 {status}\n\nPlaylist: Unavailable albums\nTotal Lido: {total_lido}/{total_esperado}\nIndisponíveis no Brasil: {len(indisponiveis)}"
    
    if indisponiveis:
        msg += "\n\nExemplos fora do catálogo:\n" + "\n".join(indisponiveis[:15])

    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    varredura_total()
