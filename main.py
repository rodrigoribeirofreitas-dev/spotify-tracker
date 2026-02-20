import requests
import base64

# Credenciais
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
REFRESH_TOKEN = 'AQC6kS3QmyiHl4HfKZgiumNDgnzyEwWIETf_4e8iUJOQIPlFn25UJuI0rN5lsCzh7wZo5i7GcsTLoxlzo_k-z2gyV9TA_89spMn4mXiFm7HygWlyg_k_LqNTrFDWKA1ISVI'

def enviar_ntfy(mensagem):
    requests.post("https://ntfy.sh/spotify_tracker", data=mensagem.encode('utf-8'))

def obter_token():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    # Construção blindada da URL para o servidor do GitHub não se perder
    host_auth = "accounts" + "." + "spotify" + "." + "com"
    url = f"https://{host_auth}/api/token"
    
    headers = {"Authorization": f"Basic {auth_str}"}
    data = {"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN}
    res = requests.post(url, headers=headers, data=data)
    
    if res.status_code != 200:
        # Se der pau no token, o script para aqui e avisa
        raise Exception(f"Erro no Token (Status {res.status_code}): {res.text}")
    return res.json()['access_token']

def rastrear_playlist():
    try:
        token = obter_token()
    except Exception as e:
        enviar_ntfy(f"🚨 ERRO DE ACESSO:\n{str(e)[:200]}")
        return

    host_api = "api" + "." + "spotify" + "." + "com"
    # Batendo direto no cofre de faixas, limitando a 100 por página
    url = f"https://{host_api}/v1/playlists/{PLAYLIST_ID}/tracks?market=BR&limit=100"
    headers = {"Authorization": f"Bearer {token}"}
    
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        enviar_ntfy(f"🚨 ERRO DA API (Status {res.status_code}):\n{res.text[:200]}")
        return
        
    dados = res.json()
    
    disponiveis = []
    indisponiveis = []
    
    items = dados.get('items', [])
    
    # Loop de paginação para ler até a última música
    while True:
        for item in items:
            t = item.get('track')
            if not t:
                continue
                
            nome_faixa = f"{t['artists'][0]['name']} - {t['name']}"
            
            # Conta se toca ou não toca no Brasil
            if t.get('is_playable') is False:
                indisponiveis.append(nome_faixa)
            else:
                disponiveis.append(nome_faixa)
                
        next_url = dados.get('next')
        if not next_url:
            break
            
        res = requests.get(next_url, headers=headers)
        if res.status_code != 200:
            enviar_ntfy(f"🚨 ERRO NA PAGINAÇÃO (Status {res.status_code}):\n{res.text[:200]}")
            return
        dados = res.json()
        items = dados.get('items', [])

    total = len(disponiveis) + len(indisponiveis)
    
    # Relatório exato com as faixas que a API realmente conseguiu ler
    msg = f"🤘 RELATÓRIO DA PLAYLIST\n\n"
    msg += f"Total lido pela API: {total}\n"
    msg += f"✅ Tocam no BR: {len(disponiveis)}\n"
    msg += f"🚫 Bloqueadas no BR: {len(indisponiveis)}\n\n"
    
    # Lista algumas disponíveis para você ter certeza de que o script leu certo
    if disponiveis:
        msg += "Últimas faixas tocáveis lidas:\n"
        for f in disponiveis[-3:]:
            msg += f"🎵 {f}\n"

    enviar_ntfy(msg)

if __name__ == "__main__":
    try:
        rastrear_playlist()
    except Exception as e:
        enviar_ntfy(f"🚨 ERRO FATAL NO SCRIPT:\n{str(e)[:200]}")
