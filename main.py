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
    
    # 1. A SUA chamada original (intocada e funcionando)
    url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?market=BR"
    res = requests.get(url, headers=headers).json()
    
    nome = res.get('name', 'Erro: Playlist não localizada')
    tracks_obj = res.get('tracks', {})
    total = tracks_obj.get('total', 0)
    
    bloqueadas = []
    
    # Pega os primeiros 100 itens da chamada inicial
    items = tracks_obj.get('items', [])
    
    # O Spotify entrega a URL pronta da "próxima página"
    url_proxima = tracks_obj.get('next') 
    
    # 2. Loop seguro: processa a página atual e busca a próxima se existir
    while True:
        # Analisa as músicas da página que estamos lendo
        for item in items:
            t = item.get('track')
            if t and t.get('is_playable') is False:
                bloqueadas.append(f"🚫 {t['artists'][0]['name']} - {t['name']}")
        
        # Se a url_proxima for nula, significa que chegamos na última música
        if not url_proxima:
            break
            
        # Se tiver mais página, faz a requisição usando o link seguro do Spotify
        res_prox = requests.get(url_proxima, headers=headers).json()
        items = res_prox.get('items', [])
        url_proxima = res_prox.get('next') # Atualiza o link para a próxima volta

    # 3. O SEU relatório para o ntfy (intocado)
    status = "⚠️ MÚSICAS BLOQUEADAS" if bloqueadas else "✅ TUDO OK"
    msg = f"🤘 {status}\n\nPlaylist: {nome}\nTotal lido: {total}\nIndisponíveis no Brasil: {len(bloqueadas)}"
    
    if bloqueadas:
        # Aumentei para mostrar as 15 primeiras, já que a lista é grande
        msg += "\n\nPrimeiras da lista:\n" + "\n".join(bloqueadas[:15])
    elif total > 0:
        msg += "\n\nSua coleção de Metal está integral no catálogo BR!"

    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    execucao_definitiva()
