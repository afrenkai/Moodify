import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.services.embedding_service import EmbeddingService
from backend.services.emotion_mapper import EmotionMapper
from backend.services.spotify_service import SpotifyService
from backend.services.playlist_generator import PlaylistGenerator

def test_emotion_queries():

    embedding_service = EmbeddingService()
    emotion_mapper = EmotionMapper(use_llm=True)
    spotify_service = SpotifyService()
    
    if not spotify_service.is_available():
        print("Spotify service not available. Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET")
        return
    
    playlist_generator = PlaylistGenerator(
        embedding_service=embedding_service,
        emotion_mapper=emotion_mapper,
        spotify_service=spotify_service
    )
    
    test_emotions = ["happy", "sad", "energetic", "calm"]
    
    for emotion in test_emotions:
        print(f"\n{'=' * 70}")
        print(f"🎭 Emotion: {emotion.upper()}")
        print(f"{'=' * 70}")
        
        genre_queries = playlist_generator._get_genre_queries_for_emotion(emotion)
        print(f"\nSearch Strategy (genre-based, not literal):")
        for i, query in enumerate(genre_queries, 1):
            print(f"   {i}. {query}")
        

        try:
            playlist, _, _ = playlist_generator.generate_playlist(
                emotion=[emotion],
                num_results=10,
                enrich_with_lyrics=False  
            )
            
            print(f"\n📋 Top 10 Results (score = 70% contextual emotion + 30% title similarity):")
            print(f"{'Rank':<6} {'Score':<8} {'Title':<40} {'Artist':<30}")
            print("-" * 90)
            
            for i, song in enumerate(playlist, 1):
                title = song.song_name[:37] + "..." if len(song.song_name) > 40 else song.song_name
                artist = song.artist[:27] + "..." if len(song.artist) > 30 else song.artist
                
                has_literal = emotion.lower() in song.song_name.lower()
                marker = "⚠️" if has_literal else "✓"
                
                print(f"{marker} {i:<4} {song.similarity_score:.4f}   {title:<40} {artist:<30}")
            
            literal_matches = sum(1 for song in playlist if emotion.lower() in song.song_name.lower())
            print(f"\n📊 Literal matches (title contains '{emotion}'): {literal_matches}/10")
            
            if literal_matches <= 2:
                print(f"GOOD: Search is semantic, not literal!")
            else:
                print(f"WARNING: Too many literal matches ({literal_matches}/10)")
            
        except Exception as e:
            print(f"Error generating playlist: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 70}")
    print("Test Complete!")
    print(f"{'=' * 70}\n")

if __name__ == "__main__":
    test_emotion_queries()
