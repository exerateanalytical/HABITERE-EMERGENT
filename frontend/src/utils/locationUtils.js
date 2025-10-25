/**
 * Location Utilities for Habitere Platform
 * 
 * Provides location detection, city mapping, and location preference management
 * for personalized property filtering based on user location.
 */

// Major cities in Cameroon
export const CAMEROON_CITIES = [
  { name: 'Douala', region: 'Littoral', coordinates: { lat: 4.0511, lng: 9.7679 } },
  { name: 'Yaounde', region: 'Centre', coordinates: { lat: 3.8480, lng: 11.5021 } },
  { name: 'Bafoussam', region: 'West', coordinates: { lat: 5.4781, lng: 10.4178 } },
  { name: 'Bamenda', region: 'Northwest', coordinates: { lat: 5.9597, lng: 10.1591 } },
  { name: 'Garoua', region: 'North', coordinates: { lat: 9.3014, lng: 13.3956 } },
  { name: 'Limbe', region: 'Southwest', coordinates: { lat: 4.0174, lng: 9.2044 } },
  { name: 'Kribi', region: 'South', coordinates: { lat: 2.9398, lng: 9.9108 } }
];

/**
 * Get user's location from browser geolocation API
 * Returns coordinates that can be mapped to nearest city
 */
export const detectUserLocation = () => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation not supported'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        resolve({ lat: latitude, lng: longitude });
      },
      (error) => {
        reject(error);
      },
      {
        timeout: 5000,
        maximumAge: 300000, // Cache for 5 minutes
        enableHighAccuracy: false
      }
    );
  });
};

/**
 * Calculate distance between two coordinates using Haversine formula
 * Returns distance in kilometers
 */
const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371; // Radius of Earth in kilometers
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = 
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
};

/**
 * Find nearest city to given coordinates
 */
export const findNearestCity = (lat, lng) => {
  let nearestCity = CAMEROON_CITIES[0];
  let minDistance = calculateDistance(
    lat,
    lng,
    CAMEROON_CITIES[0].coordinates.lat,
    CAMEROON_CITIES[0].coordinates.lng
  );

  CAMEROON_CITIES.forEach(city => {
    const distance = calculateDistance(
      lat,
      lng,
      city.coordinates.lat,
      city.coordinates.lng
    );
    if (distance < minDistance) {
      minDistance = distance;
      nearestCity = city;
    }
  });

  return nearestCity.name;
};

/**
 * Get user's location preference from localStorage
 */
export const getStoredLocation = () => {
  try {
    return localStorage.getItem('userLocation');
  } catch (error) {
    console.error('Error reading location from localStorage:', error);
    return null;
  }
};

/**
 * Store user's location preference in localStorage
 */
export const storeLocation = (location) => {
  try {
    localStorage.setItem('userLocation', location);
    console.log('Location stored:', location);
  } catch (error) {
    console.error('Error storing location:', error);
  }
};

/**
 * Clear stored location preference
 */
export const clearStoredLocation = () => {
  try {
    localStorage.removeItem('userLocation');
  } catch (error) {
    console.error('Error clearing location:', error);
  }
};

/**
 * Auto-detect and store user location
 * Returns detected city name or null if detection fails
 */
export const autoDetectAndStoreLocation = async () => {
  try {
    // First check if already stored
    const stored = getStoredLocation();
    if (stored) {
      console.log('Using stored location:', stored);
      return stored;
    }

    // Try to detect from browser
    console.log('Attempting to detect user location...');
    const coords = await detectUserLocation();
    const nearestCity = findNearestCity(coords.lat, coords.lng);
    
    console.log('Detected location:', nearestCity);
    storeLocation(nearestCity);
    
    return nearestCity;
  } catch (error) {
    console.error('Location detection failed:', error);
    // Default to Douala (largest city) if detection fails
    const defaultCity = 'Douala';
    storeLocation(defaultCity);
    return defaultCity;
  }
};

/**
 * Get location display name with region
 */
export const getCityWithRegion = (cityName) => {
  const city = CAMEROON_CITIES.find(c => c.name.toLowerCase() === cityName.toLowerCase());
  return city ? `${city.name}, ${city.region}` : cityName;
};

/**
 * Check if a location string contains a specific city
 */
export const locationContainsCity = (locationString, cityName) => {
  if (!locationString || !cityName) return false;
  return locationString.toLowerCase().includes(cityName.toLowerCase());
};
