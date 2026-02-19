import requests
import base64

# Suas credenciais
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'

def obter_token():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    res = requests.post("https://accounts.spotify.com/api/token", 
                        headers={"Authorization": f"Basic {auth_str}"},
                        data={"grant_type": "client_credentials"})
    return res.json().get('access_token')

def varredura_anti_cache():
    token = obter_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Busca apenas o nome e o total da playlist primeiro
    url_info = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?fields=name,tracks.total"
    res_info = requests.get(url_info, headers=headers).json()
    nome = res_info.get('name', 'Unavailable albums')
    total_esperado = res_info.get('tracks', {}).get('total', 0)

    # TRAVA: Se o cache do Spotify mentir que tem 0 músicas, o script ignora e força a leitura
    if total_esperado == 0:
        total_esperado = 1697 
        
    bloqueadas = []
    total_lido = 0
    offset = 0
    
    # O PULO DO GATO: Pede 99 músicas em vez de 100. Isso fura o cache preso do Spotify.
    limit = 99 

    while total_lido < total_esperado:
        # Bate direto na porta das faixas com o limit 99
        url_tracks = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?offset={offset}&limit={limit}&market=BR"
        res_tracks = requests.get(url_tracks, headers=headers)
        
        if res_tracks.status_code != 200:
            break
            
        items = res_tracks.json().get('items', [])
        
        # Se vier vazio, encerra o loop para não ficar rodando no infinito
        if not items:
            break 
            
        for item in items:
            t = item.get('track')
            if not t: continue
            
            total_lido += 1
            if t.get('is_playable') is False:
                bloqueadas.append(f"🚫 {t['artists'][0]['name']} - {t['name']}")
                
        offset += limit

    # Relatório final limpo
    status = "⚠️ MÚSICAS BLOQUEADAS" if bloqueadas else "✅ TUDO OK"
    msg = f"🤘 {status}\n\nPlaylist: {nome}\nTotal lido: {total_lido}\nIndisponíveis no Brasil: {len(bloqueadas)}"
    
    if bloqueadas:
        msg += "\n\nPrimeiras da lista:\n" + "\n".join(bloqueadas[:15])

    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    varredura_anti_cache()
