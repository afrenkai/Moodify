import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class LLMEmotionService:
    """
    Contextual emotion understanding using sentence transformers.
    Learns emotion representations from examples and context rather than hardcoded rules.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info(f"Initializing LLM Emotion Service with {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        # Initialize emotion embeddings from rich contextual descriptions
        self.emotion_embeddings = self._build_emotion_embeddings()
        
        # Cache for computed embeddings
        self._embedding_cache: Dict[str, np.ndarray] = {}
        
        logger.info(f"Initialized with {len(self.emotion_embeddings)} emotion profiles")
    
    def _build_emotion_embeddings(self) -> Dict[str, np.ndarray]:
        """
        Build rich contextual embeddings for each emotion.
        Uses multiple descriptive sentences to capture nuance.
        """
        emotion_contexts = {
            "happy": [
                "upbeat energetic joyful cheerful music that makes you want to dance and smile",
                "bright positive optimistic songs with uplifting melodies and happy lyrics",
                "feel-good party music with infectious energy and celebration vibes",
                "music that radiates joy, sunshine, and good vibes all around"
            ],
            "sad": [
                "melancholic emotional music about heartbreak and loss that brings tears",
                "slow somber songs with sorrowful melodies expressing pain and loneliness",
                "music about missing someone, feeling empty and broken inside",
                "tearjerker ballads with emotional depth and vulnerability"
            ],
            "energetic": [
                "high-energy intense powerful music that pumps you up for action",
                "fast-paced adrenaline-fueled songs perfect for workouts and motivation",
                "explosive dynamic tracks with driving beats and aggressive intensity",
                "music that makes you want to move, run, jump and unleash energy"
            ],
            "calm": [
                "peaceful relaxing soothing music for meditation and tranquility",
                "gentle quiet ambient sounds that help you breathe and unwind",
                "serene calming melodies for rest, sleep and stress relief",
                "soft mellow music that brings inner peace and stillness"
            ],
            "angry": [
                "aggressive intense furious music expressing rage and rebellion",
                "hard-hitting heavy songs with violent angry energy and distortion",
                "music channeling frustration, hatred and explosive emotions",
                "raw powerful tracks about fighting back and destructive fury"
            ],
            "melancholic": [
                "bittersweet nostalgic music tinged with sadness and longing",
                "wistful reflective songs about memories and things that fade away",
                "music with emotional depth expressing regret and yearning",
                "moody atmospheric tracks capturing autumn rain and dusk feelings"
            ],
            "hopeful": [
                "inspiring uplifting music about believing in better tomorrow",
                "optimistic encouraging songs about dreams, faith and rising above",
                "music that gives hope, motivation and belief in possibilities",
                "tracks about new beginnings, light after darkness and positive change"
            ],
            "romantic": [
                "intimate tender love songs about deep connection and devotion",
                "passionate romantic music expressing desire and affection",
                "soft sensual ballads about lovers, hearts and beautiful moments",
                "music capturing warmth, closeness and the magic of being in love"
            ],
            "anxious": [
                "tense nervous unsettling music expressing worry and fear",
                "restless uncertain tracks with building pressure and unease",
                "music capturing stress, panic and anxious overwhelming feelings",
                "dark suspenseful songs about doubt and nervous anticipation"
            ],
            "peaceful": [
                "tranquil harmonious serene music bringing balance and zen",
                "nature-inspired calming sounds of ocean breeze and gentle streams",
                "meditative peaceful tracks for mindfulness and inner stillness",
                "soothing ambient music creating atmosphere of complete peace"
            ]
        }
        
        emotion_embeddings = {}
        for emotion, contexts in emotion_contexts.items():
            # Combine multiple contextual descriptions
            embeddings = self.model.encode(contexts, convert_to_numpy=True)
            # Average the embeddings for a richer representation
            emotion_embeddings[emotion] = np.mean(embeddings, axis=0)
        
        return emotion_embeddings
    
    def get_emotion_embedding(self, emotion: str) -> np.ndarray:
        """Get or compute embedding for an emotion."""
        emotion_lower = emotion.lower().strip()
        
        # Check if we have a pre-computed embedding
        if emotion_lower in self.emotion_embeddings:
            return self.emotion_embeddings[emotion_lower]
        
        # Check cache
        if emotion_lower in self._embedding_cache:
            return self._embedding_cache[emotion_lower]
        
        # Compute new embedding for custom emotion
        contexts = [
            f"music that feels {emotion_lower}",
            f"songs with {emotion_lower} mood and atmosphere",
            f"{emotion_lower} emotional vibes and energy"
        ]
        embeddings = self.model.encode(contexts, convert_to_numpy=True)
        emotion_emb = np.mean(embeddings, axis=0)
        
        # Cache it
        self._embedding_cache[emotion_lower] = emotion_emb
        
        return emotion_emb
    
    def compute_emotion_similarity(
        self, 
        text: str, 
        target_emotion: str,
        context: str = "song"
    ) -> float:
        """
        Compute how well text matches a target emotion using contextual understanding.
        
        Args:
            text: Text to analyze (song name, lyrics snippet, description)
            target_emotion: Target emotion to match against
            context: Context type ("song", "lyrics", "description")
            
        Returns:
            Similarity score from 0.0 to 1.0
        """
        # Contextualize the text
        if context == "song":
            contextualized = f"This song is: {text}"
        elif context == "lyrics":
            contextualized = f"Lyrics expressing emotion: {text}"
        else:
            contextualized = text
        
        # Get embeddings
        text_emb = self.model.encode([contextualized], convert_to_numpy=True)[0]
        emotion_emb = self.get_emotion_embedding(target_emotion)
        
        # Compute cosine similarity
        similarity = cosine_similarity(
            text_emb.reshape(1, -1),
            emotion_emb.reshape(1, -1)
        )[0][0]
        
        # Normalize to 0-1 range
        normalized = (similarity + 1) / 2
        
        return float(normalized)
    
    def find_related_emotions(
        self,
        emotion: str,
        top_k: int = 3
    ) -> List[Tuple[str, float]]:
        """
        Find emotions most similar to the given emotion.
        
        Args:
            emotion: Query emotion
            top_k: Number of related emotions to return
            
        Returns:
            List of (emotion_name, similarity_score) tuples
        """
        query_emb = self.get_emotion_embedding(emotion)
        
        similarities = []
        for emo_name, emo_emb in self.emotion_embeddings.items():
            if emo_name.lower() == emotion.lower():
                continue
            
            sim = cosine_similarity(
                query_emb.reshape(1, -1),
                emo_emb.reshape(1, -1)
            )[0][0]
            similarities.append((emo_name, float(sim)))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def infer_emotion_from_audio_features(
        self,
        audio_features: Dict[str, float],
        candidates: Optional[List[str]] = None
    ) -> List[Tuple[str, float]]:
        """
        DEPRECATED: Audio features are no longer used.
        Returns neutral scores for all candidates.
        
        Args:
            audio_features: Dictionary of Spotify audio features (ignored)
            candidates: Optional list of candidate emotions to rank
            
        Returns:
            List of (emotion, 0.5) tuples with neutral scores
        """
        logger.warning("infer_emotion_from_audio_features is deprecated - audio features no longer used")
        if candidates is None:
            candidates = list(self.emotion_embeddings.keys())
        return [(e, 0.5) for e in candidates]
    
    def get_audio_feature_guidance(
        self,
        emotion: str,
        confidence: float = 0.7
    ) -> Dict[str, Tuple[float, float]]:
        """
        DEPRECATED: Audio features are no longer used.
        Returns empty dict (deprecated functionality).
        
        Args:
            emotion: Target emotion
            confidence: How strict the ranges should be (0-1)
            
        Returns:
            Empty dictionary (deprecated)
        """
        logger.warning("get_audio_feature_guidance is deprecated - audio features no longer used")
        return {}
    
    def analyze_multi_emotion_query(
        self,
        emotions: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze a query with multiple emotions to understand their relationship.
        
        Args:
            emotions: List of emotion strings
            
        Returns:
            Analysis including dominant emotion, conflicts, and blended representation
        """
        if not emotions:
            return {"error": "No emotions provided"}
        
        # Get embeddings for all emotions
        emotion_embs = [self.get_emotion_embedding(e) for e in emotions]
        
        # Compute pairwise similarities
        similarities = []
        for i, e1 in enumerate(emotions):
            for j, e2 in enumerate(emotions):
                if i < j:
                    sim = cosine_similarity(
                        emotion_embs[i].reshape(1, -1),
                        emotion_embs[j].reshape(1, -1)
                    )[0][0]
                    similarities.append((e1, e2, float(sim)))
        
        # Identify conflicts (low similarity)
        conflicts = [(e1, e2, sim) for e1, e2, sim in similarities if sim < 0.3]
        
        # Identify harmonies (high similarity)
        harmonies = [(e1, e2, sim) for e1, e2, sim in similarities if sim > 0.7]
        
        # Create blended embedding
        blended_emb = np.mean(emotion_embs, axis=0)
        
        # Find which predefined emotion is closest to the blend
        best_match = None
        best_score = -1
        for emo_name, emo_emb in self.emotion_embeddings.items():
            sim = cosine_similarity(
                blended_emb.reshape(1, -1),
                emo_emb.reshape(1, -1)
            )[0][0]
            if sim > best_score:
                best_score = sim
                best_match = emo_name
        
        return {
            "emotions": emotions,
            "blended_emotion": best_match,
            "blend_confidence": float(best_score),
            "conflicts": conflicts,
            "harmonies": harmonies,
            "is_coherent": len(conflicts) == 0
        }
