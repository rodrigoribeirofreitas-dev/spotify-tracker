import requests
import base64
import time

# Credenciais e Chave Mestra (Refresh Token) que funcionou às 15:43
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
REFRESH_TOKEN = 'AQCv5L8kX9mP3qZ7r2W1n4J6L8M0N2P4Q6R8S0T2U4V6W8X0Y2Z4a6b8c0d2e4f6g8h0i2j4k6l8m0n2p4q6r8s0t2u4v6w8x0y2z4A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6'

def obter_acesso():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    res = requests.post("https://accounts.spotify.com/api/token", 
                        headers={"Authorization": f"Basic {auth_str}"},
                        data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN})
    return res.json().get('access_token')

def verificar_disponibilidade():
    token = obter_acesso()
    headers = {"Authorization": f"Bearer {token}"}
    
    indisponiveis = []
    total_verificado = 0
    offset = 0
    limit = 50 # Processar em blocos menores para evitar erros

    try:
        while True:
            # Endpoint para buscar as faixas da sua biblioteca (Liked Songs)
            url = f"https://api.spotify.com/v1/me/tracks?limit={limit}&offset={offset}&market=BR"
            res = requests.get(url, headers=headers)
            
            if res.status_code != 200: break
            
            dados = res.json()
            items = dados.get('items', [])
            if not items: break

            for item in items:
                track = item['track']
                # Se a música não for tocável no Brasil, adicionamos à lista
                if not track.get('is_playable', True):
                    indisponiveis.append(f"🚫 {track['artists'][0]['name']} - {track['name']}")
                total_verificado += 1

            offset += limit
            if total_verificado >= 1699: break # Limite da sua biblioteca atual

        # Preparar mensagem final para o ntfy
        status = "✅ TUDO DISPONÍVEL" if not indisponiveis else "⚠️ FAIXAS REMOVIDAS"
        corpo = "\n".join(indisponiveis) if indisponiveis else "Todas as 1.699 músicas estão OK no Brasil."
        
        msg = f"{status}\nTotal Verificado: {total_verificado}\nIndisponíveis: {len(indisponiveis)}\n\n{corpo}"
        
        requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))
        print("Relatório enviado com sucesso!")

    except Exception as e:
        requests.post("https://ntfy.sh/spotify_tracker", data=f"❌ ERRO NO PROCESSO: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    verificar_disponibilidade()
