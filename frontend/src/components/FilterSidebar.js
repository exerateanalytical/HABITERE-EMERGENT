import React, { useState, useEffect } from 'react';
import { 
  Filter, 
  X, 
  Search, 
  MapPin, 
  Home, 
  DollarSign, 
  Star, 
  Calendar, 
  Users, 
  ChevronDown, 
  ChevronUp,
  SlidersHorizontal,
  Building,
  Wrench,
  Bed,
  Bath,
  Car,
  Wifi,
  Tv,
  Coffee,
  Dumbbell,
  Shield
} from 'lucide-react';

const FilterSidebar = ({ 
  type = 'properties', // 'properties' or 'services'
  isOpen, 
  onClose, 
  onFiltersChange,
  className = ''
}) => {
  const [filters, setFilters] = useState({
    search: '',
    location: '',
    priceRange: { min: '', max: '' },
    propertyType: '',
    serviceCategory: '',
    bedrooms: '',
    bathrooms: '',
    rating: '',
    sortBy: 'newest',
    amenities: [],
    verified: false,
    available: true
  });

  const [expandedSections, setExpandedSections] = useState({
    location: true,
    price: true,
    type: true,
    amenities: false,
    rating: true,
    sort: true
  });

  const propertyTypes = [
    { value: 'house', label: '🏠 House', count: 245 },
    { value: 'apartment', label: '🏢 Apartment', count: 387 },
    { value: 'land', label: '🏞️ Land', count: 156 },
    { value: 'commercial', label: '🏪 Commercial', count: 89 },
    { value: 'villa', label: '🏖️ Villa', count: 67 },
    { value: 'studio', label: '🏠 Studio', count: 123 }
  ];

  const serviceCategories = [
    { value: 'construction', label: '🏗️ Construction', count: 89 },
    { value: 'plumbing', label: '🔧 Plumbing', count: 76 },
    { value: 'electrical', label: '⚡ Electrical', count: 65 },
    { value: 'cleaning', label: '🧹 Cleaning', count: 54 },
    { value: 'painting', label: '🎨 Painting', count: 43 },
    { value: 'carpentry', label: '🔨 Carpentry', count: 38 },
    { value: 'architecture', label: '📐 Architecture', count: 29 },
    { value: 'interior', label: '🎨 Interior Design', count: 25 }
  ];

  const locations = [
    { value: 'douala', label: 'Douala', count: 342 },
    { value: 'yaounde', label: 'Yaoundé', count: 298 },
    { value: 'bafoussam', label: 'Bafoussam', count: 156 },
    { value: 'bamenda', label: 'Bamenda', count: 134 },
    { value: 'garoua', label: 'Garoua', count: 87 },
    { value: 'maroua', label: 'Maroua', count: 65 }
  ];

  const amenities = [
    { value: 'wifi', label: 'WiFi', icon: Wifi },
    { value: 'parking', label: 'Parking', icon: Car },
    { value: 'security', label: 'Security', icon: Shield },
    { value: 'gym', label: 'Gym', icon: Dumbbell },
    { value: 'pool', label: 'Swimming Pool', icon: Coffee },
    { value: 'tv', label: 'TV/Cable', icon: Tv }
  ];

  const sortOptions = [
    { value: 'newest', label: 'Newest First' },
    { value: 'oldest', label: 'Oldest First' },
    { value: 'price_low', label: 'Price: Low to High' },
    { value: 'price_high', label: 'Price: High to Low' },
    { value: 'rating', label: 'Highest Rated' },
    { value: 'popular', label: 'Most Popular' }
  ];

  useEffect(() => {
    onFiltersChange?.(filters);
  }, [filters, onFiltersChange]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handlePriceRangeChange = (type, value) => {
    setFilters(prev => ({
      ...prev,
      priceRange: {
        ...prev.priceRange,
        [type]: value
      }
    }));
  };

  const handleAmenityToggle = (amenity) => {
    setFilters(prev => ({
      ...prev,
      amenities: prev.amenities.includes(amenity)
        ? prev.amenities.filter(a => a !== amenity)
        : [...prev.amenities, amenity]
    }));
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const clearAllFilters = () => {
    setFilters({
      search: '',
      location: '',
      priceRange: { min: '', max: '' },
      propertyType: '',
      serviceCategory: '',
      bedrooms: '',
      bathrooms: '',
      rating: '',
      sortBy: 'newest',
      amenities: [],
      verified: false,
      available: true
    });
  };

  const FilterSection = ({ title, isExpanded, onToggle, children }) => (
    <div className="border-b border-gray-100 last:border-b-0">
      <button
        onClick={onToggle}
        className="flex items-center justify-between w-full py-4 px-1 text-left hover:bg-gray-50 transition-colors duration-200"
      >
        <h3 className="font-semibold text-gray-900">{title}</h3>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-gray-500" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-500" />
        )}
      </button>
      {isExpanded && (
        <div className="pb-4 px-1 space-y-3">
          {children}
        </div>
      )}
    </div>
  );

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed lg:static inset-y-0 left-0 z-50 lg:z-0
        w-80 bg-white shadow-xl lg:shadow-none
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        flex flex-col
        ${className}
      `}>
        {/* Enhanced Header */}
        <div className="relative overflow-hidden border-b border-gray-100">
          {/* Background gradient */}
          <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-purple-50/50 to-indigo-50"></div>
          
          <div className="relative flex items-center justify-between p-6">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 via-purple-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <SlidersHorizontal className="w-6 h-6 text-white" />
                </div>
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white"></div>
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">Smart Filters</h2>
                <p className="text-sm text-gray-600">Find your perfect {type === 'properties' ? 'property' : 'service'}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {/* Active filters count */}
              <div className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-semibold">
                {Object.values(filters).filter(value => value && value !== '' && (!Array.isArray(value) || value.length > 0)).length} active
              </div>
              
              <button
                onClick={onClose}
                className="lg:hidden w-9 h-9 flex items-center justify-center rounded-xl hover:bg-white/50 transition-colors duration-200 backdrop-blur-sm"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
          </div>
        </div>

        {/* Filters content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-1">
          {/* Enhanced Search */}
          <FilterSection
            title="🔍 Smart Search"
            isExpanded={true}
            onToggle={() => {}}
          >
            <div className="space-y-3">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder={`Search ${type} by name, location, features...`}
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  className="w-full pl-12 pr-4 py-4 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-gradient-to-r from-white to-blue-50/30 text-base"
                />
              </div>
              
              {/* Quick search suggestions */}
              <div className="flex flex-wrap gap-2">
                {type === 'properties' ? (
                  <>
                    <button className="px-3 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 text-xs rounded-full transition-colors duration-200">Modern House</button>
                    <button className="px-3 py-1 bg-purple-100 hover:bg-purple-200 text-purple-700 text-xs rounded-full transition-colors duration-200">Luxury Apartment</button>
                    <button className="px-3 py-1 bg-green-100 hover:bg-green-200 text-green-700 text-xs rounded-full transition-colors duration-200">Commercial Space</button>
                  </>
                ) : (
                  <>
                    <button className="px-3 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 text-xs rounded-full transition-colors duration-200">Expert Plumber</button>
                    <button className="px-3 py-1 bg-purple-100 hover:bg-purple-200 text-purple-700 text-xs rounded-full transition-colors duration-200">Interior Design</button>
                    <button className="px-3 py-1 bg-green-100 hover:bg-green-200 text-green-700 text-xs rounded-full transition-colors duration-200">Construction</button>
                  </>
                )}
              </div>
            </div>
          </FilterSection>

          {/* Enhanced Location */}
          <FilterSection
            title="📍 Location & Area"
            isExpanded={expandedSections.location}
            onToggle={() => toggleSection('location')}
          >
            <div className="space-y-3">
              {/* Location search */}
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search location..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                />
              </div>
              
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {locations.map((location) => (
                  <label key={location.value} className="group flex items-center justify-between p-3 rounded-xl hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 cursor-pointer transition-all duration-200 border border-transparent hover:border-blue-100">
                    <div className="flex items-center space-x-3">
                      <div className="relative">
                        <input
                          type="radio"
                          name="location"
                          value={location.value}
                          checked={filters.location === location.value}
                          onChange={(e) => handleFilterChange('location', e.target.value)}
                          className="w-4 h-4 text-blue-600 focus:ring-blue-500 border-2 border-gray-300"
                        />
                        {filters.location === location.value && (
                          <div className="absolute inset-0 bg-blue-500 rounded-full animate-pulse opacity-20"></div>
                        )}
                      </div>
                      <div>
                        <span className="text-gray-900 font-semibold group-hover:text-blue-700 transition-colors duration-200">{location.label}</span>
                        <div className="text-xs text-gray-500">Region</div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-semibold text-gray-500 bg-gray-100 group-hover:bg-blue-100 group-hover:text-blue-700 px-3 py-1 rounded-full transition-colors duration-200">
                        {location.count}
                      </span>
                      <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          </FilterSection>

          {/* Price Range */}
          <FilterSection
            title="Price Range (XAF)"
            isExpanded={expandedSections.price}
            onToggle={() => toggleSection('price')}
          >
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Min Price</label>
                  <input
                    type="number"
                    placeholder="0"
                    value={filters.priceRange.min}
                    onChange={(e) => handlePriceRangeChange('min', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Max Price</label>
                  <input
                    type="number"
                    placeholder="∞"
                    value={filters.priceRange.max}
                    onChange={(e) => handlePriceRangeChange('max', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                  />
                </div>
              </div>
              
              {/* Quick price filters */}
              <div className="grid grid-cols-2 gap-2">
                {[
                  { label: '< 500K', min: 0, max: 500000 },
                  { label: '500K - 1M', min: 500000, max: 1000000 },
                  { label: '1M - 5M', min: 1000000, max: 5000000 },
                  { label: '> 5M', min: 5000000, max: '' }
                ].map((range) => (
                  <button
                    key={range.label}
                    onClick={() => setFilters(prev => ({
                      ...prev,
                      priceRange: { min: range.min.toString(), max: range.max.toString() }
                    }))}
                    className="px-3 py-2 text-xs border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-colors duration-200"
                  >
                    {range.label}
                  </button>
                ))}
              </div>
            </div>
          </FilterSection>

          {/* Property Type or Service Category */}
          <FilterSection
            title={type === 'properties' ? 'Property Type' : 'Service Category'}
            isExpanded={expandedSections.type}
            onToggle={() => toggleSection('type')}
          >
            <div className="space-y-2">
              {(type === 'properties' ? propertyTypes : serviceCategories).map((item) => (
                <label key={item.value} className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors duration-200">
                  <div className="flex items-center space-x-3">
                    <input
                      type="radio"
                      name={type === 'properties' ? 'propertyType' : 'serviceCategory'}
                      value={item.value}
                      checked={filters[type === 'properties' ? 'propertyType' : 'serviceCategory'] === item.value}
                      onChange={(e) => handleFilterChange(
                        type === 'properties' ? 'propertyType' : 'serviceCategory',
                        e.target.value
                      )}
                      className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-gray-700 font-medium text-sm">{item.label}</span>
                  </div>
                  <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                    {item.count}
                  </span>
                </label>
              ))}
            </div>
          </FilterSection>

          {/* Bedrooms & Bathrooms (Properties only) */}
          {type === 'properties' && (
            <FilterSection
              title="Rooms"
              isExpanded={expandedSections.rooms}
              onToggle={() => toggleSection('rooms')}
            >
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Bedrooms</label>
                  <div className="flex space-x-2">
                    {['Any', '1', '2', '3', '4', '5+'].map((bed) => (
                      <button
                        key={bed}
                        onClick={() => handleFilterChange('bedrooms', bed === 'Any' ? '' : bed)}
                        className={`px-3 py-2 text-sm rounded-lg border transition-all duration-200 ${
                          (bed === 'Any' && !filters.bedrooms) || filters.bedrooms === bed
                            ? 'bg-blue-500 text-white border-blue-500'
                            : 'border-gray-200 hover:bg-gray-50'
                        }`}
                      >
                        {bed}
                      </button>
                    ))}
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Bathrooms</label>
                  <div className="flex space-x-2">
                    {['Any', '1', '2', '3', '4+'].map((bath) => (
                      <button
                        key={bath}
                        onClick={() => handleFilterChange('bathrooms', bath === 'Any' ? '' : bath)}
                        className={`px-3 py-2 text-sm rounded-lg border transition-all duration-200 ${
                          (bath === 'Any' && !filters.bathrooms) || filters.bathrooms === bath
                            ? 'bg-blue-500 text-white border-blue-500'
                            : 'border-gray-200 hover:bg-gray-50'
                        }`}
                      >
                        {bath}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </FilterSection>
          )}

          {/* Amenities (Properties only) */}
          {type === 'properties' && (
            <FilterSection
              title="Amenities"
              isExpanded={expandedSections.amenities}
              onToggle={() => toggleSection('amenities')}
            >
              <div className="grid grid-cols-2 gap-2">
                {amenities.map((amenity) => {
                  const IconComponent = amenity.icon;
                  return (
                    <label key={amenity.value} className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors duration-200">
                      <input
                        type="checkbox"
                        checked={filters.amenities.includes(amenity.value)}
                        onChange={() => handleAmenityToggle(amenity.value)}
                        className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                      />
                      <IconComponent className="w-4 h-4 text-gray-500" />
                      <span className="text-sm text-gray-700">{amenity.label}</span>
                    </label>
                  );
                })}
              </div>
            </FilterSection>
          )}

          {/* Rating */}
          <FilterSection
            title="Minimum Rating"
            isExpanded={expandedSections.rating}
            onToggle={() => toggleSection('rating')}
          >
            <div className="space-y-2">
              {[5, 4, 3, 2, 1].map((rating) => (
                <label key={rating} className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors duration-200">
                  <input
                    type="radio"
                    name="rating"
                    value={rating}
                    checked={filters.rating === rating.toString()}
                    onChange={(e) => handleFilterChange('rating', e.target.value)}
                    className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                  />
                  <div className="flex items-center space-x-1">
                    {[...Array(rating)].map((_, i) => (
                      <Star key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                    ))}
                    {[...Array(5 - rating)].map((_, i) => (
                      <Star key={i} className="w-4 h-4 text-gray-300" />
                    ))}
                  </div>
                  <span className="text-sm text-gray-600">& up</span>
                </label>
              ))}
            </div>
          </FilterSection>

          {/* Additional Filters */}
          <FilterSection
            title="Additional Options"
            isExpanded={expandedSections.additional}
            onToggle={() => toggleSection('additional')}
          >
            <div className="space-y-3">
              <label className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors duration-200">
                <input
                  type="checkbox"
                  checked={filters.verified}
                  onChange={(e) => handleFilterChange('verified', e.target.checked)}
                  className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                />
                <Shield className="w-4 h-4 text-green-500" />
                <span className="text-sm text-gray-700">Verified Only</span>
              </label>
              
              <label className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors duration-200">
                <input
                  type="checkbox"
                  checked={filters.available}
                  onChange={(e) => handleFilterChange('available', e.target.checked)}
                  className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                />
                <div className="w-4 h-4 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-700">Available Now</span>
              </label>
            </div>
          </FilterSection>

          {/* Sort By */}
          <FilterSection
            title="Sort By"
            isExpanded={expandedSections.sort}
            onToggle={() => toggleSection('sort')}
          >
            <div className="space-y-2">
              {sortOptions.map((option) => (
                <label key={option.value} className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors duration-200">
                  <input
                    type="radio"
                    name="sortBy"
                    value={option.value}
                    checked={filters.sortBy === option.value}
                    onChange={(e) => handleFilterChange('sortBy', e.target.value)}
                    className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">{option.label}</span>
                </label>
              ))}
            </div>
          </FilterSection>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-100 bg-gray-50">
          <div className="space-y-3">
            <button
              onClick={clearAllFilters}
              className="w-full px-4 py-3 text-gray-600 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors duration-200 font-medium"
            >
              Clear All Filters
            </button>
            <button
              onClick={onClose}
              className="lg:hidden w-full px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-200 font-semibold"
            >
              Apply Filters
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default FilterSidebar;