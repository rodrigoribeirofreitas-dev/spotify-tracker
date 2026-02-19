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

def raio_x_servidor():
    token = obter_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # A mesma URL que funcionou antes
    url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?market=BR"
    res = requests.get(url, headers=headers)
    
    # Pega os primeiros 800 caracteres da resposta bruta do servidor
    resposta_crua = res.text[:800] 
    
    msg = f"🔍 RAIO-X DO SERVIDOR\nStatus: {res.status_code}\n\n{resposta_crua}"
    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    raio_x_servidor()
