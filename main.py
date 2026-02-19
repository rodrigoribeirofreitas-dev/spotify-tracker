import requests
import base64

# Credenciais e Refresh Token definitivo
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
        # Busca músicas curtidas em blocos de 50
        url = f"https://api.spotify.com/v1/me/tracks?limit=50&offset={offset}&market=BR"
        res = requests.get(url, headers=headers).json()
        items = res.get('items', [])
        
        if not items: break

        for item in items:
            track = item['track']
            total_rastreado += 1
            if not track.get('is_playable', True):
                indisponiveis.append(f"🚫 {track['artists'][0]['name']} - {track['name']}")
        
        offset += 50
        if len(items) < 50: break

    # Envio do relatório corrigido
    status = "✅ TUDO OK" if not indisponiveis else "⚠️ FAIXAS REMOVIDAS"
    resumo = f"Total Verificado: {total_rastreado}\nIndisponíveis: {len(indisponiveis)}"
    corpo = "\n".join(indisponiveis) if indisponiveis else "Todas as músicas estão disponíveis no catálogo brasileiro."
    
    msg = f"{status}\n{resumo}\n\n{corpo}"
    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    monitorar()
