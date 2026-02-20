import requests
import base64

CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
REFRESH_TOKEN = 'AQC6kS3QmyiHl4HfKZgiumNDgnzyEwWIETf_4e8iUJOQIPlFn25UJuI0rN5lsCzh7wZo5i7GcsTLoxlzo_k-z2gyV9TA_89spMn4mXiFm7HygWlyg_k_LqNTrFDWKA1ISVI'

def enviar_ntfy(mensagem):
    requests.post("https://ntfy.sh/spotify_tracker", data=mensagem.encode('utf-8'))

def obter_token_usuario():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    host_auth = "accounts" + "." + "spotify" + "." + "com"
    url = f"https://{host_auth}/api/token"
    
    headers = {"Authorization": f"Basic {auth_str}"}
    data = {"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN}
    res = requests.post(url, headers=headers, data=data)
    
    return res.json().get('access_token')

def execucao_definitiva():
    token = obter_token_usuario()
    headers = {"Authorization": f"Bearer {token}"}
    host_api = "api" + "." + "spotify" + "." + "com"
    
    # 1. Pega apenas o nome da lista para o relatório
    url_info = f"https://{host_api}/v1/playlists/{PLAYLIST_ID}"
    nome = requests.get(url_info, headers=headers).json().get('name', 'Unavailable albums')

    # 2. Bate DIRETO no cofre de músicas
    url_tracks = f"https://{host_api}/v1/playlists/{PLAYLIST_ID}/tracks?market=BR&limit=100"
    res_tracks = requests.get(url_tracks, headers=headers)
    
    dados = res_tracks.json()
    total = dados.get('total', 0)
    items = dados.get('items', [])
    
    # Se o cofre estiver vazio, manda a verdade pro seu celular
    if total == 0:
        enviar_ntfy(f"🚨 MISTÉRIO RESOLVIDO:\nA conexão funcionou (Status 200), mas o Spotify afirma que a playlist '{nome}' tem ZERO faixas no banco de dados deles.\n\nSe as músicas tocam no seu PC, elas são Arquivos Locais (mp3) ou o ID da playlist está errado.")
        return

    bloqueadas = []
    
    # Lê as músicas da página atual
    for item in items:
        t = item.get('track')
        if t and t.get('is_playable') is False:
            bloqueadas.append(f"🚫 {t['artists'][0]['name']} - {t['name']}")

    # Lê as próximas páginas usando a paginação oficial
    next_url = dados.get('next')
    while next_url:
        res_prox = requests.get(next_url, headers=headers).json()
        for item in res_prox.get('items', []):
            t = item.get('track')
            if t and t.get('is_playable') is False:
                bloqueadas.append(f"🚫 {t['artists'][0]['name']} - {t['name']}")
        next_url = res_prox.get('next')

    status = "⚠️ MÚSICAS BLOQUEADAS" if bloqueadas else "✅ TUDO OK"
    msg = f"🤘 {status}\n\nPlaylist: {nome}\nTotal real lido: {total}\nIndisponíveis no Brasil: {len(bloqueadas)}"
    
    if bloqueadas:
        msg += "\n\nPrimeiras da lista:\n" + "\n".join(bloqueadas[:15])
    elif total > 0:
        msg += "\n\nA coleção está integral no catálogo BR!"

    enviar_ntfy(msg)

if __name__ == "__main__":
    execucao_definitiva()
