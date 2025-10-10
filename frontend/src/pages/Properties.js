import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import ServicesCarousel from '../components/ServicesCarousel';
import FilterSidebar from '../components/FilterSidebar';
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
  Shield
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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

  useEffect(() => {
    fetchProperties();
  }, [filters]);

  const fetchProperties = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value) {
          params.append(key, value);
        }
      });

      const response = await axios.get(`${API}/properties?${params.toString()}`);
      setProperties(response.data || []);
    } catch (err) {
      console.error('Error fetching properties:', err);
      setError('Failed to load properties');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    setSearchQuery(newFilters.search || '');
  };

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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, index) => (
              <div key={index} className="card animate-pulse">
                <div className="h-48 bg-gray-300 rounded-t-xl"></div>
                <div className="card-body">
                  <div className="h-4 bg-gray-300 rounded mb-2"></div>
                  <div className="h-3 bg-gray-300 rounded mb-4 w-3/4"></div>
                  <div className="space-y-2">
                    <div className="h-3 bg-gray-300 rounded w-1/2"></div>
                    <div className="h-3 bg-gray-300 rounded w-2/3"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="properties-page">
      {/* Enhanced Header */}
      <div className="relative bg-gradient-to-br from-white via-blue-50/40 to-purple-50/40 shadow-lg border-b border-gray-200 overflow-hidden">
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }}></div>
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-6 lg:space-y-0">
            <div className="text-center lg:text-left">
              <div className="flex flex-col lg:flex-row lg:items-center space-y-4 lg:space-y-0 lg:space-x-6 mb-4">
                <div>
                  <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 mb-2">
                    Properties in 
                    <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"> Cameroon</span>
                  </h1>
                  <p className="text-lg md:text-xl text-gray-600">
                    Discover <span className="font-bold text-blue-600">{filteredProperties.length}</span> verified properties across all regions
                  </p>
                </div>
              </div>
              
              {/* Quick stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl mx-auto lg:mx-0">
                <div className="bg-white/70 backdrop-blur-sm rounded-xl p-3 text-center shadow-lg border border-white/20">
                  <div className="text-lg font-bold text-blue-600">1000+</div>
                  <div className="text-xs text-gray-600">Total Properties</div>
                </div>
                <div className="bg-white/70 backdrop-blur-sm rounded-xl p-3 text-center shadow-lg border border-white/20">
                  <div className="text-lg font-bold text-green-600">245</div>
                  <div className="text-xs text-gray-600">For Sale</div>
                </div>
                <div className="bg-white/70 backdrop-blur-sm rounded-xl p-3 text-center shadow-lg border border-white/20">
                  <div className="text-lg font-bold text-purple-600">387</div>
                  <div className="text-xs text-gray-600">For Rent</div>
                </div>
                <div className="bg-white/70 backdrop-blur-sm rounded-xl p-3 text-center shadow-lg border border-white/20">
                  <div className="text-lg font-bold text-orange-600">156</div>
                  <div className="text-xs text-gray-600">New This Week</div>
                </div>
              </div>
            </div>

            {/* Enhanced Controls */}
            <div className="lg:text-right space-y-4">
              {/* Quick Search */}
              <div className="relative max-w-md lg:ml-auto">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search properties..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-500 shadow-lg"
                />
              </div>
              
              <div className="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-4">
                {/* Mobile Filter Button */}
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="lg:hidden w-full sm:w-auto bg-white/90 backdrop-blur-sm border border-gray-200 px-6 py-3 rounded-2xl flex items-center justify-center space-x-2 hover:bg-white hover:shadow-lg transition-all duration-200 shadow-lg"
                >
                  <SlidersHorizontal className="w-5 h-5 text-gray-600" />
                  <span className="font-semibold text-gray-700">Advanced Filters</span>
                </button>

                {/* Sort Dropdown */}
                <div className="relative w-full sm:w-auto">
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="w-full sm:w-auto bg-white/90 backdrop-blur-sm border border-gray-200 px-6 py-3 rounded-2xl appearance-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-semibold text-gray-700 shadow-lg pr-12"
                  >
                    <option value="newest">🕐 Newest First</option>
                    <option value="price_low">💰 Price: Low to High</option>
                    <option value="price_high">💎 Price: High to Low</option>
                    <option value="rating">⭐ Highest Rated</option>
                    <option value="size">📐 Largest Properties</option>
                    <option value="featured">🔥 Featured First</option>
                  </select>
                  <ChevronDown className="absolute right-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
                </div>

                {/* View Toggle */}
                <div className="flex items-center bg-white/90 backdrop-blur-sm border border-gray-200 rounded-2xl p-1 shadow-lg">
                  <button
                    onClick={() => setViewMode('grid')}
                    className={`p-3 rounded-xl transition-all duration-200 ${
                      viewMode === 'grid' 
                        ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg' 
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                    }`}
                    data-testid="grid-view-btn"
                  >
                    <Grid3x3 className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => setViewMode('list')}
                    className={`p-3 rounded-xl transition-all duration-200 ${
                      viewMode === 'list' 
                        ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg' 
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                    }`}
                    data-testid="list-view-btn"
                  >
                    <List className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content with Sidebar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* Filter Sidebar */}
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
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  {filteredProperties.length} Properties Found
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  Showing the best matches for your criteria
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
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6" data-testid="properties-grid">
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
    <div className="group bg-white rounded-3xl shadow-xl hover:shadow-2xl transition-all duration-500 overflow-hidden border border-gray-100 hover:border-blue-200 transform hover:-translate-y-2 hover:rotate-1" data-testid={`property-card-${property.id}`}>
      <div className="relative overflow-hidden h-64">
        {/* Image with loading state */}
        <div className={`w-full h-full bg-gradient-to-br from-gray-200 to-gray-300 ${!imageLoaded ? 'animate-pulse' : ''}`}>
          <img
            src={property.images?.[0] || 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&q=80'}
            alt={property.title}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
            onLoad={() => setImageLoaded(true)}
          />
        </div>
        
        {/* Enhanced overlay gradient */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-black/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        
        {/* Top badges */}
        <div className="absolute top-4 left-4 flex flex-wrap gap-2">
          <span className={`px-3 py-2 rounded-2xl text-xs font-bold shadow-xl backdrop-blur-md border border-white/20 ${
            property.listing_type === 'rent' 
              ? 'bg-emerald-500/95 text-white' 
              : property.listing_type === 'sale' 
                ? 'bg-blue-500/95 text-white' 
                : 'bg-orange-500/95 text-white'
          }`}>
            {property.listing_type === 'rent' ? '🏠 For Rent' : 
             property.listing_type === 'sale' ? '🏡 For Sale' : '🏢 For Lease'}
          </span>
          {property.verified && (
            <span className="px-3 py-2 rounded-2xl text-xs font-bold bg-emerald-600/95 text-white shadow-xl backdrop-blur-md border border-white/20 flex items-center">
              <Shield className="w-3 h-3 mr-1" />
              ✓ Verified
            </span>
          )}
          {property.featured && (
            <span className="px-3 py-2 rounded-2xl text-xs font-bold bg-yellow-500/95 text-white shadow-xl backdrop-blur-md border border-white/20 flex items-center animate-pulse">
              ⭐ Featured
            </span>
          )}
        </div>
        
        {/* Heart button */}
        <button
          onClick={() => onToggleFavorite(property.id)}
          className={`absolute top-4 right-4 p-3 rounded-2xl transition-all duration-300 shadow-xl backdrop-blur-md border border-white/20 ${
            isFavorite 
              ? 'bg-red-500 text-white scale-110 animate-bounce' 
              : 'bg-white/90 text-gray-600 hover:text-red-500 hover:bg-white hover:scale-105'
          }`}
          data-testid={`favorite-btn-${property.id}`}
        >
          <Heart className={`w-5 h-5 ${isFavorite ? 'fill-current' : ''}`} />
        </button>

        {/* Rating and stats overlay */}
        <div className="absolute bottom-4 left-4 flex items-center space-x-2">
          <div className="flex items-center bg-white/95 backdrop-blur-md rounded-xl px-3 py-2 shadow-lg border border-white/20">
            <Star className="w-4 h-4 text-yellow-400 fill-current mr-1" />
            <span className="text-sm font-bold text-gray-900">{property.rating || '4.8'}</span>
          </div>
          <div className="bg-blue-500/95 backdrop-blur-md rounded-xl px-3 py-2 shadow-lg border border-white/20">
            <span className="text-xs font-bold text-white">👁️ {property.views || '124'}</span>
          </div>
        </div>

        {/* Price overlay */}
        <div className="absolute bottom-4 right-4 bg-gradient-to-r from-blue-600 to-purple-600 backdrop-blur-md rounded-xl px-4 py-2 shadow-lg border border-white/20">
          <div className="text-lg font-bold text-white">
            {formatPrice(property.price)}
            {property.listing_type === 'rent' && <span className="text-xs opacity-80">/mo</span>}
          </div>
        </div>
      </div>

      <div className="p-6 space-y-4">
        {/* Title and location */}
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors duration-300">
            {property.title}
          </h3>
          <div className="flex items-center text-gray-500 text-sm">
            <MapPin className="w-4 h-4 mr-2 text-blue-500" />
            <span className="font-semibold">{property.location}</span>
            <span className="ml-auto text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">Available Now</span>
          </div>
        </div>

        {/* Property details */}
        <div className="grid grid-cols-3 gap-4 py-4 bg-gradient-to-br from-gray-50 to-blue-50/30 rounded-2xl">
          {property.bedrooms > 0 && (
            <div className="text-center">
              <div className="w-8 h-8 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-2">
                <BedDouble className="w-4 h-4 text-blue-600" />
              </div>
              <div className="text-sm font-bold text-gray-900">{property.bedrooms}</div>
              <div className="text-xs text-gray-500">Bedrooms</div>
            </div>
          )}
          {property.bathrooms > 0 && (
            <div className="text-center">
              <div className="w-8 h-8 bg-purple-100 rounded-xl flex items-center justify-center mx-auto mb-2">
                <Bath className="w-4 h-4 text-purple-600" />
              </div>
              <div className="text-sm font-bold text-gray-900">{property.bathrooms}</div>
              <div className="text-xs text-gray-500">Bathrooms</div>
            </div>
          )}
          {property.area_sqm && (
            <div className="text-center">
              <div className="w-8 h-8 bg-green-100 rounded-xl flex items-center justify-center mx-auto mb-2">
                <Square className="w-4 h-4 text-green-600" />
              </div>
              <div className="text-sm font-bold text-gray-900">{property.area_sqm}</div>
              <div className="text-xs text-gray-500">m²</div>
            </div>
          )}
        </div>

        {/* Amenities preview */}
        <div className="flex flex-wrap gap-2">
          {(property.amenities || ['WiFi', 'Parking', 'Security']).slice(0, 3).map((amenity, index) => (
            <span key={index} className="px-3 py-1 bg-gray-100 text-gray-700 text-xs rounded-full font-medium">
              {amenity}
            </span>
          ))}
          {(property.amenities || []).length > 3 && (
            <span className="px-3 py-1 bg-blue-100 text-blue-700 text-xs rounded-full font-medium">
              +{(property.amenities || []).length - 3} more
            </span>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center space-x-3">
          <Link
            to={`/properties/${property.id}`}
            className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold px-6 py-4 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center group-hover:scale-105"
            data-testid={`view-property-${property.id}`}
          >
            <Eye className="w-5 h-5 mr-2" />
            View Details
          </Link>
          <button className="p-4 bg-gray-100 hover:bg-blue-100 rounded-2xl transition-colors duration-200 group-hover:scale-105">
            <Phone className="w-5 h-5 text-gray-600 hover:text-blue-600" />
          </button>
        </div>
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
            src={property.images?.[0] || 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2'}
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