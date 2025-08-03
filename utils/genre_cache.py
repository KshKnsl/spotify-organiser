import json
import os
from typing import List, Dict, Optional
import spotipy

# Cache file path - save in project directory
CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'genre_cache.json')

def load_genre_cache() -> Dict[str, List[str]]:
    """Load the genre cache from JSON file."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print("Error loading genre cache, starting with empty cache")
            return {}
    return {}

def save_genre_cache(cache: Dict[str, List[str]]) -> None:
    """Save the genre cache to JSON file."""
    try:
        # Ensure the directory exists
        cache_dir = os.path.dirname(CACHE_FILE)
        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
            
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        print(f"Genre cache saved to {CACHE_FILE} with {len(cache)} artists")
    except Exception as e:
        print(f"Error saving genre cache: {e}")

def get_cache_stats() -> Dict[str, int]:
    """Get statistics about the genre cache."""
    cache = load_genre_cache()
    total_artists = len(cache)
    artists_with_genres = len([artist for artist, genres in cache.items() if genres])
    
    return {
        'total_artists': total_artists,
        'artists_with_genres': artists_with_genres,
        'artists_without_genres': total_artists - artists_with_genres
    }

def get_artist_genres(sp: spotipy.Spotify, artist_id: str, cache: Dict[str, List[str]]) -> List[str]:
    """Get genres for an artist, using cache if available."""
    if artist_id in cache:
        print(f"Using cached genres for artist {artist_id}")
        return cache[artist_id]
    
    try:
        artist_info = sp.artist(artist_id)
        genres = artist_info.get('genres', [])
        
        # Save to cache immediately
        cache[artist_id] = genres
        save_genre_cache(cache)  # Save immediately after fetching new data
        print(f"Fetched and cached genres for artist {artist_id}: {genres}")
        
        return genres
    except Exception as e:
        print(f"Error getting genres for artist {artist_id}: {e}")
        # Cache empty genres to avoid repeated failures
        cache[artist_id] = []
        save_genre_cache(cache)  # Save even empty results to avoid repeated API calls
        return []

def enrich_tracks_with_cached_genres(sp: spotipy.Spotify, tracks: List[Dict]) -> List[Dict]:
    """Enrich track data with artist genre information using cache."""
    # Load existing cache
    cache = load_genre_cache()
    
    enriched_tracks = []
    
    for track_item in tracks:
        track = track_item.copy()
        
        # Handle different track structures (liked songs vs playlist tracks)
        actual_track = track.get('track') if 'track' in track else track
        
        if actual_track and actual_track.get('artists'):
            try:
                # Get the first artist's genres using cache
                artist_id = actual_track['artists'][0]['id']
                genres = get_artist_genres(sp, artist_id, cache)
                
                # Add genres to the artist data
                if 'track' in track:
                    track['track']['artists'][0]['genres'] = genres
                else:
                    track['artists'][0]['genres'] = genres
                    
            except Exception as e:
                print(f"Error processing genres for track: {e}")
                # Set empty genres on error
                if 'track' in track:
                    track['track']['artists'][0]['genres'] = []
                else:
                    track['artists'][0]['genres'] = []
        
        enriched_tracks.append(track)
    
    print(f"Genre cache now contains {len(cache)} artists")
    return enriched_tracks
