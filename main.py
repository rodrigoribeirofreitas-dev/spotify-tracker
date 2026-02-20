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
    url = "https://" + "accounts.spotify.com" + "/api/token"
    res = requests.post(url, headers={"Authorization": f"Basic {auth_str}"}, data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN})
    return res.json().get('access_token')

def prova_real():
    token = obter_token_usuario()
    headers = {"Authorization": f"Bearer {token}"}
    host_api = "api.spotify.com"
    
    # Teste 1: A verdade global (sem filtrar por país)
    url_global = f"https://{host_api}/v1/playlists/{PLAYLIST_ID}/tracks?fields=total"
    res_global = requests.get(url_global, headers=headers).json()
    total_global = res_global.get('total', 0)
    
    # Teste 2: A mentira local (filtrando pelo Brasil)
    url_br = f"https://{host_api}/v1/playlists/{PLAYLIST_ID}/tracks?market=BR&fields=total"
    res_br = requests.get(url_br, headers=headers).json()
    total_br = res_br.get('total', 0)

    if total_global > 0 and total_br == 0:
        msg = f"🤯 VOCÊ ESTAVA CERTO E EU FUI BURRO!\n\nSem o filtro BR: {total_global} faixas no servidor.\nCom o filtro BR: {total_br} faixas.\n\nO Spotify não avisa que estão bloqueadas, ele literalmente DELETA as faixas da resposta se você perguntar sobre o mercado brasileiro!"
    elif total_global > 0 and total_br > 0:
        msg = f"📊 STATUS:\nTotal Global: {total_global}\nTotal BR: {total_br}"
    else:
        msg = f"💀 ERRO DESCONHECIDO: O servidor global devolveu {total_global} faixas. O buraco é mais embaixo."

    enviar_ntfy(msg)

if __name__ == "__main__":
    prova_real()
