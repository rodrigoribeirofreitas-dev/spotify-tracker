import requests
import base64

# Suas credenciais
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'

# O seu crachá de acesso vitalício
REFRESH_TOKEN = 'AQC6kS3QmyiHl4HfKZgiumNDgnzyEwWIETf_4e8iUJOQIPlFn25UJuI0rN5lsCzh7wZo5i7GcsTLoxlzo_k-z2gyV9TA_89spMn4mXiFm7HygWlyg_k_LqNTrFDWKA1ISVI'

def obter_token_usuario():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    # URL oficial e explícita do Spotify para tokens
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
    
    # 1. TRAVA: Se falhar a identidade, apita no celular
    if not token:
        requests.post("https://ntfy.sh/spotify_tracker", data=f"🚨 ERRO AO GERAR TOKEN:\n{erro_token}".encode('utf-8'))
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. URL oficial e explícita da API do Spotify
    url = f"
