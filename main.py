import requests
import base64

# Suas novas credenciais
CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'
MY_MARKET = 'BR'

def check_for_updates():
    try:
        # 1. Autenticação Básica (O 'Aperto de Mão' mais simples possível)
        auth_str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_str}"},
            data={"grant_type": "client_credentials"}
        )
        
        if token_res.status_code != 200:
            raise Exception(f"Erro Token: {token_res.status_code}")
            
        token = token_res.json().get('access_token')

        # 2. Acesso Direto como Visitante (Sem passar o parâmetro de usuário)
        # Usamos o link direto da API de tracks para evitar bloqueios de perfil
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100"
        headers = {"Authorization": f"Bearer {token}"}
        
        res = requests.get(url, headers=headers)
        
        if res.status_code == 403:
            # Se ainda der 403, vamos reportar o motivo que o Spotify envia no corpo
            error_details = res.json().get('error', {}).get('message', 'Acesso Negado')
            raise Exception(f"Spotify diz: {error_details}")
            
        data = res.json()
        total_playlist = data.get('total', 0)
        items = data.get('items', [])
        
        liberadas = []
        for item in items:
            track = item.get('track')
            if track and MY_MARKET in track.get('available_markets', []):
                liberadas.append(f"{track['name']} - {track['artists'][0]['name']}")

        # 3. Notificação no ntfy
        if total_playlist == 0:
            msg = "Conectado, mas a playlist parece vazia para o público. Verifique 'Adicionar ao Perfil'."
        elif liberadas:
            msg = f"BOAS NOTICIAS! {len(liberadas)} musicas liberadas no BR:\n\n" + "\n".join(liberadas)
        else:
            msg = f"Rastreador OK: {len(items)} faixas lidas de {total_playlist}. Tudo bloqueado no BR."

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Aviso: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
