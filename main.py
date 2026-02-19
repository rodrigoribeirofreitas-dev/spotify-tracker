import requests
import base64

# Suas credenciais de desenvolvedor
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'

# O código que você acabou de me enviar (Fresco)
CODIGO_NOVO = 'AQCL-gWlNbAW9W6XV0mGIHNluJ6dqr-iUfLHFG9_hjB7ZGW3AUlV2vXJB5gGM69kwiUmPCQrYjVcti_KbOxBtL_uGGSRWntoT6h5hoIpXvG0Tz-Ur9qUp7S--iJZ41kfqL0'

def obter_chave_eterna():
    try:
        # Preparação da autenticação padrão Spotify
        auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_str}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Dados para a troca do código pela chave eterna
        data = {
            "grant_type": "authorization_code",
            "code": CODIGO_NOVO,
            "redirect_uri": "https://www.google.com"
        }
        
        # Chamada ao endpoint de tokens
        res = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
        dados = res.json()
        
        refresh_token = dados.get('refresh_token')
        
        if refresh_token:
            msg = f"✅ VITÓRIA! SUA CHAVE ETERNA:\n\n{refresh_token}"
        else:
            msg = f"❌ ERRO NA TROCA: {dados.get('error_description', dados)}"
            
        # Envia o resultado para o seu ntfy
        requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))
        print(msg)

    except Exception as e:
        requests.post("https://ntfy.sh/spotify_tracker", data=f"❌ ERRO TÉCNICO: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    obter_chave_eterna()
