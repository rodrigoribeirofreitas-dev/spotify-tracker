import requests
import base64

# Suas credenciais de desenvolvedor
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'

# O código fresco que você acabou de me enviar
CODIGO_NOVO = 'AQAIHRL-ubo2GTWU3s74PSpkXSIOIjhqipfb11eW5Kj5drcd_wFNuHyizy4OvwevLjlnhbTTTav5HBOPeCR9W_hMv2GBgWJhN5EZ153_CaajekkH_ufn4GxY_HUmM4tfwOA'

def obter_chave_eterna():
    try:
        # Preparação da autenticação padrão Spotify
        auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_str}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Dados para a troca do código pela chave eterna (Refresh Token)
        data = {
            "grant_type": "authorization_code",
            "code": CODIGO_NOVO,
            "redirect_uri": "https://www.google.com"
        }
        
        # Chamada ao endpoint de tokens do Spotify
        res = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
        dados = res.json()
        
        refresh_token = dados.get('refresh_token')
        
        if refresh_token:
            msg = f"✅ VITÓRIA! SUA CHAVE ETERNA:\n\n{refresh_token}"
        else:
            msg = f"❌ ERRO NA TROCA: {dados.get('error_description', dados)}"
            
        # Envia o resultado para o seu canal ntfy
        requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))
        print(msg)

    except Exception as e:
        requests.post("https://ntfy.sh/spotify_tracker", data=f"❌ ERRO TÉCNICO: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    obter_chave_eterna()
