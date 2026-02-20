import requests
import base64

# Suas credenciais e dados
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
REFRESH_TOKEN = 'AQC6kS3QmyiHl4HfKZgiumNDgnzyEwWIETf_4e8iUJOQIPlFn25UJuI0rN5lsCzh7wZo5i7GcsTLoxlzo_k-z2gyV9TA_89spMn4mXiFm7HygWlyg_k_LqNTrFDWKA1ISVI'

def enviar_ntfy(mensagem):
    # Envia a mensagem com codificação segura
    requests.post("https://ntfy.sh/spotify_tracker", data=mensagem.encode('utf-8'))

def obter_token_usuario():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    
    # URL fragmentada para evitar bloqueios invisíveis de proxy
    url = "https://" + "accounts.spotify.com" + "/api/token"
    
    headers = {"Authorization": f"Basic {auth_str}"}
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }
    res = requests.post(url, headers=headers, data=data)
    
    if res.status_code != 200:
        return None, res.status_code
    return res.json().get('access_token'), None

def execucao_definitiva():
    token, erro_token = obter_token_usuario()
    
    if not token:
        enviar_ntfy(f"🚨 ERRO DE TOKEN: O Spotify barrou o acesso (Status {erro_token}).")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # URL oficial fragmentada para garantir a rota direta
    url = "https://" + "api.spotify.com" + f"/v1/playlists/{PLAYLIST_ID}?market=BR"
    
    res = requests.get(url, headers=headers)
    
    if res.status_code != 200:
        enviar_ntfy(f"🚨 ERRO DA API: A playlist falhou (Status {res.status_code}).")
        return
        
    dados = res.json()
    nome = dados.get('name', 'Unavailable albums')
    tracks_obj = dados.get('tracks', {})
    total = tracks_obj.get('total', 0)
    
    bloqueadas = []
    
    items = tracks_obj.get('items', [])
    for item in items:
        t = item.get('track')
        if t and t.get('is_playable') is False:
            bloqueadas.append(f"🚫 {t['artists'][0]['name']} - {t['name']}")

    next_url = tracks_obj.get('next')
    while next_url:
        res_prox = requests.get(next_url, headers=headers)
        
        if res_prox.status_code != 200:
            enviar_ntfy(f"🚨 ERRO NA PAGINAÇÃO: Falha na página seguinte (Status {res_prox.status_code}).")
            return
            
        dados_prox = res_prox.json()
        for item in dados_prox.get('items', []):
            t = item.get('track')
            if t and t.get('is_playable') is False:
                bloqueadas.append(f"🚫 {t['artists'][0]['name']} - {t['name']}")
        next_url = dados_prox.get('next')

    status = "⚠️ MÚSICAS BLOQUEADAS" if bloqueadas else "✅ TUDO OK"
    msg = f"🤘 {status}\n\nPlaylist: {nome}\nTotal lido: {total
