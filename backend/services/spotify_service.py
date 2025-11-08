import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List, Optional, Dict, Any
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()


class SpotifyService:
    """Service for interacting with Spotify API using Spotipy."""
    
    def __init__(self):
        """Initialize Spotify client with credentials from environment."""
        try:
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                logger.warning("Spotify credentials not found in environment variables")
                self.spotify = None
                return
            
            auth_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            self.spotify = spotipy.Spotify(auth_manager=auth_manager)
            logger.info("Spotify service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Spotify service: {e}")
            self.spotify = None
    
    def is_available(self) -> bool:
        """Check if Spotify service is available."""
        return self.spotify is not None
    
    def search_track(
        self,
        song_name: str,
        artist: Optional[str] = None,
        limit: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        Search for a track on Spotify.
        
        Args:
            song_name: Name of the song
            artist: Optional artist name for more accurate search
            limit: Number of results to return
            
        Returns:
            Track information or None if not found
        """
        if not self.is_available():
            logger.warning("Spotify service not available")
            return None
        
        try:
            query = f"track:{song_name}"
            if artist:
                query += f" artist:{artist}"
            
            results = self.spotify.search(q=query, type='track', limit=limit)
            
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                return self._format_track(track)
            
            logger.info(f"No track found for: {song_name} by {artist}")
            return None
            
        except Exception as e:
            logger.error(f"Error searching for track: {e}")
            return None
    
    def get_track_by_id(self, track_id: str) -> Optional[Dict[str, Any]]:
        """
        Get track information by Spotify ID.
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Track information or None if not found
        """
        if not self.is_available():
            return None
        
        try:
            track = self.spotify.track(track_id)
            return self._format_track(track)
        except Exception as e:
            logger.error(f"Error getting track by ID: {e}")
            return None
    
    def get_recommendations(
        self,
        seed_tracks: Optional[List[str]] = None,
        seed_artists: Optional[List[str]] = None,
        seed_genres: Optional[List[str]] = None,
        limit: int = 20,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Get track recommendations based on seeds.
        
        NOTE: Spotify recommendations API has been deprecated and is no longer available.
        This method now returns an empty list. Use search_by_multiple_queries instead.
        
        Args:
            seed_tracks: List of track IDs (max 5)
            seed_artists: List of artist IDs (max 5)
            seed_genres: List of genres (max 5)
            limit: Number of recommendations
            **kwargs: Additional parameters (ignored)
            
        Returns:
            Empty list (API deprecated)
        """
        logger.info("Recommendations API is deprecated, use search-based methods instead")
        return []
    
    def search_tracks_by_emotion(
        self,
        emotion: str,
        num_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for tracks matching an emotion using Spotify search.
        
        Args:
            emotion: Emotion keyword
            num_results: Number of results
            
        Returns:
            List of matching tracks
        """
        if not self.is_available():
            return []
        
        try:
            # Search using emotion as keyword
            results = self.spotify.search(
                q=emotion,
                type='track',
                limit=min(num_results, 50)
            )
            
            tracks = []
            for track in results['tracks']['items']:
                tracks.append(self._format_track(track))
            
            return tracks
            
        except Exception as e:
            logger.error(f"Error searching tracks by emotion: {e}")
            return []
    
    def search_by_multiple_queries(
        self,
        queries: List[str],
        limit_per_query: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for tracks using multiple queries and combine results.
        
        Args:
            queries: List of search queries
            limit_per_query: Maximum results per query
            
        Returns:
            Combined list of unique tracks
        """
        if not self.is_available():
            return []
        
        try:
            all_tracks = []
            seen_ids = set()
            
            for query in queries:
                results = self.spotify.search(
                    q=query,
                    type='track',
                    limit=min(limit_per_query, 50)
                )
                
                for track in results['tracks']['items']:
                    track_id = track['id']
                    if track_id not in seen_ids:
                        seen_ids.add(track_id)
                        all_tracks.append(self._format_track(track))
            
            logger.info(f"Found {len(all_tracks)} unique tracks from {len(queries)} queries")
            return all_tracks
            
        except Exception as e:
            logger.error(f"Error searching by multiple queries: {e}")
            return []
    
    def get_album_tracks(
        self,
        album_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all tracks from a Spotify album.
        
        Args:
            album_id: Spotify album ID
            
        Returns:
            List of tracks from the album
        """
        if not self.is_available():
            return []
        
        try:
            results = self.spotify.album_tracks(album_id)
            tracks = []
            
            for track in results['items']:
                # Note: album_tracks returns simplified track objects
                # We need to get full track info for complete data
                full_track = self.spotify.track(track['id'])
                tracks.append(self._format_track(full_track))
            
            logger.info(f"Got {len(tracks)} tracks from album {album_id}")
            return tracks
            
        except Exception as e:
            logger.error(f"Error getting album tracks: {e}")
            return []
    
    def search_albums_by_query(
        self,
        query: str,
        limit: int = 10
    ) -> List[str]:
        """
        Search for albums and return their IDs.
        
        Args:
            query: Search query
            limit: Number of albums to return
            
        Returns:
            List of album IDs
        """
        if not self.is_available():
            return []
        
        try:
            results = self.spotify.search(
                q=query,
                type='album',
                limit=min(limit, 50)
            )
            
            album_ids = [album['id'] for album in results['albums']['items']]
            logger.info(f"Found {len(album_ids)} albums for query: {query}")
            return album_ids
            
        except Exception as e:
            logger.error(f"Error searching albums: {e}")
            return []
    
    def get_tracks_with_features(
        self,
        track_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Get multiple tracks.
        Handles batching to avoid Spotify's 100 ID limit.
        
        Args:
            track_ids: List of Spotify track IDs
            
        Returns:
            List of tracks
        """
        if not self.is_available():
            return []
        
        try:
            # Spotify API limits to 50-100 IDs per request, use 50 to be safe
            batch_size = 50
            all_results = []
            
            for i in range(0, len(track_ids), batch_size):
                batch_ids = track_ids[i:i + batch_size]
                
                # Get tracks info
                tracks = self.spotify.tracks(batch_ids)
                
                for track in tracks['tracks']:
                    if track:
                        track_data = self._format_track(track)
                        all_results.append(track_data)
            
            return all_results
            
        except Exception as e:
            logger.error(f"Error getting tracks: {e}")
            return []
    
    def _format_track(self, track: Dict[str, Any]) -> Dict[str, Any]:
        """Format Spotify track data to our schema."""
        artists = ', '.join([artist['name'] for artist in track['artists']])
        
        return {
            'spotify_id': track['id'],
            'song_name': track['name'],
            'artist': artists,
            'album': track['album']['name'],
            'preview_url': track.get('preview_url'),
            'external_url': track['external_urls']['spotify'],
            'duration_ms': track['duration_ms'],
            'popularity': track.get('popularity', 0),
            'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None
        }
