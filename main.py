import requests
import base64

CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '7K33pCw9Dq9o9X6S8W1n4J'

def obter_token():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    res = requests.post("https://accounts.spotify.com/api/token", 
                        headers={"Authorization": f"Basic {auth_str}"},
                        data={"grant_type": "client_credentials"})
    return res.json().get('access_token')

def execucao_final():
    token = obter_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Chamada direta ao endpoint de PLAYLIST (não de TRACKS)
    # Isso evita o erro de permissão de usuário
    url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}"
    res = requests.get(url, headers=headers).json()
    
    # Pega o nome e o total real do cabeçalho da playlist
    nome = res.get('name', 'NOME NÃO ENCONTRADO')
    total = res.get('tracks', {}).get('total', 0)
    
    # Verifica as primeiras 100 músicas para ver se algo está bloqueado
    tracks_list = res.get('tracks', {}).get('items', [])
    bloqueadas = []
    
    for item in tracks_list:
        t = item.get('track')
        if t and t.get('is_playable') is False:
            bloqueadas.append(f"{t['artists'][0]['name']} - {t['name']}")

    msg = f"📌 PLAYLIST: {nome}\n"
    msg += f"🔢 TOTAL REAL: {total}\n"
    msg += f"🚫 BLOQUEADAS (Top 100): {len(bloqueadas)}"
    
    if bloqueadas:
        msg += "\n\nExemplos:\n" + "\n".join(bloqueadas[:5])

    # Envia para o seu celular
    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    execucao_final()
