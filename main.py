import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests

# 1. Configuration
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
PLAYLIST_ID = '4n3nX3eYsqaRVZSADZbhBm'  # Your Manilla Road Watchlist
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')
MY_MARKET = 'BR'  # Set specifically for Brazil

def check_for_updates():
    # --- DEBUG SECTION ---
    print("--- Debug Information ---")
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ ERROR: GitHub Secrets (ID or Secret) are MISSING!")
    else:
        print(f"✅ Client ID found (starts with: {CLIENT_ID[:4]}...)")
        print(f"✅ Client Secret found (starts with: {CLIENT_SECRET[:4]}...)")
    print(f"Checking playlist {PLAYLIST_ID} in market: {MY_MARKET}")
    print("------------------------")
    # ---------------------

    try:
        # Authenticate
        auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        sp = spotipy.Spotify(auth_manager=auth_manager)

        # Fetch tracks
        results = sp.playlist_items(PLAYLIST_ID, market=MY_MARKET)
        found_tracks = []

        for item in results['items']:
            track = item['track']
            if track and track.get('is_playable'):
                track_info = f"🎵 **{track['name']}** - {track['artists'][0]['name']}"
                found_tracks.append(track_info)

        # Notify
        if found_tracks:
            print(f"Success! Found {len(found_tracks)} available tracks.")
            payload = {
                "content": "🚨 **Spotify Availability Alert!**",
                "embeds": [{"description": "\n".join(found_tracks), "color": 3066993}]
            }
            requests.post(DISCORD_WEBHOOK, json=payload)
        else:
            print("Scan complete: No tracks are available yet.")

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        # This will help us see if it's still an auth issue
        if "invalid_client" in str(e):
            print("ADVICE: Your Client ID or Secret is still being rejected. Ensure you clicked 'SAVE' at the bottom of the Spotify Developer page!")

if __name__ == "__main__":
    check_for_updates()
