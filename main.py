import requests
import base64

# Suas credenciais
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
# Use o Refresh Token que geramos anteriormente
REFRESH_TOKEN = 'AQCv5L8kX9mP3qZ7r2W1n4J6L8M0N2P4Q6R8S0T2U4V6W8X0Y2Z4a6b8c0d2e4f6g8h0i2j4k6l8m0n2p4q6r8s0t2u4v6w8x0y2z4A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6'

def obter_token():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    res = requests.post("https://accounts.spotify.com/api/token", 
                        headers={"Authorization": f"Basic {auth_str}"},
                        data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN})
    return res.json().get('access_token')

def rastreio_real():
    token = obter_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    indisponiveis = []
    total_real = 0
    offset = 0
    
    while True:
        # Buscando suas 'Músicas Curtidas' (Liked Songs)
        # O market=BR é obrigatório para o Spotify 'confessar' o que está bloqueado aqui
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
            
            # Verificação de disponibilidade real (is_playable)
            # Se for False, a música está cinza no seu app no Brasil
            if track.get('is_playable') is False:
                indisponiveis.append(f"🚫 {track['artists'][0]['name']} - {track['name']}")
        
        offset += 50
        if len(items) < 50:
            break

    # Construção da mensagem com dados 100% capturados agora
    if total_real == 0:
        msg = "❌ ERRO: Não foi possível ler sua biblioteca. Verifique as permissões do Token."
    else:
        status = "⚠️ FAIXAS INDISPONÍVEIS" if indisponiveis else "✅ BIBLIOTECA OK"
        resumo = f"Total Real detectado: {total_real}\nBloqueadas no Brasil: {len(indisponiveis)}"
        lista = "\n".join(indisponiveis[:20]) if indisponiveis else "Nenhuma restrição encontrada."
        
        msg = f"{status}\n{resumo}\n\n{lista}"

    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    rastreio_real()
