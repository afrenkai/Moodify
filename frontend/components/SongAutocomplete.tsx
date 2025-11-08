'use client';

import { useState, useEffect, useRef } from 'react';
import { spotifyAPI, SpotifyTrack } from '@/lib/spotify-api';

interface SongAutocompleteProps {
  onSelectSong: (song: { song_name: string; artist: string; spotify_id?: string }) => void;
  placeholder?: string;
}

export default function SongAutocomplete({ onSelectSong, placeholder }: SongAutocompleteProps) {
  const [inputValue, setInputValue] = useState('');
  const [suggestions, setSuggestions] = useState<SpotifyTrack[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const debounceTimer = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (inputValue.trim().length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    // Debounce search
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    debounceTimer.current = setTimeout(async () => {
      setIsLoading(true);
      try {
        const results = await spotifyAPI.searchTracks(inputValue, undefined, 8);
        setSuggestions(results);
        setShowSuggestions(results.length > 0);
        setSelectedIndex(-1);
      } catch (error) {
        console.error('Search error:', error);
        setSuggestions([]);
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, [inputValue]);

  const handleSelectSong = (track: SpotifyTrack) => {
    onSelectSong({
      song_name: track.name,
      artist: track.artist,
      spotify_id: track.id,
    });
    setInputValue('');
    setSuggestions([]);
    setShowSuggestions(false);
    setSelectedIndex(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showSuggestions || suggestions.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((prev) => 
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
          handleSelectSong(suggestions[selectedIndex]);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        setSelectedIndex(-1);
        break;
    }
  };

  return (
    <div className="relative flex-1">
      <input
        type="text"
        placeholder={placeholder || "Search for a song..."}
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyDown}
        onFocus={() => inputValue.trim().length >= 2 && setSuggestions.length > 0 && setShowSuggestions(true)}
        onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
        className="w-full px-4 py-3 rounded-lg bg-white/10 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-green-500 placeholder-zinc-500"
      />
      
      {isLoading && (
        <div className="absolute right-4 top-1/2 -translate-y-1/2">
          <div className="w-4 h-4 border-2 border-green-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {/* Suggestions Dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute z-20 w-full mt-2 bg-zinc-800 border border-white/20 rounded-lg shadow-xl max-h-96 overflow-y-auto">
          {suggestions.map((track, index) => (
            <button
              key={track.id}
              onClick={() => handleSelectSong(track)}
              className={`w-full px-4 py-3 text-left transition-colors flex items-center gap-3 border-b border-white/5 last:border-b-0 ${
                index === selectedIndex ? 'bg-green-500/20' : 'hover:bg-white/10'
              }`}
            >
              {/* Album Art */}
              {track.album_image && (
                <img
                  src={track.album_image}
                  alt={track.album || track.name}
                  className="w-12 h-12 rounded object-cover flex-shrink-0"
                />
              )}
              
              {/* Track Info */}
              <div className="flex-1 min-w-0">
                <div className="text-white font-medium truncate">
                  {track.name}
                </div>
                <div className="text-sm text-zinc-400 truncate">
                  {track.artist}
                </div>
                {track.album && (
                  <div className="text-xs text-zinc-500 truncate">
                    {track.album}
                  </div>
                )}
              </div>

              {/* Popularity Badge */}
              {track.popularity !== undefined && (
                <div className="flex-shrink-0 px-2 py-1 rounded bg-white/10 text-xs text-zinc-400">
                  {track.popularity}%
                </div>
              )}
            </button>
          ))}
        </div>
      )}

      {showSuggestions && inputValue.trim().length >= 2 && suggestions.length === 0 && !isLoading && (
        <div className="absolute z-20 w-full mt-2 bg-zinc-800 border border-white/20 rounded-lg shadow-xl p-4 text-center text-zinc-400">
          No songs found. Try a different search term.
        </div>
      )}
    </div>
  );
}
