import requests
import base64

CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
# Esta chave mestre é a que funcionou às 15:43 e tem permissão de leitura
REFRESH_TOKEN = 'AQCv5L8kX9mP3qZ7r2W1n4J6L8M0N2P4Q6R8S0T2U4V6W8X0Y2Z4a6b8c0d2e4f6g8h0i2j4k6l8m0n2p4q6r8s0t2u4v6w8x0y2z4A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6'

def obter_token():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    res = requests.post("https://accounts.spotify.com/api/token", 
                        headers={"Authorization": f"Basic {auth_str}"},
                        data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN})
    return res.json().get('access_token')

def rastreio_dinamico():
    token = obter_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    indisponiveis = []
    total_real = 0
    offset = 0
    
    while True:
        # A URL agora busca as músicas curtidas (Liked Songs) de forma paginada
        url = f"https://api.spotify.com/v1/me/tracks?limit=50&offset={offset}&market=BR"
        res = requests.get(url, headers=headers)
        
        if res.status_code != 200:
            break
            
        dados = res.json()
        items = dados.get('items', [])
        
        if not items:
            break

        for item in items:
            track = item['track']
            total_real += 1
            
            # O ponto crucial: se is_playable for False, a música está indisponível no BR
            if track.get('is_playable') is False:
                indisponiveis.append(f"🚫 {track['artists'][0]['name']} - {track['name']}")
        
        offset += 50
        # Se o Spotify entregou menos de 50, chegamos ao fim da sua lista real
        if len(items) < 50:
            break

    # Montagem da mensagem baseada APENAS no que foi contado acima
    if total_real == 0:
        msg = "❌ ERRO: O script não conseguiu ler sua biblioteca. Verifique as permissões."
    else:
        status = "⚠️ MÚSICAS SUMIRAM" if indisponiveis else "✅ TUDO DISPONÍVEL"
        detalhes = "\n".join(indisponiveis[:25]) if indisponiveis else "Nenhuma música bloqueada encontrada."
        if len(indisponiveis) > 25:
            detalhes += f"\n... e mais {len(indisponiveis) - 25} faixas."
            
        msg = f"{status}\n\nTotal lido agora: {total_real}\nIndisponíveis: {len(indisponiveis)}\n\n{detalhes}"

    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    rastreio_dinamico()
