from typing import List, Dict, Optional
import spotipy
import json

def get_user_playlists(sp: spotipy.Spotify) -> List[Dict]:
    playlists = []
    results = sp.current_user_playlists()
    print("=== GET_USER_PLAYLISTS - API Response ===")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    print("==========================================")
    
    while results:
        playlists.extend(results['items'])
        if results['next']:
            results = sp.next(results)
            print("=== GET_USER_PLAYLISTS - Next Page ===")
            print(json.dumps(results, indent=2, ensure_ascii=False))
            print("=====================================")
        else:
            break

    print(f"Finished fetching user playlists. Total: {len(playlists)}")
    return playlists


def get_tracks_from_playlist(sp: spotipy.Spotify, playlist_id: str) -> List[Dict]:
    """Fetches all tracks from a given playlist."""
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    print(f"=== GET_TRACKS_FROM_PLAYLIST ({playlist_id}) - API Response ===")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    print("==============================================================")
    
    while results:
        tracks.extend(results['items'])
        if results['next']:
            results = sp.next(results)
            print(f"=== GET_TRACKS_FROM_PLAYLIST ({playlist_id}) - Next Page ===")
            print(json.dumps(results, indent=2, ensure_ascii=False))
            print("===========================================================")
        else:
            break
    
    print(f"Finished fetching playlist tracks. Total: {len(tracks)}")
    return tracks


def get_genres_for_track(sp: spotipy.Spotify, track: Dict) -> List[str]:
    """Fetches genres for the track based on its first artist."""
    artists = track['track']['artists']
    if not artists:
        return []
    
    artist_id = artists[0]['id']
    artist_info = sp.artist(artist_id)
    print(f"=== GET_GENRES_FOR_TRACK ({artist_id}) - API Response ===")
    print(json.dumps(artist_info, indent=2, ensure_ascii=False))
    print("========================================================")
    return artist_info.get('genres', [])


def get_user_liked_songs(sp: spotipy.Spotify, limit: int = 50) -> List[Dict]:
    """Fetches user's liked songs."""
    tracks = []
    results = sp.current_user_saved_tracks(limit=limit)
    print(f"=== GET_USER_LIKED_SONGS (limit={limit}) - API Response ===")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    print("==========================================================")
    
    while results:
        tracks.extend(results['items'])
        if results['next'] and len(tracks) < limit:
            results = sp.next(results)
            print("=== GET_USER_LIKED_SONGS - Next Page ===")
            print(json.dumps(results, indent=2, ensure_ascii=False))
            print("========================================")
        else:
            break
    
    print(f"Finished fetching liked songs. Total: {len(tracks[:limit])}")
    return tracks[:limit]


def get_current_playback(sp: spotipy.Spotify) -> Optional[Dict]:
    """Gets current playback information."""
    try:
        result = sp.current_playback()
        print("=== GET_CURRENT_PLAYBACK - API Response ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("===========================================")
        return result
    except Exception as e:
        print(f"Error getting current playback: {e}")
        return None


def get_currently_playing(sp: spotipy.Spotify) -> Optional[Dict]:
    """Gets currently playing track."""
    try:
        result = sp.currently_playing()
        print("=== GET_CURRENTLY_PLAYING - API Response ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("=============================================")
        return result
    except Exception as e:
        print(f"Error getting currently playing track: {e}")
        return None


def get_audio_analysis(sp: spotipy.Spotify, track_id: str) -> Optional[Dict]:
    """Gets audio analysis for a track."""
    try:
        result = sp.audio_analysis(track_id)
        print(f"=== GET_AUDIO_ANALYSIS ({track_id}) - API Response ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("======================================================")
        return result
    except Exception as e:
        if hasattr(e, 'http_status') and e.http_status == 403:
            print(f"Audio analysis not available for track {track_id} (403 Forbidden). Trying audio features instead.")
            # Try to get audio features as a fallback
            try:
                features = sp.audio_features(track_id)
                print(f"=== GET_AUDIO_FEATURES ({track_id}) - Fallback Response ===")
                print(json.dumps(features, indent=2, ensure_ascii=False))
                print("==========================================================")
                if features and features[0]:
                    # Convert audio features to a similar structure as audio analysis
                    converted_result = {
                        'track': {
                            'tempo': features[0].get('tempo'),
                            'key': features[0].get('key'),
                            'mode': features[0].get('mode'),
                            'time_signature': features[0].get('time_signature'),
                            'duration': features[0].get('duration_ms', 0) / 1000,  # Convert to seconds
                            'loudness': features[0].get('loudness'),
                            'energy': features[0].get('energy'),
                            'danceability': features[0].get('danceability'),
                            'valence': features[0].get('valence'),
                            'acousticness': features[0].get('acousticness'),
                            'instrumentalness': features[0].get('instrumentalness'),
                            'speechiness': features[0].get('speechiness'),
                        }
                    }
                    print(f"=== CONVERTED_AUDIO_FEATURES ({track_id}) ===")
                    print(json.dumps(converted_result, indent=2, ensure_ascii=False))
                    print("============================================")
                    return converted_result
            except Exception as fallback_error:
                print(f"Audio features also failed for track {track_id}: {fallback_error}")
        else:
            print(f"Error getting audio analysis for track {track_id}: {e}")
        return None
    except Exception as e:
        print(f"Error getting audio analysis for track {track_id}: {e}")
        return None


def search_spotify(sp: spotipy.Spotify, query: str, search_type: str = 'track', limit: int = 20) -> Dict:
    """Search Spotify for tracks, artists, albums, or playlists."""
    try:
        results = sp.search(q=query, type=search_type, limit=limit)
        print(f"=== SEARCH_SPOTIFY ('{query}', type={search_type}, limit={limit}) - API Response ===")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        print("=================================================================================")
        return results
    except Exception as e:
        print(f"Error searching Spotify: {e}")
        return {}


def get_track_audio_features(sp: spotipy.Spotify, track_id: str) -> Optional[Dict]:
    """Gets audio features for a track."""
    try:
        result = sp.audio_features(track_id)[0]
        print(f"=== GET_TRACK_AUDIO_FEATURES ({track_id}) - API Response ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("============================================================")
        return result
    except Exception as e:
        print(f"Error getting audio features for track {track_id}: {e}")
        return None


def get_artist_top_tracks(sp: spotipy.Spotify, artist_id: str, country: str = 'US') -> List[Dict]:
    """Gets an artist's top tracks."""
    try:
        results = sp.artist_top_tracks(artist_id, country=country)
        print(f"=== GET_ARTIST_TOP_TRACKS ({artist_id}, country={country}) - API Response ===")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        print("=========================================================================")
        return results.get('tracks', [])
    except Exception as e:
        print(f"Error getting top tracks for artist {artist_id}: {e}")
        return []


def get_artist_albums(sp: spotipy.Spotify, artist_id: str, album_type: str = 'album', limit: int = 20) -> List[Dict]:
    """Gets an artist's albums."""
    try:
        results = sp.artist_albums(artist_id, album_type=album_type, limit=limit)
        print(f"=== GET_ARTIST_ALBUMS ({artist_id}, type={album_type}, limit={limit}) - API Response ===")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        print("==================================================================================")
        return results.get('items', [])
    except Exception as e:
        print(f"Error getting albums for artist {artist_id}: {e}")
        return []


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
