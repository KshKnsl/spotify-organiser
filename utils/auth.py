import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'https://localhost:5000/callback')

scope = "user-library-read user-library-modify playlist-read-private playlist-modify-private playlist-modify-public user-read-playback-state user-read-currently-playing user-read-recently-played user-top-read"

def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=scope
    )

def get_spotify_client(token_info=None):
    if token_info:
        return spotipy.Spotify(auth=token_info['access_token'])
    else:
        return spotipy.Spotify(auth_manager=get_spotify_oauth())
