import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests

# 1. Configuration
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
# YOUR TOPIC: Change 'spotify_tracker_12345' to your unique name
NTFY_TOPIC = 'spotify_tracker' 
MY_MARKET = 'BR'

def check_for_updates():
    try:
        auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        sp = spotipy.Spotify(auth_manager=auth_manager)

        results = sp.playlist_items(PLAYLIST_ID, market=MY_MARKET)
        found_tracks = []

        for item in results['items']:
            track = item['track']
            if track and track.get('is_playable'):
                found_tracks.append(f"{track['name']} - {track['artists'][0]['name']}")

        if found_tracks:
            message = "New songs available:\n" + "\n".join(found_tracks)
            # Send to ntfy
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                          data=message.encode(encoding='utf-8'),
                          headers={
                              "Title": "Spotify Availability Alert 🎵",
                              "Priority": "high",
                              "Tags": "tada,headphones"
                          })
            print("Notification sent to ntfy!")
        else:
            print("No new tracks available.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_for_updates()
