#!/usr/bin/env bun

/**
 * CLI tool to test the Spotify-themed API
 * Usage: bun run scripts/test-api.ts
 */

import { spotifyAPI } from '../lib/spotify-api';

const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
};

function log(message: string, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

async function testHealthCheck() {
  log('\n🏥 Testing health check...', colors.bright);
  try {
    const health = await spotifyAPI.healthCheck();
    log(`✅ Status: ${health.status}`, colors.green);
    log(`   Version: ${health.version}`, colors.cyan);
    return true;
  } catch (error) {
    log('❌ Health check failed', colors.red);
    log(`   ${error}`, colors.red);
    return false;
  }
}

async function testEmotions() {
  log('\n😊 Testing emotions list...', colors.bright);
  try {
    const emotions = await spotifyAPI.getEmotions();
    log(`✅ Found ${emotions.length} emotions:`, colors.green);
    log(`   ${emotions.join(', ')}`, colors.cyan);
    return emotions;
  } catch (error) {
    log('❌ Failed to get emotions', colors.red);
    return [];
  }
}

async function testPlaylistGeneration() {
  log('\n🎵 Testing playlist generation...', colors.bright);
  try {
    const response = await spotifyAPI.searchByEmotion('happy', 10, true);
    log(`✅ Generated ${response.playlist.length} tracks`, colors.green);
    
    log('\n📋 Top 5 tracks:', colors.cyan);
    response.playlist.slice(0, 5).forEach((track, i) => {
      log(
        `   ${i + 1}. ${track.name} - ${track.artist} (${(track.similarity_score * 100).toFixed(1)}%)`,
        colors.reset
      );
    });
    
    if (response.mood_collage) {
      log('\n🎨 Mood collage:', colors.magenta);
      log(`   Size: ${response.mood_collage.width}x${response.mood_collage.height}`, colors.reset);
      log(`   Colors: ${response.mood_collage.dominant_colors.slice(0, 3).join(', ')}`, colors.reset);
    }
    
    if (response.emotion_features) {
      log('\n📊 Audio features:', colors.yellow);
      Object.entries(response.emotion_features).forEach(([key, value]) => {
        const percentage = typeof value === 'number' ? (value * 100).toFixed(0) : value;
        log(`   ${key}: ${percentage}%`, colors.reset);
      });
    }
    
    return true;
  } catch (error) {
    log('❌ Playlist generation failed', colors.red);
    log(`   ${error}`, colors.red);
    return false;
  }
}

async function testWithSeedTracks() {
  log('\n🌱 Testing with seed tracks...', colors.bright);
  try {
    const response = await spotifyAPI.getRecommendations(
      [
        { name: 'Bohemian Rhapsody', artist: 'Queen' },
        { name: 'Hotel California', artist: 'Eagles' },
      ],
      'energetic',
      5
    );
    
    log(`✅ Generated ${response.playlist.length} recommendations`, colors.green);
    response.playlist.forEach((track, i) => {
      log(
        `   ${i + 1}. ${track.name} - ${track.artist}`,
        colors.reset
      );
    });
    
    return true;
  } catch (error) {
    log('❌ Seed track recommendations failed', colors.red);
    log(`   ${error}`, colors.red);
    return false;
  }
}

async function testAllEmotions() {
  log('\n🌈 Testing all emotions...', colors.bright);
  
  const emotions = await testEmotions();
  let successCount = 0;
  
  for (const emotion of emotions.slice(0, 3)) { // Test first 3 to save time
    try {
      const response = await spotifyAPI.searchByEmotion(emotion, 3, false);
      log(`✅ ${emotion}: ${response.playlist.length} tracks`, colors.green);
      successCount++;
    } catch (error) {
      log(`❌ ${emotion}: failed`, colors.red);
    }
  }
  
  log(`\n📊 Results: ${successCount}/${emotions.length} emotions tested successfully`, colors.cyan);
  return successCount === emotions.length;
}

async function main() {
  log('╔════════════════════════════════════════════╗', colors.bright);
  log('║   🎵 EmoRec Spotify API Test Suite 🎵    ║', colors.bright);
  log('╚════════════════════════════════════════════╝', colors.bright);
  
  const tests = [
    testHealthCheck,
    testEmotions,
    testPlaylistGeneration,
    testWithSeedTracks,
    testAllEmotions,
  ];
  
  let passed = 0;
  let failed = 0;
  
  for (const test of tests) {
    try {
      const result = await test();
      if (result !== false) {
        passed++;
      } else {
        failed++;
      }
    } catch (error) {
      failed++;
    }
  }
  
  log('\n╔════════════════════════════════════════════╗', colors.bright);
  log(`║              Test Summary                  ║`, colors.bright);
  log('╠════════════════════════════════════════════╣', colors.bright);
  log(`║  ✅ Passed: ${passed}/${tests.length}                            ║`, colors.green);
  log(`║  ❌ Failed: ${failed}/${tests.length}                            ║`, failed > 0 ? colors.red : colors.reset);
  log('╚════════════════════════════════════════════╝', colors.bright);
  
  process.exit(failed > 0 ? 1 : 0);
}

main().catch(console.error);
