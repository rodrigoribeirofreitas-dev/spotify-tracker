import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Insira seus codigos reais entre as aspas
CLIENT_ID = 'bf24024ba81d409c9af3ce7ca8f95c3f'
CLIENT_SECRET = 'a873df6bb1974db6b963d25c14bf695a'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'

print("--- INICIANDO DEBUG ---")

try:
    auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    # Tenta ler o nome da playlist
    playlist_data = sp.playlist(PLAYLIST_ID)
    print("SUCESSO: Conectado a playlist: " + str(playlist_data['name']))
    print("Total de musicas: " + str(playlist_data['tracks']['total']))

except Exception as e:
    print("ERRO DO SPOTIFY: " + str(e))
