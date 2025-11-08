from fastapi import APIRouter, HTTPException, Request
from typing import Optional
import logging

from backend.models.schemas import (
    PlaylistRequest,
    PlaylistResponse,
    SongResult,
    MoodCollage,
    HealthResponse
)
from backend.services.playlist_generator import PlaylistGenerator
from backend.services.mood_collage_generator import MoodCollageGenerator

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate-playlist", response_model=PlaylistResponse)
async def generate_playlist(request: PlaylistRequest, fastapi_request: Request):
    """
    Generate a playlist based on user input songs and/or emotion.
    
    This endpoint:
    1. Computes embeddings for input songs
    2. Maps emotion to audio feature ranges
    3. Combines embeddings with emotion context
    4. Queries and ranks songs
    5. Optionally generates mood collage image
    """
    try:
        embedding_service = fastapi_request.app.state.embedding_service
        emotion_mapper = fastapi_request.app.state.emotion_mapper
        
        playlist_generator = PlaylistGenerator(
            embedding_service=embedding_service,
            emotion_mapper=emotion_mapper
        )
        
        logger.info(f"Generating playlist: {len(request.songs or [])} songs, emotion: {request.emotion}")
        
        playlist, combined_embedding, emotion_features = playlist_generator.generate_playlist(
            songs=request.songs,
            emotion=request.emotion,
            num_results=request.num_results
        )
        
        mood_collage = None
        if request.include_collage:
            logger.info("Generating mood collage")
            collage_generator = MoodCollageGenerator()
            image_base64, dominant_colors, visual_params = collage_generator.generate_collage(
                combined_embedding,
                request.emotion
            )
            
            mood_collage = MoodCollage(
                image_base64=image_base64,
                dominant_colors=dominant_colors,
                visual_params=visual_params,
                width=collage_generator.width,
                height=collage_generator.height
            )
        
        emotion_features_list = None
        if emotion_features:
            emotion_features_list = {
                key: list(value) for key, value in emotion_features.items()
            }
        
        response = PlaylistResponse(
            playlist=playlist,
            mood_collage=mood_collage,
            emotion_features=emotion_features_list,
            combined_embedding=combined_embedding.tolist()[:10]  # First 10 dims for debugging
        )
        
        logger.info(f"Successfully generated playlist with {len(playlist)} songs")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating playlist: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    try:
        services = {
            "embedding_service": hasattr(request.app.state, 'embedding_service'),
            "emotion_mapper": hasattr(request.app.state, 'emotion_mapper'),
        }
        
        return HealthResponse(
            status="healthy" if all(services.values()) else "degraded",
            version="0.1.0",
            services=services
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/emotions")
async def list_emotions():
    from backend.models.schemas import EmotionType
    
    return {
        "emotions": [emotion.value for emotion in EmotionType],
        "note": "You can also use custom emotion descriptions"
    }
