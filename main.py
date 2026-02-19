import requests
import base64

# Suas credenciais que já funcionam
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'

# O ID REAL de 21 caracteres
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'

def obter_token():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    res = requests.post("https://accounts.spotify.com/api/token", 
                        headers={"Authorization": f"Basic {auth_str}"},
                        data={"grant_type": "client_credentials"})
    return res.json().get('access_token')

def execucao_definitiva():
    token = obter_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. A SUA chamada original (A ÚNICA que traz o total sem bugar)
    url_base = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?market=BR"
    res = requests.get(url_base, headers=headers)
    
    # TRAVA DE SEGURANÇA: Se o Spotify barrar, te avisa o motivo real em vez de mostrar "0"
    if res.status_code != 200:
        requests.post("https://ntfy.sh/spotify_tracker", data=f"🚨 ERRO DA API: {res.text}".encode('utf-8'))
        return
        
    dados = res.json()
    nome = dados.get('name', 'Erro: Playlist não localizada')
    total = dados.get('tracks', {}).get('total', 0)
    
    bloqueadas = []
    
    # Processa as primeiras 100 músicas da sua chamada que funciona
    tracks_items = dados.get('tracks', {}).get('items', [])
    for item in tracks_items:
        t = item.get('track')
        if t and t.get('is_playable') is False:
            bloqueadas.append(f"🚫 {t['artists'][0]['name']} - {t['name']}")

    # 2. Busca o resto das faixas usando APENAS o endereço que funciona
    offset = 100
    while offset < total:
        url_tracks = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?market=BR&offset={offset}&limit=100"
        res_tracks = requests.get(url_tracks, headers=headers)
        
        if res_tracks.status_code == 200:
            items_extra = res_tracks.json().get('items', [])
            for item in items_extra:
                t = item.get('track')
                if t and t.get('is_playable') is False:
                    bloqueadas.append(f"🚫 {t['artists'][0]['name']} - {t['name']}")
        
        offset += 100

    # 3. O seu relatório para o ntfy
    status = "⚠️ MÚSICAS BLOQUEADAS" if bloqueadas else "✅ TUDO OK"
    msg = f"🤘 {status}\n\nPlaylist: {nome}\nTotal lido: {total}\nIndisponíveis no Brasil: {len(bloqueadas)}"
    
    if bloqueadas:
        msg += "\n\nPrimeiras da lista:\n" + "\n".join(bloqueadas[:15])
    elif total > 0:
        msg += "\n\nSua coleção está integral no catálogo BR!"

    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    execucao_definitiva()
