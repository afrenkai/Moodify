/**
 * Spotify-themed track card component
 */

'use client';

import { SpotifyTrack } from '@/lib/spotify-api';
import { formatSimilarityScore, getTrackPlaceholder } from '@/lib/spotify-utils';

interface TrackCardProps {
  track: SpotifyTrack;
  index: number;
  emotion?: string;
  onPlay?: (track: SpotifyTrack) => void;
}

export default function TrackCard({ track, index, emotion, onPlay }: TrackCardProps) {
  return (
    <div className="group flex items-center gap-4 rounded-lg p-3 hover:bg-white/5 transition-colors">
      {/* Track number */}
      <div className="w-8 text-center text-zinc-400 group-hover:text-green-500">
        <span className="group-hover:hidden">{index + 1}</span>
        <button
          onClick={() => onPlay?.(track)}
          className="hidden group-hover:block w-full"
        >
          ▶
        </button>
      </div>

      {/* Album art placeholder */}
      <div
        className="w-12 h-12 rounded flex items-center justify-center text-white text-xs font-bold"
        style={{ background: getTrackPlaceholder(emotion) }}
      >
        🎵
      </div>

      {/* Track info */}
      <div className="flex-1 min-w-0">
        <div className="font-medium text-white truncate">{track.name}</div>
        <div className="text-sm text-zinc-400 truncate">{track.artist}</div>
      </div>

      {/* Album */}
      {track.album && (
        <div className="hidden md:block text-sm text-zinc-400 truncate max-w-[200px]">
          {track.album}
        </div>
      )}

      {/* Similarity score */}
      <div className="text-sm text-zinc-500">
        {formatSimilarityScore(track.similarity_score)}
      </div>

      {/* Audio features indicator */}
      {track.audio_features && (
        <div className="hidden lg:flex gap-1">
          {track.audio_features.energy > 0.7 && (
            <span className="text-xs px-2 py-1 rounded-full bg-red-500/20 text-red-400">
              High Energy
            </span>
          )}
          {track.audio_features.valence > 0.7 && (
            <span className="text-xs px-2 py-1 rounded-full bg-yellow-500/20 text-yellow-400">
              Upbeat
            </span>
          )}
          {track.audio_features.danceability > 0.7 && (
            <span className="text-xs px-2 py-1 rounded-full bg-purple-500/20 text-purple-400">
              Danceable
            </span>
          )}
        </div>
      )}
    </div>
  );
}
