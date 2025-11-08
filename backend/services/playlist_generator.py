import numpy as np
from typing import List, Optional, Dict, Any
import logging
import pandas as pd
from pathlib import Path

from backend.services.embedding_service import EmbeddingService
from backend.services.emotion_mapper import EmotionMapper
from backend.services.spotify_service import SpotifyService
from backend.services.async_genius_service import AsyncGeniusService
from backend.services.llm_search_query_generator import LLMSearchQueryGenerator
from backend.models.schemas import SongInput, SongResult, ArtistInput

logger = logging.getLogger(__name__)


class PlaylistGenerator:
    
    def __init__(
        self,
        embedding_service: EmbeddingService,
        emotion_mapper: EmotionMapper,
        spotify_service: Optional[SpotifyService] = None,
        genius_service: Optional[AsyncGeniusService] = None,
        songs_db_path: Optional[str] = None
    ):
        self.embedding_service = embedding_service
        self.emotion_mapper = emotion_mapper
        self.spotify_service = spotify_service
        self.genius_service = genius_service
        self.songs_db_path = songs_db_path
        self.songs_df: Optional[pd.DataFrame] = None
        
        self.query_generator = LLMSearchQueryGenerator(spotify_service=spotify_service)
        logger.info("Playlist generator using LLM-powered dynamic query generation with runtime genre filtering")
        
        if spotify_service and spotify_service.is_available():
            success = self.query_generator.load_genre_corpus_from_spotify()
            if success:
                logger.info("Genre corpus loaded from Spotify - using runtime filtering")
            else:
                logger.info("Could not load genre corpus - using predefined genres")
        
        self.has_llm_emotions = (
            hasattr(emotion_mapper, 'llm_emotion_service') and 
            emotion_mapper.llm_emotion_service is not None
        )
        
        if self.has_llm_emotions:
            logger.info("Playlist generator using LLM-based contextual emotion understanding")
        
        if songs_db_path:
            self._load_songs_database()
    
    def _load_songs_database(self):
        try:
            if self.songs_db_path.endswith('.csv'):
                self.songs_df = pd.read_csv(self.songs_db_path)
                logger.info(f"Loaded {len(self.songs_df)} songs from database")
            else:
                logger.warning(f"Unsupported database format: {self.songs_db_path}")
        except Exception as e:
            logger.error(f"Failed to load songs database: {e}")
    
    def generate_playlist(
        self,
        songs: Optional[List[SongInput]] = None,
        artists: Optional[List[ArtistInput]] = None,
        emotion: Optional[List[str]] = None,
        num_results: int = 10,
        enrich_with_lyrics: bool = True  # Changed default to True
    ) -> tuple[List[SongResult], np.ndarray, Dict[str, Any]]:
       
        if not songs and not artists and not emotion:
            raise ValueError("Must provide either songs, artists, or emotion")
        
        emotion_str = None
        emotion_list = None
        if emotion:
            if isinstance(emotion, list):
                emotion_list = emotion
                emotion_str = " ".join(emotion)
                logger.info(f"Processing multiple emotions: {emotion_list}")
            else:
                emotion_str = emotion
                emotion_list = [emotion]
        
        combined_embedding = self._compute_combined_embedding(songs, artists, emotion_str)
        
        emotion_features = None
        if emotion_list:
            emotion_features = self.emotion_mapper.get_feature_ranges(emotion_list)
        
        if self.spotify_service and self.spotify_service.is_available():
            playlist = self._query_songs_with_spotify(
                songs,
                artists,
                combined_embedding,
                emotion_str,
                emotion_features,
                num_results,
                enrich_with_lyrics
            )
        else:
            playlist = self._query_songs(
                combined_embedding,
                emotion_str,
                emotion_features,
                num_results
            )
        
        return playlist, combined_embedding, emotion_features
    
    def _compute_combined_embedding(
        self,
        songs: Optional[List[SongInput]],
        artists: Optional[List[ArtistInput]],
        emotion: Optional[str]
    ) -> np.ndarray:
        
        embeddings = []
        weights = []
        
        if songs:
            for song in songs:
                song_emb = self.embedding_service.encode_song(
                    song.song_name,
                    song.artist
                )
                embeddings.append(song_emb)
            
            song_weight = 0.7 if emotion else 1.0
            weights.extend([song_weight / len(songs)] * len(songs))
        
        if artists and self.spotify_service:
            logger.info(f"Fetching tracks (including collabs) for {len(artists)} artists")
            for artist in artists:
                if artist.spotify_id:
                    artist_id = artist.spotify_id
                    artist_name = artist.artist_name
                else:
                    artist_results = self.spotify_service.search_artist(artist.artist_name, limit=1)
                    if artist_results:
                        artist_id = artist_results[0]['spotify_id']
                        artist_name = artist_results[0]['name']
                    else:
                        logger.warning(f"Could not find artist: {artist.artist_name}")
                        continue
                
                # Get tracks including collaborations for this artist
                artist_tracks = self.spotify_service.get_artist_tracks_including_collabs(
                    artist_id, 
                    artist_name,
                    limit=8  # Get more tracks to better represent their style
                )
                
                if artist_tracks:
                    artist_track_embeddings = []
                    for track in artist_tracks:
                        track_emb = self.embedding_service.encode_song(
                            track['song_name'],
                            track['artist']
                        )
                        artist_track_embeddings.append(track_emb)
                    
                    artist_avg_emb = np.mean(artist_track_embeddings, axis=0)
                    embeddings.append(artist_avg_emb)
                    
                    artist_weight = 0.7 if emotion else 1.0
                    weights.append(artist_weight / len(artists))
                    logger.info(
                        f"Added embedding for artist {artist_name} based on "
                        f"{len(artist_tracks)} tracks (including collabs)"
                    )
        
        if emotion:
            emotion_emb = self.embedding_service.encode_emotion(emotion)
            embeddings.append(emotion_emb)
            
            emotion_weight = 0.3 if (songs or artists) else 1.0
            weights.append(emotion_weight)
        
        combined = self.embedding_service.combine_embeddings(embeddings, weights)
        
        logger.info(f"Combined {len(embeddings)} embeddings into single vector")
        return combined
    
    def _query_songs_with_spotify(
        self,
        songs: Optional[List[SongInput]],
        artists: Optional[List[ArtistInput]],
        query_embedding: np.ndarray,
        emotion: Optional[str],
        emotion_features: Optional[Dict],
        num_results: int,
        enrich_with_lyrics: bool = False
    ) -> List[SongResult]:
        """Query songs using Spotify API for real track data."""
        try:
            seed_track_ids = []
            if songs:
                for song in songs[:5]:
                    if song.spotify_id:
                        seed_track_ids.append(song.spotify_id)
                    else:
                        track = self.spotify_service.search_track(song.song_name, song.artist)
                        if track and track.get('spotify_id'):
                            seed_track_ids.append(track['spotify_id'])
            
            if artists:
                for artist in artists:
                    if len(seed_track_ids) >= 5:
                        break
                    
                    artist_id = artist.spotify_id
                    artist_name = artist.artist_name
                    if not artist_id:
                        artist_results = self.spotify_service.search_artist(artist.artist_name, limit=1)
                        if artist_results:
                            artist_id = artist_results[0]['spotify_id']
                            artist_name = artist_results[0]['name']
                    
                    if artist_id:
                        # Use tracks including collabs for seed track IDs
                        artist_tracks = self.spotify_service.get_artist_tracks_including_collabs(
                            artist_id, 
                            artist_name, 
                            limit=3
                        )
                        for track in artist_tracks[:2]:
                            if len(seed_track_ids) >= 5:
                                break
                            seed_track_ids.append(track['spotify_id'])
            
            if seed_track_ids or songs or artists:
                logger.info("Using LLM to generate search queries based on seed songs/artists and mood")
                search_queries = []
                
                if songs or artists:
                    if emotion:
                        logger.info(f"Using LLM to generate queries for emotion '{emotion}' with seed context")
                        emotion_queries = self.query_generator.generate_queries_for_emotion(
                            emotion,
                            num_queries=6
                        )
                        search_queries.extend(emotion_queries)
                    else:
                        logger.info("Using LLM to infer mood from seed songs/artists and generate queries")
                        seed_tuples = []
                        
                        if songs:
                            seed_tuples.extend([(s.song_name, s.artist) for s in songs])
                        
                        if artists:
                            for artist in artists:
                                artist_id = artist.spotify_id
                                artist_name = artist.artist_name
                                if not artist_id:
                                    artist_results = self.spotify_service.search_artist(artist.artist_name, limit=1)
                                    if artist_results:
                                        artist_id = artist_results[0]['spotify_id']
                                        artist_name = artist_results[0]['name']
                                
                                if artist_id:
                                    # Use tracks including collabs to better represent artist style
                                    artist_tracks = self.spotify_service.get_artist_tracks_including_collabs(
                                        artist_id, 
                                        artist_name, 
                                        limit=4
                                    )
                                    for track in artist_tracks[:2]:
                                        seed_tuples.append((track['song_name'], track['artist']))
                        
                        inferred_emotions = self.query_generator.infer_emotion_from_seeds(
                            seed_tuples,
                            top_k=2
                        )
                        if inferred_emotions:
                            logger.info(f"LLM inferred moods: {inferred_emotions}")
                        
                        seed_queries = self.query_generator.generate_queries_for_seed_songs(
                            seed_tuples,
                            num_queries=7
                        )
                        search_queries.extend(seed_queries)
                
                spotify_tracks = self.spotify_service.search_by_multiple_queries(
                    queries=search_queries,
                    limit_per_query=25  # Increased to get more candidates for embedding matching
                )
                
            elif emotion:
                logger.info(f"Using LLM to generate GENRE queries for emotion: '{emotion}' (semantic matching happens AFTER)")
                
                emotion_queries = self.query_generator.generate_queries_for_emotion(
                    emotion,
                    num_queries=8,
                    include_year=True,
                    use_runtime_filtering=True  # Enable runtime corpus filtering
                )
                
                logger.info(f"Using runtime-filtered genre queries: {emotion_queries[:3]}...")
                spotify_tracks = self.spotify_service.search_by_multiple_queries(
                    queries=emotion_queries,
                    limit_per_query=30
                )
            else:
                spotify_tracks = []
            
            if spotify_tracks:
                seen_track_ids = set()
                seen_track_combos = set()
                playlist = []
                
                for track_data in spotify_tracks:
                    track_id = track_data.get('spotify_id')
                    if track_id and track_id in seen_track_ids:
                        logger.debug(f"Skipping duplicate track ID: {track_data['song_name']}")
                        continue
                    if track_id:
                        seen_track_ids.add(track_id)
                    
                    track_combo = (
                        track_data['song_name'].lower().strip(),
                        track_data['artist'].lower().strip()
                    )
                    if track_combo in seen_track_combos:
                        logger.debug(f"Skipping duplicate combination: {track_data['song_name']} by {track_data['artist']}")
                        continue
                    seen_track_combos.add(track_combo)
                    
                    track_embedding = self.embedding_service.encode_song(
                        track_data['song_name'],
                        track_data['artist']
                    )
                    similarity_score = float(
                        self.embedding_service.compute_similarity(query_embedding, track_embedding)
                    )
                    
                    literal_match_penalty = 0.0
                    if emotion:
                        title_lower = track_data['song_name'].lower()
                        emotion_words = emotion.lower().split()
                        for emotion_word in emotion_words:
                            if len(emotion_word) > 3 and emotion_word in title_lower:
                                literal_match_penalty = 0.35
                                logger.debug(
                                    f"STRONG literal match penalty for '{track_data['song_name']}': "
                                    f"contains '{emotion_word}' - likely keyword stuffing"
                                )
                                break
                    
                    popularity_penalty = 0.0
                    popularity = track_data.get('popularity', 50)
                    if popularity > 5:
                        popularity_penalty = (popularity - 5) / 100 * 0.15
                        logger.debug(
                            f"Popularity penalty for '{track_data['song_name']}': "
                            f"pop={popularity}, penalty={popularity_penalty:.3f}"
                        )
                    
                    if self.has_llm_emotions and (emotion or songs):
                        try:
                            llm_service = self.emotion_mapper.llm_emotion_service
                            
                            song_text = f"{track_data['song_name']} by {track_data['artist']}"
                            
                            if emotion:
                                target_emotion_text = emotion
                            else:
                                target_emotion_text = "music with similar emotional vibe and mood"
                            
                            emotion_similarity = llm_service.compute_emotion_similarity(
                                song_text,
                                target_emotion_text,
                                context="song"
                            )
                            
                            similarity_score = (
                                similarity_score * 0.4 +
                                emotion_similarity * 0.6 -
                                literal_match_penalty -
                                popularity_penalty
                            )
                            logger.debug(
                                f"{track_data['song_name']}: emb={similarity_score:.3f}, "
                                f"emotion={emotion_similarity:.3f}, penalty={literal_match_penalty:.2f}, "
                                f"pop_penalty={popularity_penalty:.3f}, final={similarity_score:.3f}"
                            )
                        except Exception as e:
                            logger.debug(f"LLM emotion scoring failed for {track_data['song_name']}: {e}")
                            similarity_score -= (literal_match_penalty + popularity_penalty)
                    else:
                        similarity_score -= (literal_match_penalty + popularity_penalty)
                    
                    song_result = SongResult(
                        song_name=track_data['song_name'],
                        artist=track_data['artist'],
                        spotify_id=track_data.get('spotify_id'),
                        similarity_score=similarity_score,
                        album=track_data.get('album'),
                        preview_url=track_data.get('preview_url'),
                        external_url=track_data.get('external_url'),
                        album_image=track_data.get('album_image'),
                        popularity=track_data.get('popularity', 0),
                        duration_ms=track_data.get('duration_ms')
                    )
                    playlist.append(song_result)
                
                playlist.sort(key=lambda x: x.similarity_score, reverse=True)
                
                if len(playlist) > num_results:
                    final_playlist = []
                    artist_count = {}
                    max_per_artist = 2
                    
                    for track in playlist:
                        artist = track.artist.lower()
                        
                        if len(final_playlist) < num_results:
                            if artist_count.get(artist, 0) < max_per_artist:
                                final_playlist.append(track)
                                artist_count[artist] = artist_count.get(artist, 0) + 1
                    
                    if len(final_playlist) < num_results:
                        max_per_artist = 3  # Allow up to 3 per artist
                        for track in playlist:
                            if len(final_playlist) >= num_results:
                                break
                            artist = track.artist.lower()
                            if track not in final_playlist and artist_count.get(artist, 0) < max_per_artist:
                                final_playlist.append(track)
                                artist_count[artist] = artist_count.get(artist, 0) + 1
                    
                    playlist = final_playlist
                    unique_artists = len(set(t.artist.lower() for t in playlist))
                    logger.info(
                        f"Artist diversity: {len(playlist)} tracks from {unique_artists} different artists "
                        f"(max {max_per_artist} per artist)"
                    )
                
                # Get more candidates before lyrics filtering
                if enrich_with_lyrics and self.genius_service and self.genius_service.is_available():
                    primary_emotion = emotion.split()[0] if emotion else None
                    # Get 3x the needed results for lyrics filtering
                    playlist = self._enrich_with_genius_data(
                        playlist[:num_results * 3], 
                        primary_emotion,
                        filter_threshold=0.3  # Filter out songs with low lyric match
                    )
                
                logger.info(f"Generated Spotify playlist with {len(playlist)} songs")
                return playlist[:num_results]
            
            logger.warning("No tracks from Spotify, falling back to mock results")
            return self._generate_mock_results(num_results)
            
        except Exception as e:
            logger.error(f"Error querying Spotify: {e}", exc_info=True)
            return self._generate_mock_results(num_results)
    
    def _query_songs(
        self,
        query_embedding: np.ndarray,
        emotion: Optional[str],
        emotion_features: Optional[Dict],
        num_results: int
    ) -> List[SongResult]:
        
        if self.songs_df is None or self.songs_df.empty:
            logger.warning("No songs database loaded, returning mock results")
            return self._generate_mock_results(num_results)
        
       
        song_embeddings = np.array([
            eval(emb) if isinstance(emb, str) else emb
            for emb in self.songs_df['embedding']
        ])
        
        similarity_scores = self.embedding_service.batch_similarity(
            query_embedding,
            song_embeddings
        )
        
        results_df = self.songs_df.copy()
        results_df['similarity_score'] = similarity_scores
        
        results_df['combined_score'] = results_df['similarity_score']
        
        top_results = results_df.nlargest(num_results, 'combined_score')
        
        playlist = []
        for _, row in top_results.iterrows():
            song_result = SongResult(
                song_name=row['song_name'],
                artist=row['artist'],
                spotify_id=row.get('spotify_id'),
                similarity_score=float(row['similarity_score']),
                album=row.get('album'),
                preview_url=row.get('preview_url')
            )
            
            playlist.append(song_result)
        
        logger.info(f"Generated playlist with {len(playlist)} songs")
        return playlist
    
    def _enrich_with_genius_data(
        self, 
        playlist: List[SongResult], 
        target_emotion: Optional[str] = None,
        filter_threshold: float = 0.0
    ) -> List[SongResult]:
        """
        Enrich playlist with Genius lyrics emotional analysis and RE-RANK by lyrics score.
        
        This is the primary ranking mechanism - lyrics emotion > embeddings.
        Now also FILTERS OUT songs that don't match the mood based on lyrics.
        
        Args:
            playlist: List of SongResult objects
            target_emotion: The emotion we're matching against
            filter_threshold: Minimum lyrics score to keep song (0.0-1.0)
            
        Returns:
            Re-ranked and filtered playlist based primarily on lyrics emotional match
        """
        if not self.genius_service or not self.genius_service.is_available():
            logger.info("Genius service not available, using embedding-only ranking")
            return playlist
        
        try:
            songs_to_search = [(song.song_name, song.artist) for song in playlist]
            
            logger.info(f"Fetching lyrics for {len(songs_to_search)} songs to analyze true mood...")
            genius_results = self.genius_service.batch_get_emotional_profiles_sync(
                songs_to_search,
                target_emotion=target_emotion,
                max_concurrent=5  # Increased for faster processing
            )
            
            lyrics_scored_count = 0
            filtered_count = 0
            
            for song in playlist:
                key = f"{song.song_name}|{song.artist}"
                if key in genius_results and genius_results[key]:
                    genius_data = genius_results[key]
                    
                    song.genius_url = genius_data.get('genius_url')
                    
                    lyrics_score = genius_data.get('emotion_match_score', 0.0)
                    dominant_emotion = genius_data.get('dominant_emotion')
                    emotional_keywords = genius_data.get('emotional_keywords', {})
                    
                    # Store lyrics metadata for debugging
                    song.lyrics_emotion = dominant_emotion
                    song.lyrics_score = lyrics_score
                    
                    if lyrics_score > 0:
                        original_embedding_score = song.similarity_score
                        
                        # More aggressive weighting: 85% lyrics, 15% embeddings
                        # Lyrics are the ground truth for mood!
                        song.similarity_score = (
                            lyrics_score * 0.85 +
                            original_embedding_score * 0.15
                        )
                        
                        # Additional boost if dominant emotion matches target
                        if target_emotion and dominant_emotion:
                            if dominant_emotion == target_emotion.lower():
                                song.similarity_score += 0.1
                                logger.debug(f"Boosted {song.song_name} - dominant emotion matches!")
                        
                        lyrics_scored_count += 1
                        
                        logger.debug(
                            f"{song.song_name}: lyrics={lyrics_score:.3f} (mood: {dominant_emotion}), "
                            f"embedding={original_embedding_score:.3f}, "
                            f"final={song.similarity_score:.3f}, "
                            f"keywords={list(emotional_keywords.keys())[:3]}"
                        )
                    else:
                        # No lyrics match - penalize heavily
                        song.similarity_score *= 0.5
                        logger.debug(f"{song.song_name}: No lyrics emotional match - penalized")
            
            # FILTER out songs below threshold (mood mismatch)
            if filter_threshold > 0.0:
                original_length = len(playlist)
                playlist = [
                    song for song in playlist 
                    if hasattr(song, 'lyrics_score') and song.lyrics_score >= filter_threshold
                    or not hasattr(song, 'lyrics_score')  # Keep songs without lyrics data
                ]
                filtered_count = original_length - len(playlist)
                
                if filtered_count > 0:
                    logger.info(
                        f"Filtered out {filtered_count} songs with low lyrics match "
                        f"(threshold={filter_threshold})"
                    )
            
            # Re-rank after scoring
            playlist.sort(key=lambda x: x.similarity_score, reverse=True)
            
            logger.info(
                f"Re-ranked playlist with lyrics analysis: {lyrics_scored_count}/{len(songs_to_search)} "
                f"songs scored (85% lyrics, 15% embeddings), {filtered_count} filtered out"
            )
            
        except Exception as e:
            logger.warning(f"Could not enrich with Genius data: {e}", exc_info=True)
        
        return playlist
    
    def _generate_mock_results(self, num_results: int) -> List[SongResult]:
        mock_songs = [
            ("Bohemian Rhapsody", "Queen"),
            ("Imagine", "John Lennon"),
            ("Hotel California", "Eagles"),
            ("Stairway to Heaven", "Led Zeppelin"),
            ("Hey Jude", "The Beatles"),
            ("Smells Like Teen Spirit", "Nirvana"),
            ("Billie Jean", "Michael Jackson"),
            ("Sweet Child O' Mine", "Guns N' Roses"),
            ("Come Together", "The Beatles"),
            ("Purple Haze", "Jimi Hendrix"),
        ]
        
        results = []
        for i, (song_name, artist) in enumerate(mock_songs[:num_results]):
            results.append(SongResult(
                song_name=song_name,
                artist=artist,
                similarity_score=0.9 - (i * 0.05),
            ))
        
        return results
