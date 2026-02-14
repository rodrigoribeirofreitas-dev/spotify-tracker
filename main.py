import requests
import base64

CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = '0ced5b2211c5471ca53c3fe938aa3ba3'
PLAYLIST_ID = '2Cj8Wf0yD2eS15p63Vl0Gq'
NTFY_TOPIC = 'spotify_tracker'
MY_MARKET = 'BR'

def check_for_updates():
    try:
        # 1. Autenticação
        auth_str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        token_res = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_str}"},
            data={"grant_type": "client_credentials"}
        ).json()
        token = token_res.get('access_token')

        # 2. Chamada com Parâmetro de Mercado (Evita itens vazios)
        # Adicionamos market=BR direto na URL da API
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100&market={MY_MARKET}"
        headers = {"Authorization": f"Bearer {token}"}
        
        res = requests.get(url, headers=headers).json()
        
        # Pegamos o total direto do cabeçalho da resposta
        total_na_api = res.get('total', 0)
        items = res.get('items', [])
        
        total_analisado = 0
        liberadas = []

        for item in items:
            track = item.get('track')
            if track:
                total_analisado += 1
                # Se a música aparece aqui com o market=BR, ela está disponível
                artist = track['artists'][0]['name'] if track.get('artists') else "Unknown"
                liberadas.append(f"{track['name']} - {artist}")

        # 3. Notificação
        if total_analisado > 0:
            msg = f"SUCESSO! Rastreador leu {total_analisado} de {total_na_api} músicas.\n"
            if liberadas:
                msg += f"\nDISPONÍVEIS NO BR:\n" + "\n".join(liberadas)
            else:
                msg += "Nenhuma música disponível no Brasil ainda."
        else:
            msg = f"ERRO DE LEITURA: A API diz que há {total_na_api} músicas, mas não enviou os detalhes. Tentando nova rota..."

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro Script: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
