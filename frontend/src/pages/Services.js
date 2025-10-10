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
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [viewMode, setViewMode] = useState('grid');
  const [sortBy, setSortBy] = useState('newest');

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
      <div className="bg-gradient-to-br from-white via-purple-50/30 to-blue-50/30 shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-6 lg:space-y-0">
            <div className="text-center lg:text-left">
              <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
                Professional Services
              </h1>
              <p className="text-lg text-gray-600">
                Connect with <span className="font-semibold text-purple-600">{filteredServices.length}</span> verified professionals across Cameroon
              </p>
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
                  className="w-full sm:w-auto bg-white border border-gray-200 px-4 py-3 rounded-xl appearance-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 font-medium text-gray-700"
                >
                  <option value="newest">Newest First</option>
                  <option value="rating">Highest Rated</option>
                  <option value="popular">Most Popular</option>
                  <option value="price_low">Price: Low to High</option>
                  <option value="price_high">Price: High to Low</option>
                </select>
                <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
              </div>

              {/* View Toggle */}
              <div className="flex items-center bg-white border border-gray-200 rounded-xl p-1">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-lg transition-all duration-200 ${
                    viewMode === 'grid' 
                      ? 'bg-purple-500 text-white shadow-md' 
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
                      ? 'bg-purple-500 text-white shadow-md' 
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
            type="services"
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            onFiltersChange={handleFilterChange}
            className="hidden lg:block lg:w-80 flex-shrink-0"
          />

          {/* Mobile Sidebar */}
          <FilterSidebar
            type="services"
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            onFiltersChange={handleFilterChange}
            className="lg:hidden"
          />

          {/* Main Content */}
          <div className="flex-1 min-w-0">
            {/* Results Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  {filteredServices.length} Services Available
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  Certified professionals ready to help
                </p>
              </div>
            </div>
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-6 mb-6" data-testid="error-message">
                <p className="text-red-700">{error}</p>
              </div>
            )}

            {filteredServices.length === 0 && !loading && (
              <div className="text-center py-12 bg-white rounded-2xl shadow-sm border border-gray-100" data-testid="no-services">
                <div className="w-24 h-24 bg-gradient-to-br from-purple-100 to-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Wrench className="w-12 h-12 text-purple-500" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-3">No Services Found</h3>
                <p className="text-gray-600 mb-6 max-w-md mx-auto">
                  We couldn't find any services matching your criteria. Try adjusting your filters or search terms.
                </p>
                <button
                  onClick={clearFilters}
                  className="btn-primary"
                >
                  Clear All Filters
                </button>
              </div>
            )}

            {/* Services grid/list */}
            {viewMode === 'grid' ? (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6" data-testid="services-grid">
                {filteredServices.map((service) => (
                  <EnhancedServiceCard key={service.id} service={service} />
                ))}
              </div>
            ) : (
              <div className="space-y-6" data-testid="services-list">
                {filteredServices.map((service) => (
                  <ServiceListItem key={service.id} service={service} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const EnhancedServiceCard = ({ service }) => {
  const categoryInfo = serviceCategories.find(cat => cat.value === service.category) || 
                      { label: service.category, icon: Wrench };
  const Icon = categoryInfo.icon;

  return (
    <div className="group bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden border border-gray-100 hover:border-purple-200 transform hover:-translate-y-1" data-testid={`service-card-${service.id}`}>
      <div className="relative overflow-hidden h-56">
        <img
          src={service.images?.[0] || 'https://images.unsplash.com/photo-1505798577917-a65157d3320a?w=600&q=80'}
          alt={service.title}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
        />
        
        {/* Overlay gradient */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        
        <div className="absolute top-4 left-4 flex flex-wrap gap-2">
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-purple-500/90 text-white shadow-lg backdrop-blur-sm flex items-center">
            <Icon className="w-3 h-3 mr-1" />
            {categoryInfo.label}
          </span>
          {service.verified && (
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/90 text-white shadow-lg backdrop-blur-sm flex items-center">
              <Shield className="w-3 h-3 mr-1" />
              Verified
            </span>
          )}
        </div>

        {/* Rating overlay */}
        <div className="absolute bottom-4 left-4 flex items-center bg-white/90 backdrop-blur-sm rounded-lg px-2 py-1 shadow-lg">
          <Star className="w-4 h-4 text-yellow-400 fill-current mr-1" />
          <span className="text-sm font-semibold text-gray-900">4.8</span>
          <span className="text-xs text-gray-600 ml-1">(24)</span>
        </div>
      </div>

      <div className="p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2 group-hover:text-purple-600 transition-colors duration-200">
            {service.title}
          </h3>
          <div className="flex items-center text-gray-500 text-sm mb-2">
            <MapPin className="w-4 h-4 mr-2 text-purple-500" />
            <span className="font-medium">{service.location}</span>
          </div>
          <p className="text-gray-600 text-sm line-clamp-2">
            {service.description}
          </p>
        </div>

        <div className="flex items-center justify-between mb-4 py-3 bg-gray-50 rounded-xl px-4">
          <div className="flex items-center">
            <Users className="w-4 h-4 text-purple-500 mr-1" />
            <span className="text-xs font-semibold text-gray-700">15 Projects</span>
          </div>
          <div className="flex items-center">
            <Award className="w-4 h-4 text-purple-500 mr-1" />
            <span className="text-xs font-semibold text-gray-700">Expert</span>
          </div>
        </div>

        {service.price_range && (
          <div className="mb-4">
            <div className="text-lg font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              {service.price_range}
            </div>
          </div>
        )}

        <div className="flex items-center space-x-2 mb-4">
          <button className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold px-4 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center group-hover:scale-105">
            <Eye className="w-4 h-4 mr-2" />
            View Details
          </button>
          <button className="p-3 bg-gray-100 hover:bg-purple-100 rounded-xl transition-colors duration-200">
            <Phone className="w-4 h-4 text-gray-600 hover:text-purple-600" />
          </button>
          <button className="p-3 bg-gray-100 hover:bg-purple-100 rounded-xl transition-colors duration-200">
            <Mail className="w-4 h-4 text-gray-600 hover:text-purple-600" />
          </button>
        </div>
      </div>
    </div>
  );
};

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