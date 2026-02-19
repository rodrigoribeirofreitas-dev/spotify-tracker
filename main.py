import requests
import base64

# Suas credenciais fixas
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'

# O código que você acabou de me enviar
CODIGO_NOVO = 'AQBMVda0DYEAg-05bF_nWHFbKRuAkqSx4l8_i0m9wI-o0SlQxWzw4q7fPlAaovbyVw8_5jC__EYi317J-lwt0Df-SAcePRrL99NXdctqrYclE-JS-Tx1xgNxuXwzFO8n4YI'

def obter_chave_eterna():
    try:
        # Codificação das credenciais para o padrão Spotify
        auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_str}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Dados da requisição de troca
        data = {
            "grant_type": "authorization_code",
            "code": CODIGO_NOVO,
            "redirect_uri": "https://www.google.com"
        }
        
        # Chamada para o endpoint de tokens do Spotify
        res = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
        dados = res.json()
        
        # Extração do Refresh Token
        refresh_token = dados.get('refresh_token')
        
        if refresh_token:
            msg = f"✅ AGORA SIM! SUA CHAVE ETERNA:\n\n{refresh_token}"
        else:
            msg = f"❌ O SPOTIFY NEGOU: {dados.get('error_description', dados)}"
            
        # Envio direto para o seu ntfy
        requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))
        print(msg)

    except Exception as e:
        requests.post("https://ntfy.sh/spotify_tracker", data=f"❌ ERRO TÉCNICO: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    obter_chave_eterna()
