

import { AudioFeatures } from './spotify-api';


export function formatDuration(ms: number): string {
  const totalSeconds = Math.floor(ms / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}


export function getEmotionColor(emotion: string): {
  primary: string;
  secondary: string;
  gradient: string;
} {
  const colorSchemes: Record<string, any> = {
    happy: {
      primary: '#ffd700',
      secondary: '#ffa500',
      gradient: 'from-yellow-400 to-orange-500',
    },
    sad: {
      primary: '#4169e1',
      secondary: '#1e3a8a',
      gradient: 'from-blue-500 to-blue-900',
    },
    energetic: {
      primary: '#ff4500',
      secondary: '#dc143c',
      gradient: 'from-red-500 to-pink-600',
    },
    calm: {
      primary: '#87ceeb',
      secondary: '#4682b4',
      gradient: 'from-sky-300 to-blue-500',
    },
    angry: {
      primary: '#dc143c',
      secondary: '#8b0000',
      gradient: 'from-red-600 to-red-900',
    },
    melancholic: {
      primary: '#708090',
      secondary: '#2f4f4f',
      gradient: 'from-slate-500 to-slate-700',
    },
    hopeful: {
      primary: '#90ee90',
      secondary: '#32cd32',
      gradient: 'from-green-400 to-green-600',
    },
    romantic: {
      primary: '#ff69b4',
      secondary: '#ff1493',
      gradient: 'from-pink-400 to-pink-600',
    },
    anxious: {
      primary: '#9370db',
      secondary: '#663399',
      gradient: 'from-purple-500 to-purple-700',
    },
    peaceful: {
      primary: '#b0e0e6',
      secondary: '#5f9ea0',
      gradient: 'from-cyan-300 to-teal-500',
    },
  };

  return (
    colorSchemes[emotion.toLowerCase()] || {
      primary: '#1db954',
      secondary: '#1ed760',
      gradient: 'from-green-500 to-green-400',
    }
  );
}


export function getEmotionEmoji(emotion: string): string {
  const emojiMap: Record<string, string> = {
    happy: '😊',
    sad: '😢',
    energetic: '⚡',
    calm: '😌',
    angry: '😠',
    melancholic: '😔',
    hopeful: '🌟',
    romantic: '💕',
    anxious: '😰',
    peaceful: '☮️',
  };

  return emojiMap[emotion.toLowerCase()] || '🎵';
}


export function formatAudioFeature(feature: string, value: number): string {
  const percentage = Math.round(value * 100);
  return `${percentage}%`;
}


export function getAudioFeatureDescription(feature: string): string {
  const descriptions: Record<string, string> = {
    valence: 'Musical positiveness',
    energy: 'Intensity and activity',
    danceability: 'How suitable for dancing',
    tempo: 'Beats per minute',
    acousticness: 'Acoustic confidence',
    instrumentalness: 'Vocal presence',
    liveness: 'Audience presence',
    speechiness: 'Spoken words',
  };

  return descriptions[feature] || feature;
}


export function calculateVibeScore(features: AudioFeatures): number {
  const weights = {
    valence: 0.3,
    energy: 0.25,
    danceability: 0.2,
    acousticness: 0.1,
    liveness: 0.15,
  };

  return (
    features.valence * weights.valence +
    features.energy * weights.energy +
    features.danceability * weights.danceability +
    features.acousticness * weights.acousticness +
    features.liveness * weights.liveness
  );
}


export function getVibeDescription(score: number): string {
  if (score > 0.8) return 'High Energy Vibes';
  if (score > 0.6) return 'Upbeat Mood';
  if (score > 0.4) return 'Balanced Flow';
  if (score > 0.2) return 'Mellow Atmosphere';
  return 'Chill Vibes';
}


export function formatSimilarityScore(score: number): string {
  return `${Math.round(score * 100)}% match`;
}


export function generateSpotifyURI(type: 'track' | 'playlist' | 'album', id: string): string {
  return `spotify:${type}:${id}`;
}


export function parseSpotifyURI(uri: string): { type: string; id: string } | null {
  const match = uri.match(/spotify:([a-z]+):([a-zA-Z0-9]+)/);
  if (!match) return null;
  return { type: match[1], id: match[2] };
}


export function getTrackPlaceholder(emotion?: string): string {
  const color = emotion ? getEmotionColor(emotion) : { primary: '#1db954', secondary: '#1ed760' };
  return `linear-gradient(135deg, ${color.primary}, ${color.secondary})`;
}


export function formatNumber(num: number): string {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }
  return num.toString();
}


export function shuffleArray<T>(array: T[]): T[] {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}


export function getComplementaryEmotions(emotion: string): string[] {
  const complementary: Record<string, string[]> = {
    happy: ['energetic', 'hopeful', 'romantic'],
    sad: ['melancholic', 'calm', 'peaceful'],
    energetic: ['happy', 'angry', 'hopeful'],
    calm: ['peaceful', 'hopeful', 'romantic'],
    angry: ['energetic', 'sad', 'anxious'],
    melancholic: ['sad', 'calm', 'peaceful'],
    hopeful: ['happy', 'calm', 'romantic'],
    romantic: ['hopeful', 'happy', 'peaceful'],
    anxious: ['calm', 'peaceful', 'hopeful'],
    peaceful: ['calm', 'hopeful', 'romantic'],
  };

  return complementary[emotion.toLowerCase()] || ['happy', 'calm', 'energetic'];
}
