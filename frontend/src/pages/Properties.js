import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import ServicesCarousel from '../components/ServicesCarousel';
import SearchFilters from '../components/SearchFilters';
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
  X
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
  const [showFilters, setShowFilters] = useState(false);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [favorites, setFavorites] = useState(new Set());

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

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      property_type: '',
      listing_type: '',
      location: '',
      min_price: '',
      max_price: '',
      bedrooms: ''
    });
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
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Properties</h1>
              <p className="text-gray-600 mt-1">
                Discover {filteredProperties.length} properties available in Cameroon
              </p>
            </div>

            {/* View toggle */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-md transition-colors ${
                    viewMode === 'grid' ? 'bg-white shadow text-blue-600' : 'text-gray-500'
                  }`}
                  data-testid="grid-view-btn"
                >
                  <Grid3x3 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-md transition-colors ${
                    viewMode === 'list' ? 'bg-white shadow text-blue-600' : 'text-gray-500'
                  }`}
                  data-testid="list-view-btn"
                >
                  <List className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Search and filters */}
          <div className="mt-6 space-y-4">
            {/* Search bar */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search properties by title, location, or description..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="form-input pl-10 w-full"
                data-testid="search-input"
              />
            </div>

            {/* Filter toggle */}
            <div className="flex items-center justify-between">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="btn-secondary flex items-center"
                data-testid="toggle-filters-btn"
              >
                <Filter className="w-4 h-4 mr-2" />
                Filters
                <ChevronDown className={`w-4 h-4 ml-2 transform transition-transform ${
                  showFilters ? 'rotate-180' : ''
                }`} />
              </button>

              {Object.values(filters).some(value => value) && (
                <button
                  onClick={clearFilters}
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center"
                  data-testid="clear-filters-btn"
                >
                  <X className="w-4 h-4 mr-1" />
                  Clear Filters
                </button>
              )}
            </div>

            {/* Filters */}
            {showFilters && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Property Type
                    </label>
                    <select
                      value={filters.property_type}
                      onChange={(e) => handleFilterChange('property_type', e.target.value)}
                      className="form-select"
                      data-testid="filter-property-type"
                    >
                      <option value="">All Types</option>
                      <option value="house">House</option>
                      <option value="apartment">Apartment</option>
                      <option value="land">Land</option>
                      <option value="commercial">Commercial</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Listing Type
                    </label>
                    <select
                      value={filters.listing_type}
                      onChange={(e) => handleFilterChange('listing_type', e.target.value)}
                      className="form-select"
                      data-testid="filter-listing-type"
                    >
                      <option value="">All Listings</option>
                      <option value="rent">For Rent</option>
                      <option value="sale">For Sale</option>
                      <option value="lease">For Lease</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Location
                    </label>
                    <input
                      type="text"
                      placeholder="Enter location"
                      value={filters.location}
                      onChange={(e) => handleFilterChange('location', e.target.value)}
                      className="form-input"
                      data-testid="filter-location"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Min Price (XAF)
                    </label>
                    <input
                      type="number"
                      placeholder="Minimum"
                      value={filters.min_price}
                      onChange={(e) => handleFilterChange('min_price', e.target.value)}
                      className="form-input"
                      data-testid="filter-min-price"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Max Price (XAF)
                    </label>
                    <input
                      type="number"
                      placeholder="Maximum"
                      value={filters.max_price}
                      onChange={(e) => handleFilterChange('max_price', e.target.value)}
                      className="form-input"
                      data-testid="filter-max-price"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Bedrooms
                    </label>
                    <select
                      value={filters.bedrooms}
                      onChange={(e) => handleFilterChange('bedrooms', e.target.value)}
                      className="form-select"
                      data-testid="filter-bedrooms"
                    >
                      <option value="">Any</option>
                      <option value="1">1+</option>
                      <option value="2">2+</option>
                      <option value="3">3+</option>
                      <option value="4">4+</option>
                      <option value="5">5+</option>
                    </select>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Professional Services Carousel */}
        <div className="mb-8">
          <ServicesCarousel 
            title="Find Property Services" 
            limit={8}
            showAll={true}
          />
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 mb-6" data-testid="error-message">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {filteredProperties.length === 0 && !loading && (
          <div className="text-center py-12" data-testid="no-properties">
            <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-12 h-12 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Properties Found</h3>
            <p className="text-gray-600 mb-4">
              Try adjusting your search criteria or clearing the filters
            </p>
            <button
              onClick={clearFilters}
              className="btn-primary"
            >
              Clear Filters
            </button>
          </div>
        )}

        {/* Properties grid/list */}
        {viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="properties-grid">
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
          <div className="space-y-4" data-testid="properties-list">
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
  );
};

const PropertyCard = ({ property, isFavorite, onToggleFavorite, formatPrice }) => {
  return (
    <div className="property-card group" data-testid={`property-card-${property.id}`}>
      <div className="relative overflow-hidden">
        <img
          src={property.images?.[0] || 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2'}
          alt={property.title}
          className="property-image group-hover:scale-110"
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
        
        <button
          onClick={() => onToggleFavorite(property.id)}
          className={`absolute top-3 right-3 p-2 rounded-full transition-colors ${
            isFavorite ? 'bg-red-500 text-white' : 'bg-white text-gray-600 hover:text-red-500'
          }`}
          data-testid={`favorite-btn-${property.id}`}
        >
          <Heart className={`w-4 h-4 ${isFavorite ? 'fill-current' : ''}`} />
        </button>
      </div>

      <div className="card-body">
        <div className="mb-3">
          <h3 className="text-lg font-semibold text-gray-900 mb-1 line-clamp-2">
            {property.title}
          </h3>
          <div className="flex items-center text-gray-500 text-sm">
            <MapPin className="w-4 h-4 mr-1" />
            {property.location}
          </div>
        </div>

        <div className="text-2xl font-bold text-blue-600 mb-3">
          {formatPrice(property.price)}
          {property.listing_type === 'rent' && <span className="text-sm text-gray-500">/month</span>}
        </div>

        <div className="flex items-center text-gray-600 text-sm space-x-4 mb-4">
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
        </div>

        <div className="flex items-center justify-between">
          <Link
            to={`/properties/${property.id}`}
            className="btn-primary flex-1 mr-2 justify-center"
            data-testid={`view-property-${property.id}`}
          >
            <Eye className="w-4 h-4 mr-2" />
            View Details
          </Link>
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