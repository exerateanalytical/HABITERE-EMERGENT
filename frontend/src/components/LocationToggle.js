import React from 'react';
import { MapPin, Compass, Globe } from 'lucide-react';
import { useLocation } from '../context/LocationContext';

const LocationToggle = ({ className = '' }) => {
  const { viewMode, setViewMode, userLocation } = useLocation();

  const modes = [
    {
      id: 'my-location',
      label: 'My Location',
      icon: MapPin,
      description: `Properties in ${userLocation || 'your city'}`
    },
    {
      id: 'nearby',
      label: 'Nearby',
      icon: Compass,
      description: 'Properties in nearby cities'
    },
    {
      id: 'all',
      label: 'All Locations',
      icon: Globe,
      description: 'Properties across Cameroon'
    }
  ];

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-1 ${className}`}>
      <div className="grid grid-cols-3 gap-1">
        {modes.map((mode) => {
          const Icon = mode.icon;
          const isActive = viewMode === mode.id;
          
          return (
            <button
              key={mode.id}
              onClick={() => setViewMode(mode.id)}
              className={`
                relative px-3 py-2 rounded-lg transition-all
                ${isActive
                  ? 'bg-green-600 text-white shadow-md'
                  : 'bg-transparent text-gray-600 hover:bg-gray-50'
                }
              `}
            >
              <div className="flex flex-col items-center space-y-1">
                <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-gray-500'}`} />
                <span className={`text-xs font-medium ${isActive ? 'text-white' : 'text-gray-700'}`}>
                  {mode.label}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default LocationToggle;
