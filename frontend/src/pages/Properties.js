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

            {/* Controls */}
            <div className="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-4">
              {/* Mobile Filter Button */}
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden w-full sm:w-auto bg-white border border-gray-200 px-4 py-3 rounded-xl flex items-center justify-center space-x-2 hover:bg-gray-50 transition-colors duration-200"
              >
                <SlidersHorizontal className="w-5 h-5 text-gray-600" />
                <span className="font-medium text-gray-700">Filters</span>
              </button>

              {/* Sort Dropdown */}
              <div className="relative w-full sm:w-auto">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="w-full sm:w-auto bg-white border border-gray-200 px-4 py-3 rounded-xl appearance-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-medium text-gray-700"
                >
                  <option value="newest">Newest First</option>
                  <option value="price_low">Price: Low to High</option>
                  <option value="price_high">Price: High to Low</option>
                  <option value="rating">Highest Rated</option>
                </select>
                <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
              </div>

              {/* View Toggle */}
              <div className="flex items-center bg-white border border-gray-200 rounded-xl p-1">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-lg transition-all duration-200 ${
                    viewMode === 'grid' 
                      ? 'bg-blue-500 text-white shadow-md' 
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                  data-testid="grid-view-btn"
                >
                  <Grid3x3 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-lg transition-all duration-200 ${
                    viewMode === 'list' 
                      ? 'bg-blue-500 text-white shadow-md' 
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                  data-testid="list-view-btn"
                >
                  <List className="w-4 h-4" />
                </button>
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
  return (
    <div className="group bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden border border-gray-100 hover:border-blue-200 transform hover:-translate-y-1" data-testid={`property-card-${property.id}`}>
      <div className="relative overflow-hidden h-56">
        <img
          src={property.images?.[0] || 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=600&q=80'}
          alt={property.title}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
        />
        
        {/* Overlay gradient */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        
        <div className="absolute top-4 left-4 flex flex-wrap gap-2">
          <span className={`px-3 py-1 rounded-full text-xs font-semibold shadow-lg backdrop-blur-sm ${
            property.listing_type === 'rent' 
              ? 'bg-green-500/90 text-white' 
              : property.listing_type === 'sale' 
                ? 'bg-blue-500/90 text-white' 
                : 'bg-orange-500/90 text-white'
          }`}>
            {property.listing_type === 'rent' ? 'For Rent' : 
             property.listing_type === 'sale' ? 'For Sale' : 'For Lease'}
          </span>
          {property.verified && (
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/90 text-white shadow-lg backdrop-blur-sm flex items-center">
              <Shield className="w-3 h-3 mr-1" />
              Verified
            </span>
          )}
        </div>
        
        <button
          onClick={() => onToggleFavorite(property.id)}
          className={`absolute top-4 right-4 p-3 rounded-full transition-all duration-200 shadow-lg backdrop-blur-sm ${
            isFavorite 
              ? 'bg-red-500 text-white scale-110' 
              : 'bg-white/90 text-gray-600 hover:text-red-500 hover:bg-white'
          }`}
          data-testid={`favorite-btn-${property.id}`}
        >
          <Heart className={`w-5 h-5 ${isFavorite ? 'fill-current' : ''}`} />
        </button>

        {/* Rating overlay */}
        {property.rating && (
          <div className="absolute bottom-4 left-4 flex items-center bg-white/90 backdrop-blur-sm rounded-lg px-2 py-1 shadow-lg">
            <Star className="w-4 h-4 text-yellow-400 fill-current mr-1" />
            <span className="text-sm font-semibold text-gray-900">{property.rating}</span>
          </div>
        )}
      </div>

      <div className="p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors duration-200">
            {property.title}
          </h3>
          <div className="flex items-center text-gray-500 text-sm">
            <MapPin className="w-4 h-4 mr-2 text-blue-500" />
            <span className="font-medium">{property.location}</span>
          </div>
        </div>

        <div className="mb-4">
          <div className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            {formatPrice(property.price)}
            {property.listing_type === 'rent' && <span className="text-sm text-gray-500 font-normal">/month</span>}
          </div>
        </div>

        <div className="flex items-center justify-center space-x-6 mb-6 py-3 bg-gray-50 rounded-xl">
          {property.bedrooms > 0 && (
            <div className="flex flex-col items-center">
              <BedDouble className="w-5 h-5 text-blue-500 mb-1" />
              <span className="text-xs font-semibold text-gray-700">{property.bedrooms} Beds</span>
            </div>
          )}
          {property.bathrooms > 0 && (
            <div className="flex flex-col items-center">
              <Bath className="w-5 h-5 text-blue-500 mb-1" />
              <span className="text-xs font-semibold text-gray-700">{property.bathrooms} Baths</span>
            </div>
          )}
          {property.area_sqm && (
            <div className="flex flex-col items-center">
              <Square className="w-5 h-5 text-blue-500 mb-1" />
              <span className="text-xs font-semibold text-gray-700">{property.area_sqm}m²</span>
            </div>
          )}
        </div>

        <Link
          to={`/properties/${property.id}`}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold px-6 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center group-hover:scale-105"
          data-testid={`view-property-${property.id}`}
        >
          <Eye className="w-5 h-5 mr-2" />
          View Details
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