import requests
import base64

client_id = 'bf24024ba81d409c9af3ce7ca8f95c3f'
client_secret = '0ced5b2211c5471ca53c3fe938aa3ba3'
code = 'AQDL0EE7beZ59P3ni0TTt4DIRXhzjmGdCa2yyGvcUtruRp0SnmysxSzsXCRLMBRxwDVDqOUaA5hMabJiVBzRGibYmGFIE2Ke32S428C9cDGvJEAYZT3aoyrcTRQ_hBi4rZmFMro3-7ntADitbiCnYAy4oXyyLDt1guCiFYVuEb-xsAjryEBgDR9c9sUVFmrrMPZDGt9jfMJRlYwzQKqo-JhuJ3xz3D4u7VNUby3Bd4z75QSBwT9PACeWJIYOCFy-XQ'
redirect_uri = 'https://www.google.com'

auth_str = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
headers = {"Authorization": f"Basic {auth_str}"}
data = {
    "grant_type": "authorization_code",
    "code": code,
    "redirect_uri": redirect_uri
}

res = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
print(res.json()) # O 'refresh_token' vai aparecer aqui!
