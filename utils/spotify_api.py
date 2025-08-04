from typing import List, Dict, Optional
import spotipy
import json
from .genre_cache import enrich_tracks_with_cached_genres

def get_user_playlists(sp: spotipy.Spotify) -> List[Dict]:
    pl = []
    res = sp.current_user_playlists()
    while res:
        pl.extend(res['items'])
        if res['next']:
            res = sp.next(res)
        else:
            break

    print(f"Finished fetching user playlists. Total: {len(pl)}")
    return pl


def get_tracks_from_playlist(sp: spotipy.Spotify, playlist_id: str) -> List[Dict]:
    tr = []
    res = sp.playlist_tracks(playlist_id)
    
    while res:
        tr.extend(res['items'])
        if res['next']:
            res = sp.next(res)
        else:
            break
    
    print(f"Finished fetching playlist tracks. Total: {len(tr)}")
    return tr


def get_user_liked_songs(sp: spotipy.Spotify, limit: int = None) -> List[Dict]:
    tr = []
    batch = 50
    off = 0
    
    while True:
        try:
            res = sp.current_user_saved_tracks(limit=batch, offset=off)
            if not res or not res['items']:
                break
                
            tr.extend(res['items'])
            
            if limit and len(tr) >= limit:
                tr = tr[:limit]
                break
                
            if not res['next']:
                break
                
            off += batch
            
        except Exception as e:
            print(f"Error fetching liked songs at offset {off}: {e}")
            break
    
    print(f"Finished fetching liked songs. Total: {len(tr)}")
    return tr


def get_current_playback(sp: spotipy.Spotify) -> Optional[Dict]:
    try:
        res = sp.current_playback()
        return res
    except Exception as e:
        print(f"Error getting current playback: {e}")
        return None


def detect_duplicate_liked_songs(sp: spotipy.Spotify) -> List[Dict]:
    songs = get_user_liked_songs(sp)
    
    grp = {}
    dup = []
    
    for item in songs:
        tr = item.get('track')
        if not tr or not tr.get('name'):
            continue
            
        name = tr['name'].lower().strip()
        art = tr['artists'][0]['name'].lower().strip() if tr.get('artists') else 'unknown'
        key = (name, art)
        
        if key not in grp:
            grp[key] = []
        grp[key].append(item)
    
    for key, tr in grp.items():
        if len(tr) > 1:
            dup.append({
                'track_name': tr[0]['track']['name'],
                'artist_name': tr[0]['track']['artists'][0]['name'] if tr[0]['track'].get('artists') else 'Unknown Artist',
                'duplicate_count': len(tr),
                'tracks': tr
            })
    
    dup.sort(key=lambda x: x['duplicate_count'], reverse=True)
    
    print(f"Found {len(dup)} sets of duplicate tracks in liked songs")
    return dup


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
        dup = detect_duplicate_liked_songs(sp)
        rem = 0
        ids = []
        
        for grp in dup:
            for item in grp['tracks'][1:]:
                ids.append(item['track']['id'])
        
        for i in range(0, len(ids), 50):
            batch = ids[i:i + 50]
            try:
                sp.current_user_saved_tracks_delete(batch)
                rem += len(batch)
            except Exception as e:
                print(f"Error removing batch: {e}")
        
        return {'tracks_removed': rem, 'duplicate_groups_processed': len(dup)}
        
    except Exception as e:
        print(f"Error merging duplicates: {e}")
        return {'tracks_removed': 0, 'duplicate_groups_processed': 0}

def create_genre_playlists(sp: spotipy.Spotify, genre_filter: str = None) -> Dict[str, any]:
    try:
        usr = sp.current_user()
        songs = get_user_liked_songs(sp)
        
        from .genre_cache import enrich_tracks_with_cached_genres
        enr = enrich_tracks_with_cached_genres(sp, songs)
        
        gen_tr = {}
        
        for item in enr:
            tr = item.get('track')
            if not tr or not tr.get('artists'):
                continue
                
            gen = tr['artists'][0].get('genres', [])
            for g in gen:
                if genre_filter and genre_filter.lower() not in g.lower():
                    continue
                if g not in gen_tr:
                    gen_tr[g] = []
                gen_tr[g].append(tr['uri'])
        
        crt = []
        for g, uris in gen_tr.items():
            if len(uris) >= 5:
                name = f"Liked Songs - {g.title()}"
                desc = f"Auto-generated playlist for {g} tracks from liked songs"
                
                pl = create_playlist(sp, usr['id'], name, desc)
                if pl:
                    ok = add_tracks_to_playlist(sp, pl['id'], uris)
                    if ok:
                        crt.append({
                            'name': name,
                            'genre': g,
                            'track_count': len(uris),
                            'playlist_id': pl['id']
                        })
        
        return {
            'playlists_created': len(crt),
            'playlists': crt,
            'total_genres': len(gen_tr)
        }
        
    except Exception as e:
        print(f"Error creating genre playlists: {e}")
        return {'playlists_created': 0, 'playlists': [], 'total_genres': 0}

def create_playlist(sp: spotipy.Spotify, user_id: str, name: str, desc: str) -> Dict[str, any]:
    try:
        pl = sp.user_playlist_create(user_id, name, public=False, description=desc)
        return pl
    except Exception as e:
        print(f"Error creating playlist: {e}")
        return None

def add_tracks_to_playlist(sp: spotipy.Spotify, playlist_id: str, uris: List[str]) -> bool:
    try:
        sz = 100
        for i in range(0, len(uris), sz):
            batch = uris[i:i + sz]
            sp.playlist_add_items(playlist_id, batch)
        return True
    except Exception as e:
        print(f"Error adding tracks to playlist: {e}")
        return False

def get_available_genres(sp: spotipy.Spotify) -> List[str]:
    try:
        songs = get_user_liked_songs(sp)
        from .genre_cache import enrich_tracks_with_cached_genres
        enr = enrich_tracks_with_cached_genres(sp, songs)
        
        all_gen = set()
        for item in enr:
            tr = item.get('track')
            if tr and tr.get('artists'):
                gen = tr['artists'][0].get('genres', [])
                all_gen.update(gen)
        
        return sorted(list(all_gen))
    except Exception as e:
        print(f"Error getting genres: {e}")
        return []

def get_playlist_genres(sp: spotipy.Spotify, playlist_id: str) -> Dict[str, int]:
    tr = get_tracks_from_playlist(sp, playlist_id)
    gen = {}
    
    for item in tr:
        if item['track'] and item['track']['artists']:
            tr_gen = get_genres_for_track(sp, item)
            for g in tr_gen:
                gen[g] = gen.get(g, 0) + 1
    
    return dict(sorted(gen.items(), key=lambda x: x[1], reverse=True))
