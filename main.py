import requests
import base64
import json

CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'

def obter_token():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    # URL oficial e direta de autenticação
    res = requests.post("https://accounts.spotify.com/api/token", 
                        headers={"Authorization": f"Basic {auth_str}"},
                        data={"grant_type": "client_credentials"})
    return res.json().get('access_token')

def forca_bruta_github():
    token = obter_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # FORÇA BRUTA: Endpoint direto nas faixas, usando 'fields' para forçar a entrega
    url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?market=BR&limit=5&fields=total,items(track(name,is_playable))"
    
    print("Executando Força Bruta no cofre de faixas...")
    res = requests.get(url, headers=headers)
    print(f"Status da resposta: {res.status_code}")
    
    # Imprime a verdade nua e crua no console do GitHub
    try:
        dados = res.json()
        print("\n--- INÍCIO DA RESPOSTA (FORÇA BRUTA) ---\n")
        print(json.dumps(dados, indent=2, ensure_ascii=False))
        print("\n--- FIM DA RESPOSTA ---\n")
    except:
        print(res.text)

if __name__ == "__main__":
    forca_bruta_github()
