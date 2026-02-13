import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests

# 1. Setup Credentials
CLIENT_ID = os.getenv('ea5f9e4831d2429d90564b630c921666')
CLIENT_SECRET = os.getenv('eb5c0211d7c9442eb36425870ccf78ae')
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm?si=3056fbc771cd41fc&pt=55897c37bbeac6c83e448b5801b890e4'
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')

auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

def check_songs():
    # Fetch tracks from the playlist
    results = sp.playlist_items(PLAYLIST_ID, market='US') # Change 'US' to your country code
    available_tracks = []

    for item in results['items']:
        track = item['track']
        # Spotify returns 'is_playable' as True if the song is now active
        if track.get('is_playable'):
            available_tracks.append(f"**{track['name']}** by {track['artists'][0]['name']}")

    # 2. Send Notification
    if available_tracks:
        message = "🎉 New songs available:\n" + "\n".join(available_tracks)
        requests.post(DISCORD_WEBHOOK, json={"content": message})

if __name__ == "__main__":
    check_songs()
