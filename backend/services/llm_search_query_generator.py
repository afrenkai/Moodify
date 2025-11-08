"""
LLM-powered dynamic search query generation.
Replaces hardcoded genre/artist mappings with intelligent inference.
"""
import logging
from typing import List, Optional, Dict, Set
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)


class LLMSearchQueryGenerator:
    """
    Uses LLM/embeddings to dynamically generate search queries for emotions and songs.
    No hardcoded mappings - learns from semantic understanding.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", spotify_service=None):
        logger.info(f"Initializing LLM Search Query Generator with {model_name}")
        self.model = SentenceTransformer(model_name)
        self.spotify_service = spotify_service
        
        # Build a semantic knowledge base of genres, moods, and artists
        # This is learned, not hardcoded rules
        self._build_search_vocabulary()
        
        # Runtime genre corpus - will be populated from Spotify if available
        self.available_genres: Optional[Set[str]] = None
        self.genre_corpus_embeddings: Optional[Dict[str, np.ndarray]] = None
        
        logger.info("LLM Search Query Generator initialized with learned vocabulary")
    
    def _build_search_vocabulary(self):
        """
        Build semantic understanding of musical concepts.
        Uses embeddings to understand relationships, not hardcoded rules.
        """
        # Core genre vocabulary (descriptive, not prescriptive)
        self.genre_descriptions = {
            "indie": "independent alternative music with artistic creativity and emotional depth",
            "pop": "popular mainstream catchy accessible music with broad appeal",
            "rock": "guitar-driven energetic powerful music with strong rhythms",
            "electronic": "synthesizer electronic beats digital production modern sounds",
            "folk": "acoustic traditional storytelling organic natural instruments",
            "r&b": "rhythm and blues soul smooth vocals emotional expression",
            "hip-hop": "rap beats urban poetry rhythmic spoken word",
            "jazz": "improvisation sophisticated complex harmonies instrumental",
            "classical": "orchestral traditional composed instrumental sophisticated",
            "metal": "heavy distorted aggressive intense powerful dark",
            "punk": "fast raw rebellious energetic simple direct",
            "ambient": "atmospheric soundscape minimal relaxing textural",
            "soul": "emotional expressive vocals heartfelt passion",
            "country": "storytelling acoustic traditional americana roots",
            "reggae": "offbeat rhythm relaxed caribbean groove positive",
            "blues": "emotional guitar melancholic storytelling raw feelings",
        }
        
        # Mood descriptors (learned understanding)
        self.mood_descriptors = {
            "uplifting": "inspiring hopeful positive bright encouraging energizing",
            "melancholic": "sad reflective nostalgic bittersweet wistful longing",
            "energetic": "active dynamic powerful intense driving exciting",
            "calm": "peaceful relaxing soothing gentle quiet tranquil",
            "dark": "moody atmospheric somber brooding intense heavy",
            "romantic": "loving tender intimate passionate affectionate emotional",
            "aggressive": "intense powerful forceful angry rebellious raw",
            "dreamy": "ethereal floating soft atmospheric hazy ambient",
            "groovy": "funky rhythmic danceable smooth moving infectious",
            "raw": "authentic unpolished emotional honest direct stripped",
        }
        
        # Encode all descriptions for similarity search
        logger.info("Encoding genre and mood vocabulary...")
        self.genre_embeddings = {
            genre: self.model.encode(desc, convert_to_numpy=True)
            for genre, desc in self.genre_descriptions.items()
        }
        self.mood_embeddings = {
            mood: self.model.encode(desc, convert_to_numpy=True)
            for mood, desc in self.mood_descriptors.items()
        }
        
        logger.info(f"Encoded {len(self.genre_embeddings)} genres and {len(self.mood_embeddings)} moods")
    
    def load_genre_corpus_from_spotify(self) -> bool:
        """
        Load available genres from Spotify at runtime to create a searchable corpus.
        This allows us to dynamically filter out irrelevant genres.
        
        Returns:
            True if corpus was loaded successfully
        """
        if not self.spotify_service or not self.spotify_service.is_available():
            logger.warning("Spotify service not available, cannot load genre corpus")
            return False
        
        try:
            # Get available genre seeds from Spotify
            genres = self.spotify_service.get_available_genre_seeds()
            
            if not genres:
                logger.warning("No genres returned from Spotify")
                return False
            
            self.available_genres = set(genres)
            logger.info(f"Loaded {len(self.available_genres)} genres from Spotify: {sorted(list(self.available_genres))[:10]}...")
            
            # Encode all available genres for semantic matching
            self.genre_corpus_embeddings = {}
            for genre in self.available_genres:
                # Use genre name as description if not in our predefined descriptions
                description = self.genre_descriptions.get(
                    genre,
                    f"{genre} music genre with characteristic sound and style"
                )
                self.genre_corpus_embeddings[genre] = self.model.encode(
                    description,
                    convert_to_numpy=True
                )
            
            logger.info(f"Encoded {len(self.genre_corpus_embeddings)} Spotify genres for semantic search")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load genre corpus from Spotify: {e}")
            return False
    
    def filter_relevant_genres(
        self,
        emotion: str,
        min_similarity: float = 0.15,
        max_genres: int = 10
    ) -> List[tuple]:
        """
        Filter the genre corpus to find only relevant genres for the given emotion.
        This eliminates impossible candidates at runtime.
        
        Args:
            emotion: Target emotion
            min_similarity: Minimum similarity threshold (filters out irrelevant genres)
            max_genres: Maximum number of genres to return
            
        Returns:
            List of (genre, similarity_score) tuples, sorted by relevance
        """
        # If we have a runtime corpus from Spotify, use it
        if self.genre_corpus_embeddings:
            corpus_to_search = self.genre_corpus_embeddings
            logger.info(f"Filtering {len(corpus_to_search)} Spotify genres for emotion '{emotion}'")
        else:
            # Fallback to our predefined genres
            corpus_to_search = self.genre_embeddings
            logger.info(f"Filtering {len(corpus_to_search)} predefined genres for emotion '{emotion}'")
        
        # Encode the emotion
        emotion_embedding = self.model.encode(
            f"music that feels {emotion}, songs with {emotion} mood and emotional vibe",
            convert_to_numpy=True
        )
        
        # Compute similarity for all genres
        genre_scores = []
        for genre, genre_emb in corpus_to_search.items():
            similarity = self._cosine_similarity(emotion_embedding, genre_emb)
            if similarity >= min_similarity:  # Filter out irrelevant genres
                genre_scores.append((genre, float(similarity)))
        
        # Sort by similarity and take top K
        genre_scores.sort(key=lambda x: x[1], reverse=True)
        relevant_genres = genre_scores[:max_genres]
        
        logger.info(
            f"Filtered to {len(relevant_genres)} relevant genres for '{emotion}': "
            f"{[f'{g}({s:.2f})' for g, s in relevant_genres[:5]]}"
        )
        
        if len(relevant_genres) < max_genres * 0.3:  # Less than 30% of requested
            logger.warning(
                f"Only found {len(relevant_genres)} relevant genres (threshold={min_similarity}), "
                f"might want to lower threshold"
            )
        
        return relevant_genres
    
    def generate_queries_for_emotion(
        self,
        emotion: str,
        num_queries: int = 6,
        include_year: bool = True,
        use_runtime_filtering: bool = True
    ) -> List[str]:
        """
        Dynamically generate search queries for an emotion using LLM understanding.
        No hardcoded mappings!
        
        Args:
            emotion: Target emotion (any text)
            num_queries: Number of queries to generate
            include_year: Whether to include recent year filters
            use_runtime_filtering: Whether to use runtime genre corpus filtering
            
        Returns:
            List of Spotify search queries
        """
        logger.info(f"Generating search queries for emotion: '{emotion}'")
        
        # Use runtime genre filtering if available
        if use_runtime_filtering and (self.genre_corpus_embeddings or self.spotify_service):
            # Try to load corpus if not already loaded
            if not self.genre_corpus_embeddings:
                self.load_genre_corpus_from_spotify()
            
            # Filter to relevant genres only
            if self.genre_corpus_embeddings:
                relevant_genres = self.filter_relevant_genres(
                    emotion,
                    min_similarity=0.15,  # Eliminate clearly irrelevant genres
                    max_genres=8
                )
                
                if relevant_genres:
                    logger.info(f"Using {len(relevant_genres)} runtime-filtered genres")
                    queries = []
                    
                    # Generate queries from filtered genres
                    for genre, score in relevant_genres[:6]:
                        if include_year and score > 0.25:
                            queries.append(f"genre:{genre} year:2015-2024")
                        else:
                            queries.append(f"genre:{genre}")
                    
                    # Add some variety with different year ranges
                    if relevant_genres and include_year:
                        top_genre = relevant_genres[0][0]
                        queries.append(f"genre:{top_genre} year:2010-2024")
                    
                    logger.info(f"Generated {len(queries)} runtime-filtered queries: {queries[:3]}...")
                    return queries[:num_queries]
        
        # Fallback to predefined genre embeddings
        logger.info("Using predefined genre mappings (no runtime corpus)")
        
        # Encode the emotion
        emotion_embedding = self.model.encode(
            f"music that feels {emotion}, songs with {emotion} mood and emotional vibe",
            convert_to_numpy=True
        )
        
        # Find most relevant genres from predefined set
        genre_similarities = {}
        for genre, genre_emb in self.genre_embeddings.items():
            similarity = self._cosine_similarity(emotion_embedding, genre_emb)
            genre_similarities[genre] = similarity
        
        # Filter out low-similarity genres
        relevant_genres = {g: s for g, s in genre_similarities.items() if s >= 0.15}
        
        # Get top matches
        top_genres = sorted(relevant_genres.items(), key=lambda x: x[1], reverse=True)[:6]
        
        logger.info(
            f"Filtered predefined genres for '{emotion}': {[f'{g}({s:.2f})' for g, s in top_genres]}"
        )
        
        # Generate queries
        queries = []
        
        # Genre-based queries
        for genre, score in top_genres[:4]:
            if include_year and score > 0.25:
                queries.append(f"genre:{genre} year:2015-2024")
            else:
                queries.append(f"genre:{genre}")
        
        # Add variety with different year ranges
        if top_genres and include_year:
            for genre, _ in top_genres[:2]:
                queries.append(f"genre:{genre} year:2010-2024")
        
        logger.info(f"Generated {len(queries)} queries from predefined genres")
        return queries[:num_queries]
    
    def generate_queries_for_seed_songs(
        self,
        seed_songs: List[tuple],  # List of (song_name, artist) tuples
        num_queries: int = 7
    ) -> List[str]:
        """
        Dynamically generate search queries based on seed songs.
        Infers mood/genre from song characteristics.
        
        Args:
            seed_songs: List of (song_name, artist) tuples
            num_queries: Number of queries to generate
            
        Returns:
            List of Spotify search queries
        """
        logger.info(f"Generating search queries from {len(seed_songs)} seed songs")
        
        # Encode seed songs
        seed_texts = [f"{song} by {artist}" for song, artist in seed_songs]
        seed_embeddings = self.model.encode(seed_texts, convert_to_numpy=True)
        
        # Average seed embeddings to get overall vibe
        if len(seed_embeddings.shape) == 1:
            avg_embedding = seed_embeddings
        else:
            avg_embedding = np.mean(seed_embeddings, axis=0)
        
        # Find genres that match the vibe
        genre_similarities = {}
        for genre, genre_emb in self.genre_embeddings.items():
            similarity = self._cosine_similarity(avg_embedding, genre_emb)
            genre_similarities[genre] = similarity
        
        # Find moods that match
        mood_similarities = {}
        for mood, mood_emb in self.mood_embeddings.items():
            similarity = self._cosine_similarity(avg_embedding, mood_emb)
            mood_similarities[mood] = similarity
        
        top_genres = sorted(genre_similarities.items(), key=lambda x: x[1], reverse=True)[:5]
        top_moods = sorted(mood_similarities.items(), key=lambda x: x[1], reverse=True)[:3]
        
        logger.info(
            f"Inferred from seeds - genres: {[g[0] for g in top_genres[:3]]}, "
            f"moods: {[m[0] for m in top_moods[:2]]}"
        )
        
        # Generate diverse queries
        queries = []
        
        # Primary genre matches
        for genre, score in top_genres[:3]:
            queries.append(f"genre:{genre}")
        
        # Genre + mood combinations for nuance
        if top_moods and top_genres:
            mood = top_moods[0][0]
            for genre, _ in top_genres[:2]:
                queries.append(f"genre:{genre} {mood}")
                if len(queries) >= num_queries:
                    break
        
        # Add year filter for freshness
        if top_genres:
            queries.append(f"genre:{top_genres[0][0]} year:2010-2024")
        
        logger.info(f"Generated {len(queries)} seed-based queries")
        return queries[:num_queries]
    
    def infer_emotion_from_seeds(
        self,
        seed_songs: List[tuple],
        top_k: int = 3
    ) -> List[tuple]:
        """
        Infer likely emotions from seed songs.
        
        Args:
            seed_songs: List of (song_name, artist) tuples
            top_k: Number of top emotions to return
            
        Returns:
            List of (emotion_description, confidence_score) tuples
        """
        logger.info(f"Inferring emotions from {len(seed_songs)} seed songs")
        
        # Encode seeds
        seed_texts = [f"{song} by {artist}" for song, artist in seed_songs]
        seed_embeddings = self.model.encode(seed_texts, convert_to_numpy=True)
        
        if len(seed_embeddings.shape) == 1:
            avg_embedding = seed_embeddings
        else:
            avg_embedding = np.mean(seed_embeddings, axis=0)
        
        # Compare to mood descriptors to infer emotion
        mood_scores = []
        for mood, mood_emb in self.mood_embeddings.items():
            similarity = self._cosine_similarity(avg_embedding, mood_emb)
            mood_scores.append((mood, float(similarity)))
        
        mood_scores.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Inferred emotions: {mood_scores[:top_k]}")
        return mood_scores[:top_k]
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        a_flat = a.flatten()
        b_flat = b.flatten()
        dot_product = np.dot(a_flat, b_flat)
        norm_a = np.linalg.norm(a_flat)
        norm_b = np.linalg.norm(b_flat)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot_product / (norm_a * norm_b))
