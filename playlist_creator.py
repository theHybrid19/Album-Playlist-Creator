import os
import shutil
import requests
import logging
from pathlib import Path
from PIL import Image
from io import BytesIO

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class PlaylistCreator:
    def __init__(self, music_dir, playlist_dir, output_dir, service="deezer"):
        self.music_dir = Path(music_dir)
        self.playlist_dir = Path(playlist_dir)
        self.output_dir = Path(output_dir)
        self.supported_formats = ['.mp3', '.wav', '.flac', '.m4a']
        self.service = service
        self.deezer_api_url = "https://api.deezer.com/search"
        self.spotify_api_url = "https://api.spotify.com/v1/search"
        self.spotify_token = self.get_spotify_token() if service == "spotify" else None

    def validate_directories(self):
        """Ensure the music, playlist, and output directories exist."""
        if not self.music_dir.exists():
            raise FileNotFoundError(f"Music directory not found: {self.music_dir}")
        if not self.playlist_dir.exists():
            self.playlist_dir.mkdir(parents=True, exist_ok=True)
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_albums(self):
        """Scan the music directory and organize songs into albums."""
        albums = {}
        for root, _, files in os.walk(self.music_dir):
            for file in files:
                if any(file.lower().endswith(ext) for ext in self.supported_formats):
                    album_name = Path(root).name
                    if album_name not in albums:
                        albums[album_name] = []
                    albums[album_name].append(Path(root) / file)
        return albums

    def get_spotify_token(self):
        """Get Spotify API token using client credentials flow."""
        client_id = os.getenv("SPOTIFY_CLIENT_ID", "your_spotify_client_id")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET", "your_spotify_client_secret")
        if client_id == "your_spotify_client_id" or client_secret == "your_spotify_client_secret":
            logging.warning("Spotify client ID or secret not set. Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET.")
            return None

        auth_url = "https://accounts.spotify.com/api/token"
        auth_response = requests.post(
            auth_url,
            data={"grant_type": "client_credentials"},
            auth=(client_id, client_secret),
        )
        auth_response.raise_for_status()
        return auth_response.json()["access_token"]

    def fetch_album_metadata(self, album_name):
        """Fetch album metadata (art, artist, release year, genre) using Deezer or Spotify API."""
        metadata = {"art": None, "artist": None, "release_year": None, "genre": None}

        try:
            if self.service == "deezer":
                response = requests.get(self.deezer_api_url, params={"q": album_name, "type": "album"})
                data = response.json()
                if data.get("data"):
                    album_data = data["data"][0]
                    metadata["art"] = album_data.get("cover_big")
                    metadata["artist"] = album_data.get("artist", {}).get("name")
                    metadata["release_year"] = album_data.get("release_date", "").split("-")[0]
                    metadata["genre"] = album_data.get("genres", {}).get("data", [{}])[0].get("name")

            elif self.service == "spotify" and self.spotify_token:
                headers = {"Authorization": f"Bearer {self.spotify_token}"}
                response = requests.get(
                    self.spotify_api_url, headers=headers, params={"q": album_name, "type": "album"}
                )
                data = response.json()
                if data.get("albums", {}).get("items"):
                    album_data = data["albums"]["items"][0]
                    metadata["art"] = album_data.get("images", [{}])[0].get("url")
                    metadata["artist"] = album_data.get("artists", [{}])[0].get("name")
                    metadata["release_year"] = album_data.get("release_date", "").split("-")[0]
                    metadata["genre"] = album_data.get("genres", [""])[0]

        except Exception as e:
            logging.error(f"Error fetching metadata for {album_name}: {e}")

        return metadata

    def download_album_art(self, album_name, output_dir):
        """Download and save album art for a given album."""
        metadata = self.fetch_album_metadata(album_name)
        if metadata["art"]:
            try:
                response = requests.get(metadata["art"])
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    image_path = output_dir / f"{album_name}.jpg"
                    image.save(image_path)
                    logging.info(f"Downloaded album art for: {album_name} at {image_path}")
                    return image_path
            except Exception as e:
                logging.error(f"Error downloading album art for {album_name}: {e}")
        logging.warning(f"No album art found for: {album_name}")
        return None

    def save_metadata(self, album_name, output_dir, metadata):
        """Save album metadata to a text file."""
        metadata_path = output_dir / f"{album_name}_metadata.txt"
        try:
            with open(metadata_path, "w", encoding="utf-8") as metadata_file:
                metadata_file.write(f"Album: {album_name}\n")
                metadata_file.write(f"Artist: {metadata['artist']}\n")
                metadata_file.write(f"Release Year: {metadata['release_year']}\n")
                metadata_file.write(f"Genre: {metadata['genre']}\n")
            logging.info(f"Saved metadata for: {album_name} at {metadata_path}")
        except Exception as e:
            logging.error(f"Error saving metadata for {album_name}: {e}")

    def create_playlists(self):
        """Create playlists for each album."""
        self.validate_directories()
        albums = self.get_albums()

        for album, songs in albums.items():
            playlist_path = self.playlist_dir / f"{album}.m3u"
            try:
                with open(playlist_path, 'w', encoding='utf-8') as playlist_file:
                    for song in songs:
                        playlist_file.write(f"{song}\n")
                logging.info(f"Created playlist for album: {album} at {playlist_path}")
            except Exception as e:
                logging.error(f"Error creating playlist for {album}: {e}")

    def copy_albums(self):
        """Copy albums to a new directory, organized by album name, and add album art and metadata."""
        self.validate_directories()
        albums = self.get_albums()

        for album, songs in albums.items():
            album_dir = self.output_dir / album
            album_dir.mkdir(exist_ok=True)
            for song in songs:
                try:
                    shutil.copy(song, album_dir / song.name)
                except Exception as e:
                    logging.error(f"Error copying song {song} for album {album}: {e}")
            # Download and add album art
            self.download_album_art(album, album_dir)
            # Fetch and save metadata
            metadata = self.fetch_album_metadata(album)
            self.save_metadata(album, album_dir, metadata)
            logging.info(f"Copied album: {album} to {album_dir}")

if __name__ == "__main__":
    # Example usage
    music_directory = input("Enter the path to your music directory: ")
    playlist_directory = input("Enter the path to save playlists: ")
    output_directory = input("Enter the path to copy organized albums: ")
    service = input("Choose metadata service (deezer/spotify): ").lower()

    if service not in ["deezer", "spotify"]:
        logging.error("Invalid service choice. Defaulting to Deezer.")
        service = "deezer"

    creator = PlaylistCreator(music_directory, playlist_directory, output_directory, service)
    creator.create_playlists()
    creator.copy_albums()
