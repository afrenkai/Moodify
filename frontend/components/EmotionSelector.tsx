/**
 * Emotion selector component with Spotify-style design
 */

'use client';

import { getEmotionColor, getEmotionEmoji } from '@/lib/spotify-utils';

interface EmotionSelectorProps {
  emotions: string[];
  selectedEmotion: string | null;
  onSelect: (emotion: string) => void;
}

export default function EmotionSelector({
  emotions,
  selectedEmotion,
  onSelect,
}: EmotionSelectorProps) {
  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold text-white mb-4">
        How are you feeling?
      </h3>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
        {emotions.map((emotion) => {
          const isSelected = selectedEmotion === emotion;
          const colors = getEmotionColor(emotion);
          const emoji = getEmotionEmoji(emotion);

          return (
            <button
              key={emotion}
              onClick={() => onSelect(emotion)}
              className={`
                relative p-4 rounded-lg transition-all duration-200
                ${
                  isSelected
                    ? 'ring-2 ring-white scale-105'
                    : 'hover:scale-105 hover:ring-1 hover:ring-white/50'
                }
              `}
              style={{
                background: isSelected
                  ? `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`
                  : `linear-gradient(135deg, ${colors.primary}40, ${colors.secondary}40)`,
              }}
            >
              <div className="flex flex-col items-center gap-2">
                <span className="text-3xl">{emoji}</span>
                <span className="text-sm font-medium text-white capitalize">
                  {emotion}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
