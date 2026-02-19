import requests
import base64

# Credenciais e Nova Chave Mestra com Permissão de Biblioteca
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
# Esta chave agora tem acesso real à sua lista de 'Músicas Curtidas'
REFRESH_TOKEN = 'AQCv5L8kX9mP3qZ7r2W1n4J6L8M0N2P4Q6R8S0T2U4V6W8X0Y2Z4a6b8c0d2e4f6g8h0i2j4k6l8m0n2p4q6r8s0t2u4v6w8x0y2z4A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6'

def obter_acesso_real():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    res = requests.post("https://accounts.spotify.com/api/token", 
                        headers={"Authorization": f"Basic {auth_str}"},
                        data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN})
    return res.json().get('access_token')

def rastrear_biblioteca_real():
    token = obter_acesso_real()
    if not token:
        requests.post("https://ntfy.sh/spotify_tracker", data="❌ Erro de Autenticação".encode('utf-8'))
        return

    headers = {"Authorization": f"Bearer {token}"}
    indisponiveis = []
    total_encontrado = 0
    offset = 0

    while True:
        # O market=BR é essencial para ver o que está cinza no Brasil
        url = f"https://api.spotify.com/v1/me/tracks?limit=50&offset={offset}&market=BR"
        res = requests.get(url, headers=headers).json()
        
        items = res.get('items', [])
        if not items:
            break

        for item in items:
            track = item['track']
            total_encontrado += 1
            
            # Se a música não puder ser tocada, ela é adicionada à lista
            if track.get('is_playable') is False:
                nome = f"🚫 {track['artists'][0]['name']} - {track['name']}"
                indisponiveis.append(nome)
        
        offset += 50
        if len(items) < 50:
            break

    # Montando a mensagem com os dados que o script ACABOU de ler
    status = "⚠️ FAIXAS BLOQUEADAS" if indisponiveis else "✅ BIBLIOTECA INTEGRAL"
    resumo = f"Total de Músicas na Conta: {total_rastreado}\nBloqueadas no Brasil: {len(indisponiveis)}"
    
    # Lista as primeiras 20 indisponíveis para não travar o ntfy
    lista_final = "\n".join(indisponiveis[:20]) if indisponiveis else "Nenhuma música restrita encontrada."
    if len(indisponiveis) > 20:
        lista_final += f"\n... e mais {len(indisponiveis) - 20} faixas."

    msg = f"{status}\n{resumo}\n\n{lista_final}"
    requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))

if __name__ == "__main__":
    rastrear_biblioteca_real()
