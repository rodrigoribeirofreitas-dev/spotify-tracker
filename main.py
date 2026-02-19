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

def execucao_blindada():
    token = obter_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Pede o TOTAL real primeiro (isso nunca vem zerado se o ID estiver certo)
    res_meta = requests.get(f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?fields=total", headers=headers).json()
    total_esperado = res_meta.get('total', 0)

    indisponiveis = []
    total_lido = 0
    offset = 0

    # 2. O Loop de Varredura Completa (Garante que lê as 1697)
    while total_lido < total_esperado:
        # Forçamos o Spotify a entregar os ITENS de 100 em 100
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?offset={offset}&limit=100&market=BR"
        res = requests.get(url, headers=headers).json()
        items = res.get('items', [])
        
        if not items:
            break

        for item in items:
            t = item.get('track')
            if not t: continue
            total_lido += 1
            if t.get('is_playable') is False:
                indisponiveis.append(f"🚫 {t['artists'][0]['name']} - {t['name']}")
        
        offset += 100

    # 3. Envio para o ntfy
    status = "⚠️ MÚSICAS BLOQUEADAS" if indisponiveis else "✅ TUDO OK"
    msg = f"🤘 {status}\n\nPlaylist: Unavailable albums\nTotal Lido: {total_lido}/{total_esperado}\nBloqueadas no BR: {len(indisponiveis)}"
    
    if indisponiveis:
        msg += "\n\nExemplos sumidos:\n" + "\n".join(indisponiveis[:15])

    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    execucao_blindada()
