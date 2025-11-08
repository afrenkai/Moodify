# Genius API Inspector

A utility to fetch and inspect complete Genius API response objects.

## Usage

### Basic Usage

```bash
cd /home/artem/Projects/random/EmoRec
python -m backend.utils.genius_inspector
```

This will:
1. Search for "Blinding Lights The Weeknd"
2. Fetch detailed song information
3. Fetch artist information
4. Fetch artist's songs
5. Save all responses as JSON files
6. Print the structure of each response

### Custom Usage

```python
import asyncio
from backend.utils.genius_inspector import GeniusInspector

inspector = GeniusInspector()

# Search for a song
results = asyncio.run(inspector.get_search_results(
    "Song Name Artist Name",
    output_file="my_search.json"
))

# Get song details by ID
song = asyncio.run(inspector.get_song_details(
    song_id=123456,
    output_file="my_song.json"
))

# Get artist details
artist = asyncio.run(inspector.get_artist_details(
    artist_id=789,
    output_file="my_artist.json"
))

# Get artist's songs
songs = asyncio.run(inspector.get_artist_songs(
    artist_id=789,
    per_page=50,
    page=1,
    output_file="my_artist_songs.json"
))

# Print structure of response
inspector.print_structure(results, max_depth=3)
```

## Output Files

The script generates JSON files containing the complete API responses:

- `genius_search_example.json` - Search results with all metadata
- `genius_song_example.json` - Complete song details
- `genius_artist_example.json` - Artist information
- `genius_artist_songs_example.json` - List of artist's songs

## Available Methods

### `get_search_results(query, output_file)`
Search for songs/artists and save complete results.

### `get_song_details(song_id, output_file)`
Get all available information about a specific song.

### `get_artist_details(artist_id, output_file)`
Get complete artist information.

### `get_artist_songs(artist_id, per_page, page, output_file)`
Get paginated list of an artist's songs.

### `print_structure(data, max_depth)`
Print a tree structure of the API response showing all available fields.

## Requirements

- GENIUS_ACCESS_TOKEN must be set in your `.env` file
- aiohttp library (already installed)

## Example Output Structure

```
📋 API Response Structure:
============================================================
meta: dict
  status: int = 200
response: dict
  hits: list
    [0]: dict
      type: str = song
      result: dict
        id: int = 123456
        title: str = Song Title
        primary_artist: dict
          id: int = 789
          name: str = Artist Name
          url: str = https://genius.com/artists/...
        url: str = https://genius.com/...
        ... (100+ items total)
============================================================
```
