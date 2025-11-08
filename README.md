# 🎵 EmoRec

**Emotion-based music recommendation system** powered by AI embeddings and audio feature analysis.

Generate personalized playlists that match your mood with a beautiful Spotify-themed interface.

[![Built with Bun](https://img.shields.io/badge/Built%20with-Bun-000000?style=flat&logo=bun)](https://bun.sh)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat&logo=next.js&logoColor=white)](https://nextjs.org)

## ✨ Features

- 🎭 **Emotion-Based Playlists** - Generate music based on 10+ emotions
- 🎨 **AI Mood Visualization** - Visual representation of your emotional state
- 📊 **Audio Feature Analysis** - Deep dive into valence, energy, danceability, and more
- 🎵 **Seed Track Recommendations** - Get similar songs based on your favorites
- 🌈 **Spotify-Style UI** - Beautiful, modern interface inspired by Spotify
- ⚡ **Real-time Generation** - Fast playlist creation using embeddings
- 🔄 **Shuffle & Play** - Interactive playlist controls

## 🚀 Quick Start

### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python run.py
```

The backend will start on `http://localhost:8000`

### Frontend (Spotify-themed UI)

```bash
cd frontend

# Install dependencies
bun install

# Start development server
bun run dev
```

Visit `http://localhost:3000` to use the app!

**See [frontend/docs/QUICK_START.md](frontend/docs/QUICK_START.md) for detailed setup.**

## 📁 Project Structure

```
EmoRec/
├── backend/                  # FastAPI backend
│   ├── api/                  # API routes
│   ├── models/               # Pydantic schemas
│   └── services/             # Core services
│       ├── embedding_service.py
│       ├── emotion_mapper.py
│       ├── playlist_generator.py
│       └── mood_collage_generator.py
├── frontend/                 # Next.js frontend
│   ├── app/                  # Next.js app
│   ├── components/           # React components
│   │   ├── EmotionSelector.tsx
│   │   ├── PlaylistDisplay.tsx
│   │   ├── TrackCard.tsx
│   │   └── MoodCollageDisplay.tsx
│   ├── lib/                  # Core libraries
│   │   ├── spotify-api.ts    # API client
│   │   ├── spotify-utils.ts  # Utilities
│   │   └── examples.ts       # Usage examples
│   ├── docs/                 # Documentation
│   │   ├── API_REFERENCE.md
│   │   └── QUICK_START.md
│   └── scripts/
│       └── test-api.ts       # API test suite
└── testing/                  # Test scripts
```

## 🎯 Available Emotions

- 😊 Happy
- 😢 Sad
- ⚡ Energetic
- 😌 Calm
- 😠 Angry
- 😔 Melancholic
- 🌟 Hopeful
- 💕 Romantic
- 😰 Anxious
- ☮️ Peaceful

*Plus support for custom emotion descriptions!*

## 💻 API Usage

### Generate Playlist by Emotion

```typescript
import { spotifyAPI } from '@/lib/spotify-api';

const response = await spotifyAPI.searchByEmotion('happy', 20, true);

console.log(`Generated ${response.playlist.length} tracks`);
response.playlist.forEach(track => {
  console.log(`${track.name} - ${track.artist}`);
});
```

### Get Recommendations from Seed Tracks

```typescript
const response = await spotifyAPI.getRecommendations(
  [
    { name: 'Bohemian Rhapsody', artist: 'Queen' },
    { name: 'Imagine', artist: 'John Lennon' }
  ],
  'energetic',
  15
);
```

### Custom Request

```typescript
const response = await spotifyAPI.generatePlaylist({
  songs: [
    { song_name: 'Hotel California', artist: 'Eagles' }
  ],
  emotion: ['calm', 'nostalgic'],
  num_results: 30,
  include_collage: true
});
```

**Full API documentation: [frontend/docs/API_REFERENCE.md](frontend/docs/API_REFERENCE.md)**

## 🧪 Testing

### Test Frontend API

```bash
cd frontend
bun run test:api
```

### Test Backend

```bash
python test_backend.py
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Sentence Transformers** - Text embedding models
- **NumPy** - Numerical computing
- **Pillow** - Image generation

### Frontend
- **Next.js 16** - React framework
- **Bun** - Fast JavaScript runtime
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React 19** - UI library

## 📖 Documentation

- **[Quick Start Guide](frontend/docs/QUICK_START.md)** - Get started in 5 minutes
- **[API Reference](frontend/docs/API_REFERENCE.md)** - Complete API documentation
- **[Spotify API README](frontend/SPOTIFY_API_README.md)** - Frontend API overview
- **[Examples](frontend/lib/examples.ts)** - Code examples

## 🎨 Features Deep Dive

### Emotion Mapping
The system maps emotions to audio features:
- **Valence**: Musical positiveness (0-1)
- **Energy**: Intensity and activity (0-1)
- **Danceability**: Suitable for dancing (0-1)
- **Tempo**: Beats per minute
- **Acousticness**: Acoustic confidence (0-1)

### Embedding-Based Search
Uses sentence transformers to:
1. Encode song descriptions
2. Encode emotion descriptions
3. Combine embeddings with weights
4. Find similar songs via cosine similarity

### Mood Visualization
AI-generated collages representing emotional states:
- Abstract geometric patterns
- Emotion-specific color palettes
- Visual parameters derived from audio features

## 🔧 Development

### Backend Development

```bash
# Install in development mode
pip install -e .

# Run with auto-reload
uvicorn backend.main:app --reload
```

### Frontend Development

```bash
cd frontend

# Development mode (hot reload)
bun run dev

# Lint
bun run lint

# Build for production
bun run build
```

## 🌐 API Endpoints

### Backend (FastAPI)

- `GET /` - API information
- `GET /health` - Health check
- `GET /api/v1/health` - Service health
- `GET /api/v1/emotions` - List emotions
- `POST /api/v1/generate-playlist` - Generate playlist

Visit `http://localhost:8000/docs` for interactive API docs.

## 📊 Response Examples

### Playlist Response

```json
{
  "playlist": [
    {
      "song_name": "Happy",
      "artist": "Pharrell Williams",
      "spotify_id": "60nZcImufyMA1MKQY3dcCH",
      "similarity_score": 0.92,
      "audio_features": {
        "valence": 0.96,
        "energy": 0.81,
        "danceability": 0.82
      }
    }
  ],
  "mood_collage": {
    "image_base64": "iVBORw0KGgo...",
    "dominant_colors": ["#FFD700", "#FFA500"],
    "width": 800,
    "height": 800
  }
}
```

## 🚢 Deployment

### Backend
- Deploy to any Python hosting (AWS, GCP, Azure, Railway, etc.)
- Ensure environment variables are set
- Use production ASGI server (uvicorn, gunicorn)

### Frontend
```bash
cd frontend
bun run build

# Deploy to Vercel, Netlify, or any Node.js host
```

Set `NEXT_PUBLIC_API_URL` to your backend URL.

## 🤝 Contributing

Contributions welcome! Please ensure:
- TypeScript types are updated
- Tests pass
- Code follows existing style
- Documentation is updated

## 📝 License

See LICENSE file for details.

## 🙏 Acknowledgments

- Sentence Transformers for embeddings
- FastAPI for backend framework
- Next.js and Bun for frontend
- Spotify for UI inspiration

---

Built with ❤️ using AI and emotion