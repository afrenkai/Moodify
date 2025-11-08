import argparse
import base64
import requests
from pathlib import Path
from PIL import Image
from io import BytesIO
import sys


def decode_and_show_image(base64_string: str, save_path: str = None):

    try:
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        if save_path:
            image.save(save_path)
            print(f"Image saved to: {save_path}")
        try:
            image.show()
            print("Image displayed")
        except Exception as e:
            print(f"Could not display image automatically: {e}")
            print("  Image was decoded successfully. Try saving it instead.")
        
        return image
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None


def fetch_and_display_collage(
    emotion: str = None,
    song_name: str = None,
    artist: str = None,
    num_results: int = 5,
    save_path: str = None,
    api_url: str = "http://localhost:8000"
):

    payload = {
        "num_results": num_results,
        "include_collage": True
    }
    
    if emotion:
        payload["emotion"] = emotion
    
    if song_name and artist:
        payload["songs"] = [
            {"song_name": song_name, "artist": artist}
        ]
    
    if not emotion and not (song_name and artist):
        print("Error: Must provide either --emotion or both --song and --artist")
        return None

    print(f"Fetching mood collage from {api_url}...")
    if emotion:
        print(f"  Emotion: {emotion}")
    if song_name:
        print(f"  Song: {song_name} by {artist}")
    
    try:
        response = requests.post(
            f"{api_url}/api/v1/generate-playlist",
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"✗ API Error ({response.status_code}): {response.text}")
            return None
        
        data = response.json()

        if not data.get("mood_collage"):
            print("No mood collage in response")
            return None
        
        collage = data["mood_collage"]
        print(f"Received mood collage ({collage['width']}x{collage['height']})")
        print(f"  Dominant colors: {', '.join(collage['dominant_colors'][:3])}")
        

        print(f"\nGenerated playlist with {len(data['playlist'])} songs:")
        for i, song in enumerate(data['playlist'][:5], 1):
            print(f"  {i}. {song['song_name']} by {song['artist']} ({song['similarity_score']:.3f})")
        

        print("\nDecoding image...")
        image = decode_and_show_image(collage["image_base64"], save_path)
        
        return image
        
    except requests.exceptions.ConnectionError:
        print(f"Could not connect to API at {api_url}")
        print("  Make sure the server is running with: python run.py")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and display mood collage from EmoRec API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from emotion
  python show_collage.py "happy"
  python show_collage.py "melancholic but hopeful"
  
  # Generate from song
  python show_collage.py --song "Bohemian Rhapsody" --artist "Queen"
  
  # Save to file
  python show_collage.py "calm" --save my_mood.png
  
  # Combine emotion and song
  python show_collage.py "energetic" --song "Don't Stop Me Now" --artist "Queen"
  
  # Custom API URL
  python show_collage.py "sad" --api-url http://example.com:8000
        """
    )
    
    parser.add_argument(
        "emotion",
        nargs="?",
        help="Emotion descriptor (e.g., 'happy', 'melancholic but hopeful')"
    )
    parser.add_argument(
        "--song",
        help="Song name for song-based generation"
    )
    parser.add_argument(
        "--artist",
        help="Artist name (required with --song)"
    )
    parser.add_argument(
        "--num-results",
        type=int,
        default=5,
        help="Number of playlist results (default: 5)"
    )
    parser.add_argument(
        "--save",
        help="Path to save the image (e.g., 'mood.png')"
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    if not args.emotion and not (args.song and args.artist):
        parser.print_help()
        print("\nError: Must provide either emotion or both --song and --artist")
        sys.exit(1)
    
    if args.song and not args.artist:
        print("Error: --artist is required when using --song")
        sys.exit(1)
    
    image = fetch_and_display_collage(
        emotion=args.emotion,
        song_name=args.song,
        artist=args.artist,
        num_results=args.num_results,
        save_path=args.save,
        api_url=args.api_url
    )
    
    if image:
        print("\nSuccess!")
    else:
        print("\nFailed to fetch or display collage")
        sys.exit(1)


if __name__ == "__main__":
    main()
