import requests
import base64

# Suas credenciais
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
REFRESH_TOKEN = 'AQC3aYLD47sUBKvJKmpU_RSnKVROxkcmvUyqmkxKyueiU7h96G1hfXNneEHEYcSGH5YE7G8a79P-eczN14-YGsHsMu2UiK-kTtOrvBbb3VFIRg3rLICSG9-2H-wiK_pMVWA'

def obter_token_usuario():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    # URL oficial e explícita
    url = "https://accounts.spotify.com/api/token"
    headers = {"Authorization": f"Basic {auth_str}"}
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }
    res = requests.post(url, headers=headers, data=data)
    
    if res.status_code != 200:
        return None, res.text
    return res.json().get('access_token'), None

def execucao_definitiva():
    token, erro_token = obter_token_usuario()
    
    # 1. TRAVA ANTI-MENTIRA DO TOKEN
    if not token:
        requests.post("https://ntfy.sh/spotify_tracker", data=f"🚨 ERRO AO GERAR TOKEN:\n{erro_token}".encode('utf-8'))
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # URL oficial e explícita da Playlist
    url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?market=BR"
    res = requests.get(url, headers=headers)
    
    # 2. TRAVA ANTI-MENTIRA DA API
    if res.status_code != 200:
        requests.post("https://ntfy.sh/spotify_tracker", data=f"🚨 ERRO DA API SPOTIFY:\nStatus: {res.status_code}\n{res.text}".encode('utf-8'))
        return
        
    dados = res.json()
    
    # Agora pega os dados reais. Se não achar, o erro foi pego na trava acima.
    nome = dados.get('name')
    tracks_obj = dados.get('tracks', {})
    total = tracks_obj.get('total', 0)
    
    bloqueadas = []
    
    # Lê a primeira página
    items = tracks_obj.get('items', [])
    for item in items:
        t = item.get('track')
        if t and t.get('is_playable') is False:
            bloqueadas.append(f"🚫 {t['artists'][0]['name']} - {t['name']}")

    # Lê as próximas páginas usando a URL oficial do Spotify
    next_url = tracks_obj.get('next')
    while next_url:
        res_prox = requests.get(next_url, headers=headers)
        
        # 3. TRAVA ANTI-MENTIRA DA PAGINAÇÃO
        if res_prox.status_code != 200:
            requests.post("https://ntfy.sh/spotify_tracker", data=f"🚨 ERRO NA LEITURA DA LISTA:\n{res_prox.text}".encode('utf-8'))
            return
            
        dados_prox = res_prox.json()
        for item in dados_prox.get('items', []):
            t = item.get('track')
            if t and t.get('is_playable') is False:
                bloqueadas.append(f"🚫 {t['artists'][0]['name']} - {t['name']}")
        next_url = dados_prox.get('next')

    # Relatório final
    status = "⚠️ MÚSICAS BLOQUEADAS" if bloqueadas else "✅ TUDO OK"
    msg = f"🤘 {status}\n\nPlaylist: {nome}\nTotal lido: {total}\nIndisponíveis no Brasil: {len(bloqueadas)}"
    
    if bloqueadas:
        msg += "\n\nPrimeiras da lista:\n" + "\n".join(bloqueadas[:15])

    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    execucao_definitiva()
