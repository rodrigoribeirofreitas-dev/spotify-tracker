import requests
import base64

# Suas credenciais
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'

# O seu crachá de acesso vitalício
REFRESH_TOKEN = 'AQC-8YJoC-PCJmVyVbRZKL2AvB-3OI8jfQPPrQTeiUSH_iDL06VMh2UaQyeHx5VGvyOwMoYijt6Ck-YsIZFvp-_eINm2L2veWxMSV-_wjRdzFHRbJrnIoBeC0Gk3xDS79KHqeOKypG5bkOqiLjK99UABlDK51BhagLmMYjpELvoYUsIeOQ6WEbn9CqBubhVBCg'

def obter_token_usuario():
    # Troca o seu Refresh Token por uma chave de acesso nova (Access Token)
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    url = "https://accounts.spotify.com/api/token"
    headers = {"Authorization": f"Basic {auth_str}"}
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }
    res = requests.post(url, headers=headers, data=data)
    return res.json().get('access_token')

def execucao_definitiva():
    token = obter_token_usuario()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Bate na porta como o dono da playlist usando URLs oficiais
    url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?market=BR"
    res = requests.get(url, headers=headers).json()
    
    nome = res.get('name', 'Unavailable albums')
    tracks_obj = res.get('tracks', {})
    total = tracks_obj.get('total', 0)
    
    bloqueadas = []
    
    # Processa a primeira página
    items = tracks_obj.get('items', [])
    for item in items:
        t = item.get('track')
        if t and t.get('is_playable') is False:
            bloqueadas.append(f"🚫 {t['artists'][0]['name']} - {t['name']}")

    # Loop seguro para ler até a última música (Paginação oficial do Spotify)
    next_url = tracks_obj.get('next')
    while next_url:
        res_prox = requests.get(next_url, headers=headers).json()
        for item in res_prox.get('items', []):
            t = item.get('track')
            if t and t.get('is_playable') is False:
                bloqueadas.append(f"🚫 {t['artists'][0]['name']} - {t['name']}")
        next_url = res_prox.get('next')

    # Relatório final para o seu celular
    status = "⚠️ MÚSICAS BLOQUEADAS" if bloqueadas else "✅ TUDO OK"
    msg = f"🤘 {status}\n\nPlaylist: {nome}\nTotal lido: {total}\nIndisponíveis no Brasil: {len(bloqueadas)}"
    
    if bloqueadas:
        # Mostra as 15 primeiras indisponíveis
        msg += "\n\nPrimeiras da lista:\n" + "\n".join(bloqueadas[:15])
    elif total > 0:
        msg += "\n\nSua coleção de Metal está integral no catálogo BR!"

    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    execucao_definitiva()
