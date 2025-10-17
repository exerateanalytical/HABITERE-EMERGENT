import React from 'react';

/**
 * PropertyCardSkeleton - Enhanced skeleton for property cards
 * Matches actual PropertyCard structure for better perceived performance
 */
export const PropertyCardSkeleton = ({ className = '' }) => {
  return (
    <div className={`bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden ${className}`}>
      {/* Image Skeleton */}
      <div className="relative">
        <div className="h-48 sm:h-56 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 animate-shimmer bg-[length:200%_100%]"></div>
        
        {/* Badge Skeletons */}
        <div className="absolute top-3 left-3 flex gap-2">
          <div className="h-6 w-16 bg-gray-300/80 rounded-full animate-pulse"></div>
          <div className="h-6 w-16 bg-gray-300/80 rounded-full animate-pulse"></div>
        </div>
        
        {/* Heart Icon Skeleton */}
        <div className="absolute top-3 right-3">
          <div className="w-9 h-9 bg-gray-300/80 rounded-full animate-pulse"></div>
        </div>
      </div>
      
      {/* Content Skeleton */}
      <div className="p-4 space-y-3">
        {/* Price */}
        <div className="h-7 bg-gray-200 rounded w-2/3 animate-pulse"></div>
        
        {/* Title */}
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 rounded w-full animate-pulse"></div>
          <div className="h-4 bg-gray-200 rounded w-4/5 animate-pulse"></div>
        </div>
        
        {/* Location */}
        <div className="h-3 bg-gray-200 rounded w-3/5 animate-pulse"></div>
        
        {/* Features */}
        <div className="flex gap-4 pt-2">
          <div className="h-4 bg-gray-200 rounded w-16 animate-pulse"></div>
          <div className="h-4 bg-gray-200 rounded w-16 animate-pulse"></div>
          <div className="h-4 bg-gray-200 rounded w-16 animate-pulse"></div>
        </div>
        
        {/* Footer */}
        <div className="flex items-center justify-between pt-3 border-t border-gray-100">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gray-200 rounded-full animate-pulse"></div>
            <div className="h-3 bg-gray-200 rounded w-20 animate-pulse"></div>
          </div>
          <div className="h-8 w-20 bg-gray-200 rounded-lg animate-pulse"></div>
        </div>
      </div>
    </div>
  );
};

/**
 * ServiceCardSkeleton - Enhanced skeleton for service cards
 * Matches actual ServiceCard structure
 */
export const ServiceCardSkeleton = ({ className = '' }) => {
  return (
    <div className={`bg-white rounded-2xl shadow-sm border border-gray-200 p-4 sm:p-5 ${className}`}>
      {/* Header with Icon and Status */}
      <div className="flex items-start justify-between mb-4">
        <div className="w-14 h-14 bg-gradient-to-br from-gray-200 to-gray-300 rounded-xl animate-pulse"></div>
        <div className="h-5 w-16 bg-gray-200 rounded-full animate-pulse"></div>
      </div>
      
      {/* Title and Category */}
      <div className="space-y-2 mb-3">
        <div className="h-5 bg-gray-200 rounded w-3/4 animate-pulse"></div>
        <div className="h-3 bg-gray-200 rounded w-1/2 animate-pulse"></div>
      </div>
      
      {/* Location */}
      <div className="h-3 bg-gray-200 rounded w-2/3 mb-4 animate-pulse"></div>
      
      {/* Stats */}
      <div className="flex items-center gap-4 mb-4">
        <div className="h-4 bg-gray-200 rounded w-16 animate-pulse"></div>
        <div className="h-4 bg-gray-200 rounded w-20 animate-pulse"></div>
      </div>
      
      {/* Button */}
      <div className="h-10 bg-gray-200 rounded-lg animate-pulse"></div>
    </div>
  );
};

/**
 * TextSkeleton - Generic text skeleton
 */
export const TextSkeleton = ({ width = 'full', height = 4, className = '' }) => {
  const widthClasses = {
    full: 'w-full',
    '3/4': 'w-3/4',
    '2/3': 'w-2/3',
    '1/2': 'w-1/2',
    '1/3': 'w-1/3',
    '1/4': 'w-1/4'
  };
  
  return (
    <div 
      className={`h-${height} bg-gray-200 rounded animate-pulse ${widthClasses[width]} ${className}`}
    ></div>
  );
};

/**
 * GridSkeleton - Skeleton for grid layouts
 */
export const GridSkeleton = ({ 
  count = 3, 
  CardComponent = PropertyCardSkeleton,
  cols = { mobile: 1, tablet: 2, desktop: 3 }
}) => {
  return (
    <div className={`grid grid-cols-${cols.mobile} sm:grid-cols-${cols.tablet} lg:grid-cols-${cols.desktop} gap-4 sm:gap-6`}>
      {[...Array(count)].map((_, index) => (
        <CardComponent key={index} />
      ))}
    </div>
  );
};

export default {
  PropertyCardSkeleton,
  ServiceCardSkeleton,
  TextSkeleton,
  GridSkeleton
};
