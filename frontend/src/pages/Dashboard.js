import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import ServicesCarousel from '../components/ServicesCarousel';
import { 
  Building, 
  Wrench, 
  MessageSquare, 
  Calendar, 
  DollarSign, 
  Plus, 
  Eye, 
  Edit,
  Trash2,
  Star,
  TrendingUp,
  Users,
  CheckCircle,
  Clock,
  AlertCircle
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    properties: 0,
    services: 0,
    bookings: 0,
    messages: 0
  });
  const [recentProperties, setRecentProperties] = useState([]);
  const [recentServices, setRecentServices] = useState([]);
  const [recentBookings, setRecentBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchDashboardData();
    }
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch user's properties if they can list properties
      if (['property_owner', 'real_estate_agent', 'real_estate_company'].includes(user.role)) {
        const propertiesResponse = await axios.get(`${API}/properties`);
        const userProperties = propertiesResponse.data.filter(p => p.owner_id === user.id);
        setRecentProperties(userProperties.slice(0, 3));
        setStats(prev => ({ ...prev, properties: userProperties.length }));
      }

      // Fetch user's services if they can provide services
      const serviceProviderRoles = [
        'construction_company', 'bricklayer', 'plumber', 'electrician', 
        'interior_designer', 'borehole_driller', 'cleaning_company', 
        'painter', 'architect', 'carpenter', 'evaluator', 
        'building_material_supplier', 'furnishing_shop'
      ];
      
      if (serviceProviderRoles.includes(user.role)) {
        const servicesResponse = await axios.get(`${API}/services`);
        const userServices = servicesResponse.data.filter(s => s.provider_id === user.id);
        setRecentServices(userServices.slice(0, 3));
        setStats(prev => ({ ...prev, services: userServices.length }));
      }

      // Fetch user's bookings
      const bookingsResponse = await axios.get(`${API}/bookings`);
      setRecentBookings(bookingsResponse.data.slice(0, 5));
      setStats(prev => ({ ...prev, bookings: bookingsResponse.data.length }));

      // Fetch messages count
      const messagesResponse = await axios.get(`${API}/messages`);
      const unreadCount = messagesResponse.data.filter(m => 
        m.receiver_id === user.id && !m.is_read
      ).length;
      setStats(prev => ({ ...prev, messages: unreadCount }));

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const canListProperties = ['property_owner', 'real_estate_agent', 'real_estate_company'].includes(user?.role);
  
  const serviceProviderRoles = [
    'construction_company', 'bricklayer', 'plumber', 'electrician', 
    'interior_designer', 'borehole_driller', 'cleaning_company', 
    'painter', 'architect', 'carpenter', 'evaluator', 
    'building_material_supplier', 'furnishing_shop'
  ];
  
  const canProvideServices = serviceProviderRoles.includes(user?.role);

  const formatPrice = (price) => {
    return new Intl.NumberFormat('fr-CM', {
      style: 'currency',
      currency: 'XAF',
      minimumFractionDigits: 0
    }).format(price);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'successful':
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'failed':
      case 'cancelled':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status) => {
    const baseClasses = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium";
    
    switch (status) {
      case 'successful':
      case 'completed':
        return `${baseClasses} bg-green-100 text-green-800`;
      case 'pending':
      case 'confirmed':
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      case 'failed':
      case 'cancelled':
        return `${baseClasses} bg-red-100 text-red-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, index) => (
              <div key={index} className="card animate-pulse">
                <div className="card-body">
                  <div className="h-4 bg-gray-300 rounded mb-2"></div>
                  <div className="h-8 bg-gray-300 rounded"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="dashboard">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.name}!
          </h1>
          <p className="text-gray-600 mt-1 capitalize">
            {user?.role?.replace('_', ' ')} Dashboard
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {canListProperties && (
            <div className="card hover-lift" data-testid="properties-stat">
              <div className="card-body">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Building className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Properties Listed</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.properties}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {canProvideServices && (
            <div className="card hover-lift" data-testid="services-stat">
              <div className="card-body">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <Wrench className="w-6 h-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Services Offered</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.services}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="card hover-lift" data-testid="bookings-stat">
            <div className="card-body">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Calendar className="w-6 h-6 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Bookings</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.bookings}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="card hover-lift" data-testid="messages-stat">
            <div className="card-body">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                  <MessageSquare className="w-6 h-6 text-yellow-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Unread Messages</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.messages}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="flex flex-wrap gap-4">
            {canListProperties && (
              <Link
                to="/properties/new"
                className="btn-primary"
                data-testid="add-property-btn"
              >
                <Plus className="w-5 h-5 mr-2" />
                Add Property
              </Link>
            )}
            
            {canProvideServices && (
              <Link
                to="/services/new"
                className="btn-primary"
                data-testid="add-service-btn"
              >
                <Plus className="w-5 h-5 mr-2" />
                Add Service
              </Link>
            )}

            <Link
              to="/properties"
              className="btn-secondary"
              data-testid="browse-properties-btn"
            >
              <Building className="w-5 h-5 mr-2" />
              Browse Properties
            </Link>

            <Link
              to="/services"
              className="btn-secondary"
              data-testid="browse-services-btn"
            >
              <Wrench className="w-5 h-5 mr-2" />
              Find Services
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
          {/* Recent Properties */}
          {canListProperties && recentProperties.length > 0 && (
            <div className="card" data-testid="recent-properties">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-gray-900">Recent Properties</h3>
                <Link to="/properties" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                  View all
                </Link>
              </div>
              <div className="card-body">
                <div className="space-y-4">
                  {recentProperties.map((property) => (
                    <div key={property.id} className="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
                      <img
                        src={property.images?.[0] || 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2'}
                        alt={property.title}
                        className="w-16 h-16 object-cover rounded-lg"
                      />
                      <div className="flex-1 min-w-0">
                        <h4 className="text-sm font-medium text-gray-900 truncate">
                          {property.title}
                        </h4>
                        <p className="text-sm text-gray-500 truncate">
                          {property.location}
                        </p>
                        <p className="text-sm font-semibold text-blue-600">
                          {formatPrice(property.price)}
                        </p>
                      </div>
                      <Link
                        to={`/properties/${property.id}`}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        <Eye className="w-4 h-4" />
                      </Link>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Recent Services */}
          {canProvideServices && recentServices.length > 0 && (
            <div className="card" data-testid="recent-services">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-gray-900">Recent Services</h3>
                <Link to="/services" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                  View all
                </Link>
              </div>
              <div className="card-body">
                <div className="space-y-4">
                  {recentServices.map((service) => (
                    <div key={service.id} className="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
                      <img
                        src={service.images?.[0] || 'https://images.unsplash.com/photo-1505798577917-a65157d3320a'}
                        alt={service.title}
                        className="w-16 h-16 object-cover rounded-lg"
                      />
                      <div className="flex-1 min-w-0">
                        <h4 className="text-sm font-medium text-gray-900 truncate">
                          {service.title}
                        </h4>
                        <p className="text-sm text-gray-500 truncate">
                          {service.location}
                        </p>
                        <span className="inline-block px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full capitalize">
                          {service.category}
                        </span>
                      </div>
                      <Link
                        to={`/services/${service.id}`}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        <Eye className="w-4 h-4" />
                      </Link>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Recent Bookings */}
          <div className="card" data-testid="recent-bookings">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">Recent Bookings</h3>
              <Link to="/bookings" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                View all
              </Link>
            </div>
            <div className="card-body">
              {recentBookings.length > 0 ? (
                <div className="space-y-4">
                  {recentBookings.map((booking) => (
                    <div key={booking.id} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(booking.status)}
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {booking.property_id ? 'Property Booking' : 'Service Booking'}
                          </p>
                          <p className="text-xs text-gray-500">
                            {new Date(booking.scheduled_date).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <span className={getStatusBadge(booking.status)}>
                        {booking.status}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No bookings yet</p>
                  <Link to="/properties" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                    Browse properties to book
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Role-specific tips */}
        <div className="mt-8">
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">
              Tips for {user?.role?.replace('_', ' ')}s
            </h3>
            <div className="text-blue-800">
              {user?.role === 'property_seeker' && (
                <ul className="space-y-1 text-sm">
                  <li>• Use filters to narrow down your property search</li>
                  <li>• Save your favorite properties for quick access</li>
                  <li>• Contact property owners directly through messaging</li>
                </ul>
              )}
              
              {canListProperties && (
                <ul className="space-y-1 text-sm">
                  <li>• Upload high-quality photos to attract more inquiries</li>
                  <li>• Keep your property information updated</li>
                  <li>• Respond quickly to potential tenant messages</li>
                </ul>
              )}
              
              {canProvideServices && (
                <ul className="space-y-1 text-sm">
                  <li>• Showcase your best work with portfolio images</li>
                  <li>• Keep your service availability status updated</li>
                  <li>• Build trust by completing projects on time</li>
                </ul>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;