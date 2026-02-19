import requests
import base64

# Suas credenciais
CID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CSEC = '0ced5b2211c5471ca53c3fe938aa3ba3'

# O novo código que você acabou de me enviar
CODIGO_NOVO = 'AQC15tLpCL9MZlLfYiiNDk57fiFj7M_jSBl-TfLiOCBKwIcgvT_F_x292L-YyGjO_n5ftTrs10YEXY3gjR9QWXewgAiNduSHVrK65ex2dmK29MeaN2vheM2l9HBc9tWV97U'

def obter_chave_eterna():
    try:
        # Preparação da autenticação
        auth_str = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_str}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "authorization_code",
            "code": CODIGO_NOVO,
            "redirect_uri": "https://www.google.com"
        }
        
        # Troca do código temporário pela chave eterna
        res = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
        dados = res.json()
        
        refresh_token = dados.get('refresh_token')
        
        if refresh_token:
            msg = f"✅ SUCESSO! COPIE ESTA CHAVE:\n\n{refresh_token}"
        else:
            msg = f"❌ ERRO SPOTIFY: {dados.get('error_description', dados)}"
            
        # Envia para o seu ntfy
        requests.post("https://ntfy.sh/spotify_tracker", data=msg.encode('utf-8'))
        print(msg)

    except Exception as e:
        requests.post("https://ntfy.sh/spotify_tracker", data=f"❌ ERRO: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    obter_chave_eterna()
