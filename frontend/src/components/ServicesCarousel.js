import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { 
  ChevronLeft, 
  ChevronRight, 
  Star, 
  MapPin, 
  Wrench,
  Building,
  Palette,
  Zap,
  Droplets,
  User,
  ArrowRight,
  Heart
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const serviceIcons = {
  'construction': Building,
  'plumbing': Droplets,
  'electrical': Zap,
  'painting': Palette,
  'carpentry': Wrench,
  'interior_design': Palette,
  'cleaning': Wrench,
  'architecture': Building,
  'bricklaying': Building,
  'borehole_drilling': Droplets,
  'evaluation': Building,
  'materials': Building,
  'furnishing': Wrench,
  'default': User
};

const ServicesCarousel = ({ title = "Professional Services", showAll = true, limit = 12 }) => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);
  const carouselRef = useRef(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    fetchServices();
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (isAutoPlaying && services.length > 0) {
      intervalRef.current = setInterval(() => {
        setCurrentIndex(prev => {
          const maxIndex = Math.max(0, services.length - getVisibleCards());
          return prev >= maxIndex ? 0 : prev + 1;
        });
      }, 3000);
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
  }, [isAutoPlaying, services.length]);

  const fetchServices = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/services?limit=${limit}`);
      const servicesData = response.data || [];
      
      // Add mock ratings and enhance data for carousel
      const enhancedServices = servicesData.map(service => ({
        ...service,
        rating: Math.random() * 2 + 3, // Random rating between 3-5
        completedProjects: Math.floor(Math.random() * 50) + 5,
        responseTime: ['< 1 hour', '< 2 hours', '< 4 hours'][Math.floor(Math.random() * 3)],
        isOnline: Math.random() > 0.3 // 70% chance of being online
      }));
      
      setServices(enhancedServices);
    } catch (error) {
      console.error('Error fetching services:', error);
    } finally {
      setLoading(false);
    }
  };

  const getVisibleCards = () => {
    if (typeof window === 'undefined') return 4;
    if (window.innerWidth < 640) return 2; // Show 2 cards on mobile
    if (window.innerWidth < 768) return 2;
    if (window.innerWidth < 1024) return 3;
    return 4;
  };

  const nextSlide = () => {
    const maxIndex = Math.max(0, services.length - getVisibleCards());
    setCurrentIndex(prev => (prev >= maxIndex ? 0 : prev + 1));
  };

  const prevSlide = () => {
    const maxIndex = Math.max(0, services.length - getVisibleCards());
    setCurrentIndex(prev => (prev <= 0 ? maxIndex : prev - 1));
  };

  // Touch/Mouse drag handlers for mobile
  const handleStart = (e) => {
    setIsDragging(true);
    const clientX = e.type === 'mousedown' ? e.clientX : e.touches[0].clientX;
    setStartX(clientX - carouselRef.current.offsetLeft);
    setScrollLeft(carouselRef.current.scrollLeft);
  };

  const handleMove = (e) => {
    if (!isDragging) return;
    e.preventDefault();
    const clientX = e.type === 'mousemove' ? e.clientX : e.touches[0].clientX;
    const x = clientX - carouselRef.current.offsetLeft;
    const walk = (x - startX) * 2;
    carouselRef.current.scrollLeft = scrollLeft - walk;
  };

  const handleEnd = () => {
    setIsDragging(false);
  };

  const handleMouseEnter = () => {
    setIsAutoPlaying(false);
  };

  const handleMouseLeave = () => {
    setIsAutoPlaying(true);
  };

  if (loading) {
    return (
      <div className="py-8" data-testid="services-carousel-loading">
        <div className="flex items-center justify-between mb-6">
          <div className="h-6 bg-gray-300 rounded w-48 animate-pulse"></div>
          <div className="h-4 bg-gray-300 rounded w-20 animate-pulse"></div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, index) => (
            <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 animate-pulse">
              <div className="w-full h-40 bg-gray-300 rounded-lg mb-4"></div>
              <div className="h-4 bg-gray-300 rounded mb-2"></div>
              <div className="h-3 bg-gray-300 rounded w-2/3 mb-2"></div>
              <div className="h-3 bg-gray-300 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (services.length === 0) {
    return null;
  }

  return (
    <div className="py-8" data-testid="services-carousel">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
        {showAll && (
          <Link 
            to="/services" 
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
        <button
          onClick={prevSlide}
          className="absolute -left-4 top-1/2 transform -translate-y-1/2 z-10 bg-white shadow-lg hover:shadow-xl rounded-full p-3 transition-all duration-200 hover:scale-105 border border-gray-100"
          data-testid="carousel-prev-btn"
        >
          <ChevronLeft className="w-5 h-5 text-gray-600" />
        </button>

        <button
          onClick={nextSlide}
          className="absolute -right-4 top-1/2 transform -translate-y-1/2 z-10 bg-white shadow-lg hover:shadow-xl rounded-full p-3 transition-all duration-200 hover:scale-105 border border-gray-100"
          data-testid="carousel-next-btn"
        >
          <ChevronRight className="w-5 h-5 text-gray-600" />
        </button>

        {/* Carousel Track */}
        <div className="overflow-hidden">
          <div 
            ref={carouselRef}
            className="flex transition-transform duration-500 ease-out"
            style={{
              transform: `translateX(-${currentIndex * (100 / getVisibleCards())}%)`
            }}
          >
            {services.map((service, index) => (
              <ServiceCard key={service.id || index} service={service} />
            ))}
          </div>
        </div>

        {/* Indicators */}
        <div className="flex justify-center space-x-2 mt-6">
          {Array.from({ 
            length: Math.max(1, Math.ceil((services.length - getVisibleCards() + 1)))
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
      </div>
    </div>
  );
};

const ServiceCard = ({ service }) => {
  const IconComponent = serviceIcons[service.category] || serviceIcons.default;

  return (
    <div 
      className="flex-shrink-0 px-2" 
      style={{ width: `${100 / 4}%` }} // 4 cards visible on desktop
      data-testid={`service-card-${service.id}`}
    >
      <Link to={`/services/${service.id}`}>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg hover:border-blue-200 transition-all duration-300 group h-full">
          {/* Image */}
          <div className="relative h-40 overflow-hidden">
            <img
              src={service.images?.[0] || 'https://images.unsplash.com/photo-1505798577917-a65157d3320a'}
              alt={service.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
            
            {/* Online Status */}
            {service.isOnline && (
              <div className="absolute top-3 right-3 flex items-center bg-green-500 text-white text-xs px-2 py-1 rounded-full">
                <div className="w-2 h-2 bg-white rounded-full mr-1 animate-pulse"></div>
                Online
              </div>
            )}

            {/* Category Badge */}
            <div className="absolute top-3 left-3 bg-blue-600 bg-opacity-90 text-white px-2 py-1 rounded-full text-xs font-medium flex items-center">
              <IconComponent className="w-3 h-3 mr-1" />
              {service.category?.replace('_', ' ') || 'Service'}
            </div>
          </div>

          {/* Content */}
          <div className="p-4">
            <h3 className="font-semibold text-gray-900 mb-1 line-clamp-1 group-hover:text-blue-600 transition-colors">
              {service.title}
            </h3>
            
            <div className="flex items-center text-gray-500 text-sm mb-2">
              <MapPin className="w-3 h-3 mr-1" />
              <span className="truncate">{service.location}</span>
            </div>

            {/* Rating */}
            <div className="flex items-center mb-2">
              <div className="flex items-center">
                <Star className="w-4 h-4 text-yellow-400 fill-current" />
                <span className="text-sm font-medium text-gray-900 ml-1">
                  {service.rating?.toFixed(1) || '4.5'}
                </span>
              </div>
              <span className="text-xs text-gray-500 ml-2">
                ({service.completedProjects} projects)
              </span>
            </div>

            {/* Stats */}
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>Responds in {service.responseTime}</span>
              {service.price_range && (
                <span className="font-medium text-blue-600">
                  {service.price_range}
                </span>
              )}
            </div>
          </div>
        </div>
      </Link>
    </div>
  );
};

// Responsive wrapper for different screen sizes
const ResponsiveServiceCard = ({ service }) => {
  return (
    <div className="w-full sm:w-1/2 md:w-1/3 lg:w-1/4 px-2">
      <ServiceCard service={service} />
    </div>
  );
};

export default ServicesCarousel;