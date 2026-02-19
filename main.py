import requests
import base64
import json

# Suas credenciais
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'

def obter_token():
    auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    # URL oficial de autenticação do Spotify
    res = requests.post("https://accounts.spotify.com/api/token", 
                        headers={"Authorization": f"Basic {auth_str}"},
                        data={"grant_type": "client_credentials"})
    return res.json().get('access_token')

def gerar_log_completo():
    print("Gerando token...")
    token = obter_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # URL oficial da API do Spotify
    url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}?market=BR"
    
    print("Consultando a playlist...")
    res = requests.get(url, headers=headers)
    
    print(f"Status da resposta: {res.status_code}")
    
    # Cria o arquivo e salva o conteúdo cru lá dentro
    with open("log_spotify.txt", "w", encoding="utf-8") as f:
        try:
            # Tenta salvar formatado bonitinho para facilitar a leitura
            dados = res.json()
            f.write(json.dumps(dados, indent=4, ensure_ascii=False))
            print("✅ Sucesso! Abra o arquivo 'log_spotify.txt' para ver o resultado.")
        except json.JSONDecodeError:
            # Se der erro e não for um JSON, salva o texto puro
            f.write(res.text)
            print("⚠️ A resposta não era um JSON. Salvo em texto bruto.")

if __name__ == "__main__":
    gerar_log_completo()
