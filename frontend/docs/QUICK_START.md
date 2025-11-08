# 🚀 Quick Start Guide

Get up and running with the EmoRec Spotify-themed API in 5 minutes.

## Prerequisites

- [Bun](https://bun.sh) installed
- Backend API running (see main README)

## 1. Installation

```bash
cd frontend
bun install
```

## 2. Configuration

```bash
# Copy environment template
cp .env.local.example .env.local

# Edit if needed (default works for local development)
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 3. Start Development Server

```bash
bun run dev
```

Open [http://localhost:3000](http://localhost:3000)

## 4. Your First Playlist

### In the Browser

1. Select an emotion (e.g., "Happy" 😊)
2. Choose number of tracks
3. Click "Generate Playlist"
4. Enjoy your mood-based playlist!

### In Code

```typescript
import { spotifyAPI } from '@/lib/spotify-api';

// Generate happy playlist
const response = await spotifyAPI.searchByEmotion('happy', 20, true);

// Display tracks
response.playlist.forEach(track => {
  console.log(`${track.name} by ${track.artist}`);
});

// View mood collage
if (response.mood_collage) {
  console.log('Colors:', response.mood_collage.dominant_colors);
}
```

## 5. Test the API

```bash
bun run test:api
```

This will test all API endpoints and show results.

## Common Tasks

### Generate Playlist by Emotion

```typescript
const response = await spotifyAPI.searchByEmotion('energetic', 15);
```

### Get Recommendations from Seed Tracks

```typescript
const response = await spotifyAPI.getRecommendations(
  [
    { name: 'Bohemian Rhapsody', artist: 'Queen' },
    { name: 'Imagine', artist: 'John Lennon' }
  ],
  'calm',
  20
);
```

### Use Custom Emotion

```typescript
const response = await spotifyAPI.generatePlaylist({
  emotion: ['nostalgic and uplifting'],
  num_results: 25,
  include_collage: true
});
```

### Display Tracks in UI

```tsx
import PlaylistDisplay from '@/components/PlaylistDisplay';

<PlaylistDisplay
  tracks={response.playlist}
  emotion="happy"
  title="My Happy Playlist"
  onPlayTrack={(track) => console.log('Playing:', track)}
/>
```

## Project Structure

```
frontend/
├── app/
│   └── page.tsx              # Main app page
├── components/
│   ├── EmotionSelector.tsx   # Emotion picker
│   ├── PlaylistDisplay.tsx   # Playlist view
│   ├── TrackCard.tsx         # Track component
│   ├── MoodCollageDisplay.tsx # Visualization
│   └── LoadingSpinner.tsx    # Loading state
├── lib/
│   ├── spotify-api.ts        # API client ⭐
│   ├── spotify-utils.ts      # Utilities
│   └── examples.ts           # Example code
└── scripts/
    └── test-api.ts           # Test suite
```

## Available Emotions

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

You can also use custom emotion descriptions!

## Key Features

✅ Emotion-based playlist generation
✅ AI-powered mood visualization
✅ Audio feature analysis
✅ Spotify-style UI
✅ Full TypeScript support
✅ Seed track recommendations
✅ Shuffle & play controls

## Next Steps

1. **Read the docs**: `docs/API_REFERENCE.md`
2. **Explore examples**: `lib/examples.ts`
3. **Customize themes**: `lib/spotify-utils.ts`
4. **Build features**: Check component props in docs

## Troubleshooting

### Backend not connecting?

```bash
# Check backend is running
curl http://localhost:8000/health

# Check environment variable
cat .env.local
```

### TypeScript errors?

```bash
# Clear and rebuild
rm -rf .next
bun run dev
```

### Need help?

- Check `docs/API_REFERENCE.md`
- Run examples: `bun run scripts/test-api.ts`
- Review `lib/examples.ts`

## Pro Tips

💡 Use `Ctrl+Space` in VS Code for autocomplete
💡 All API functions return typed responses
💡 Components are fully customizable with Tailwind
💡 Use browser devtools to inspect API calls
💡 Test with `bun run test:api` before deploying

## Build for Production

```bash
bun run build
bun run start
```

Deploy to Vercel, Netlify, or any Node.js host!

---

Happy coding! 🎵
