import React from 'react';
import { Star } from 'lucide-react';

const StarRating = ({ rating, maxRating = 5, size = 'md', interactive = false, onChange }) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
    xl: 'w-8 h-8'
  };

  const handleClick = (value) => {
    if (interactive && onChange) {
      onChange(value);
    }
  };

  return (
    <div className="flex items-center">
      {[...Array(maxRating)].map((_, index) => {
        const starValue = index + 1;
        const isFilled = starValue <= rating;
        const isPartiallyFilled = starValue - 0.5 <= rating && starValue > rating;

        return (
          <button
            key={index}
            type="button"
            onClick={() => handleClick(starValue)}
            disabled={!interactive}
            className={`${interactive ? 'cursor-pointer hover:scale-110' : 'cursor-default'} transition-transform ${
              interactive ? '' : 'pointer-events-none'
            }`}
          >
            {isPartiallyFilled ? (
              <div className="relative">
                <Star className={`${sizes[size]} text-gray-300`} fill="currentColor" />
                <div className="absolute top-0 left-0 overflow-hidden" style={{ width: '50%' }}>
                  <Star className={`${sizes[size]} text-yellow-400`} fill="currentColor" />
                </div>
              </div>
            ) : (
              <Star
                className={`${sizes[size]} ${
                  isFilled ? 'text-yellow-400' : 'text-gray-300'
                }`}
                fill={isFilled ? 'currentColor' : 'none'}
              />
            )}
          </button>
        );
      })}
    </div>
  );
};

export default StarRating;
