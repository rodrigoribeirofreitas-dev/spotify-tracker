import requests
import base64

# Suas credenciais fixas
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'

# COLE O NOVO CÓDIGO AQUI O MAIS RÁPIDO POSSÍVEL
CODIGO_NOVO = 'AQCtY6Ed0VoFqddYNNXbguL3bNWSQhzyFUqi27kptFw-DBsVQsyaKK65Q4u2YlWRjY_IOtqmvZIouyoCu8aObzhMj5uTbKLwPRfP0fc-Hr5psrOdJLFOJTbip11lcDj-XFwejLG88uZuDLFcj8_W1G7o5DfWLO_WAFndX1uvh9o9dYPKS8iaWge-KRBC2M2G5oUJkOy0lEZVzBV4wMXGrDhVIvpeF001J97uLG9r9jZUanhSNfzLzssp4ew5GuKIZA' 

def obter_chave_mestra():
    try:
        auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
        headers = {"Authorization": f"Basic {auth_str}", "Content-Type": "application/x-www-form-urlencoded"}
        data = {"grant_type": "authorization_code", "code": CODIGO_NOVO, "redirect_uri": "https://www.google.com"}
        
        res = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
        token = res.json().get('refresh_token')
        
        if token:
            msg = f"✅ SUCESSO! CHAVE MESTRA:\n\n{token}"
        else:
            msg = f"❌ O SPOTIFY DISSE: {res.json().get('error_description', res.json())}"
            
        requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))
    except Exception as e:
        requests.post("https://ntfy.sh/spotify_tracker", data=f"❌ ERRO: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    obter_chave_mestra()
