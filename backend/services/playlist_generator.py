import numpy as np
from typing import List, Optional, Dict, Any
import logging
import pandas as pd
from pathlib import Path

from backend.services.embedding_service import EmbeddingService
from backend.services.emotion_mapper import EmotionMapper
from backend.models.schemas import SongInput, SongResult, AudioFeatures

logger = logging.getLogger(__name__)


class PlaylistGenerator:
    
    def __init__(
        self,
        embedding_service: EmbeddingService,
        emotion_mapper: EmotionMapper,
        songs_db_path: Optional[str] = None
    ):
        self.embedding_service = embedding_service
        self.emotion_mapper = emotion_mapper
        self.songs_db_path = songs_db_path
        self.songs_df: Optional[pd.DataFrame] = None
        
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
        emotion: Optional[str] = None,
        num_results: int = 10
    ) -> tuple[List[SongResult], np.ndarray, Dict[str, Any]]:
       
        if not songs and not emotion:
            raise ValueError("Must provide either songs or emotion")
        
        combined_embedding = self._compute_combined_embedding(songs, emotion)
        
        emotion_features = None
        if emotion:
            emotion_features = self.emotion_mapper.get_feature_ranges(emotion)
        
        playlist = self._query_songs(
            combined_embedding,
            emotion,
            emotion_features,
            num_results
        )
        
        return playlist, combined_embedding, emotion_features
    
    def _compute_combined_embedding(
        self,
        songs: Optional[List[SongInput]],
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
        
        if emotion:
            emotion_emb = self.embedding_service.encode_emotion(emotion)
            embeddings.append(emotion_emb)
            
            emotion_weight = 0.3 if songs else 1.0
            weights.append(emotion_weight)
        
        combined = self.embedding_service.combine_embeddings(embeddings, weights)
        
        logger.info(f"Combined {len(embeddings)} embeddings into single vector")
        return combined
    
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
        
      
        if emotion and 'audio_features' in results_df.columns:
            emotion_scores = results_df['audio_features'].apply(
                lambda features: self.emotion_mapper.compute_emotion_score(
                    features, emotion
                ) if isinstance(features, dict) else 0.5
            )
            
            results_df['combined_score'] = (
                0.6 * results_df['similarity_score'] +
                0.4 * emotion_scores
            )
        else:
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
            
            if 'audio_features' in row and isinstance(row['audio_features'], dict):
                song_result.audio_features = AudioFeatures(**row['audio_features'])
            
            playlist.append(song_result)
        
        logger.info(f"Generated playlist with {len(playlist)} songs")
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
