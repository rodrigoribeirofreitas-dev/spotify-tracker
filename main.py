import requests
import base64

# Suas credenciais
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'

# COLE O NOVO CÓDIGO DA URL AQUI
CODIGO_NOVO = 'AQBWsd-5pn3D0fW8ajwk4kOBvujlf9E4P-bwEUd1cA1lr7CfOUqS04EjdpOlQL1WiWzcg8abIvZKi9u9S14gEq3h0DgSrd3KxDk96myJfLRqzGjCUBDIK4R4enx9cDyGgGtm7i2jYUfl5dxDPGc4xY2c0ayinbHIACZIfCmfAzvr5DnDwSHe1Eo7Wm-W5FDD0mKXMPeA3vD_l1AezntWUzuA6lWmwL-4tx1Y1nwb'

def obter_chave_mestra():
    try:
        auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_str}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "authorization_code",
            "code": CODIGO_NOVO,
            "redirect_uri": "https://www.google.com"
        }
        
        res = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
        token = res.json().get('refresh_token')
        
        if token:
            msg = f"✅ AGORA SIM! SUA CHAVE MESTRA:\n\n{token}"
        else:
            msg = f"❌ O SPOTIFY DISSE: {res.json().get('error_description', res.json())}"
            
        requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))
    except Exception as e:
        requests.post("https://ntfy.sh/spotify_tracker", data=f"❌ ERRO: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    obter_chave_mestra()
