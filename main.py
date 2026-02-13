import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests

# 1. Configuration - These come from your GitHub Secrets later
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
PLAYLIST_ID = 'YOUR_PLAYLIST_ID'  # Replace with your actual Playlist ID
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')
MY_MARKET = 'US'  # <--- CHANGE THIS to your 2-letter country code (e.g., 'BR', 'GB', 'CA')

# 2. Authenticate
auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

def check_for_updates():
    print(f"Checking playlist {PLAYLIST_ID} for available tracks in {MY_MARKET}...")
    
    # Get all items from the playlist
    results = sp.playlist_items(PLAYLIST_ID, market=MY_MARKET)
    found_tracks = []

    for item in results['items']:
        track = item['track']
        if track is None: continue # Skip if track is empty
        
        # The API only returns 'is_playable' if market is specified
        if track.get('is_playable') == True:
            track_info = f"🎵 **{track['name']}** - {track['artists'][0]['name']}"
            found_tracks.append(track_info)
            print(f"Found available track: {track['name']}")

    # 3. Notify if anything is found
    if found_tracks:
        payload = {
            "content": "🚨 **Spotify Availability Alert!**\nThe following songs are now playable:",
            "embeds": [{"description": "\n".join(found_tracks), "color": 3066993}]
        }
        requests.post(DISCORD_WEBHOOK, json=payload)
    else:
        print("No new tracks found yet. Stay patient!")

if __name__ == "__main__":
    check_for_updates()
