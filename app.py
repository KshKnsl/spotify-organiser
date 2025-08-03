from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
from utils.auth import get_spotify_oauth, get_spotify_client
from utils.spotify_api import (
    get_user_playlists, get_user_liked_songs,
    get_current_playback, get_currently_playing, get_audio_analysis,
    search_spotify, get_tracks_from_playlist
)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

@app.route('/')
def index():
    """Home page"""
    if 'token_info' not in session:
        return render_template('login.html')
    
    try:
        sp = get_spotify_client(session['token_info'])
        user_info = sp.current_user()
        playlists = get_user_playlists(sp)
        liked_songs = get_user_liked_songs(sp, limit=20)
        current_playback = get_current_playback(sp)
        
        return render_template('index.html', 
                             user=user_info, 
                             playlists=playlists,
                             liked_songs=liked_songs,
                             current_playback=current_playback)
    except Exception as e:
        flash(f'Error loading data: {str(e)}', 'error')
        return render_template('login.html')

@app.route('/login')
def login():
    """Initiate Spotify OAuth login"""
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """Handle Spotify OAuth callback"""
    sp_oauth = get_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    
    try:
        token_info = sp_oauth.get_access_token(code)
        session['token_info'] = token_info
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Authentication failed: {str(e)}', 'error')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/playlist/<playlist_id>')
def view_playlist(playlist_id):
    """View detailed playlist with tracks"""
    if 'token_info' not in session:
        return redirect(url_for('login'))
    
    try:
        sp = get_spotify_client(session['token_info'])
        playlist = sp.playlist(playlist_id)
        tracks = get_tracks_from_playlist(sp, playlist_id)
        
        return render_template('playlist_detail.html', 
                             playlist=playlist, 
                             tracks=tracks)
    except Exception as e:
        flash(f'Error loading playlist: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/liked-songs')
def view_liked_songs():
    """View detailed liked songs"""
    if 'token_info' not in session:
        return redirect(url_for('login'))
    
    try:
        sp = get_spotify_client(session['token_info'])
        liked_songs = get_user_liked_songs(sp, limit=100)
        
        return render_template('liked_songs_detail.html', 
                             liked_songs=liked_songs)
    except Exception as e:
        flash(f'Error loading liked songs: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/search')
def search():
    """Search page"""
    if 'token_info' not in session:
        return redirect(url_for('login'))
    
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'track')
    results = {}
    
    if query:
        try:
            sp = get_spotify_client(session['token_info'])
            results = search_spotify(sp, query, search_type, limit=20)
        except Exception as e:
            flash(f'Search error: {str(e)}', 'error')
    
    return render_template('search.html', 
                         query=query, 
                         search_type=search_type,
                         results=results)

@app.route('/api/audio-analysis/<track_id>')
def api_audio_analysis(track_id):
    """API endpoint to get audio analysis for a track"""
    if 'token_info' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        sp = get_spotify_client(session['token_info'])
        analysis = get_audio_analysis(sp, track_id)
        
        if analysis:
            # Extract key features for easier display
            track_data = analysis.get('track', {})
            features = {
                'tempo': track_data.get('tempo'),
                'key': track_data.get('key'),
                'mode': track_data.get('mode'),
                'time_signature': track_data.get('time_signature'),
                'duration': track_data.get('duration'),
                'loudness': track_data.get('loudness'),
                'energy': track_data.get('energy'),
                'danceability': track_data.get('danceability'),
                'valence': track_data.get('valence'),
                'acousticness': track_data.get('acousticness'),
                'instrumentalness': track_data.get('instrumentalness'),
                'speechiness': track_data.get('speechiness'),
            }
            return jsonify({'analysis': analysis, 'features': features})
        else:
            return jsonify({'error': 'Analysis not available'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/current-playback')
def api_current_playback():
    """API endpoint to get current playback info"""
    if 'token_info' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        sp = get_spotify_client(session['token_info'])
        playback = get_current_playback(sp)
        currently_playing = get_currently_playing(sp)
        
        return jsonify({
            'playback': playback,
            'currently_playing': currently_playing
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/album/<album_id>')
def api_album_details(album_id):
    """API endpoint to get album details"""
    if 'token_info' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        sp = get_spotify_client(session['token_info'])
        album = sp.album(album_id)
        return jsonify(album)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
