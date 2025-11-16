import os, base64, requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

TOKEN_URL = "https://accounts.spotify.com/api/token"
REC_URL = "https://api.spotify.com/v1/recommendations"

# Load kredensial dari .env
load_dotenv()
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
))

def get_token(client_id, client_secret):
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}"}
    data = {"grant_type":"client_credentials"}
    r = requests.post(TOKEN_URL, headers=headers, data=data)
    r.raise_for_status()
    return r.json().get('access_token')

def get_recommendations_by_seed(token, seed_genres, limit=10):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"seed_genres":",".join(seed_genres[:5]), "limit":limit}
    r = requests.get(REC_URL, headers=headers, params=params)
    r.raise_for_status()
    return r.json()

def get_preview_url_from_id(track_id: str):
    # Mengambil preview_url dari Spotify API berdasarkan track_id
    try:
        track = sp.track(track_id)
        return track.get("preview_url"), track.get("external_urls", {}).get("spotify")
    except Exception as e:
        print(f"Error fetching track {track_id}: {e}")
        return None, None