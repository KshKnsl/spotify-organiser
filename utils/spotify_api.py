from typing import List, Dict, Optional
import spotipy
import json
from .genre_cache import enrich_tracks_with_cached_genres

def get_user_playlists(sp: spotipy.Spotify) -> List[Dict]:
    playlists = []
    results = sp.current_user_playlists()
    while results:
        playlists.extend(results['items'])
        if results['next']:
            results = sp.next(results)
        else:
            break

    print(f"Finished fetching user playlists. Total: {len(playlists)}")
    return playlists


def get_tracks_from_playlist(sp: spotipy.Spotify, playlist_id: str) -> List[Dict]:
    """Fetches all tracks from a given playlist."""
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    
    while results:
        tracks.extend(results['items'])
        if results['next']:
            results = sp.next(results)
        else:
            break
    
    print(f"Finished fetching playlist tracks. Total: {len(tracks)}")
    return tracks


def get_user_liked_songs(sp: spotipy.Spotify, limit: int = None) -> List[Dict]:
    """Fetches user's liked songs. If limit is None, fetches all liked songs."""
    tracks = []
    # Spotify API max limit per request is 50 for saved tracks
    batch_size = 50
    offset = 0
    
    while True:
        try:
            results = sp.current_user_saved_tracks(limit=batch_size, offset=offset)
            if not results or not results['items']:
                break
                
            tracks.extend(results['items'])
            
            # If we have a limit and we've reached it, stop
            if limit and len(tracks) >= limit:
                tracks = tracks[:limit]
                break
                
            # If there are no more results, stop
            if not results['next']:
                break
                
            offset += batch_size
            
        except Exception as e:
            print(f"Error fetching liked songs at offset {offset}: {e}")
            break
    
    print(f"Finished fetching liked songs. Total: {len(tracks)}")
    return tracks


def get_current_playback(sp: spotipy.Spotify) -> Optional[Dict]:
    """Gets current playback information."""
    try:
        result = sp.current_playback()
        return result
    except Exception as e:
        print(f"Error getting current playback: {e}")
        return None

def create_playlist(sp: spotipy.Spotify, user_id: str, name: str, description: str = "", public: bool = True) -> Optional[Dict]:
    """Creates a new playlist for the user."""
    try:
        result = sp.user_playlist_create(user_id, name, public=public, description=description)
        print(f"=== CREATE_PLAYLIST (user={user_id}, name='{name}') - API Response ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("==================================================================")
        return result
    except Exception as e:
        print(f"Error creating playlist: {e}")
        return None


def add_tracks_to_playlist(sp: spotipy.Spotify, playlist_id: str, track_uris: List[str]) -> bool:
    """Adds tracks to a playlist."""
    try:
        result = sp.playlist_add_items(playlist_id, track_uris)
        print(f"=== ADD_TRACKS_TO_PLAYLIST ({playlist_id}, {len(track_uris)} tracks) - API Response ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("================================================================================")
        return True
    except Exception as e:
        print(f"Error adding tracks to playlist: {e}")
        return False


def get_playlist_genres(sp: spotipy.Spotify, playlist_id: str) -> Dict[str, int]:
    """Analyzes a playlist and returns genre distribution."""
    tracks = get_tracks_from_playlist(sp, playlist_id)
    genre_count = {}
    
    for item in tracks:
        if item['track'] and item['track']['artists']:
            genres = get_genres_for_track(sp, item)
            for genre in genres:
                genre_count[genre] = genre_count.get(genre, 0) + 1
    
    return dict(sorted(genre_count.items(), key=lambda x: x[1], reverse=True))
