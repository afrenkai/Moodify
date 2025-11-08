/**
 * Main export index for EmoRec Spotify API
 * Import everything from here for convenience
 */

// API Client
export { SpotifyAPI, spotifyAPI } from './spotify-api';

// Types
export type {
  SpotifyTrack,
  AudioFeatures,
  MoodCollage,
  PlaylistGenerationRequest,
  PlaylistGenerationResponse,
  SpotifyAPIError,
} from './spotify-api';

// Utilities
export {
  formatDuration,
  getEmotionColor,
  getEmotionEmoji,
  formatAudioFeature,
  getAudioFeatureDescription,
  calculateVibeScore,
  getVibeDescription,
  formatSimilarityScore,
  generateSpotifyURI,
  parseSpotifyURI,
  getTrackPlaceholder,
  formatNumber,
  shuffleArray,
  getComplementaryEmotions,
} from './spotify-utils';

// Examples
export {
  exampleEmotionOnly,
  exampleWithSeedTracks,
  exampleCustomAPI,
  exampleListEmotions,
  exampleHealthCheck,
  exampleAnalyzeTracks,
  exampleErrorHandling,
  runAllExamples,
} from './examples';
