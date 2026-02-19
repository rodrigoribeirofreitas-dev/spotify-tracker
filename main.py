import requests
import base64

# Suas credenciais que já funcionam
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'

# O ID REAL de 21 caracteres que você enviou agora
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
    
    # Buscando a playlist correta
    url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?market=BR"
    res = requests.get(url, headers=headers).json()
    
    nome = res.get('name', 'Erro: Playlist não localizada')
    total = res.get('tracks', {}).get('total', 0)
    
    # Analisando faixas indisponíveis
    tracks_items = res.get('tracks', {}).get('items', [])
    bloqueadas = []
    
    for item in tracks_items:
        t = item.get('track')
        if t and t.get('is_playable') is False:
            bloqueadas.append(f"🚫 {t['artists'][0]['name']} - {t['name']}")

    # Relatório para o ntfy
    status = "⚠️ MÚSICAS BLOQUEADAS" if bloqueadas else "✅ TUDO OK"
    msg = f"🤘 {status}\n\nPlaylist: {nome}\nTotal lido: {total}\nIndisponíveis no Brasil: {len(bloqueadas)}"
    
    if bloqueadas:
        msg += "\n\nPrimeiras da lista:\n" + "\n".join(bloqueadas[:100])
    elif total > 0:
        msg += "\n\nSua coleção de Metal está integral no catálogo BR!"

    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    execucao_definitiva()
