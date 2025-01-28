# Album-Playlist-Creator
Create a customized album or playlist (Eg: Oldies Playlist, Underground Hiphop Playlist e.t.c) with various artists from a folder.

How To Install and Run
* Transfer all your songs to one folder
* python3 -m pip install -r requirements.txt
* python3 playlist_creator.py

Key Features Added:
Logging: Added logging to track progress and errors.

Error Handling: Robust error handling for API requests, file operations, and user input.

Configurability: Allowed the user to choose between Deezer and Spotify for metadata fetching. Used environment variables for Spotify API credentials.

Metadata and Album Art: Fetched and saved album art and metadata for each album.

User Interaction: Prompted the user for input paths and service choice.

Playlist and Album Copying: Created .m3u playlists and copied albums with metadata and album art.

APC Version 2.0
