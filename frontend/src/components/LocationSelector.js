import React, { useState } from 'react';
import { MapPin, ChevronDown, Navigation } from 'lucide-react';
import { useLocation } from '../context/LocationContext';

const LocationSelector = ({ className = '' }) => {
  const { userLocation, setUserLocation, cities, isDetecting, refreshLocation } = useLocation();
  const [isOpen, setIsOpen] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleLocationChange = (cityName) => {
    setUserLocation(cityName);
    setIsOpen(false);
  };

  const handleRefreshLocation = async () => {
    setIsRefreshing(true);
    try {
      await refreshLocation();
    } finally {
      setIsRefreshing(false);
    }
  };

  if (isDetecting) {
    return (
      <div className={`flex items-center text-gray-600 ${className}`}>
        <MapPin className="w-4 h-4 mr-1 animate-pulse" />
        <span className="text-sm">Detecting...</span>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      {/* Location Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 bg-white border border-gray-300 rounded-lg hover:border-green-500 transition-all focus:outline-none focus:ring-2 focus:ring-green-500"
      >
        <MapPin className="w-4 h-4 text-green-600" />
        <span className="text-sm font-medium text-gray-700">
          {userLocation || 'Select Location'}
        </span>
        <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown */}
          <div className="absolute top-full mt-2 left-0 w-64 bg-white border border-gray-200 rounded-lg shadow-xl z-20 overflow-hidden">
            {/* Auto-detect option */}
            <button
              onClick={handleRefreshLocation}
              disabled={isRefreshing}
              className="w-full flex items-center space-x-3 px-4 py-3 hover:bg-green-50 transition-colors border-b border-gray-100"
            >
              <Navigation className={`w-4 h-4 text-green-600 ${isRefreshing ? 'animate-spin' : ''}`} />
              <div className="flex-1 text-left">
                <div className="text-sm font-medium text-gray-900">
                  {isRefreshing ? 'Detecting...' : 'Auto-detect Location'}
                </div>
                <div className="text-xs text-gray-500">Use GPS to find you</div>
              </div>
            </button>

            {/* Cities list */}
            <div className="max-h-64 overflow-y-auto">
              {cities.map((city) => (
                <button
                  key={city.name}
                  onClick={() => handleLocationChange(city.name)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 hover:bg-gray-50 transition-colors ${
                    userLocation === city.name ? 'bg-green-50 border-l-4 border-green-600' : ''
                  }`}
                >
                  <MapPin className={`w-4 h-4 ${userLocation === city.name ? 'text-green-600' : 'text-gray-400'}`} />
                  <div className="flex-1 text-left">
                    <div className={`text-sm font-medium ${
                      userLocation === city.name ? 'text-green-700' : 'text-gray-900'
                    }`}>
                      {city.name}
                    </div>
                    <div className="text-xs text-gray-500">{city.region} Region</div>
                  </div>
                  {userLocation === city.name && (
                    <div className="w-2 h-2 bg-green-600 rounded-full" />
                  )}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default LocationSelector;
