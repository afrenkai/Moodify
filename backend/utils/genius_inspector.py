import os
import json
import asyncio
import aiohttp
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class GeniusInspector:
    
    def __init__(self):
        self.access_token = os.getenv('GENIUS_ACCESS_TOKEN')
        self.base_url = "https://api.genius.com"
        
        if not self.access_token:
            raise ValueError("GENIUS_ACCESS_TOKEN not found in environment")
    
    async def get_search_results(
        self,
        query: str,
        output_file: str = "genius_search_results.json"
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/search"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {"q": query}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    raise Exception(f"API returned status {response.status}")
                
                data = await response.json()
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Search results saved to: {output_file}")
                print(f"   Found {len(data.get('response', {}).get('hits', []))} hits")
                
                return data
    
    async def get_song_details(
        self,
        song_id: int,
        output_file: str = "genius_song_details.json"
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/songs/{song_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"API returned status {response.status}")
                
                data = await response.json()
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Song details saved to: {output_file}")
                
                return data
    
    async def get_artist_details(
        self,
        artist_id: int,
        output_file: str = "genius_artist_details.json"
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/artists/{artist_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"API returned status {response.status}")
                
                data = await response.json()
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Artist details saved to: {output_file}")
                
                return data
    
    async def get_artist_songs(
        self,
        artist_id: int,
        per_page: int = 20,
        page: int = 1,
        output_file: str = "genius_artist_songs.json"
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/artists/{artist_id}/songs"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {
            "per_page": per_page,
            "page": page,
            "sort": "popularity"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    raise Exception(f"API returned status {response.status}")
                
                data = await response.json()
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Artist songs saved to: {output_file}")
                print(f"   Got {len(data.get('response', {}).get('songs', []))} songs")
                
                return data
    
    def print_structure(self, data: Dict[str, Any], max_depth: int = 3):
       def _print_recursive(obj, depth=0, prefix=""):
            if depth > max_depth:
                return
            
            indent = "  " * depth
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, (dict, list)):
                        print(f"{indent}{prefix}{key}: {type(value).__name__}")
                        _print_recursive(value, depth + 1, "")
                    else:
                        value_preview = str(value)[:50]
                        print(f"{indent}{prefix}{key}: {type(value).__name__} = {value_preview}")
            
            elif isinstance(obj, list):
                if len(obj) > 0:
                    print(f"{indent}[0]: {type(obj[0]).__name__}")
                    _print_recursive(obj[0], depth + 1, "")
                    if len(obj) > 1:
                        print(f"{indent}... ({len(obj)} items total)")
        
 
async def main():
    inspector = GeniusInspector()
    
    print("Genius API Inspector")

    print("\n Searching for 'Blinding Lights The Weeknd'...")
    search_results = await inspector.get_search_results(
        "Blinding Lights The Weeknd",
        output_file="genius_search_example.json"
    )
    inspector.print_structure(search_results)
    
    hits = search_results.get('response', {}).get('hits', [])
    if hits:
        song_id = hits[0]['result']['id']
        
        print(f"\n2️⃣  Fetching song details for ID {song_id}...")
        song_details = await inspector.get_song_details(
            song_id,
            output_file="genius_song_example.json"
        )
        inspector.print_structure(song_details)
        
        artist_id = song_details.get('response', {}).get('song', {}).get('primary_artist', {}).get('id')
        
        if artist_id:
            print(f"\nFetching artist details for ID {artist_id}...")
            artist_details = await inspector.get_artist_details(
                artist_id,
                output_file="genius_artist_example.json"
            )
            
            print(f"\nFetching artist's songs...")
            artist_songs = await inspector.get_artist_songs(
                artist_id,
                per_page=10,
                output_file="genius_artist_songs_example.json"
            )
    
if __name__ == "__main__":
    asyncio.run(main())
    
    # Custom usage examples:
    # 
    # inspector = GeniusInspector()
    # 
    # # Search for any song
    # results = asyncio.run(inspector.get_search_results("your query here"))
    # 
    # # Get specific song by ID
    # song = asyncio.run(inspector.get_song_details(12345))
    # 
    # # Get artist info
    # artist = asyncio.run(inspector.get_artist_details(67890))
    # 
    # # Get artist's songs
    # songs = asyncio.run(inspector.get_artist_songs(67890, per_page=50))
