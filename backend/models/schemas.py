from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class EmotionType(str, Enum):
    HAPPY = "happy"
    SAD = "sad"
    ENERGETIC = "energetic"
    CALM = "calm"
    ANGRY = "angry"
    MELANCHOLIC = "melancholic"
    HOPEFUL = "hopeful"
    ROMANTIC = "romantic"
    ANXIOUS = "anxious"
    PEACEFUL = "peaceful"
    TIRED = "tired"
    CONFIDENT = "confident"
    REBELLIOUS = "rebellious"
    PLAYFUL = "playful"
    SENSUAL = "sensual"
    EMPOWERED = "empowered"
    VULNERABLE = "vulnerable"
    MYSTERIOUS = "mysterious"
    DREAMY = "dreamy"
    GRATEFUL = "grateful"
    LONELY = "lonely"
    INSPIRED = "inspired"
    CONFLICTED = "conflicted"
    CAREFREE = "carefree"
    LOVE = "love"
    NOSTALGIC = "nostalgic"


class SongInput(BaseModel):
    song_name: str = Field(..., description="Name of the song")
    artist: str = Field(..., description="Artist name")
    spotify_id: Optional[str] = Field(None, description="Spotify track ID if available")


class ArtistInput(BaseModel):
    artist_name: str = Field(..., description="Name of the artist")
    spotify_id: Optional[str] = Field(None, description="Spotify artist ID if available")


class PlaylistRequest(BaseModel):
    songs: Optional[List[SongInput]] = Field(
        None,
        description="List of user input songs for embedding-based search"
    )
    artists: Optional[List[ArtistInput]] = Field(
        None,
        description="List of user input artists - we'll use their top tracks for embedding-based search"
    )
    emotion: Optional[List[str]] = Field(
        None,
        description="Emotion descriptor (can be predefined or free text)"
    )
    num_results: int = Field(
        10,
        ge=1,
        le=50,
        description="Number of songs to return in playlist"
    )
    enrich_with_lyrics: bool = Field(
        True,
        description="Whether to enrich results with Genius lyrics metadata for better mood matching (recommended)"
    )


class SongResult(BaseModel):
    song_name: str
    artist: str
    spotify_id: Optional[str] = None
    similarity_score: float = Field(..., description="Similarity score (0-1)")
    album: Optional[str] = None
    preview_url: Optional[str] = None
    external_url: Optional[str] = None
    duration_ms: Optional[int] = None
    popularity: Optional[int] = None
    album_image: Optional[str] = None
    genius_url: Optional[str] = Field(None, description="Genius lyrics page URL")
    lyrics_emotion: Optional[str] = Field(None, description="Dominant emotion detected from lyrics")
    lyrics_score: Optional[float] = Field(None, description="Lyrics-based emotion match score (0-1)")


class PlaylistResponse(BaseModel):
    playlist: List[SongResult] = Field(..., description="Generated playlist songs")
    emotion_features: Optional[Dict[str, Any]] = Field(
        None,
        description="Audio feature ranges used for emotion matching (can be single values or ranges)"
    )
    combined_embedding: Optional[List[float]] = Field(
        None,
        description="Combined embedding vector (for debugging)"
    )


class HealthResponse(BaseModel):
    status: str
    version: str
    services: Dict[str, bool]


class SpotifyTrackInfo(BaseModel):
    spotify_id: str
    song_name: str
    artist: str
    album: str
    preview_url: Optional[str] = None
    external_url: str
    duration_ms: int
    popularity: int
    album_image: Optional[str] = None


class SpotifyRecommendationsRequest(BaseModel):
    seed_tracks: Optional[List[str]] = Field(None, description="List of track IDs (max 5)")
    emotion: Optional[str] = Field(None, description="Emotion for feature targets")
    num_results: int = Field(20, ge=1, le=50, description="Number of recommendations")


class SpotifySearchRequest(BaseModel):
    song_name: str = Field(..., description="Song name to search")
    artist: Optional[str] = Field(None, description="Artist name for more accurate search")


class SpotifyArtistInfo(BaseModel):
    spotify_id: str
    name: str
    genres: List[str] = Field(default_factory=list)
    popularity: int
    image_url: Optional[str] = None
    external_url: str

