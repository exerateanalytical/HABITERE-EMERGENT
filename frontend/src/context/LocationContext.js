import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import {
  autoDetectAndStoreLocation,
  getStoredLocation,
  storeLocation,
  CAMEROON_CITIES
} from '../utils/locationUtils';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const LocationContext = createContext();

export const useLocation = () => {
  const context = useContext(LocationContext);
  if (!context) {
    throw new Error('useLocation must be used within LocationProvider');
  }
  return context;
};

export const LocationProvider = ({ children }) => {
  const [userLocation, setUserLocation] = useState(null);
  const [isDetecting, setIsDetecting] = useState(true);
  const [viewMode, setViewMode] = useState('my-location'); // 'my-location', 'nearby', 'all'

  // Initialize location on mount
  useEffect(() => {
    initializeLocation();
  }, []);

  const initializeLocation = async () => {
    setIsDetecting(true);
    try {
      // Try to get stored location first
      let location = getStoredLocation();
      
      if (!location) {
        // Auto-detect if not stored
        location = await autoDetectAndStoreLocation();
      }
      
      setUserLocation(location);
      console.log('[LocationContext] Initialized with location:', location);
    } catch (error) {
      console.error('[LocationContext] Initialization error:', error);
      // Default to Douala
      setUserLocation('Douala');
      storeLocation('Douala');
    } finally {
      setIsDetecting(false);
    }
  };

  const updateLocation = async (newLocation) => {
    try {
      setUserLocation(newLocation);
      storeLocation(newLocation);
      
      // Update in backend if user is authenticated
      try {
        await axios.put(
          `${BACKEND_URL}/api/users/location`,
          null,
          {
            params: { location: newLocation },
            withCredentials: true
          }
        );
        console.log('[LocationContext] Location updated in backend:', newLocation);
      } catch (error) {
        // Silently fail if user not authenticated
        console.log('[LocationContext] Backend update skipped (not authenticated)');
      }
    } catch (error) {
      console.error('[LocationContext] Error updating location:', error);
    }
  };

  const changeViewMode = (mode) => {
    setViewMode(mode);
    console.log('[LocationContext] View mode changed to:', mode);
  };

  const value = {
    userLocation,
    setUserLocation: updateLocation,
    viewMode,
    setViewMode: changeViewMode,
    isDetecting,
    cities: CAMEROON_CITIES,
    refreshLocation: initializeLocation
  };

  return (
    <LocationContext.Provider value={value}>
      {children}
    </LocationContext.Provider>
  );
};

export default LocationContext;
