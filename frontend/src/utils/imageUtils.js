const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * Get the full image URL, handling relative paths from backend
 * @param {string} url - Image URL (relative or absolute)
 * @param {string} fallback - Fallback image URL if none provided
 * @returns {string} - Full image URL
 */
export const getImageUrl = (url, fallback = 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&q=80') => {
  if (!url) return fallback;
  // If URL starts with /uploads/, prepend backend URL
  if (url.startsWith('/uploads/')) {
    return `${BACKEND_URL}${url}`;
  }
  // If it's already a full URL (http:// or https://), return as is
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }
  // Otherwise, assume it's a relative path and prepend backend URL
  return `${BACKEND_URL}/${url}`;
};

/**
 * Get service image URL with appropriate fallback
 * @param {string} url - Image URL
 * @returns {string} - Full image URL
 */
export const getServiceImageUrl = (url) => {
  return getImageUrl(url, 'https://images.unsplash.com/photo-1505798577917-a65157d3320a?w=800&q=80');
};

/**
 * Get property image URL with appropriate fallback
 * @param {string} url - Image URL
 * @returns {string} - Full image URL
 */
export const getPropertyImageUrl = (url) => {
  return getImageUrl(url, 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&q=80');
};
