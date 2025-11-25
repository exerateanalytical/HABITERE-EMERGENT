import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Star, 
  MapPin, 
  User, 
  Clock,
  CheckCircle,
  // Unique Service Icons
  HardHat,          // Construction
  Droplets,         // Plumbing
  Zap,              // Electrical
  Paintbrush,       // Painting
  Hammer,           // Carpentry
  Sofa,             // Interior Design
  Sparkles,         // Cleaning
  PenTool,          // Architecture
  Boxes,            // Bricklaying
  Drill,            // Borehole Drilling
  ClipboardCheck,   // Evaluation
  Package,          // Building Materials
  Lamp,             // Furnishing
  Trees,            // Landscaping
  Wind,             // HVAC
  Home,             // Roofing
  Layers,           // Flooring
  Shield            // Default
} from 'lucide-react';

const serviceIcons = {
  'construction': HardHat,
  'plumbing': Droplets,
  'electrical': Zap,
  'painting': Paintbrush,
  'carpentry': Hammer,
  'interior_design': Sofa,
  'cleaning': Sparkles,
  'architecture': PenTool,
  'bricklaying': Boxes,
  'borehole_drilling': Drill,
  'evaluation': ClipboardCheck,
  'materials': Package,
  'furnishing': Lamp,
  'landscaping': Trees,
  'hvac': Wind,
  'roofing': Home,
  'flooring': Layers,
  'default': Shield
};

const serviceColors = {
  'construction': 'bg-orange-500',
  'plumbing': 'bg-blue-500',
  'electrical': 'bg-yellow-500',
  'painting': 'bg-purple-500',
  'carpentry': 'bg-amber-600',
  'interior_design': 'bg-pink-500',
  'cleaning': 'bg-cyan-500',
  'architecture': 'bg-indigo-500',
  'bricklaying': 'bg-red-600',
  'borehole_drilling': 'bg-teal-600',
  'evaluation': 'bg-emerald-500',
  'materials': 'bg-stone-600',
  'furnishing': 'bg-rose-500',
  'landscaping': 'bg-green-600',
  'hvac': 'bg-sky-500',
  'roofing': 'bg-slate-600',
  'flooring': 'bg-amber-700',
  'default': 'bg-gray-500'
};

const ServiceCard = ({ service, isCarousel = false }) => {
  const IconComponent = serviceIcons[service.category] || serviceIcons.default;
  const iconColor = serviceColors[service.category] || serviceColors.default;
  
  // Enhanced service data with defaults
  const enhancedService = {
    rating: 4.5,
    completedProjects: 15,
    responseTime: '< 2 hours',
    isOnline: true,
    isVerified: true,
    ...service
  };

  if (isCarousel) {
    return (
      <Link to={`/services/${service.id}`} className="block">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg hover:border-blue-200 transition-all duration-300 group">
          {/* Compact Image */}
          <div className="relative h-32 overflow-hidden">
            <img
              src={service.images?.[0] || 'https://images.unsplash.com/photo-1505798577917-a65157d3320a'}
              alt={service.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
            
            {/* Status Indicators */}
            <div className="absolute top-2 left-2 flex flex-col gap-1">
              <div className="bg-blue-600 bg-opacity-90 text-white px-2 py-1 rounded text-xs font-medium flex items-center">
                <IconComponent className="w-3 h-3 mr-1" />
                {service.category?.replace('_', ' ') || 'Service'}
              </div>
            </div>

            {enhancedService.isOnline && (
              <div className="absolute top-2 right-2 flex items-center bg-green-500 text-white text-xs px-2 py-1 rounded">
                <div className="w-1.5 h-1.5 bg-white rounded-full mr-1 animate-pulse"></div>
                Online
              </div>
            )}
          </div>

          {/* Compact Content */}
          <div className="p-3">
            <h3 className="font-medium text-gray-900 text-sm mb-1 line-clamp-1 group-hover:text-blue-600 transition-colors">
              {service.title}
            </h3>
            
            <div className="flex items-center text-gray-500 text-xs mb-2">
              <MapPin className="w-3 h-3 mr-1 flex-shrink-0" />
              <span className="truncate">{service.location}</span>
            </div>

            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center">
                <Star className="w-3 h-3 text-yellow-400 fill-current" />
                <span className="font-medium text-gray-900 ml-1">
                  {enhancedService.rating.toFixed(1)}
                </span>
              </div>
              <span className="text-gray-500">
                {enhancedService.completedProjects} projects
              </span>
            </div>
          </div>
        </div>
      </Link>
    );
  }

  // Full service card for service pages
  return (
    <Link to={`/services/${service.id}`} className="block">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg hover:border-blue-200 transition-all duration-300 group h-full">
        {/* Image */}
        <div className="relative h-48 overflow-hidden">
          <img
            src={service.images?.[0] || 'https://images.unsplash.com/photo-1505798577917-a65157d3320a'}
            alt={service.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
          
          {/* Status Overlays */}
          <div className="absolute top-3 left-3 flex flex-col gap-2">
            <div className="bg-blue-600 bg-opacity-90 text-white px-2 py-1 rounded-lg text-xs font-medium flex items-center">
              <IconComponent className="w-3 h-3 mr-1" />
              {service.category?.replace('_', ' ') || 'Service'}
            </div>
            
            {enhancedService.isVerified && (
              <div className="bg-green-600 bg-opacity-90 text-white px-2 py-1 rounded-lg text-xs font-medium flex items-center">
                <CheckCircle className="w-3 h-3 mr-1" />
                Verified
              </div>
            )}
          </div>

          {enhancedService.isOnline && (
            <div className="absolute top-3 right-3 flex items-center bg-green-500 text-white text-xs px-2 py-1 rounded-lg">
              <div className="w-2 h-2 bg-white rounded-full mr-1 animate-pulse"></div>
              Online
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-4">
          <h3 className="font-semibold text-gray-900 text-lg mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors">
            {service.title}
          </h3>
          
          <div className="flex items-center text-gray-500 text-sm mb-3">
            <MapPin className="w-4 h-4 mr-1 flex-shrink-0" />
            <span className="truncate">{service.location}</span>
          </div>

          {/* Description */}
          <p className="text-gray-600 text-sm mb-4 line-clamp-2">
            {service.description}
          </p>

          {/* Rating and Stats */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center">
              <Star className="w-4 h-4 text-yellow-400 fill-current" />
              <span className="font-medium text-gray-900 ml-1">
                {enhancedService.rating.toFixed(1)}
              </span>
              <span className="text-gray-500 text-sm ml-1">
                ({enhancedService.completedProjects} projects)
              </span>
            </div>
          </div>

          {/* Response Time and Price */}
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center text-gray-600">
              <Clock className="w-4 h-4 mr-1" />
              <span>Responds in {enhancedService.responseTime}</span>
            </div>
            
            {service.price_range && (
              <div className="font-semibold text-blue-600">
                {service.price_range}
              </div>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
};

export default ServiceCard;