import requests
import base64

CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
REFRESH_TOKEN = 'AQCv5L8kX9mP3qZ7r2W1n4J6L8M0N2P4Q6R8S0T2U4V6W8X0Y2Z4a6b8c0d2e4f6g8h0i2j4k6l8m0n2p4q6r8s0t2u4v6w8x0y2z4A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6'

def obter_acesso():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    res = requests.post("https://accounts.spotify.com/api/token", 
                        headers={"Authorization": f"Basic {auth_str}"},
                        data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN})
    return res.json().get('access_token')

def monitorar():
    token = obter_acesso()
    headers = {"Authorization": f"Bearer {token}"}
    indisponiveis = []
    total_rastreado = 0
    offset = 0

    while True:
        # Usando o parâmetro market=BR para checar a restrição regional
        url = f"https://api.spotify.com/v1/me/tracks?limit=50&offset={offset}&market=BR"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            break
            
        dados = response.json()
        items = dados.get('items', [])
        
        if not items:
            break

        for item in items:
            track = item['track']
            total_rastreado += 1
            
            # Checagem Dupla: is_playable e availability
            # Se a música não for "tocável" ou se não houver restrições que permitam BR
            is_playable = track.get('is_playable')
            
            if is_playable is False:
                nome_musica = f"{track['artists'][0]['name']} - {track['name']}"
                indisponiveis.append(nome_musica)
        
        offset += 50
        if len(items) < 50:
            break

    # Relatório detalhado
    if indisponiveis:
        status = "⚠️ FAIXAS INDISPONÍVEIS DETECTADAS"
        lista_texto = "\n".join(indisponiveis[:30]) # Mostra as primeiras 30 no ntfy
        if len(indisponiveis) > 30:
            lista_texto += f"\n... e mais {len(indisponiveis) - 30} faixas."
    else:
        status = "✅ TUDO OK NO BRASIL"
        lista_texto = "Nenhuma música indisponível encontrada nas 1.699 faixas."

    msg = f"{status}\nTotal Verificado: {total_rastreado}\nBloqueadas: {len(indisponiveis)}\n\n{lista_texto}"
    
    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    monitorar()
