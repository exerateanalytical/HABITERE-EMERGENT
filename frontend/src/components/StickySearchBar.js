import React, { useState, useEffect } from 'react';
import { Search, SlidersHorizontal, X } from 'lucide-react';

const StickySearchBar = () => {
  const [isSticky, setIsSticky] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    type: '',
    location: '',
    price: ''
  });

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 400) {
        setIsSticky(true);
      } else {
        setIsSticky(false);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const clearFilters = () => {
    setFilters({ type: '', location: '', price: '' });
  };

  const activeFilterCount = Object.values(filters).filter(v => v).length;

  return (
    <>
      {/* Sticky Search Bar */}
      <div
        className={`fixed top-0 left-0 right-0 z-40 bg-white shadow-lg transition-transform duration-300 safe-area-top ${
          isSticky ? 'translate-y-0' : '-translate-y-full'
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="flex gap-2">
            {/* Search Input */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search properties..."
                className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base min-h-[48px]"
              />
            </div>

            {/* Filter Button */}
            <button
              onClick={() => setShowFilters(true)}
              className="relative px-4 bg-blue-600 active:bg-blue-700 text-white rounded-xl flex items-center gap-2 touch-manipulation min-w-[48px] min-h-[48px] transform active:scale-95 transition-all duration-100"
              aria-label="Open filters"
            >
              <SlidersHorizontal className="w-5 h-5" />
              {activeFilterCount > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
                  {activeFilterCount}
                </span>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Sheet Filter Modal */}
      {showFilters && (
        <>
          {/* Overlay */}
          <div
            className="fixed inset-0 bg-black/50 z-50 transition-opacity duration-300"
            onClick={() => setShowFilters(false)}
          ></div>

          {/* Bottom Sheet */}
          <div className="fixed bottom-0 left-0 right-0 z-50 bg-white rounded-t-3xl shadow-2xl max-h-[80vh] overflow-y-auto animate-slide-up safe-area-bottom">
            {/* Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h3 className="text-xl font-bold text-gray-900">Filters</h3>
              <button
                onClick={() => setShowFilters(false)}
                className="w-10 h-10 rounded-full bg-gray-100 active:bg-gray-200 flex items-center justify-center touch-manipulation"
                aria-label="Close filters"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Filter Content */}
            <div className="p-6 space-y-6">
              {/* Property Type */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">Property Type</label>
                <div className="flex flex-wrap gap-2">
                  {['House', 'Apartment', 'Land', 'Commercial'].map((type) => (
                    <button
                      key={type}
                      onClick={() => setFilters({ ...filters, type })}
                      className={`px-5 py-3 rounded-full border-2 font-semibold text-sm min-h-[48px] touch-manipulation transition-all duration-100 transform active:scale-95 ${
                        filters.type === type
                          ? 'bg-blue-600 border-blue-600 text-white'
                          : 'bg-white border-gray-200 text-gray-700 active:border-blue-400'
                      }`}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>

              {/* Location */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">Location</label>
                <select
                  value={filters.location}
                  onChange={(e) => setFilters({ ...filters, location: e.target.value })}
                  className="w-full px-4 py-4 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 text-base min-h-[56px]"
                >
                  <option value="">All Locations</option>
                  <option value="douala">Douala</option>
                  <option value="yaounde">Yaoundé</option>
                  <option value="bafoussam">Bafoussam</option>
                  <option value="bamenda">Bamenda</option>
                </select>
              </div>

              {/* Price Range */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">Price Range</label>
                <select
                  value={filters.price}
                  onChange={(e) => setFilters({ ...filters, price: e.target.value })}
                  className="w-full px-4 py-4 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 text-base min-h-[56px]"
                >
                  <option value="">Any Price</option>
                  <option value="0-100k">Under 100K XAF</option>
                  <option value="100k-500k">100K - 500K XAF</option>
                  <option value="500k-1m">500K - 1M XAF</option>
                  <option value="1m+">Over 1M XAF</option>
                </select>
              </div>
            </div>

            {/* Footer Actions */}
            <div className="sticky bottom-0 bg-white border-t border-gray-200 p-6 flex gap-3">
              <button
                onClick={clearFilters}
                className="flex-1 px-6 py-4 border-2 border-gray-300 text-gray-700 font-bold rounded-xl min-h-[56px] touch-manipulation active:bg-gray-100 transition-all duration-100 transform active:scale-95"
              >
                Clear All
              </button>
              <button
                onClick={() => setShowFilters(false)}
                className="flex-1 px-6 py-4 bg-gradient-to-r from-blue-600 to-purple-600 active:from-blue-700 active:to-purple-700 text-white font-bold rounded-xl min-h-[56px] touch-manipulation transition-all duration-100 transform active:scale-95"
              >
                Apply Filters
              </button>
            </div>
          </div>
        </>
      )}
    </>
  );
};

// Add animation to App.css
export default StickySearchBar;
