import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests

# 1. Configuration
CLIENT_ID = 'ea5f9e4831d2429d90564b630c921666'
CLIENT_SECRET = 'c5fa223490da45fcafbdcea1ac47623e'
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
NTFY_TOPIC = 'spotify_tracker' # Ensure this matches your phone app
MY_MARKET = 'BR'

def check_for_updates():
    try:
        # Authenticate with Spotify
        auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        sp = spotipy.Spotify(auth_manager=auth_manager)

        # Fetch tracks from the watchlist
        results = sp.playlist_items(PLAYLIST_ID, market=MY_MARKET)
        found_tracks = []
        total_songs_scanned = 0

        for item in results['items']:
            track = item['track']
            if track:
                total_songs_scanned += 1
                if track.get('is_playable'):
                    found_tracks.append(f"{track['name']} - {track['artists'][0]['name']}")

        # 2. Notification Logic
        if found_tracks:
            title = "New Songs Available"
            message = "The following tracks are now playable:\n" + "\n".join(found_tracks)
            tags = "tada,headphones"
        else:
            title = "Status: No Updates"
            message = f"Scanned {total_songs_scanned} tracks. All still unavailable in {MY_MARKET}."
            tags = "white_check_mark"

        # Send to ntfy.sh (No emojis in the Title header to avoid crash)
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=message.encode(encoding='utf-8'),
                      headers={
                          "Title": title,
                          "Tags": tags
                      })

    except Exception as e:
        error_str = str(e)
        print(f"Error detail: {error_str}")
        
        # Safe error notification
        # We check for 'invalid_client' to give you a specific hint
        if "invalid_client" in error_str:
            hint = "Check your Spotify Client ID and Secret in GitHub Secrets. Ensure NO SPACES exist."
        else:
            hint = error_str

        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=hint.encode(encoding='utf-8'),
                      headers={"Title": "Tracker Error Alert"})

if __name__ == "__main__":
    check_for_updates()
