import React, { useState } from 'react';
import { Search, Filter, MapPin, DollarSign, Home, ChevronDown, X } from 'lucide-react';

const SearchFilters = ({ 
  onSearch, 
  onFilterChange, 
  showAdvanced = false,
  type = 'property' // 'property' or 'service'
}) => {
  const [isAdvancedOpen, setIsAdvancedOpen] = useState(showAdvanced);
  const [filters, setFilters] = useState({
    search: '',
    location: '',
    min_price: '',
    max_price: '',
    property_type: '',
    listing_type: '',
    bedrooms: '',
    category: ''
  });

  const handleInputChange = (field, value) => {
    const newFilters = { ...filters, [field]: value };
    setFilters(newFilters);
    if (onFilterChange) {
      onFilterChange(newFilters);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (onSearch) {
      onSearch(filters);
    }
  };

  const clearFilters = () => {
    const clearedFilters = {
      search: '',
      location: '',
      min_price: '',
      max_price: '',
      property_type: '',
      listing_type: '',
      bedrooms: '',
      category: ''
    };
    setFilters(clearedFilters);
    if (onFilterChange) {
      onFilterChange(clearedFilters);
    }
  };

  const hasActiveFilters = Object.values(filters).some(value => value !== '');

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
      {/* Main Search Bar */}
      <form onSubmit={handleSearch} className="space-y-4">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search Input */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder={type === 'property' ? "Search properties by title, location..." : "Search services by name, category..."}
              value={filters.search}
              onChange={(e) => handleInputChange('search', e.target.value)}
              className="form-input pl-10 w-full"
              data-testid="main-search-input"
            />
          </div>

          {/* Location Filter */}
          <div className="relative">
            <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Location"
              value={filters.location}
              onChange={(e) => handleInputChange('location', e.target.value)}
              className="form-input pl-10 w-full lg:w-48"
              data-testid="location-filter"
            />
          </div>

          {/* Quick Filters for Property */}
          {type === 'property' && (
            <>
              <select
                value={filters.listing_type}
                onChange={(e) => handleInputChange('listing_type', e.target.value)}
                className="form-select lg:w-36"
                data-testid="listing-type-filter"
              >
                <option value="">All Types</option>
                <option value="rent">For Rent</option>
                <option value="sale">For Sale</option>
                <option value="lease">For Lease</option>
              </select>

              <select
                value={filters.property_type}
                onChange={(e) => handleInputChange('property_type', e.target.value)}
                className="form-select lg:w-36"
                data-testid="property-type-filter"
              >
                <option value="">Property Type</option>
                <option value="house">House</option>
                <option value="apartment">Apartment</option>
                <option value="land">Land</option>
                <option value="commercial">Commercial</option>
              </select>
            </>
          )}

          {/* Quick Filters for Service */}
          {type === 'service' && (
            <select
              value={filters.category}
              onChange={(e) => handleInputChange('category', e.target.value)}
              className="form-select lg:w-48"
              data-testid="service-category-filter"
            >
              <option value="">All Categories</option>
              <option value="construction">Construction</option>
              <option value="plumbing">Plumbing</option>
              <option value="electrical">Electrical</option>
              <option value="painting">Painting</option>
              <option value="carpentry">Carpentry</option>
              <option value="interior_design">Interior Design</option>
              <option value="cleaning">Cleaning</option>
              <option value="architecture">Architecture</option>
            </select>
          )}

          {/* Search Button */}
          <button
            type="submit"
            className="btn-primary px-6"
            data-testid="search-btn"
          >
            <Search className="w-4 h-4 mr-2" />
            Search
          </button>
        </div>

        {/* Advanced Filters Toggle */}
        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={() => setIsAdvancedOpen(!isAdvancedOpen)}
            className="flex items-center text-gray-600 hover:text-blue-600 transition-colors"
            data-testid="toggle-advanced-filters"
          >
            <Filter className="w-4 h-4 mr-2" />
            Advanced Filters
            <ChevronDown className={`w-4 h-4 ml-1 transform transition-transform ${
              isAdvancedOpen ? 'rotate-180' : ''
            }`} />
          </button>

          {hasActiveFilters && (
            <button
              type="button"
              onClick={clearFilters}
              className="flex items-center text-red-600 hover:text-red-700 text-sm font-medium"
              data-testid="clear-filters-btn"
            >
              <X className="w-4 h-4 mr-1" />
              Clear All Filters
            </button>
          )}
        </div>

        {/* Advanced Filters Panel */}
        {isAdvancedOpen && (
          <div className="border-t border-gray-200 pt-4 mt-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Price Range */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <DollarSign className="w-4 h-4 inline mr-1" />
                  Price Range (XAF)
                </label>
                <div className="flex space-x-2">
                  <input
                    type="number"
                    placeholder="Min"
                    value={filters.min_price}
                    onChange={(e) => handleInputChange('min_price', e.target.value)}
                    className="form-input text-sm"
                    data-testid="min-price-filter"
                  />
                  <input
                    type="number"
                    placeholder="Max"
                    value={filters.max_price}
                    onChange={(e) => handleInputChange('max_price', e.target.value)}
                    className="form-input text-sm"
                    data-testid="max-price-filter"
                  />
                </div>
              </div>

              {/* Property Specific Advanced Filters */}
              {type === 'property' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <Home className="w-4 h-4 inline mr-1" />
                      Bedrooms
                    </label>
                    <select
                      value={filters.bedrooms}
                      onChange={(e) => handleInputChange('bedrooms', e.target.value)}
                      className="form-select text-sm"
                      data-testid="bedrooms-filter"
                    >
                      <option value="">Any</option>
                      <option value="1">1+ Bedrooms</option>
                      <option value="2">2+ Bedrooms</option>
                      <option value="3">3+ Bedrooms</option>
                      <option value="4">4+ Bedrooms</option>
                      <option value="5">5+ Bedrooms</option>
                    </select>
                  </div>

                  {/* Additional property filters can be added here */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Verification Status
                    </label>
                    <select className="form-select text-sm">
                      <option value="">All Properties</option>
                      <option value="verified">Verified Only</option>
                      <option value="unverified">Unverified</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Availability
                    </label>
                    <select className="form-select text-sm">
                      <option value="">All</option>
                      <option value="available">Available Now</option>
                      <option value="coming_soon">Coming Soon</option>
                    </select>
                  </div>
                </>
              )}

              {/* Service Specific Advanced Filters */}
              {type === 'service' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Availability
                    </label>
                    <select className="form-select text-sm">
                      <option value="">All Services</option>
                      <option value="available">Available Now</option>
                      <option value="busy">Busy</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Rating
                    </label>
                    <select className="form-select text-sm">
                      <option value="">All Ratings</option>
                      <option value="4">4+ Stars</option>
                      <option value="4.5">4.5+ Stars</option>
                      <option value="5">5 Stars Only</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Response Time
                    </label>
                    <select className="form-select text-sm">
                      <option value="">Any Response Time</option>
                      <option value="1">Within 1 hour</option>
                      <option value="2">Within 2 hours</option>
                      <option value="24">Within 24 hours</option>
                    </select>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </form>

      {/* Active Filters Display */}
      {hasActiveFilters && (
        <div className="border-t border-gray-200 pt-4 mt-4">
          <div className="flex flex-wrap gap-2">
            <span className="text-sm text-gray-600 mr-2">Active filters:</span>
            {Object.entries(filters).map(([key, value]) => {
              if (!value) return null;
              return (
                <span
                  key={key}
                  className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                >
                  {key.replace('_', ' ')}: {value}
                  <button
                    onClick={() => handleInputChange(key, '')}
                    className="ml-1 hover:text-blue-600"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchFilters;