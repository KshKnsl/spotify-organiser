from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
from utils.auth import get_spotify_oauth, get_spotify_client
from utils.spotify_api import (
    get_user_playlists, get_user_liked_songs,
    get_current_playback, get_tracks_from_playlist
)
from utils.genre_cache import enrich_tracks_with_cached_genres

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
        
        # Enrich the liked songs preview with genre information
        enriched_liked_songs = enrich_tracks_with_cached_genres(sp, liked_songs)
        
        return render_template('index.html', 
                             user=user_info, 
                             playlists=playlists,
                             liked_songs=enriched_liked_songs,
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
        user_info = sp.current_user()
        playlist = sp.playlist(playlist_id)
        tracks = get_tracks_from_playlist(sp, playlist_id)
        
        # Enrich tracks with genre information
        enriched_tracks = enrich_tracks_with_cached_genres(sp, tracks)
        
        return render_template('playlist_detail.html', 
                             user=user_info,
                             playlist=playlist, 
                             tracks=enriched_tracks)
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
        user_info = sp.current_user()
        liked_songs = get_user_liked_songs(sp)  # Fetch all liked songs
        
        # Enrich tracks with genre information
        enriched_liked_songs = enrich_tracks_with_cached_genres(sp, liked_songs)
        
        return render_template('liked_songs_detail.html', 
                             user=user_info,
                             liked_songs=enriched_liked_songs)
    except Exception as e:
        flash(f'Error loading liked songs: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/current-playback')
def api_current_playback():
    """API endpoint to get current playback info"""
    if 'token_info' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        sp = get_spotify_client(session['token_info'])
        playback = get_current_playback(sp)
        
        return jsonify({
            'playback': playback
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
