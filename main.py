import requests

# Apenas o ID da sua playlist importa agora. Adeus credenciais de desenvolvedor!
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'

def enviar_ntfy(mensagem):
    requests.post("https://ntfy.sh/spotify_tracker", data=mensagem.encode('utf-8'))

def sequestrar_token_web():
    # 1. Colocamos uma "máscara" no script para ele parecer um navegador Chrome real no Windows
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }
    
    # 2. Batemos no endpoint secreto que o Spotify usa para dar acesso ao próprio site
    url = "https://open.spotify.com/get_access_token?reason=transport&productType=web_player"
    res = requests.get(url, headers=headers)
    
    if res.status_code != 200:
        raise Exception(f"Falha ao sequestrar token interno (Status {res.status_code})")
        
    # Roubamos a chave do próprio Spotify
    return res.json().get("accessToken")

def invasao_web_scraping():
    try:
        token = sequestrar_token_web()
    except Exception as e:
        enviar_ntfy(f"🚨 ERRO NO SEQUESTRO DE TOKEN:\n{str(e)[:200]}")
        return

    # 3. Agora usamos o token roubado para bater na API com permissões totais
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }
    
    url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?market=BR&limit=100"
    res = requests.get(url, headers=headers)
    
    if res.status_code != 200:
        enviar_ntfy(f"🚨 O SPOTIFY BARROU A INVASÃO (Status {res.status_code}):\n{res.text[:200]}")
        return
        
    dados = res.json()
    disponiveis = []
    indisponiveis = []
    
    items = dados.get('items', [])
    
    while True:
        for item in items:
            t = item.get('track')
            if not t:
                continue
                
            nome_faixa = f"{t['artists'][0]['name']} - {t['name']}"
            
            if t.get('is_playable') is False:
                indisponiveis.append(nome_faixa)
            else:
                disponiveis.append(nome_faixa)
                
        next_url = dados.get('next')
        if not next_url:
            break
            
        res = requests.get(next_url, headers=headers)
        if res.status_code != 200:
            enviar_ntfy(f"🚨 ERRO NA PAGINAÇÃO:\n{res.text[:200]}")
            return
            
        dados = res.json()
        items = dados.get('items', [])

    total = len(disponiveis) + len(indisponiveis)
    
    msg = f"🏴‍☠️ INVASÃO CONCLUÍDA\n\n"
    msg += f"Playlist varrida usando token interno.\n"
    msg += f"Total real encontrado: {total}\n"
    msg += f"✅ Livres no BR: {len(disponiveis)}\n"
    msg += f"🚫 Bloqueadas no BR: {len(indisponiveis)}\n"
    
    enviar_ntfy(msg)

if __name__ == "__main__":
    try:
        invasao_web_scraping()
    except Exception as e:
        enviar_ntfy(f"🚨 ERRO FATAL NO SCRIPT:\n{str(e)[:200]}")
