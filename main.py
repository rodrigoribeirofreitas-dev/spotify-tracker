import requests
import base64

# Suas credenciais validadas
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'

def obter_token():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    # Usando a URL oficial da API
    res = requests.post("https://accounts.spotify.com/api/token", 
                        headers={"Authorization": f"Basic {auth_str}"},
                        data={"grant_type": "client_credentials"})
    return res.json().get('access_token')

def execucao_definitiva():
    token = obter_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Usando a URL oficial da API
    url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?market=BR"
    res = requests.get(url, headers=headers)
    
    # 🚨 TRAVA DE SEGURANÇA: Se não for sucesso (200), manda o erro real para o celular
    if res.status_code != 200:
        requests.post("https://ntfy.sh/spotify_tracker", data=f"🚨 ERRO DO SPOTIFY:\nCódigo: {res.status_code}\nMotivo: {res.text}".encode('utf-8'))
        return
        
    dados = res.json()
    nome = dados.get('name', 'Erro: Playlist não localizada')
    total = dados.get('tracks', {}).get('total', 0)
    
    bloqueadas = []
    
    # Lendo a primeira página
    tracks_obj = dados.get('tracks', {})
    items = tracks_obj.get('items', [])
    for item in items:
        t = item.get('track')
        if t and t.get('is_playable') is False:
            bloqueadas.append(f"🚫 {t['artists'][0]['name']} - {t['name']}")

    # Lendo o resto da playlist usando a paginação oficial
    next_url = tracks_obj.get('next')
    while next_url:
        res_prox = requests.get(next_url, headers=headers)
        
        # Se a página seguinte der erro, avisa também
        if res_prox.status_code != 200:
            requests.post("https://ntfy.sh/spotify_tracker", data=f"🚨 ERRO NA PÁGINA SEGUINTE:\nCódigo: {res_prox.status_code}\nMotivo: {res_prox.text}".encode('utf-8'))
            return
            
        dados_prox = res_prox.json()
        for item in dados_prox.get('items', []):
            t = item.get('track')
            if t and t.get('is_playable') is False:
                bloqueadas.append(f"🚫 {t['artists'][0]['name']} - {t['name']}")
        next_url = dados_prox.get('next')

    # Relatório Final
    status = "⚠️ MÚSICAS BLOQUEADAS" if bloqueadas else "✅ TUDO OK"
    msg = f"🤘 {status}\n\nPlaylist: {nome}\nTotal lido: {total}\nIndisponíveis no Brasil: {len(bloqueadas)}"
    
    if bloqueadas:
        msg += "\n\nPrimeiras da lista:\n" + "\n".join(bloqueadas[:15])

    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    execucao_definitiva()
