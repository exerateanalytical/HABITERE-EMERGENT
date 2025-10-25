import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import SEOHead from '../components/SEOHead';
import { generateSEOData, generateStructuredData } from '../utils/seoData';
import ServicesCarousel from '../components/ServicesCarousel';
import FilterSidebar from '../components/FilterSidebar';
import RippleButton from '../components/RippleButton';
import { PropertyCardSkeleton } from '../components/SkeletonLoader';
import LocationToggle from '../components/LocationToggle';
import { useLocation as useLocationContext } from '../context/LocationContext';
import { 
  Search, 
  Filter, 
  MapPin, 
  BedDouble, 
  Bath, 
  Square, 
  Heart, 
  Eye,
  Grid3x3,
  List,
  ChevronDown,
  X,
  SlidersHorizontal,
  Star,
  Shield,
  Phone
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Helper function to get proper image URL
const getImageUrl = (url) => {
  if (!url) return 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&q=80';
  return url.startsWith('/uploads/') ? `${BACKEND_URL}${url}` : url;
};

const Properties = () => {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    property_type: '',
    listing_type: '',
    location: '',
    min_price: '',
    max_price: '',
    bedrooms: ''
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [favorites, setFavorites] = useState(new Set());
  const [sortBy, setSortBy] = useState('newest');
  const { userLocation, viewMode: locationViewMode } = useLocationContext();

  useEffect(() => {
    fetchProperties();
  }, [filters, userLocation, locationViewMode]);

  const fetchProperties = async () => {
    try {
      setLoading(true);
      setError('');
      const params = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value && value !== '') {
          params.append(key, value);
        }
      });

      const queryString = params.toString();
      const url = queryString ? `${API}/properties?${queryString}` : `${API}/properties`;
      
      console.log('Fetching properties from:', url);
      const response = await axios.get(url);
      console.log('Properties received:', response.data?.length || 0);
      setProperties(response.data || []);
    } catch (err) {
      console.error('Error fetching properties:', err);
      setError('Failed to load properties. Please try again.');
      setProperties([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = useCallback((newFilters) => {
    // Transform FilterSidebar filters to match backend API expectations
    const transformedFilters = {
      property_type: newFilters.propertyType || '',
      listing_type: newFilters.listingType || '',
      location: newFilters.location || '',
      min_price: newFilters.priceRange?.min || '',
      max_price: newFilters.priceRange?.max || '',
      bedrooms: newFilters.bedrooms || ''
    };
    setFilters(transformedFilters);
    setSearchQuery(newFilters.search || '');
  }, []);

  const handleSearch = (searchFilters) => {
    setFilters(searchFilters);
    setSearchQuery(searchFilters.search || '');
  };

  const clearFilters = () => {
    const clearedFilters = {
      property_type: '',
      listing_type: '',
      location: '',
      min_price: '',
      max_price: '',
      bedrooms: ''
    };
    setFilters(clearedFilters);
    setSearchQuery('');
  };

  const toggleFavorite = (propertyId) => {
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

  const formatPrice = (price) => {
    return new Intl.NumberFormat('fr-CM', {
      style: 'currency',
      currency: 'XAF',
      minimumFractionDigits: 0
    }).format(price);
  };

  const filteredProperties = properties.filter(property =>
    property.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    property.location.toLowerCase().includes(searchQuery.toLowerCase()) ||
    property.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Generate dynamic SEO data based on current filters and location
  const seoData = generateSEOData('properties', {
    location: searchQuery || 'Cameroon',
    count: filteredProperties.length,
    propertyType: 'Properties'
  });
  
  const structuredData = generateStructuredData('RealEstateAgent', {
    location: searchQuery || 'Cameroon',
    region: 'Centre'
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-6">
            <div className="h-10 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded w-64 animate-shimmer bg-[length:200%_100%] mb-2"></div>
            <div className="h-6 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded w-48 animate-shimmer bg-[length:200%_100%]"></div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
            {[...Array(6)].map((_, index) => (
              <PropertyCardSkeleton key={index} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="properties-page">
      <SEOHead
        title={seoData.title}
        description={seoData.description}
        keywords={seoData.keywords}
        focusKeyword={seoData.focusKeyword}
        structuredData={structuredData}
        ogImage="https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=1200&q=80"
        location={searchQuery || 'Cameroon'}
      />
      {/* Enhanced Header */}
      <div className="relative bg-gradient-to-br from-white via-blue-50/40 to-purple-50/40 shadow-lg border-b border-gray-200 overflow-hidden">
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }}></div>
        </div>
        
        <div className="relative max-w-7xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8 py-6 sm:py-8 md:py-10">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-6 lg:space-y-0">
            <div className="text-center lg:text-left">
              <div className="flex flex-col lg:flex-row lg:items-center space-y-3 sm:space-y-4 lg:space-y-0 lg:space-x-6 mb-3 sm:mb-4">
                <div>
                  <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 mb-2">
                    Properties in 
                    <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"> Cameroon</span>
                  </h1>
                  <p className="text-sm sm:text-base md:text-lg lg:text-xl text-gray-600">
                    Discover <span className="font-bold text-blue-600">{filteredProperties.length}</span> verified properties
                  </p>
                </div>
              </div>
              
              {/* Quick stats */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3 md:gap-4 max-w-2xl mx-auto lg:mx-0">
                <div className="bg-white/70 backdrop-blur-sm rounded-lg sm:rounded-xl p-2 sm:p-3 text-center shadow-lg border border-white/20">
                  <div className="text-base sm:text-lg font-bold text-blue-600">1000+</div>
                  <div className="text-xs text-gray-600">Properties</div>
                </div>
                <div className="bg-white/70 backdrop-blur-sm rounded-lg sm:rounded-xl p-2 sm:p-3 text-center shadow-lg border border-white/20">
                  <div className="text-base sm:text-lg font-bold text-green-600">245</div>
                  <div className="text-xs text-gray-600">For Sale</div>
                </div>
                <div className="bg-white/70 backdrop-blur-sm rounded-lg sm:rounded-xl p-2 sm:p-3 text-center shadow-lg border border-white/20">
                  <div className="text-base sm:text-lg font-bold text-purple-600">387</div>
                  <div className="text-xs text-gray-600">For Rent</div>
                </div>
                <div className="bg-white/70 backdrop-blur-sm rounded-lg sm:rounded-xl p-2 sm:p-3 text-center shadow-lg border border-white/20">
                  <div className="text-base sm:text-lg font-bold text-orange-600">156</div>
                  <div className="text-xs text-gray-600">New</div>
                </div>
              </div>
            </div>

            {/* Enhanced Controls */}
            <div className="lg:text-right space-y-3 sm:space-y-4">
              {/* Quick Search */}
              <div className="relative max-w-md lg:ml-auto">
                <Search className="absolute left-3 sm:left-4 top-1/2 transform -translate-y-1/2 w-4 h-4 sm:w-5 sm:h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 sm:pl-12 pr-3 sm:pr-4 py-2.5 sm:py-3 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-xl sm:rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm sm:text-base text-gray-900 placeholder-gray-500 shadow-lg"
                />
              </div>
              
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center space-y-2 sm:space-y-0 sm:space-x-3">
                {/* Mobile Filter Button */}
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="lg:hidden w-full sm:w-auto bg-white/90 backdrop-blur-sm border border-gray-200 px-4 py-2.5 sm:px-6 sm:py-3 rounded-xl sm:rounded-2xl flex items-center justify-center space-x-2 hover:bg-white hover:shadow-lg transition-all duration-200 shadow-lg text-sm sm:text-base"
                >
                  <SlidersHorizontal className="w-4 h-4 sm:w-5 sm:h-5 text-gray-600" />
                  <span className="font-semibold text-gray-700">Filters</span>
                </button>

                {/* Sort Dropdown */}
                <div className="relative w-full sm:flex-1">
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="w-full bg-white/90 backdrop-blur-sm border border-gray-200 px-4 py-2.5 sm:px-6 sm:py-3 rounded-xl sm:rounded-2xl appearance-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-semibold text-gray-700 shadow-lg pr-10 sm:pr-12 text-sm sm:text-base"
                  >
                    <option value="newest">🕐 Newest</option>
                    <option value="price_low">💰 Low-High</option>
                    <option value="price_high">💎 High-Low</option>
                    <option value="rating">⭐ Top Rated</option>
                  </select>
                  <ChevronDown className="absolute right-3 sm:right-4 top-1/2 transform -translate-y-1/2 w-4 h-4 sm:w-5 sm:h-5 text-gray-400 pointer-events-none" />
                </div>

                {/* View Toggle */}
                <div className="hidden sm:flex items-center bg-white/90 backdrop-blur-sm border border-gray-200 rounded-2xl p-1 shadow-lg">
                  <button
                    onClick={() => setViewMode('grid')}
                    className={`p-2.5 sm:p-3 rounded-xl transition-all duration-200 ${
                      viewMode === 'grid' 
                        ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg' 
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                    }`}
                    data-testid="grid-view-btn"
                  >
                    <Grid3x3 className="w-4 h-4 sm:w-5 sm:h-5" />
                  </button>
                  <button
                    onClick={() => setViewMode('list')}
                    className={`p-2.5 sm:p-3 rounded-xl transition-all duration-200 ${
                      viewMode === 'list' 
                        ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg' 
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                    }`}
                    data-testid="list-view-btn"
                  >
                    <List className="w-4 h-4 sm:w-5 sm:h-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content with Sidebar */}
      <div className="max-w-7xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8 py-4 sm:py-6 md:py-8">
        <div className="flex gap-8">
          {/* Filter Sidebar - Desktop */}
          <FilterSidebar
            type="properties"
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            onFiltersChange={handleFilterChange}
            className="hidden lg:block lg:w-80 flex-shrink-0"
          />

          {/* Mobile Sidebar */}
          <FilterSidebar
            type="properties"
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            onFiltersChange={handleFilterChange}
            className="lg:hidden"
          />

          {/* Main Content */}
          <div className="flex-1 min-w-0">
            {/* Professional Services Carousel */}
            <div className="mb-8">
              <ServicesCarousel 
                title="Find Property Services" 
                limit={8}
                showAll={true}
              />
            </div>

            {/* Results Header */}
            <div className="flex items-center justify-between mb-4 sm:mb-6">
              <div>
                <h2 className="text-base sm:text-lg md:text-xl font-semibold text-gray-900">
                  {filteredProperties.length} Properties
                </h2>
                <p className="text-xs sm:text-sm text-gray-600 mt-0.5 sm:mt-1">
                  Best matches for you
                </p>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-6 mb-6" data-testid="error-message">
                <p className="text-red-700">{error}</p>
              </div>
            )}

            {filteredProperties.length === 0 && !loading && (
              <div className="text-center py-12 bg-white rounded-2xl shadow-sm border border-gray-100" data-testid="no-properties">
                <div className="w-24 h-24 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Search className="w-12 h-12 text-blue-500" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-3">No Properties Found</h3>
                <p className="text-gray-600 mb-6 max-w-md mx-auto">
                  We couldn't find any properties matching your criteria. Try adjusting your filters or search terms.
                </p>
                <button
                  onClick={clearFilters}
                  className="btn-primary"
                >
                  Clear All Filters
                </button>
              </div>
            )}

            {/* Properties grid/list */}
            {viewMode === 'grid' ? (
              <div className="grid grid-cols-2 md:grid-cols-2 xl:grid-cols-3 gap-3 sm:gap-4 md:gap-6" data-testid="properties-grid">
                {filteredProperties.map((property) => (
                  <PropertyCard 
                    key={property.id} 
                    property={property} 
                    isFavorite={favorites.has(property.id)}
                    onToggleFavorite={toggleFavorite}
                    formatPrice={formatPrice}
                  />
                ))}
              </div>
            ) : (
              <div className="space-y-6" data-testid="properties-list">
                {filteredProperties.map((property) => (
                  <PropertyListItem 
                    key={property.id} 
                    property={property} 
                    isFavorite={favorites.has(property.id)}
                    onToggleFavorite={toggleFavorite}
                    formatPrice={formatPrice}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const PropertyCard = ({ property, isFavorite, onToggleFavorite, formatPrice }) => {
  const [imageLoaded, setImageLoaded] = React.useState(false);
  
  return (
    <div className="group bg-white rounded-2xl sm:rounded-3xl shadow-lg sm:shadow-xl hover:shadow-2xl transition-all duration-500 overflow-hidden border border-gray-100 hover:border-blue-200 transform hover:-translate-y-1 sm:hover:-translate-y-2" data-testid={`property-card-${property.id}`}>
      <div className="relative overflow-hidden h-40 sm:h-48 md:h-56 lg:h-64">
        {/* Image with loading state */}
        <div className={`w-full h-full bg-gradient-to-br from-gray-200 to-gray-300 ${!imageLoaded ? 'animate-pulse' : ''}`}>
          <img
            src={getImageUrl(property.images?.[0])}
            alt={property.title}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
            onLoad={() => setImageLoaded(true)}
          />
        </div>
        
        {/* Enhanced overlay gradient */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-black/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        
        {/* Top badges */}
        <div className="absolute top-2 left-2 sm:top-3 sm:left-3 flex flex-col sm:flex-row flex-wrap gap-1 sm:gap-2">
          <span className={`px-2 py-1 sm:px-3 sm:py-2 rounded-lg sm:rounded-2xl text-xs font-bold shadow-lg backdrop-blur-md border border-white/20 ${
            property.listing_type === 'rent' 
              ? 'bg-emerald-500/95 text-white' 
              : property.listing_type === 'sale' 
                ? 'bg-blue-500/95 text-white' 
                : 'bg-orange-500/95 text-white'
          }`}>
            {property.listing_type === 'rent' ? 'Rent' : 
             property.listing_type === 'sale' ? 'Sale' : 'Lease'}
          </span>
          {property.verified && (
            <span className="px-2 py-1 sm:px-3 sm:py-2 rounded-lg sm:rounded-2xl text-xs font-bold bg-emerald-600/95 text-white shadow-lg backdrop-blur-md border border-white/20 flex items-center">
              <Shield className="w-2.5 h-2.5 sm:w-3 sm:h-3 mr-0.5 sm:mr-1" />
              ✓
            </span>
          )}
        </div>
        
        {/* Heart button */}
        <button
          onClick={() => onToggleFavorite(property.id)}
          className={`absolute top-2 right-2 sm:top-3 sm:right-3 p-2 sm:p-3 rounded-xl sm:rounded-2xl transition-all duration-300 shadow-lg backdrop-blur-md border border-white/20 ${
            isFavorite 
              ? 'bg-red-500 text-white' 
              : 'bg-white/90 text-gray-600 hover:text-red-500 hover:bg-white'
          }`}
          data-testid={`favorite-btn-${property.id}`}
        >
          <Heart className={`w-4 h-4 sm:w-5 sm:h-5 ${isFavorite ? 'fill-current' : ''}`} />
        </button>

        {/* Price overlay - moved to always visible */}
        <div className="absolute bottom-2 right-2 sm:bottom-3 sm:right-3 bg-gradient-to-r from-blue-600 to-purple-600 backdrop-blur-md rounded-lg sm:rounded-xl px-2 py-1 sm:px-3 sm:py-2 shadow-lg border border-white/20">
          <div className="text-sm sm:text-base md:text-lg font-bold text-white">
            {formatPrice(property.price)}
            {property.listing_type === 'rent' && <span className="text-xs opacity-80">/mo</span>}
          </div>
        </div>
      </div>

      <div className="p-3 sm:p-4 md:p-5 space-y-2 sm:space-y-3">
        {/* Title and location */}
        <div>
          <h3 className="text-sm sm:text-base md:text-lg font-bold text-gray-900 mb-1 sm:mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors duration-300">
            {property.title}
          </h3>
          <div className="flex items-start sm:items-center text-gray-500 text-xs sm:text-sm">
            <MapPin className="w-3 h-3 sm:w-4 sm:h-4 mr-1 text-blue-500 flex-shrink-0 mt-0.5 sm:mt-0" />
            <span className="font-medium truncate">{property.location}</span>
          </div>
        </div>

        {/* Property details */}
        <div className="grid grid-cols-3 gap-2 sm:gap-3 py-2 sm:py-3 bg-gradient-to-br from-gray-50 to-blue-50/30 rounded-xl sm:rounded-2xl">
          {property.bedrooms > 0 && (
            <div className="text-center">
              <div className="w-6 h-6 sm:w-8 sm:h-8 bg-blue-100 rounded-lg sm:rounded-xl flex items-center justify-center mx-auto mb-1">
                <BedDouble className="w-3 h-3 sm:w-4 sm:h-4 text-blue-600" />
              </div>
              <div className="text-xs sm:text-sm font-bold text-gray-900">{property.bedrooms}</div>
              <div className="text-xs text-gray-500 hidden sm:block">Beds</div>
            </div>
          )}
          {property.bathrooms > 0 && (
            <div className="text-center">
              <div className="w-6 h-6 sm:w-8 sm:h-8 bg-purple-100 rounded-lg sm:rounded-xl flex items-center justify-center mx-auto mb-1">
                <Bath className="w-3 h-3 sm:w-4 sm:h-4 text-purple-600" />
              </div>
              <div className="text-xs sm:text-sm font-bold text-gray-900">{property.bathrooms}</div>
              <div className="text-xs text-gray-500 hidden sm:block">Baths</div>
            </div>
          )}
          {property.area_sqm && (
            <div className="text-center">
              <div className="w-6 h-6 sm:w-8 sm:h-8 bg-green-100 rounded-lg sm:rounded-xl flex items-center justify-center mx-auto mb-1">
                <Square className="w-3 h-3 sm:w-4 sm:h-4 text-green-600" />
              </div>
              <div className="text-xs sm:text-sm font-bold text-gray-900">{property.area_sqm}</div>
              <div className="text-xs text-gray-500 hidden sm:block">m²</div>
            </div>
          )}
        </div>

        {/* Amenities preview - hidden on mobile, shown on tablet+ */}
        <div className="hidden sm:flex flex-wrap gap-1.5 sm:gap-2">
          {(property.amenities || ['WiFi', 'Parking', 'Security']).slice(0, 2).map((amenity, index) => (
            <span key={index} className="px-2 py-0.5 sm:px-3 sm:py-1 bg-gray-100 text-gray-700 text-xs rounded-full font-medium">
              {amenity}
            </span>
          ))}
          {(property.amenities || []).length > 2 && (
            <span className="px-2 py-0.5 sm:px-3 sm:py-1 bg-blue-100 text-blue-700 text-xs rounded-full font-medium">
              +{(property.amenities || []).length - 2}
            </span>
          )}
        </div>

        {/* Actions */}
        <Link
          to={`/properties/${property.id}`}
          className="block w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold px-3 py-2.5 sm:px-4 sm:py-3 md:px-6 md:py-4 rounded-xl sm:rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 text-center text-sm sm:text-base"
          data-testid={`view-property-${property.id}`}
        >
          <span className="flex items-center justify-center">
            <Eye className="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" />
            View
          </span>
        </Link>
      </div>
    </div>
  );
};

const PropertyListItem = ({ property, isFavorite, onToggleFavorite, formatPrice }) => {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow" data-testid={`property-list-${property.id}`}>
      <div className="flex flex-col md:flex-row">
        <div className="md:w-80 h-48 md:h-auto relative overflow-hidden flex-shrink-0">
          <img
            src={getImageUrl(property.images?.[0])}
            alt={property.title}
            className="w-full h-full object-cover"
          />
          
          <div className="absolute top-3 left-3 flex flex-wrap gap-2">
            <span className={`badge ${
              property.listing_type === 'rent' ? 'badge-success' : 
              property.listing_type === 'sale' ? 'badge-primary' : 'badge-warning'
            }`}>
              {property.listing_type === 'rent' ? 'For Rent' : 
               property.listing_type === 'sale' ? 'For Sale' : 'For Lease'}
            </span>
            {property.verified && (
              <span className="badge badge-success">Verified</span>
            )}
          </div>
        </div>

        <div className="flex-1 p-6">
          <div className="flex justify-between items-start mb-3">
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-1">
                {property.title}
              </h3>
              <div className="flex items-center text-gray-500 text-sm">
                <MapPin className="w-4 h-4 mr-1" />
                {property.location}
              </div>
            </div>
            
            <button
              onClick={() => onToggleFavorite(property.id)}
              className={`p-2 rounded-full transition-colors ${
                isFavorite ? 'bg-red-500 text-white' : 'bg-gray-100 text-gray-600 hover:text-red-500'
              }`}
            >
              <Heart className={`w-5 h-5 ${isFavorite ? 'fill-current' : ''}`} />
            </button>
          </div>

          <p className="text-gray-600 mb-4 line-clamp-2">
            {property.description}
          </p>

          <div className="flex items-center text-gray-600 text-sm space-x-6 mb-4">
            {property.bedrooms > 0 && (
              <div className="flex items-center">
                <BedDouble className="w-4 h-4 mr-1" />
                {property.bedrooms} beds
              </div>
            )}
            {property.bathrooms > 0 && (
              <div className="flex items-center">
                <Bath className="w-4 h-4 mr-1" />
                {property.bathrooms} baths
              </div>
            )}
            {property.area_sqm && (
              <div className="flex items-center">
                <Square className="w-4 h-4 mr-1" />
                {property.area_sqm}m²
              </div>
            )}
            <div className="capitalize">
              {property.property_type}
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="text-2xl font-bold text-blue-600">
              {formatPrice(property.price)}
              {property.listing_type === 'rent' && <span className="text-sm text-gray-500">/month</span>}
            </div>
            
            <Link
              to={`/properties/${property.id}`}
              className="btn-primary"
            >
              <Eye className="w-4 h-4 mr-2" />
              View Details
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Properties;