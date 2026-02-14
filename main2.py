import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

CLIENT_ID = 'SEU_ID'
CLIENT_SECRET = 'SEU_SECRET'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'

auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

try:
    # Tenta pegar apenas o nome da playlist
    pl = sp.playlist(PLAYLIST_ID)
    print(f"Sucesso! Playlist: {pl['name']}")
except Exception as e:
    print(f"DEBUG: {e}")
