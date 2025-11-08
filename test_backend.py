import pytest
from fastapi.testclient import TestClient
import numpy as np

from backend.main import app
from backend.services.embedding_service import EmbeddingService
from backend.services.emotion_mapper import EmotionMapper
from backend.services.mood_collage_generator import MoodCollageGenerator
from backend.models.schemas import PlaylistRequest, SongInput


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def embedding_service():
    return EmbeddingService()


@pytest.fixture
def emotion_mapper():
    return EmotionMapper()


@pytest.fixture
def collage_generator():
    return MoodCollageGenerator(width=400, height=300)


class TestEmbeddingService:
    def test_encode_text(self, embedding_service):
        text = "This is a test"
        embedding = embedding_service.encode_text(text)
        
        assert isinstance(embedding, np.ndarray)
        assert len(embedding) == embedding_service.embedding_dim
    
    def test_encode_song(self, embedding_service):
        embedding = embedding_service.encode_song("Bohemian Rhapsody", "Queen")
        
        assert isinstance(embedding, np.ndarray)
        assert len(embedding) == embedding_service.embedding_dim
    
    def test_encode_emotion(self, embedding_service):
        embedding = embedding_service.encode_emotion("happy")
        
        assert isinstance(embedding, np.ndarray)
        assert len(embedding) == embedding_service.embedding_dim
    
    def test_combine_embeddings(self, embedding_service):
        emb1 = embedding_service.encode_text("song 1")
        emb2 = embedding_service.encode_text("song 2")
        
        combined = embedding_service.combine_embeddings([emb1, emb2])
        
        assert isinstance(combined, np.ndarray)
        assert len(combined) == embedding_service.embedding_dim
    
    def test_compute_similarity(self, embedding_service):
        emb1 = embedding_service.encode_text("happy music")
        emb2 = embedding_service.encode_text("joyful song")
        emb3 = embedding_service.encode_text("sad melancholic")
        
        sim_similar = embedding_service.compute_similarity(emb1, emb2)
        sim_different = embedding_service.compute_similarity(emb1, emb3)
        
        assert 0 <= sim_similar <= 1
        assert 0 <= sim_different <= 1
        assert sim_similar > sim_different 


class TestEmotionMapper:
    
    def test_get_feature_ranges_predefined(self, emotion_mapper):
        ranges = emotion_mapper.get_feature_ranges("happy")
        
        assert isinstance(ranges, dict)
        assert "valence" in ranges
        assert isinstance(ranges["valence"], tuple)
        assert len(ranges["valence"]) == 2
    
    def test_get_feature_ranges_custom(self, emotion_mapper):
        """Test getting feature ranges for custom emotions."""
        ranges = emotion_mapper.get_feature_ranges("melancholic but hopeful")
        
        assert isinstance(ranges, dict)
        assert len(ranges) > 0
    
    def test_compute_emotion_score(self, emotion_mapper):
        happy_features = {
            "valence": 0.8,
            "energy": 0.7,
            "danceability": 0.6,
            "tempo": 120
        }
        
        score = emotion_mapper.compute_emotion_score(happy_features, "happy")
        
        assert 0 <= score <= 1
        assert score > 0.5


class TestMoodCollageGenerator:
    
    def test_generate_collage(self, collage_generator, embedding_service):
        embedding = embedding_service.encode_emotion("happy")
        
        image_base64, colors, params = collage_generator.generate_collage(
            embedding,
            emotion="happy"
        )
        
        assert isinstance(image_base64, str)
        assert len(image_base64) > 0
        assert isinstance(colors, list)
        assert len(colors) > 0
        assert isinstance(params, dict)
        assert "primary_hue" in params
    
    def test_embedding_to_visual_params(self, collage_generator, embedding_service):
        embedding = embedding_service.encode_emotion("calm")
        
        params = collage_generator._embedding_to_visual_params(embedding, "calm")
        
        assert "primary_hue" in params
        assert "saturation" in params
        assert "value" in params
        assert "complexity" in params
        assert 0 <= params["primary_hue"] <= 360
        assert 0 <= params["saturation"] <= 1


class TestAPI:
    
    def test_root_endpoint(self, client):
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "EmoRec API"
    
    def test_health_endpoint(self, client):
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_emotions_endpoint(self, client):
        response = client.get("/api/v1/emotions")
        
        assert response.status_code == 200
        data = response.json()
        assert "emotions" in data
        assert len(data["emotions"]) > 0
    
    def test_generate_playlist_emotion_only(self, client):
        response = client.post(
            "/api/v1/generate-playlist",
            json={
                "emotion": "happy",
                "num_results": 5,
                "include_collage": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "playlist" in data
        assert len(data["playlist"]) > 0
        assert "mood_collage" in data
        assert data["mood_collage"] is not None
    
    def test_generate_playlist_with_songs(self, client):
        response = client.post(
            "/api/v1/generate-playlist",
            json={
                "songs": [
                    {"song_name": "Bohemian Rhapsody", "artist": "Queen"}
                ],
                "emotion": "energetic",
                "num_results": 10,
                "include_collage": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "playlist" in data
        assert len(data["playlist"]) > 0
    
    def test_generate_playlist_validation_error(self, client):
        response = client.post(
            "/api/v1/generate-playlist",
            json={
                "num_results": 10
            }
        )
        
        assert response.status_code in [400, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
