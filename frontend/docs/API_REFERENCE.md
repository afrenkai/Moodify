# 📚 Spotify API Documentation

Complete API reference for the EmoRec Spotify-themed frontend.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Client](#api-client)
- [Types](#types)
- [Components](#components)
- [Utilities](#utilities)
- [Examples](#examples)

## Installation

```bash
cd frontend
bun install
```

## Quick Start

```typescript
import { spotifyAPI } from '@/lib/spotify-api';

// Generate a happy playlist
const response = await spotifyAPI.searchByEmotion('happy', 20, true);

// Display tracks
response.playlist.forEach(track => {
  console.log(`${track.name} - ${track.artist}`);
});
```

## API Client

### SpotifyAPI Class

```typescript
class SpotifyAPI {
  constructor(baseUrl?: string);
  
  generatePlaylist(request: PlaylistGenerationRequest): Promise<PlaylistGenerationResponse>;
  getEmotions(): Promise<string[]>;
  healthCheck(): Promise<{ status: string; version: string }>;
  searchByEmotion(emotion: string, numResults?: number, includeCollage?: boolean): Promise<PlaylistGenerationResponse>;
  getRecommendations(seedTracks: SeedTrack[], emotion?: string, numResults?: number): Promise<PlaylistGenerationResponse>;
}
```

### Methods

#### `generatePlaylist(request)`

Generate a playlist with full control over parameters.

**Parameters:**
- `request`: `PlaylistGenerationRequest`
  - `songs?`: Array of seed tracks
  - `emotion?`: Array of emotion strings
  - `num_results?`: Number of tracks (1-50, default: 10)
  - `include_collage?`: Generate mood visualization (default: true)

**Returns:** `Promise<PlaylistGenerationResponse>`

**Example:**
```typescript
const response = await spotifyAPI.generatePlaylist({
  songs: [
    { song_name: 'Imagine', artist: 'John Lennon' }
  ],
  emotion: ['peaceful'],
  num_results: 15,
  include_collage: true
});
```

#### `searchByEmotion(emotion, numResults, includeCollage)`

Convenience method for emotion-only search.

**Parameters:**
- `emotion`: string - Emotion descriptor
- `numResults?`: number - Number of tracks (default: 20)
- `includeCollage?`: boolean - Include visualization (default: true)

**Returns:** `Promise<PlaylistGenerationResponse>`

**Example:**
```typescript
const response = await spotifyAPI.searchByEmotion('energetic', 25, true);
```

#### `getRecommendations(seedTracks, emotion, numResults)`

Get recommendations based on seed tracks with optional emotion filter.

**Parameters:**
- `seedTracks`: Array of tracks with name and artist
- `emotion?`: string - Optional emotion filter
- `numResults?`: number - Number of tracks (default: 20)

**Returns:** `Promise<PlaylistGenerationResponse>`

**Example:**
```typescript
const response = await spotifyAPI.getRecommendations(
  [
    { name: 'Bohemian Rhapsody', artist: 'Queen' },
    { name: 'Hotel California', artist: 'Eagles' }
  ],
  'calm',
  30
);
```

#### `getEmotions()`

Fetch available emotion types.

**Returns:** `Promise<string[]>`

**Example:**
```typescript
const emotions = await spotifyAPI.getEmotions();
// ['happy', 'sad', 'energetic', ...]
```

#### `healthCheck()`

Check API availability and version.

**Returns:** `Promise<{ status: string; version: string }>`

**Example:**
```typescript
const health = await spotifyAPI.healthCheck();
// { status: 'healthy', version: '0.1.0' }
```

## Types

### SpotifyTrack

```typescript
interface SpotifyTrack {
  id: string;                    // Track ID
  name: string;                  // Track name
  artist: string;                // Artist name
  album?: string;                // Album name
  preview_url?: string;          // Preview URL
  similarity_score: number;      // Match score (0-1)
  audio_features?: AudioFeatures; // Audio analysis
}
```

### AudioFeatures

```typescript
interface AudioFeatures {
  valence: number;           // 0-1: Musical positiveness
  energy: number;            // 0-1: Intensity and activity
  danceability: number;      // 0-1: Suitable for dancing
  tempo: number;             // BPM
  acousticness: number;      // 0-1: Acoustic confidence
  instrumentalness: number;  // 0-1: Vocal presence
  liveness: number;          // 0-1: Audience presence
  speechiness: number;       // 0-1: Spoken words
}
```

### MoodCollage

```typescript
interface MoodCollage {
  image_base64: string;           // Base64 encoded PNG
  dominant_colors: string[];      // Hex color codes
  visual_params: Record<string, any>; // Generation parameters
  width: number;                  // Image width
  height: number;                 // Image height
}
```

### PlaylistGenerationRequest

```typescript
interface PlaylistGenerationRequest {
  songs?: Array<{
    song_name: string;
    artist: string;
    spotify_id?: string;
  }>;
  emotion?: string[];
  num_results?: number;      // 1-50
  include_collage?: boolean;
}
```

### PlaylistGenerationResponse

```typescript
interface PlaylistGenerationResponse {
  playlist: SpotifyTrack[];
  mood_collage?: MoodCollage;
  emotion_features?: Record<string, number>;
  combined_embedding?: number[];
}
```

## Components

### EmotionSelector

Interactive emotion picker with Spotify-style design.

**Props:**
```typescript
interface EmotionSelectorProps {
  emotions: string[];
  selectedEmotion: string | null;
  onSelect: (emotion: string) => void;
}
```

**Usage:**
```tsx
<EmotionSelector
  emotions={['happy', 'sad', 'energetic']}
  selectedEmotion="happy"
  onSelect={(emotion) => console.log(emotion)}
/>
```

### PlaylistDisplay

Spotify-style playlist view with shuffle functionality.

**Props:**
```typescript
interface PlaylistDisplayProps {
  tracks: SpotifyTrack[];
  emotion?: string;
  title?: string;
  onPlayTrack?: (track: SpotifyTrack) => void;
}
```

**Usage:**
```tsx
<PlaylistDisplay
  tracks={playlist}
  emotion="energetic"
  title="Your Energetic Mix"
  onPlayTrack={(track) => console.log('Playing:', track)}
/>
```

### TrackCard

Individual track component with hover effects.

**Props:**
```typescript
interface TrackCardProps {
  track: SpotifyTrack;
  index: number;
  emotion?: string;
  onPlay?: (track: SpotifyTrack) => void;
}
```

### MoodCollageDisplay

Mood visualization display with expandable details.

**Props:**
```typescript
interface MoodCollageDisplayProps {
  collage: MoodCollage;
  emotion?: string;
}
```

**Usage:**
```tsx
<MoodCollageDisplay
  collage={moodCollage}
  emotion="calm"
/>
```

### LoadingSpinner

Spotify-themed loading animation.

**Props:**
```typescript
interface LoadingSpinnerProps {
  message?: string;
}
```

## Utilities

### Color Functions

```typescript
// Get emotion color scheme
getEmotionColor(emotion: string): {
  primary: string;
  secondary: string;
  gradient: string;
}

// Get emotion emoji
getEmotionEmoji(emotion: string): string
```

### Formatting Functions

```typescript
// Format duration (ms to MM:SS)
formatDuration(ms: number): string

// Format audio feature as percentage
formatAudioFeature(feature: string, value: number): string

// Format similarity score
formatSimilarityScore(score: number): string

// Format large numbers (K, M)
formatNumber(num: number): string
```

### Analysis Functions

```typescript
// Calculate overall vibe score
calculateVibeScore(features: AudioFeatures): number

// Get vibe description
getVibeDescription(score: number): string

// Get complementary emotions
getComplementaryEmotions(emotion: string): string[]
```

### Audio Feature Descriptions

```typescript
// Get feature description
getAudioFeatureDescription(feature: string): string
```

### Utility Functions

```typescript
// Shuffle array
shuffleArray<T>(array: T[]): T[]

// Generate Spotify URI
generateSpotifyURI(type: 'track' | 'playlist' | 'album', id: string): string

// Parse Spotify URI
parseSpotifyURI(uri: string): { type: string; id: string } | null

// Get track placeholder
getTrackPlaceholder(emotion?: string): string
```

## Examples

### Basic Usage

```typescript
// Simple emotion search
const happy = await spotifyAPI.searchByEmotion('happy', 20);

// With seed tracks
const recs = await spotifyAPI.getRecommendations(
  [{ name: 'Imagine', artist: 'John Lennon' }],
  'peaceful'
);
```

### Advanced Usage

```typescript
// Multiple emotions
const response = await spotifyAPI.generatePlaylist({
  emotion: ['happy', 'energetic'],
  num_results: 30,
  include_collage: true
});

// Analyze tracks
response.playlist.forEach(track => {
  if (track.audio_features) {
    const vibe = calculateVibeScore(track.audio_features);
    console.log(`${track.name}: ${getVibeDescription(vibe)}`);
  }
});
```

### Error Handling

```typescript
try {
  const response = await spotifyAPI.searchByEmotion('happy', 20);
  // Handle success
} catch (error) {
  if (error instanceof Error) {
    console.error('Failed:', error.message);
  }
}
```

### Testing

Run the test suite:

```bash
bun run test:api
```

Or use the example functions:

```typescript
import { runAllExamples } from '@/lib/examples';

await runAllExamples();
```

## Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Backend Requirements

The API expects these backend endpoints:

- `POST /api/v1/generate-playlist`
- `GET /api/v1/emotions`
- `GET /api/v1/health`

See backend documentation for details.

## Best Practices

1. **Error Handling**: Always wrap API calls in try-catch
2. **Loading States**: Show loading indicator during requests
3. **Rate Limiting**: Consider implementing request throttling
4. **Caching**: Cache emotion list and health checks
5. **Type Safety**: Use TypeScript types for all API interactions

## Troubleshooting

### Common Issues

**CORS Error:**
```
Access to fetch has been blocked by CORS policy
```
Solution: Ensure backend allows your origin in CORS settings.

**Connection Refused:**
```
Failed to fetch
```
Solution: Check `NEXT_PUBLIC_API_URL` and backend status.

**Type Errors:**
```
Type 'X' is not assignable to type 'Y'
```
Solution: Ensure you're using the correct interfaces from `spotify-api.ts`.

## Support

For issues and questions, see the main project repository.

---

Last updated: November 2025
