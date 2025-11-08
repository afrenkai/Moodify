from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from backend.api.routes import router
from backend.services.embedding_service import EmbeddingService
from backend.services.emotion_mapper import EmotionMapper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting EmoRec backend...")
    try:
        app.state.embedding_service = EmbeddingService()
        app.state.emotion_mapper = EmotionMapper()
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    logger.info("Shutting down EmoRec backend...")


app = FastAPI(
    title="EmoRec API",
    description="Emotion-based playlist and mood collage generation API",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "EmoRec API",
        "version": "0.1.0",
        "description": "Emotion-based playlist and mood collage generation",
        "endpoints": {
            "docs": "/docs",
            "generate_playlist": "/api/v1/generate-playlist",
            "health": "/api/v1/health"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
