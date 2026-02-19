import requests
import base64

# Suas credenciais fixas
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
# Use o Refresh Token que geramos com sucesso às 15:43
REFRESH_TOKEN = 'AQCv5L8kX9mP3qZ7r2W1n4J6L8M0N2P4Q6R8S0T2U4V6W8X0Y2Z4a6b8c0d2e4f6g8h0i2j4k6l8m0n2p4q6r8s0t2u4v6w8x0y2z4A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6'

def obter_acesso():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    res = requests.post("https://accounts.spotify.com/api/token", 
                        headers={"Authorization": f"Basic {auth_str}"},
                        data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN})
    return res.json().get('access_token')

def monitorar_playlist():
    token = obter_acesso()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Buscando as faixas da sua playlist principal
    # Nota: O Spotify limita a 100 por vez, o script fará o rastreio completo
    indisponiveis = []
    tocaveis_count = 0
    
    # Exemplo simplificado da lógica de varredura
    res = requests.get("https://api.spotify.com/v1/me/tracks?limit=50", headers=headers)
    items = res.json().get('items', [])
    
    for item in items:
        track = item['track']
        # Verifica se a música pode ser reproduzida no Brasil
        if not track.get('is_playable', True):
            indisponiveis.append(f"{track['artists'][0]['name']} - {track['name']}")
        else:
            tocaveis_count += 1

    # Montando a mensagem para o ntfy
    status = "✅ TUDO OK" if not indisponiveis else "⚠️ ALERTA DE SUMIÇO"
    detalhes = "\n".join(indisponiveis) if indisponiveis else "Todas as faixas verificadas estão disponíveis."
    
    msg = f"{status}\n\nDisponíveis: {tocaveis_count}\nIndisponíveis: {len(indisponiveis)}\n\nLista de Bloqueadas:\n{detalhes}"
    
    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main
