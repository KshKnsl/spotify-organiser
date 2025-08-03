import json
import os
from typing import List, Dict, Optional
import spotipy

CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'genre_cache.json')

def load_genre_cache() -> Dict[str, List[str]]:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print("Error loading genre cache, starting with empty cache")
            return {}
    return {}

def save_genre_cache(cache: Dict[str, List[str]]) -> None:
    try:
        dir_path = os.path.dirname(CACHE_FILE)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        print(f"Genre cache saved to {CACHE_FILE} with {len(cache)} artists")
    except Exception as e:
        print(f"Error saving genre cache: {e}")

def get_cache_stats() -> Dict[str, int]:
    cache = load_genre_cache()
    total = len(cache)
    with_genres = len([artist for artist, genres in cache.items() if genres])
    
    return {
        'total_artists': total,
        'artists_with_genres': with_genres,
        'artists_without_genres': total - with_genres
    }

def get_artist_genres(sp: spotipy.Spotify, artist_id: str, cache: Dict[str, List[str]]) -> List[str]:
    if artist_id in cache:
        print(f"Using cached genres for artist {artist_id}")
        return cache[artist_id]
    
    try:
        info = sp.artist(artist_id)
        genres = info.get('genres', [])
        
        cache[artist_id] = genres
        save_genre_cache(cache)
        print(f"Fetched and cached genres for artist {artist_id}: {genres}")
        
        return genres
    except Exception as e:
        print(f"Error getting genres for artist {artist_id}: {e}")
        cache[artist_id] = []
        save_genre_cache(cache)
        return []

def enrich_tracks_with_cached_genres(sp: spotipy.Spotify, tracks: List[Dict]) -> List[Dict]:
    cache = load_genre_cache()
    
    enriched = []
    
    for item in tracks:
        track = item.copy()
        
        actual = track.get('track') if 'track' in track else track
        
        if actual and actual.get('artists'):
            try:
                artist_id = actual['artists'][0]['id']
                genres = get_artist_genres(sp, artist_id, cache)
                
                if 'track' in track:
                    track['track']['artists'][0]['genres'] = genres
                else:
                    track['artists'][0]['genres'] = genres
                    
            except Exception as e:
                print(f"Error processing genres for track: {e}")
                if 'track' in track:
                    track['track']['artists'][0]['genres'] = []
                else:
                    track['artists'][0]['genres'] = []
        
        enriched.append(track)
    
    print(f"Genre cache now contains {len(cache)} artists")
    return enriched
