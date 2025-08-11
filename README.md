# 🎧 Spotify Organiser

A Flask web application that helps you organize your Spotify playlists by automatically categorizing tracks by genre and creating new organized playlists.

## Features

- **Spotify Authentication**: Secure OAuth login with Spotify
- **Playlist Analysis**: Analyze your playlists and see genre distribution
- **Genre-based Organization**: Automatically categorize tracks by genre
- **Create Genre Playlists**: Generate separate playlists for each genre
- **Custom Filtering**: Create custom playlists with selected genres
- **Duplicate Removal**: Remove duplicate tracks from playlists
- **Beautiful Web Interface**: Modern, Spotify-themed UI with responsive design

## Setup

### Prerequisites

- Python
- A Spotify account
- Spotify Developer App credentials

### 1. Spotify Developer Setup

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Create a new app
3. Note down your `Client ID` and `Client Secret`
4. Add `http://localhost:5000/callback` to your app's redirect URIs

### 2. Installation

1. Clone or download this repository
2. Install dependencies using uv (recommended) or pip:

```bash
# Using uv (recommended)
uv add spotipy flask python-dotenv

# Or using pip
pip install spotipy flask python-dotenv
```

### 3. Configuration

1. Create a `.env` file in the project root:

```bash
# Create .env file
touch .env
```

2. Add your Spotify credentials to the `.env` file:
```
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:5000/callback
SECRET_KEY=your_secret_key_here_change_this_to_something_secure
```

## Usage

### Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. Open your browser and go to `http://localhost:5000`

3. Click "Login with Spotify" and authorize the application

4. Explore your music library with genre information!

### Using the Features

#### Analyze a Playlist
- Click on any playlist from your dashboard
- View the genre distribution chart
- See detailed breakdown of tracks by genre

#### Create Genre Playlists
- In the playlist analysis page, click "Create Genre Playlists"
- The app will automatically create separate playlists for each genre with at least 5 tracks

#### Create Custom Filtered Playlists
- Select specific genres you want to include
- Give your playlist a custom name
- Click "Create Custom Playlist"

#### Remove Duplicates
- Click "Remove Duplicates" on any playlist analysis page
- The app will automatically remove duplicate tracks

## Project Structure

```
spotify-organiser/
├── app.py                      # Main Flask application with routes
├── utils/
│   ├── auth.py                # Spotify OAuth authentication
│   ├── spotify_api.py         # Spotify API interactions and data fetching
│   └── genre_cache.py         # Genre caching system for performance
├── templates/
│   ├── base.html              # Base template with navigation
│   ├── index.html             # Dashboard with playlists and liked songs
│   ├── login.html             # Spotify OAuth login page
│   ├── playlist_detail.html   # Detailed playlist view with tracks
│   ├── liked_songs_detail.html # Complete liked songs collection
│   └── search.html            # Search functionality (if implemented)
├── assets/
│   └── logo.png               # Application logo
├── genre_cache.json          # Local genre cache (auto-generated)
├── .env                      # Environment variables (create this)
└── README.md                 # This documentation
```

## Contributing

Contributions are welcome! Please feel free to submit issues, fork the repository, and create pull requests for improvements.

## License

This project is open source and available under the [MIT License](LICENSE).

---

*Built with ❤️ for music lovers who want to better organize and understand their Spotify libraries.*