/**
 * Component showcase and demo page
 * Use this to test components in isolation
 */

'use client';

import { useState } from 'react';
import EmotionSelector from '@/components/EmotionSelector';
import PlaylistDisplay from '@/components/PlaylistDisplay';
import TrackCard from '@/components/TrackCard';
import MoodCollageDisplay from '@/components/MoodCollageDisplay';
import LoadingSpinner from '@/components/LoadingSpinner';
import { SpotifyTrack, MoodCollage } from '@/lib/spotify-api';

// Mock data for demonstration
const mockTracks: SpotifyTrack[] = [
  {
    id: '1',
    name: 'Bohemian Rhapsody',
    artist: 'Queen',
    album: 'A Night at the Opera',
    similarity_score: 0.95,
    audio_features: {
      valence: 0.6,
      energy: 0.8,
      danceability: 0.5,
      tempo: 145,
      acousticness: 0.2,
      instrumentalness: 0.1,
      liveness: 0.3,
      speechiness: 0.05,
    },
  },
  {
    id: '2',
    name: 'Hotel California',
    artist: 'Eagles',
    album: 'Hotel California',
    similarity_score: 0.92,
    audio_features: {
      valence: 0.5,
      energy: 0.7,
      danceability: 0.6,
      tempo: 147,
      acousticness: 0.4,
      instrumentalness: 0.2,
      liveness: 0.2,
      speechiness: 0.03,
    },
  },
  {
    id: '3',
    name: 'Imagine',
    artist: 'John Lennon',
    album: 'Imagine',
    similarity_score: 0.89,
    audio_features: {
      valence: 0.7,
      energy: 0.4,
      danceability: 0.4,
      tempo: 76,
      acousticness: 0.8,
      instrumentalness: 0.0,
      liveness: 0.1,
      speechiness: 0.04,
    },
  },
];

const mockCollage: MoodCollage = {
  image_base64: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
  dominant_colors: ['#FFD700', '#FFA500', '#FF6347', '#FF4500', '#DC143C'],
  visual_params: {
    complexity: 0.7,
    saturation: 0.8,
    brightness: 0.6,
  },
  width: 800,
  height: 800,
};

const emotions = [
  'happy',
  'sad',
  'energetic',
  'calm',
  'angry',
  'melancholic',
  'hopeful',
  'romantic',
  'anxious',
  'peaceful',
];

export default function ComponentShowcase() {
  const [selectedEmotion, setSelectedEmotion] = useState<string | null>('happy');
  const [showLoading, setShowLoading] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-zinc-900 to-black p-8">
      <div className="max-w-7xl mx-auto space-y-12">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-2">
            Component Showcase
          </h1>
          <p className="text-zinc-400">
            Preview and test all EmoRec components
          </p>
        </div>

        {/* Emotion Selector */}
        <section className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
          <h2 className="text-2xl font-semibold text-white mb-4">
            Emotion Selector
          </h2>
          <EmotionSelector
            emotions={emotions}
            selectedEmotion={selectedEmotion}
            onSelect={setSelectedEmotion}
          />
        </section>

        {/* Loading Spinner */}
        <section className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-semibold text-white">
              Loading Spinner
            </h2>
            <button
              onClick={() => setShowLoading(!showLoading)}
              className="px-4 py-2 rounded-lg bg-green-500 text-black hover:bg-green-400"
            >
              {showLoading ? 'Hide' : 'Show'}
            </button>
          </div>
          {showLoading && (
            <LoadingSpinner message="Generating your playlist..." />
          )}
        </section>

        {/* Track Cards */}
        <section className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
          <h2 className="text-2xl font-semibold text-white mb-4">
            Track Cards
          </h2>
          <div className="space-y-2">
            {mockTracks.map((track, index) => (
              <TrackCard
                key={track.id}
                track={track}
                index={index}
                emotion={selectedEmotion || undefined}
                onPlay={(t) => console.log('Playing:', t.name)}
              />
            ))}
          </div>
        </section>

        {/* Playlist Display */}
        <section className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
          <h2 className="text-2xl font-semibold text-white mb-4">
            Playlist Display
          </h2>
          <PlaylistDisplay
            tracks={mockTracks}
            emotion={selectedEmotion || undefined}
            title="Sample Playlist"
            onPlayTrack={(track) => console.log('Playing:', track.name)}
          />
        </section>

        {/* Mood Collage (Mock) */}
        <section className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
          <h2 className="text-2xl font-semibold text-white mb-4">
            Mood Collage Display
          </h2>
          <p className="text-sm text-zinc-400 mb-4">
            Note: Using placeholder image. Generate real playlist for actual collage.
          </p>
          <MoodCollageDisplay
            collage={mockCollage}
            emotion={selectedEmotion || undefined}
          />
        </section>

        {/* Color Palette */}
        <section className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
          <h2 className="text-2xl font-semibold text-white mb-4">
            Emotion Color Palettes
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {emotions.map((emotion) => {
              const colors = getEmotionColors(emotion);
              return (
                <div key={emotion} className="text-center">
                  <div
                    className="h-24 rounded-lg mb-2"
                    style={{
                      background: `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`,
                    }}
                  />
                  <div className="text-sm text-white capitalize">{emotion}</div>
                  <div className="text-xs text-zinc-500 font-mono">
                    {colors.primary}
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Usage Instructions */}
        <section className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
          <h2 className="text-2xl font-semibold text-white mb-4">
            Usage Instructions
          </h2>
          <div className="space-y-4 text-sm text-zinc-300">
            <div>
              <h3 className="font-semibold text-white mb-2">
                1. Import Components
              </h3>
              <code className="block bg-black/50 p-3 rounded font-mono text-xs">
                import EmotionSelector from '@/components/EmotionSelector';
                <br />
                import PlaylistDisplay from '@/components/PlaylistDisplay';
              </code>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-2">2. Use in JSX</h3>
              <code className="block bg-black/50 p-3 rounded font-mono text-xs overflow-x-auto">
                {'<EmotionSelector\n  emotions={emotions}\n  selectedEmotion={selected}\n  onSelect={setSelected}\n/>'}
              </code>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-2">
                3. Generate Playlist
              </h3>
              <code className="block bg-black/50 p-3 rounded font-mono text-xs">
                const response = await spotifyAPI.searchByEmotion('happy', 20);
              </code>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

// Helper function
function getEmotionColors(emotion: string) {
  const colorSchemes: Record<string, any> = {
    happy: { primary: '#ffd700', secondary: '#ffa500' },
    sad: { primary: '#4169e1', secondary: '#1e3a8a' },
    energetic: { primary: '#ff4500', secondary: '#dc143c' },
    calm: { primary: '#87ceeb', secondary: '#4682b4' },
    angry: { primary: '#dc143c', secondary: '#8b0000' },
    melancholic: { primary: '#708090', secondary: '#2f4f4f' },
    hopeful: { primary: '#90ee90', secondary: '#32cd32' },
    romantic: { primary: '#ff69b4', secondary: '#ff1493' },
    anxious: { primary: '#9370db', secondary: '#663399' },
    peaceful: { primary: '#b0e0e6', secondary: '#5f9ea0' },
  };
  return (
    colorSchemes[emotion] || { primary: '#1db954', secondary: '#1ed760' }
  );
}
