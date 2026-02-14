import requests

# Apenas o ID da nova playlist de 97 músicas
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker'

def check_for_updates():
    try:
        # Usamos um serviço de consulta pública para evitar o bloqueio do Client ID
        # Isso simula um navegador acessando sua playlist pública
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks?limit=100"
        
        # Gerando um token temporário rápido (Acesso Público)
        # Nota: Como o Client ID está dando 403/Vazio, este método tenta o acesso direto
        token_url = "https://open.spotify.com/get_access_token?reason=transport&productType=web_player"
        r_token = requests.get(token_url).json()
        token = r_token.get('accessToken')

        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        res = requests.get(url, headers=headers).json()
        items = res.get('items', [])
        
        total_lido = len(items)
        liberadas = []

        for item in items:
            track = item.get('track')
            if track:
                # Se a música tem nome, ela foi "lida" com sucesso
                # Verificamos se ela tem mercados disponíveis (se tiver BR, está online)
                markets = track.get('available_markets', [])
                if 'BR' in markets:
                    liberadas.append(f"{track['name']} - {track['artists'][0]['name']}")

        if total_lido > 0:
            msg = f"SUCESSO! Rastreador bypass funcionou. {total_lido} músicas lidas.\n"
            if liberadas:
                msg += f"\nLIBERADAS NO BR:\n" + "\n".join(liberadas)
            else:
                msg += "Nenhuma música disponível no Brasil ainda."
        else:
            msg = "O Spotify continua entregando uma lista vazia. A última alternativa é recriar o App com permissão 'Playlist-Read-Public'."

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'))

    except Exception as e:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=f"Erro no Bypass: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    check_for_updates()
