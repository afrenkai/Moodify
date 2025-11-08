'use client';

import { useState, useEffect } from 'react';
import {
  spotifyAPI,
  SpotifyTrack,
  PlaylistGenerationResponse,
} from '@/lib/spotify-api';
import { getEmotionColor } from '@/lib/spotify-utils';
import EmotionSelector from '@/components/EmotionSelector';
import PlaylistDisplay from '@/components/PlaylistDisplay';
import MoodCollageDisplay from '@/components/MoodCollageDisplay';
import LoadingSpinner from '@/components/LoadingSpinner';

const DEFAULT_EMOTIONS = [
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

export default function Home() {
  const [emotions, setEmotions] = useState<string[]>(DEFAULT_EMOTIONS);
  const [selectedEmotion, setSelectedEmotion] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [playlistData, setPlaylistData] = useState<PlaylistGenerationResponse | null>(null);
  const [numTracks, setNumTracks] = useState(20);

  // Fetch available emotions on mount
  useEffect(() => {
    spotifyAPI
      .getEmotions()
      .then(setEmotions)
      .catch((err) => {
        console.error('Failed to fetch emotions:', err);
        // Keep default emotions
      });
  }, []);

  const handleGeneratePlaylist = async () => {
    if (!selectedEmotion) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await spotifyAPI.searchByEmotion(
        selectedEmotion,
        numTracks,
        true
      );
      setPlaylistData(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate playlist');
      console.error('Error generating playlist:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const gradientColors = selectedEmotion
    ? getEmotionColor(selectedEmotion)
    : { primary: '#1db954', secondary: '#1ed760' };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-zinc-900 to-black">
      {/* Hero Section */}
      <div
        className="relative overflow-hidden"
        style={{
          background: `linear-gradient(180deg, ${gradientColors.primary}20 0%, transparent 100%)`,
        }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-4">
              🎵 EmoRec
            </h1>
            <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
              Discover music that matches your emotions. Powered by AI-driven mood
              analysis.
            </p>
          </div>

          {/* Emotion Selector */}
          <div className="mb-8">
            <EmotionSelector
              emotions={emotions}
              selectedEmotion={selectedEmotion}
              onSelect={setSelectedEmotion}
            />
          </div>

          {/* Controls */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <div className="flex items-center gap-3">
              <label htmlFor="numTracks" className="text-sm text-zinc-400">
                Number of tracks:
              </label>
              <select
                id="numTracks"
                value={numTracks}
                onChange={(e) => setNumTracks(Number(e.target.value))}
                className="px-4 py-2 rounded-lg bg-white/10 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={30}>30</option>
                <option value={50}>50</option>
              </select>
            </div>

            <button
              onClick={handleGeneratePlaylist}
              disabled={!selectedEmotion || isLoading}
              className="px-8 py-3 rounded-full bg-green-500 text-black font-semibold hover:bg-green-400 disabled:bg-zinc-700 disabled:text-zinc-500 disabled:cursor-not-allowed transition-all transform hover:scale-105 active:scale-95"
            >
              {isLoading ? 'Generating...' : '🎵 Generate Playlist'}
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-6 p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-400 text-center max-w-2xl mx-auto">
              {error}
            </div>
          )}
        </div>
      </div>

      {/* Results Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {isLoading && (
          <LoadingSpinner message="Creating your perfect playlist..." />
        )}

        {!isLoading && playlistData && (
          <div className="space-y-8">
            {/* Mood Collage */}
            {playlistData.mood_collage && (
              <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
                <MoodCollageDisplay
                  collage={playlistData.mood_collage}
                  emotion={selectedEmotion || undefined}
                />
              </div>
            )}

            {/* Playlist */}
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
              <PlaylistDisplay
                tracks={playlistData.playlist}
                emotion={selectedEmotion || undefined}
                title={`Your ${selectedEmotion ? selectedEmotion.charAt(0).toUpperCase() + selectedEmotion.slice(1) : 'Emotion-Based'} Playlist`}
                onPlayTrack={(track) => console.log('Playing:', track)}
              />
            </div>

            {/* Audio Features Summary */}
            {playlistData.emotion_features && (
              <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
                <h3 className="text-lg font-semibold text-white mb-4">
                  Emotion Audio Features
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries(playlistData.emotion_features).map(
                    ([feature, value]) => (
                      <div key={feature} className="flex flex-col">
                        <span className="text-sm text-zinc-400 capitalize mb-1">
                          {feature}
                        </span>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-green-500 rounded-full transition-all"
                              style={{
                                width: `${typeof value === 'number' ? value * 100 : 50}%`,
                              }}
                            />
                          </div>
                          <span className="text-xs text-white font-mono">
                            {typeof value === 'number'
                              ? (value * 100).toFixed(0)
                              : value}
                            %
                          </span>
                        </div>
                      </div>
                    )
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Empty State */}
        {!isLoading && !playlistData && !error && (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">🎧</div>
            <h3 className="text-2xl font-semibold text-white mb-2">
              Ready to discover your soundtrack?
            </h3>
            <p className="text-zinc-400">
              Select an emotion above and generate your personalized playlist
            </p>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-white/10 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-zinc-500">
              © 2025 EmoRec • Emotion-based music recommendation
            </p>
            <div className="flex gap-6 text-sm text-zinc-400">
              <a href="#" className="hover:text-white transition-colors">
                About
              </a>
              <a href="#" className="hover:text-white transition-colors">
                API Docs
              </a>
              <a href="#" className="hover:text-white transition-colors">
                GitHub
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
