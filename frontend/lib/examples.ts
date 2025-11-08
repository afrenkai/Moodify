/**
 * Example usage of the Spotify-themed API
 * This file demonstrates all major features
 */

import { spotifyAPI, SpotifyAPI } from './spotify-api';
import type {
  PlaylistGenerationRequest,
  PlaylistGenerationResponse,
  SpotifyTrack,
} from './spotify-api';

// Example 1: Generate playlist by emotion only
export async function exampleEmotionOnly() {
  console.log('🎵 Example 1: Emotion-based playlist');
  
  try {
    const response = await spotifyAPI.searchByEmotion('happy', 10, true);
    
    console.log(`✅ Generated ${response.playlist.length} tracks`);
    console.log('Top 3 tracks:');
    response.playlist.slice(0, 3).forEach((track, i) => {
      console.log(`  ${i + 1}. ${track.name} - ${track.artist}`);
    });
    
    if (response.mood_collage) {
      console.log('🎨 Mood collage generated');
      console.log('Dominant colors:', response.mood_collage.dominant_colors);
    }
    
    return response;
  } catch (error) {
    console.error('❌ Error:', error);
    throw error;
  }
}

// Example 2: Generate with seed tracks
export async function exampleWithSeedTracks() {
  console.log('🎵 Example 2: Seed tracks + emotion');
  
  const seedTracks = [
    { name: 'Bohemian Rhapsody', artist: 'Queen' },
    { name: 'Stairway to Heaven', artist: 'Led Zeppelin' },
  ];
  
  try {
    const response = await spotifyAPI.getRecommendations(
      seedTracks,
      'energetic',
      15
    );
    
    console.log(`✅ Generated ${response.playlist.length} recommendations`);
    console.log('Audio features:', response.emotion_features);
    
    return response;
  } catch (error) {
    console.error('❌ Error:', error);
    throw error;
  }
}

// Example 3: Custom API instance with different base URL
export async function exampleCustomAPI() {
  console.log('🎵 Example 3: Custom API instance');
  
  const customAPI = new SpotifyAPI('https://api.emorec.example.com/v1');
  
  const request: PlaylistGenerationRequest = {
    emotion: ['calm', 'peaceful'],
    num_results: 20,
    include_collage: true,
  };
  
  try {
    const response = await customAPI.generatePlaylist(request);
    console.log(`✅ Generated playlist with ${response.playlist.length} tracks`);
    return response;
  } catch (error) {
    console.error('❌ Error:', error);
    throw error;
  }
}

// Example 4: Get and display all emotions
export async function exampleListEmotions() {
  console.log('🎵 Example 4: Available emotions');
  
  try {
    const emotions = await spotifyAPI.getEmotions();
    console.log('Available emotions:', emotions);
    return emotions;
  } catch (error) {
    console.error('❌ Error:', error);
    throw error;
  }
}

// Example 5: Health check
export async function exampleHealthCheck() {
  console.log('🎵 Example 5: Health check');
  
  try {
    const health = await spotifyAPI.healthCheck();
    console.log('API Status:', health.status);
    console.log('Version:', health.version);
    return health;
  } catch (error) {
    console.error('❌ Error: API unreachable');
    throw error;
  }
}

// Example 6: Process and analyze tracks
export async function exampleAnalyzeTracks() {
  console.log('🎵 Example 6: Analyze track features');
  
  try {
    const response = await spotifyAPI.searchByEmotion('energetic', 5, false);
    
    console.log('Track Analysis:');
    response.playlist.forEach((track: SpotifyTrack) => {
      console.log(`\n${track.name} - ${track.artist}`);
      console.log(`  Match: ${(track.similarity_score * 100).toFixed(1)}%`);
      
      if (track.audio_features) {
        const features = track.audio_features;
        console.log(`  Energy: ${(features.energy * 100).toFixed(0)}%`);
        console.log(`  Valence: ${(features.valence * 100).toFixed(0)}%`);
        console.log(`  Danceability: ${(features.danceability * 100).toFixed(0)}%`);
        console.log(`  Tempo: ${features.tempo.toFixed(0)} BPM`);
      }
    });
    
    return response;
  } catch (error) {
    console.error('❌ Error:', error);
    throw error;
  }
}

// Example 7: Error handling
export async function exampleErrorHandling() {
  console.log('🎵 Example 7: Error handling');
  
  try {
    // Invalid request - no songs or emotion
    const response = await spotifyAPI.generatePlaylist({});
    return response;
  } catch (error) {
    if (error instanceof Error) {
      console.log('✅ Caught expected error:', error.message);
    }
    // This is expected to fail
  }
  
  try {
    // Too many results
    const response = await spotifyAPI.generatePlaylist({
      emotion: ['happy'],
      num_results: 1000, // Exceeds limit
    });
    return response;
  } catch (error) {
    if (error instanceof Error) {
      console.log('✅ Caught expected error:', error.message);
    }
  }
}

// Run all examples
export async function runAllExamples() {
  console.log('🎵 Running all Spotify API examples...\n');
  
  try {
    await exampleHealthCheck();
    console.log('\n---\n');
    
    await exampleListEmotions();
    console.log('\n---\n');
    
    await exampleEmotionOnly();
    console.log('\n---\n');
    
    await exampleWithSeedTracks();
    console.log('\n---\n');
    
    await exampleAnalyzeTracks();
    console.log('\n---\n');
    
    await exampleErrorHandling();
    
    console.log('\n✅ All examples completed!');
  } catch (error) {
    console.error('❌ Example suite failed:', error);
  }
}

// Browser-friendly test function
if (typeof window !== 'undefined') {
  (window as any).spotifyAPIExamples = {
    emotionOnly: exampleEmotionOnly,
    withSeeds: exampleWithSeedTracks,
    customAPI: exampleCustomAPI,
    listEmotions: exampleListEmotions,
    healthCheck: exampleHealthCheck,
    analyzeTracks: exampleAnalyzeTracks,
    errorHandling: exampleErrorHandling,
    runAll: runAllExamples,
  };
  
  console.log('💡 Spotify API examples loaded!');
  console.log('Run: spotifyAPIExamples.runAll()');
}
