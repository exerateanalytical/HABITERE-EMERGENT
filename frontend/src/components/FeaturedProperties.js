import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { 
  ChevronLeft, 
  ChevronRight, 
  Star, 
  MapPin, 
  BedDouble,
  Bath,
  Square,
  Eye,
  Heart,
  ArrowRight
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const FeaturedProperties = ({ title = "Featured Properties", showAll = true, limit = 8 }) => {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);
  const [favorites, setFavorites] = useState(new Set());
  const carouselRef = useRef(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    fetchProperties();
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (isAutoPlaying && properties.length > 0) {
      intervalRef.current = setInterval(() => {
        setCurrentIndex(prev => {
          const maxIndex = Math.max(0, properties.length - getVisibleCards());
          return prev >= maxIndex ? 0 : prev + 1;
        });
      }, 4000); // Slower auto-scroll for properties
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isAutoPlaying, properties.length]);

  const fetchProperties = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/properties?limit=${limit}`);
      setProperties(response.data || []);
    } catch (error) {
      console.error('Error fetching properties:', error);
    } finally {
      setLoading(false);
    }
  };

  const getVisibleCards = () => {
    if (typeof window === 'undefined') return 3;
    if (window.innerWidth < 640) return 1;
    if (window.innerWidth < 1024) return 2;
    return 3;
  };

  const nextSlide = () => {
    const maxIndex = Math.max(0, properties.length - getVisibleCards());
    setCurrentIndex(prev => (prev >= maxIndex ? 0 : prev + 1));
  };

  const prevSlide = () => {
    const maxIndex = Math.max(0, properties.length - getVisibleCards());
    setCurrentIndex(prev => (prev <= 0 ? maxIndex : prev - 1));
  };

  const toggleFavorite = (propertyId, event) => {
    event.preventDefault();
    event.stopPropagation();
    
    setFavorites(prev => {
      const newFavorites = new Set(prev);
      if (newFavorites.has(propertyId)) {
        newFavorites.delete(propertyId);
      } else {
        newFavorites.add(propertyId);
      }
      return newFavorites;
    });
  };

  const handleMouseEnter = () => {
    setIsAutoPlaying(false);
  };

  const handleMouseLeave = () => {
    setIsAutoPlaying(true);
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('fr-CM', {
      style: 'currency',
      currency: 'XAF',
      minimumFractionDigits: 0
    }).format(price);
  };

  if (loading) {
    return (
      <div className="py-8" data-testid="properties-carousel-loading">
        <div className="flex items-center justify-between mb-6">
          <div className="h-6 bg-gray-300 rounded w-48 animate-pulse"></div>
          <div className="h-4 bg-gray-300 rounded w-20 animate-pulse"></div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(3)].map((_, index) => (
            <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden animate-pulse">
              <div className="h-48 bg-gray-300"></div>
              <div className="p-4 space-y-3">
                <div className="h-4 bg-gray-300 rounded w-3/4"></div>
                <div className="h-3 bg-gray-300 rounded w-1/2"></div>
                <div className="h-6 bg-gray-300 rounded w-2/3"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (properties.length === 0) {
    return null;
  }

  return (
    <div className="py-8" data-testid="properties-carousel">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
        {showAll && (
          <Link 
            to="/properties" 
            className="flex items-center text-blue-600 hover:text-blue-700 font-medium group"
          >
            View All
            <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
          </Link>
        )}
      </div>

      {/* Carousel */}
      <div 
        className="relative"
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        {/* Navigation Buttons */}
        {properties.length > getVisibleCards() && (
          <>
            <button
              onClick={prevSlide}
              className="absolute -left-4 top-1/2 transform -translate-y-1/2 z-10 bg-white shadow-lg hover:shadow-xl rounded-full p-3 transition-all duration-200 hover:scale-105 border border-gray-100"
              data-testid="properties-carousel-prev-btn"
            >
              <ChevronLeft className="w-5 h-5 text-gray-600" />
            </button>

            <button
              onClick={nextSlide}
              className="absolute -right-4 top-1/2 transform -translate-y-1/2 z-10 bg-white shadow-lg hover:shadow-xl rounded-full p-3 transition-all duration-200 hover:scale-105 border border-gray-100"
              data-testid="properties-carousel-next-btn"
            >
              <ChevronRight className="w-5 h-5 text-gray-600" />
            </button>
          </>
        )}

        {/* Carousel Track */}
        <div className="overflow-hidden">
          <div 
            ref={carouselRef}
            className="flex transition-transform duration-500 ease-out"
            style={{
              transform: `translateX(-${currentIndex * (100 / getVisibleCards())}%)`
            }}
          >
            {properties.map((property, index) => (
              <PropertyCard 
                key={property.id || index} 
                property={property} 
                isFavorite={favorites.has(property.id)}
                onToggleFavorite={toggleFavorite}
                formatPrice={formatPrice}
              />
            ))}
          </div>
        </div>

        {/* Indicators */}
        {properties.length > getVisibleCards() && (
          <div className="flex justify-center space-x-2 mt-6">
            {Array.from({ 
              length: Math.max(1, Math.ceil((properties.length - getVisibleCards() + 1)))
            }).map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentIndex(index)}
                className={`w-2 h-2 rounded-full transition-colors duration-200 ${
                  index === currentIndex ? 'bg-blue-600' : 'bg-gray-300 hover:bg-gray-400'
                }`}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const PropertyCard = ({ property, isFavorite, onToggleFavorite, formatPrice }) => {
  return (
    <div 
      className="flex-shrink-0 px-3" 
      style={{ width: `${100 / 3}%` }} // 3 cards visible on desktop
      data-testid={`property-card-${property.id}`}
    >
      <Link to={`/properties/${property.id}`}>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg hover:border-blue-200 transition-all duration-300 group h-full">
          {/* Image */}
          <div className="relative h-48 overflow-hidden">
            <img
              src={property.images?.[0] || 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2'}
              alt={property.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
            
            {/* Status Badges */}
            <div className="absolute top-3 left-3 flex flex-col gap-2">
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                property.listing_type === 'rent' ? 'bg-green-600 text-white' : 
                property.listing_type === 'sale' ? 'bg-blue-600 text-white' : 'bg-orange-600 text-white'
              }`}>
                {property.listing_type === 'rent' ? 'For Rent' : 
                 property.listing_type === 'sale' ? 'For Sale' : 'For Lease'}
              </span>
              
              {property.verified && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-600 bg-opacity-90 text-white">
                  Verified
                </span>
              )}
            </div>

            {/* Favorite Button */}
            <button
              onClick={(e) => onToggleFavorite(property.id, e)}
              className={`absolute top-3 right-3 p-2 rounded-full transition-colors ${
                isFavorite ? 'bg-red-500 text-white' : 'bg-white bg-opacity-80 text-gray-600 hover:text-red-500'
              }`}
            >
              <Heart className={`w-4 h-4 ${isFavorite ? 'fill-current' : ''}`} />
            </button>
          </div>

          {/* Content */}
          <div className="p-4">
            <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors">
              {property.title}
            </h3>
            
            <div className="flex items-center text-gray-500 text-sm mb-3">
              <MapPin className="w-4 h-4 mr-1 flex-shrink-0" />
              <span className="truncate">{property.location}</span>
            </div>

            {/* Property Details */}
            <div className="flex items-center space-x-4 text-sm text-gray-600 mb-3">
              {property.bedrooms > 0 && (
                <div className="flex items-center">
                  <BedDouble className="w-4 h-4 mr-1" />
                  <span>{property.bedrooms}</span>
                </div>
              )}
              {property.bathrooms > 0 && (
                <div className="flex items-center">
                  <Bath className="w-4 h-4 mr-1" />
                  <span>{property.bathrooms}</span>
                </div>
              )}
              {property.area_sqm && (
                <div className="flex items-center">
                  <Square className="w-4 h-4 mr-1" />
                  <span>{property.area_sqm}m²</span>
                </div>
              )}
            </div>

            {/* Price */}
            <div className="flex items-center justify-between">
              <div className="text-lg font-bold text-blue-600">
                {formatPrice(property.price)}
                {property.listing_type === 'rent' && (
                  <span className="text-sm text-gray-500 font-normal">/month</span>
                )}
              </div>
              
              <div className="flex items-center text-sm text-gray-500">
                <Eye className="w-4 h-4 mr-1" />
                <span>View</span>
              </div>
            </div>
          </div>
        </div>
      </Link>
    </div>
  );
};

export default FeaturedProperties;