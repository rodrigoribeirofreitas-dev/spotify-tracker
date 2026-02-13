import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests

# 1. Configuration
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'
# Change this to your unique ntfy topic name
NTFY_TOPIC = 'spotify_tracker' 
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
            # Alert for new available songs
            title = "🚨 New Songs Available!"
            message = "The following tracks are now playable:\n" + "\n".join(found_tracks)
            tags = "tada,headphones,musical_note"
            priority = "high"
        else:
            # Status update for no news
            title = "✅ Status: No Updates"
            message = f"Scanned {total_songs_scanned} tracks. All are still unavailable in {MY_MARKET}."
            tags = "white_check_mark,mag"
            priority = "default"

        # 3. Send to ntfy.sh
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=message.encode(encoding='utf-8'),
                      headers={
                          "Title": title,
                          "Priority": priority,
                          "Tags": tags
                      })
        print(f"Update sent: {title}")

    except Exception as e:
        # Emergency notification if the script crashes
        error_msg = f"The tracker encountered an error: {str(e)}"
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=error_msg.encode(encoding='utf-8'),
                      headers={"Title": "⚠️ Tracker Error", "Priority": "urgent", "Tags": "x"})
        print(f"Error: {e}")

if __name__ == "__main__":
    check_for_updates()
