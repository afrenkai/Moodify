/**
 * Mood collage display component
 */

'use client';

import { MoodCollage } from '@/lib/spotify-api';
import { useState } from 'react';

interface MoodCollageDisplayProps {
  collage: MoodCollage;
  emotion?: string;
}

export default function MoodCollageDisplay({ collage, emotion }: MoodCollageDisplayProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Mood Visualization</h3>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-sm text-zinc-400 hover:text-white transition-colors"
        >
          {isExpanded ? 'Collapse' : 'Expand'}
        </button>
      </div>

      <div className={`transition-all duration-300 ${isExpanded ? 'h-auto' : 'h-64'}`}>
        <div className="relative rounded-lg overflow-hidden">
          <img
            src={`data:image/png;base64,${collage.image_base64}`}
            alt={`${emotion || 'Mood'} visualization`}
            className="w-full h-auto object-cover"
          />
          
          {/* Dominant colors */}
          <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
            <div className="flex gap-2">
              {collage.dominant_colors.slice(0, 5).map((color, index) => (
                <div
                  key={index}
                  className="w-8 h-8 rounded-full border-2 border-white/30"
                  style={{ backgroundColor: color }}
                  title={color}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Visual parameters */}
        {isExpanded && (
          <div className="mt-4 p-4 bg-white/5 rounded-lg">
            <h4 className="text-sm font-semibold text-white mb-2">
              Visual Parameters
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs">
              {Object.entries(collage.visual_params).map(([key, value]) => (
                <div key={key} className="flex flex-col">
                  <span className="text-zinc-400 capitalize">
                    {key.replace(/_/g, ' ')}
                  </span>
                  <span className="text-white font-mono">
                    {typeof value === 'number' ? value.toFixed(2) : String(value)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
