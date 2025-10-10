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

  const handleFilterChange = (newFilters) => {
    // Handle both old format (key, value) and new format (filters object)
    if (typeof newFilters === 'object' && newFilters !== null) {
      setFilters(prev => ({
        ...prev,
        ...newFilters
      }));
      setSearchQuery(newFilters.search || '');
    }
  };

  const handleOldFilterChange = (key, value) => {
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
      {/* Enhanced Services Header */}
      <div className="relative bg-gradient-to-br from-white via-purple-50/40 to-indigo-50/40 shadow-lg border-b border-gray-200 overflow-hidden">
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='0.1'%3E%3Cpath d='M30 30m-2 0a2 2 0 1 1 4 0a2 2 0 1 1-4 0'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }}></div>
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-6 lg:space-y-0">
            <div className="text-center lg:text-left">
              <div className="flex flex-col lg:flex-row lg:items-center space-y-4 lg:space-y-0 lg:space-x-6 mb-4">
                <div>
                  <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 mb-2">
                    Professional
                    <span className="bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent"> Services</span>
                  </h1>
                  <p className="text-lg md:text-xl text-gray-600">
                    Connect with <span className="font-bold text-purple-600">{filteredServices.length}</span> verified professionals across Cameroon
                  </p>
                </div>
              </div>
              
              {/* Service categories preview */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl mx-auto lg:mx-0">
                <div className="bg-white/70 backdrop-blur-sm rounded-xl p-3 text-center shadow-lg border border-white/20">
                  <div className="text-lg font-bold text-purple-600">89</div>
                  <div className="text-xs text-gray-600">Construction</div>
                </div>
                <div className="bg-white/70 backdrop-blur-sm rounded-xl p-3 text-center shadow-lg border border-white/20">
                  <div className="text-lg font-bold text-blue-600">76</div>
                  <div className="text-xs text-gray-600">Plumbing</div>
                </div>
                <div className="bg-white/70 backdrop-blur-sm rounded-xl p-3 text-center shadow-lg border border-white/20">
                  <div className="text-lg font-bold text-indigo-600">65</div>
                  <div className="text-xs text-gray-600">Electrical</div>
                </div>
                <div className="bg-white/70 backdrop-blur-sm rounded-xl p-3 text-center shadow-lg border border-white/20">
                  <div className="text-lg font-bold text-green-600">54</div>
                  <div className="text-xs text-gray-600">Cleaning</div>
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
                  placeholder="Search services..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-2xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-gray-900 placeholder-gray-500 shadow-lg"
                />
              </div>
              
              <div className="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-4">
                {/* Mobile Filter Button */}
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="lg:hidden w-full sm:w-auto bg-white/90 backdrop-blur-sm border border-gray-200 px-6 py-3 rounded-2xl flex items-center justify-center space-x-2 hover:bg-white hover:shadow-lg transition-all duration-200 shadow-lg"
                >
                  <SlidersHorizontal className="w-5 h-5 text-gray-600" />
                  <span className="font-semibold text-gray-700">Smart Filters</span>
                </button>

                {/* Sort Dropdown */}
                <div className="relative w-full sm:w-auto">
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="w-full sm:w-auto bg-white/90 backdrop-blur-sm border border-gray-200 px-6 py-3 rounded-2xl appearance-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 font-semibold text-gray-700 shadow-lg pr-12"
                  >
                    <option value="newest">🕐 Newest Professionals</option>
                    <option value="rating">⭐ Highest Rated</option>
                    <option value="popular">🔥 Most Popular</option>
                    <option value="price_low">💰 Most Affordable</option>
                    <option value="price_high">💎 Premium Services</option>
                    <option value="experience">👨‍💼 Most Experienced</option>
                  </select>
                  <ChevronDown className="absolute right-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
                </div>

                {/* View Toggle */}
                <div className="flex items-center bg-white/90 backdrop-blur-sm border border-gray-200 rounded-2xl p-1 shadow-lg">
                  <button
                    onClick={() => setViewMode('grid')}
                    className={`p-3 rounded-xl transition-all duration-200 ${
                      viewMode === 'grid' 
                        ? 'bg-gradient-to-r from-purple-500 to-indigo-500 text-white shadow-lg' 
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
                        ? 'bg-gradient-to-r from-purple-500 to-indigo-500 text-white shadow-lg' 
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
  const [imageLoaded, setImageLoaded] = React.useState(false);

  return (
    <div className="group bg-white rounded-3xl shadow-xl hover:shadow-2xl transition-all duration-500 overflow-hidden border border-gray-100 hover:border-purple-300 transform hover:-translate-y-3 hover:rotate-1" data-testid={`service-card-${service.id}`}>
      <div className="relative overflow-hidden h-64">
        {/* Professional image with loading state */}
        <div className={`w-full h-full bg-gradient-to-br from-purple-200 to-indigo-300 ${!imageLoaded ? 'animate-pulse' : ''}`}>
          <img
            src={service.images?.[0] || 'https://images.unsplash.com/photo-1505798577917-a65157d3320a?w=800&q=80'}
            alt={service.title}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
            onLoad={() => setImageLoaded(true)}
          />
        </div>
        
        {/* Enhanced overlay gradient */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-black/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        
        {/* Top badges */}
        <div className="absolute top-4 left-4 flex flex-wrap gap-2">
          <span className="px-3 py-2 rounded-2xl text-xs font-bold bg-purple-600/95 text-white shadow-xl backdrop-blur-md border border-white/20 flex items-center">
            <Icon className="w-3 h-3 mr-1" />
            {categoryInfo.label}
          </span>
          {service.verified && (
            <span className="px-3 py-2 rounded-2xl text-xs font-bold bg-emerald-600/95 text-white shadow-xl backdrop-blur-md border border-white/20 flex items-center animate-pulse">
              <Shield className="w-3 h-3 mr-1" />
              ✓ Verified Pro
            </span>
          )}
          {service.top_rated && (
            <span className="px-3 py-2 rounded-2xl text-xs font-bold bg-yellow-500/95 text-white shadow-xl backdrop-blur-md border border-white/20 flex items-center">
              👑 Top Rated
            </span>
          )}
        </div>
        
        {/* Online status indicator */}
        <div className="absolute top-4 right-4 flex items-center space-x-2">
          <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse shadow-lg"></div>
          <span className="text-xs font-bold text-white bg-black/50 backdrop-blur-md px-2 py-1 rounded-full">Online</span>
        </div>

        {/* Rating and response time */}
        <div className="absolute bottom-4 left-4 flex items-center space-x-2">
          <div className="flex items-center bg-white/95 backdrop-blur-md rounded-xl px-3 py-2 shadow-lg border border-white/20">
            <Star className="w-4 h-4 text-yellow-400 fill-current mr-1" />
            <span className="text-sm font-bold text-gray-900">{service.rating || '4.9'}</span>
            <span className="text-xs text-gray-600 ml-1">({service.reviews || '47'})</span>
          </div>
          <div className="bg-blue-500/95 backdrop-blur-md rounded-xl px-3 py-2 shadow-lg border border-white/20">
            <span className="text-xs font-bold text-white">⚡ Responds in 1hr</span>
          </div>
        </div>

        {/* Price badge */}
        <div className="absolute bottom-4 right-4 bg-gradient-to-r from-purple-600 to-indigo-600 backdrop-blur-md rounded-xl px-4 py-2 shadow-lg border border-white/20">
          <div className="text-sm font-bold text-white">
            {service.price_range || 'From 25,000 XAF'}
          </div>
        </div>
      </div>

      <div className="p-6 space-y-4">
        {/* Professional info */}
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-2 line-clamp-2 group-hover:text-purple-600 transition-colors duration-300">
            {service.title}
          </h3>
          <div className="flex items-center justify-between text-sm mb-2">
            <div className="flex items-center text-gray-500">
              <MapPin className="w-4 h-4 mr-2 text-purple-500" />
              <span className="font-semibold">{service.location}</span>
            </div>
            <span className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-xs font-bold">
              {service.experience || '5+ Years'}
            </span>
          </div>
          <p className="text-gray-600 text-sm line-clamp-2 leading-relaxed">
            {service.description}
          </p>
        </div>

        {/* Professional stats */}
        <div className="grid grid-cols-3 gap-3 py-4 bg-gradient-to-br from-purple-50 to-indigo-50 rounded-2xl">
          <div className="text-center">
            <div className="w-8 h-8 bg-purple-100 rounded-xl flex items-center justify-center mx-auto mb-2">
              <Users className="w-4 h-4 text-purple-600" />
            </div>
            <div className="text-sm font-bold text-gray-900">{service.completed_projects || '24'}</div>
            <div className="text-xs text-gray-500">Projects</div>
          </div>
          <div className="text-center">
            <div className="w-8 h-8 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-2">
              <Award className="w-4 h-4 text-blue-600" />
            </div>
            <div className="text-sm font-bold text-gray-900">{service.certifications || '3'}</div>
            <div className="text-xs text-gray-500">Certified</div>
          </div>
          <div className="text-center">
            <div className="w-8 h-8 bg-green-100 rounded-xl flex items-center justify-center mx-auto mb-2">
              <Shield className="w-4 h-4 text-green-600" />
            </div>
            <div className="text-sm font-bold text-gray-900">100%</div>
            <div className="text-xs text-gray-500">Success</div>
          </div>
        </div>

        {/* Skills/Specialties */}
        <div className="flex flex-wrap gap-2">
          {(service.skills || ['Licensed', 'Insured', 'Same Day']).slice(0, 3).map((skill, index) => (
            <span key={index} className="px-3 py-1 bg-gradient-to-r from-purple-100 to-indigo-100 text-purple-700 text-xs rounded-full font-semibold border border-purple-200">
              {skill}
            </span>
          ))}
        </div>

        {/* Action buttons */}
        <div className="flex items-center space-x-3">
          <Link
            to={`/services/${service.id}`}
            className="flex-1 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-bold px-6 py-4 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center group-hover:scale-105"
          >
            <Eye className="w-5 h-5 mr-2" />
            View Profile
          </Link>
          <button className="p-4 bg-gray-100 hover:bg-purple-100 rounded-2xl transition-colors duration-200 group-hover:scale-105">
            <Phone className="w-5 h-5 text-gray-600 hover:text-purple-600" />
          </button>
          <button className="p-4 bg-gray-100 hover:bg-purple-100 rounded-2xl transition-colors duration-200 group-hover:scale-105">
            <Mail className="w-5 h-5 text-gray-600 hover:text-purple-600" />
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