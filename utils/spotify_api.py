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
    tracks = []
    batch = 50
    offset = 0
    
    while True:
        try:
            results = sp.current_user_saved_tracks(limit=batch, offset=offset)
            if not results or not results['items']:
                break
                
            tracks.extend(results['items'])
            
            if limit and len(tracks) >= limit:
                tracks = tracks[:limit]
                break
                
            if not results['next']:
                break
                
            offset += batch
            
        except Exception as e:
            print(f"Error fetching liked songs at offset {offset}: {e}")
            break
    
    print(f"Finished fetching liked songs. Total: {len(tracks)}")
    return tracks


def get_current_playback(sp: spotipy.Spotify) -> Optional[Dict]:
    try:
        result = sp.current_playback()
        return result
    except Exception as e:
        print(f"Error getting current playback: {e}")
        return None


def detect_duplicate_liked_songs(sp: spotipy.Spotify) -> List[Dict]:
    songs = get_user_liked_songs(sp)
    
    groups = {}
    dupes = []
    
    for item in songs:
        track = item.get('track')
        if not track or not track.get('name'):
            continue
            
        name = track['name'].lower().strip()
        artist = track['artists'][0]['name'].lower().strip() if track.get('artists') else 'unknown'
        key = (name, artist)
        
        if key not in groups:
            groups[key] = []
        groups[key].append(item)
    
    for key, tracks in groups.items():
        if len(tracks) > 1:
            dupes.append({
                'track_name': tracks[0]['track']['name'],
                'artist_name': tracks[0]['track']['artists'][0]['name'] if tracks[0]['track'].get('artists') else 'Unknown Artist',
                'duplicate_count': len(tracks),
                'tracks': tracks
            })
    
    dupes.sort(key=lambda x: x['duplicate_count'], reverse=True)
    
    print(f"Found {len(dupes)} sets of duplicate tracks in liked songs")
    return dupes


def unlike_track(sp: spotipy.Spotify, track_id: str) -> bool:
    try:
        sp.current_user_saved_tracks_delete([track_id])
        print(f"=== UNLIKE_TRACK - Successfully removed track {track_id} from liked songs ===")
        return True
    except Exception as e:
        print(f"Error unliking track {track_id}: {e}")
        return False

def merge_all_duplicates(sp: spotipy.Spotify) -> Dict[str, int]:
    try:
        dupes = detect_duplicate_liked_songs(sp)
        removed = 0
        ids = []
        
        for group in dupes:
            for item in group['tracks'][1:]:
                ids.append(item['track']['id'])
        
        for i in range(0, len(ids), 50):
            batch = ids[i:i + 50]
            try:
                sp.current_user_saved_tracks_delete(batch)
                removed += len(batch)
            except Exception as e:
                print(f"Error removing batch: {e}")
        
        return {'tracks_removed': removed, 'duplicate_groups_processed': len(dupes)}
        
    except Exception as e:
        print(f"Error merging duplicates: {e}")
        return {'tracks_removed': 0, 'duplicate_groups_processed': 0}

def create_playlist(sp: spotipy.Spotify, user_id: str, name: str, description: str = "", public: bool = True) -> Optional[Dict]:
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
    tracks = get_tracks_from_playlist(sp, playlist_id)
    genres = {}
    
    for item in tracks:
        if item['track'] and item['track']['artists']:
            track_genres = get_genres_for_track(sp, item)
            for genre in track_genres:
                genres[genre] = genres.get(genre, 0) + 1
    
    return dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))
