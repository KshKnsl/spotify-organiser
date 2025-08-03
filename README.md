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

## Screenshots

![Dashboard](assets/dashboard.png)
![Analysis](assets/analysis.png)

## Setup

### Prerequisites

- Python 3.9 or higher
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

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your Spotify credentials:
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

4. You'll see your profile and all your playlists

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
├── app.py                 # Main Flask application
├── utils/
│   ├── auth.py           # Spotify authentication
│   ├── spotify_api.py    # Spotify API interactions
│   ├── genre_sorter.py   # Genre categorization logic
│   └── playlist_creator.py # Playlist creation utilities
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Dashboard
│   └── analyze.html      # Playlist analysis page
├── assets/
│   └── logo.png          # App logo
├── .env.example          # Environment variables template
├── .env                  # Your environment variables (not in git)
├── pyproject.toml        # Project dependencies
└── README.md            # This file
```

## API Endpoints

- `GET /` - Dashboard with user profile and playlists
- `GET /login` - Initiate Spotify OAuth
- `GET /callback` - OAuth callback handler
- `GET /logout` - Logout and clear session
- `GET /analyze_playlist/<id>` - Analyze a specific playlist
- `POST /create_genre_playlists/<id>` - Create genre-based playlists
- `POST /filter_genre` - Create filtered playlist
- `POST /remove_duplicates/<id>` - Remove duplicate tracks
- `GET /api/playlist/<id>/genres` - JSON API for genre data

## How It Works

1. **Authentication**: Uses Spotify's OAuth 2.0 for secure authentication
2. **Genre Detection**: Analyzes track artists to determine genres using Spotify's genre data
3. **Categorization**: Groups tracks by their primary genres
4. **Playlist Creation**: Uses Spotify's API to create new playlists and add tracks

## Limitations

- Genre detection depends on Spotify's genre data for artists
- Some tracks may not have clear genre information
- Rate limiting applies based on Spotify's API limits
- Requires active internet connection

## Troubleshooting

### "Authentication failed"
- Check your Spotify Client ID and Secret
- Ensure redirect URI matches exactly: `http://localhost:5000/callback`
- Make sure your Spotify app is not in development mode restrictions

### "No genres found"
- Some tracks may not have genre information in Spotify's database
- This is normal for very new releases or obscure artists

### App running slowly
- Genre analysis can take time for large playlists
- The app processes tracks in batches to respect API limits

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the [MIT License](LICENSE).
