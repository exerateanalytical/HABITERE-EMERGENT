import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import ServiceCard from '../components/ServiceCard';
import FilterSidebar from '../components/FilterSidebar';
import { 
  Search, 
  Filter, 
  MapPin, 
  Star, 
  Users, 
  Eye,
  Grid3x3,
  List,
  ChevronDown,
  X,
  Wrench,
  Building,
  Palette,
  Zap,
  Droplets,
  SlidersHorizontal,
  Shield,
  Phone,
  Mail,
  Award
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const serviceCategories = [
  { value: 'construction', label: 'Construction', icon: Building },
  { value: 'plumbing', label: 'Plumbing', icon: Droplets },
  { value: 'electrical', label: 'Electrical', icon: Zap },
  { value: 'painting', label: 'Painting', icon: Palette },
  { value: 'carpentry', label: 'Carpentry', icon: Wrench },
  { value: 'interior_design', label: 'Interior Design', icon: Palette },
  { value: 'cleaning', label: 'Cleaning', icon: Wrench },
  { value: 'architecture', label: 'Architecture', icon: Building },
  { value: 'bricklaying', label: 'Bricklaying', icon: Building },
  { value: 'borehole_drilling', label: 'Borehole Drilling', icon: Droplets },
  { value: 'evaluation', label: 'Property Evaluation', icon: Building },
  { value: 'materials', label: 'Building Materials', icon: Building },
  { value: 'furnishing', label: 'Furnishing', icon: Wrench }
];

const Services = () => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    category: '',
    location: ''
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [viewMode, setViewMode] = useState('grid');

  useEffect(() => {
    fetchServices();
  }, [filters]);

  const fetchServices = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value) {
          params.append(key, value);
        }
      });

      const response = await axios.get(`${API}/services?${params.toString()}`);
      setServices(response.data || []);
    } catch (err) {
      console.error('Error fetching services:', err);
      setError('Failed to load services');
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
      category: '',
      location: ''
    });
  };

  const filteredServices = services.filter(service =>
    service.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    service.location.toLowerCase().includes(searchQuery.toLowerCase()) ||
    service.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    service.category.toLowerCase().includes(searchQuery.toLowerCase())
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
    <div className="min-h-screen bg-gray-50" data-testid="services-page">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Professional Services</h1>
              <p className="text-gray-600 mt-1">
                Connect with {filteredServices.length} verified professionals across Cameroon
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
                placeholder="Search services by title, category, location, or description..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="form-input pl-10 w-full"
                data-testid="search-input"
              />
            </div>

            {/* Service categories */}
            <div className="flex flex-wrap gap-2">
              {serviceCategories.slice(0, 8).map((category) => {
                const Icon = category.icon;
                return (
                  <button
                    key={category.value}
                    onClick={() => handleFilterChange('category', 
                      filters.category === category.value ? '' : category.value
                    )}
                    className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                      filters.category === category.value
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-700 hover:bg-blue-50 border border-gray-200'
                    }`}
                    data-testid={`category-${category.value}`}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {category.label}
                  </button>
                );
              })}
            </div>

            {/* Filter toggle */}
            <div className="flex items-center justify-between">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="btn-secondary flex items-center"
                data-testid="toggle-filters-btn"
              >
                <Filter className="w-4 h-4 mr-2" />
                More Filters
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

            {/* Additional filters */}
            {showFilters && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Service Category
                    </label>
                    <select
                      value={filters.category}
                      onChange={(e) => handleFilterChange('category', e.target.value)}
                      className="form-select"
                      data-testid="filter-category"
                    >
                      <option value="">All Categories</option>
                      {serviceCategories.map((category) => (
                        <option key={category.value} value={category.value}>
                          {category.label}
                        </option>
                      ))}
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
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 mb-6" data-testid="error-message">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {filteredServices.length === 0 && !loading && (
          <div className="text-center py-12" data-testid="no-services">
            <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Wrench className="w-12 h-12 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Services Found</h3>
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

        {/* Services grid/list */}
        {viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="services-grid">
            {filteredServices.map((service) => (
              <ServiceCard key={service.id} service={service} />
            ))}
          </div>
        ) : (
          <div className="space-y-4" data-testid="services-list">
            {filteredServices.map((service) => (
              <ServiceListItem key={service.id} service={service} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// ServiceCard component is imported from ../components/ServiceCard

const ServiceListItem = ({ service }) => {
  const categoryInfo = serviceCategories.find(cat => cat.value === service.category) || 
                      { label: service.category, icon: Wrench };
  const Icon = categoryInfo.icon;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow" data-testid={`service-list-${service.id}`}>
      <div className="flex flex-col md:flex-row">
        <div className="md:w-80 h-48 md:h-auto relative overflow-hidden flex-shrink-0">
          <img
            src={service.images?.[0] || 'https://images.unsplash.com/photo-1505798577917-a65157d3320a'}
            alt={service.title}
            className="w-full h-full object-cover"
          />
          
          <div className="absolute top-3 left-3 flex flex-wrap gap-2">
            <span className="badge badge-primary flex items-center">
              <Icon className="w-3 h-3 mr-1" />
              {categoryInfo.label}
            </span>
            {service.verified && (
              <span className="badge badge-success">Verified</span>
            )}
          </div>
        </div>

        <div className="flex-1 p-6">
          <div className="mb-3">
            <h3 className="text-xl font-semibold text-gray-900 mb-1">
              {service.title}
            </h3>
            <div className="flex items-center text-gray-500 text-sm">
              <MapPin className="w-4 h-4 mr-1" />
              {service.location}
            </div>
          </div>

          <p className="text-gray-600 mb-4 line-clamp-2">
            {service.description}
          </p>

          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-6 text-sm text-gray-500">
              <div className="flex items-center">
                <Star className="w-4 h-4 text-yellow-400 fill-current mr-1" />
                <span>4.8 (24 reviews)</span>
              </div>
              <div className="flex items-center">
                <Users className="w-4 h-4 mr-1" />
                <span>15 projects</span>
              </div>
            </div>

            {service.price_range && (
              <div className="text-lg font-semibold text-blue-600">
                {service.price_range}
              </div>
            )}
          </div>

          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-500">
              Available for new projects
            </div>
            
            <Link
              to={`/services/${service.id}`}
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

export default Services;