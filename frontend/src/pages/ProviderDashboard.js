import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Shield, Plus, Edit, Trash2, Eye, CheckCircle, Clock, Calendar } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const ProviderDashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [services, setServices] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('services'); // services, bookings
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [serviceForm, setServiceForm] = useState({
    title: '',
    description: '',
    service_type: 'Security Guards',
    price_range: '',
    location: '',
    features: '',
    certifications: '',
    availability: 'Available',
    response_time: ''
  });

  useEffect(() => {
    if (!user) {
      navigate('/auth/login');
      return;
    }
    if (user.role !== 'security_provider' && user.role !== 'admin') {
      alert('Access denied. Security providers only.');
      navigate('/security');
      return;
    }
    fetchData();
  }, [user]);

  const fetchData = async () => {
    try {
      const [servicesRes, bookingsRes] = await Promise.all([
        axios.get(`${BACKEND_URL}/api/security/services`, { withCredentials: true }),
        axios.get(`${BACKEND_URL}/api/security/bookings`, { withCredentials: true })
      ]);
      
      // Filter to show only user's services
      const userServices = servicesRes.data.filter(s => s.provider_id === user.id);
      setServices(userServices);
      
      // Filter bookings for user's services
      const userBookings = bookingsRes.data.filter(b => b.provider_id === user.id);
      setBookings(userBookings);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateService = async (e) => {
    e.preventDefault();
    try {
      const serviceData = {
        ...serviceForm,
        features: serviceForm.features.split(',').map(f => f.trim()).filter(f => f),
        certifications: serviceForm.certifications.split(',').map(c => c.trim()).filter(c => c)
      };
      
      await axios.post(
        `${BACKEND_URL}/api/security/services`,
        serviceData,
        { withCredentials: true }
      );
      
      alert('Service created successfully!');
      setShowCreateModal(false);
      setServiceForm({
        title: '',
        description: '',
        service_type: 'Security Guards',
        price_range: '',
        location: '',
        features: '',
        certifications: '',
        availability: 'Available',
        response_time: ''
      });
      fetchData();
    } catch (error) {
      console.error('Error creating service:', error);
      alert(error.response?.data?.detail || 'Failed to create service');
    }
  };

  const handleDeleteService = async (serviceId) => {
    if (!window.confirm('Are you sure you want to delete this service?')) return;
    
    try {
      await axios.delete(
        `${BACKEND_URL}/api/security/services/${serviceId}`,
        { withCredentials: true }
      );
      alert('Service deleted successfully');
      fetchData();
    } catch (error) {
      console.error('Error deleting service:', error);
      alert('Failed to delete service');
    }
  };

  const handleConfirmBooking = async (bookingId) => {
    try {
      await axios.put(
        `${BACKEND_URL}/api/security/bookings/${bookingId}/confirm`,
        {},
        { withCredentials: true }
      );
      alert('Booking confirmed successfully!');
      fetchData();
    } catch (error) {
      console.error('Error confirming booking:', error);
      alert('Failed to confirm booking');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8\">
      <div className="container mx-auto px-4\">
        <div className="mb-8\">
          <h1 className="text-3xl font-bold mb-2\">Provider Dashboard</h1>
          <p className="text-gray-600\">Manage your security services and bookings</p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8\">
          <div className="bg-white rounded-lg shadow-md p-6\">
            <div className="text-3xl font-bold text-green-600 mb-2\">{services.length}</div>
            <div className="text-gray-600\">Active Services</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6\">
            <div className="text-3xl font-bold text-blue-600 mb-2\">
              {bookings.filter(b => b.status === 'pending').length}
            </div>
            <div className="text-gray-600\">Pending Bookings</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6\">
            <div className="text-3xl font-bold text-green-600 mb-2\">
              {bookings.filter(b => b.status === 'confirmed' || b.status === 'active').length}
            </div>
            <div className="text-gray-600\">Active Bookings</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6\">
            <div className="text-3xl font-bold text-gray-600 mb-2\">{bookings.length}</div>
            <div className="text-gray-600\">Total Bookings</div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-md mb-6\">
          <div className="flex border-b\">
            <button
              onClick={() => setActiveTab('services')}
              className={`px-6 py-4 font-semibold ${
                activeTab === 'services'
                  ? 'text-green-600 border-b-2 border-green-600'
                  : 'text-gray-600 hover:text-green-600'
              }`}
            >
              My Services ({services.length})
            </button>
            <button
              onClick={() => setActiveTab('bookings')}
              className={`px-6 py-4 font-semibold ${
                activeTab === 'bookings'
                  ? 'text-green-600 border-b-2 border-green-600'
                  : 'text-gray-600 hover:text-green-600'
              }`}
            >
              Bookings ({bookings.length})
            </button>
          </div>
        </div>

        {/* Services Tab */}
        {activeTab === 'services' && (
          <div>
            <div className="mb-6\">
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 flex items-center\"
              >
                <Plus className="w-5 h-5 mr-2\" />
                Create New Service
              </button>
            </div>

            {services.length === 0 ? (
              <div className="bg-white rounded-lg shadow-md p-12 text-center\">
                <Shield className="w-16 h-16 text-gray-400 mx-auto mb-4\" />
                <h3 className="text-xl font-bold mb-2\">No services yet</h3>
                <p className="text-gray-600 mb-6\">Create your first security service offering</p>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700\"
                >
                  Create Service
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6\">
                {services.map((service) => (
                  <div key={service.id} className="bg-white rounded-lg shadow-md p-6\">
                    <div className="flex items-start justify-between mb-3\">
                      <h3 className="text-lg font-bold\">{service.title}</h3>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        service.availability === 'Available'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-orange-100 text-orange-800'
                      }`}>
                        {service.availability}
                      </span>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-3 line-clamp-2\">{service.description}</p>
                    
                    <div className="flex items-center justify-between text-sm mb-4\">
                      <div>
                        <div className="text-gray-600\">Bookings</div>
                        <div className="font-bold\">{service.booking_count || 0}</div>
                      </div>
                      <div>
                        <div className="text-gray-600\">Type</div>
                        <div className="font-bold text-sm\">{service.service_type}</div>
                      </div>
                    </div>

                    <div className="flex gap-2\">
                      <button
                        onClick={() => navigate(`/security/services/${service.id}`)}
                        className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 flex items-center justify-center\"
                      >
                        <Eye className="w-4 h-4 mr-1\" />
                        View
                      </button>
                      <button
                        onClick={() => handleDeleteService(service.id)}
                        className="bg-red-600 text-white p-2 rounded-lg hover:bg-red-700\"
                      >
                        <Trash2 className="w-4 h-4\" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Bookings Tab */}
        {activeTab === 'bookings' && (
          <div>
            {bookings.length === 0 ? (
              <div className="bg-white rounded-lg shadow-md p-12 text-center\">
                <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4\" />
                <h3 className="text-xl font-bold mb-2\">No bookings yet</h3>
                <p className="text-gray-600\">Bookings for your services will appear here</p>
              </div>
            ) : (
              <div className="space-y-4\">
                {bookings.map((booking) => (
                  <div key={booking.id} className="bg-white rounded-lg shadow-md p-6\">
                    <div className="flex items-start justify-between mb-4\">
                      <div>
                        <h3 className="text-xl font-bold mb-2\">{booking.service_title}</h3>
                        <div className="text-sm text-gray-600\">
                          Customer: {booking.user_name} ({booking.user_email})
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                        booking.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                        booking.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                        booking.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {booking.status}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4\">
                      <div>
                        <div className="text-sm text-gray-600\">Start Date</div>
                        <div className="font-semibold\">{booking.start_date}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600\">Duration</div>
                        <div className="font-semibold\">{booking.duration}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600\">Guards</div>
                        <div className="font-semibold\">{booking.num_guards}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600\">Type</div>
                        <div className="font-semibold capitalize\">{booking.booking_type}</div>
                      </div>
                    </div>

                    <div className="mb-4\">
                      <div className="text-sm text-gray-600 mb-1\">Location</div>
                      <div className="font-medium\">{booking.location}</div>
                    </div>

                    {booking.special_requirements && (
                      <div className="mb-4\">
                        <div className="text-sm text-gray-600 mb-1\">Special Requirements</div>
                        <div className="text-sm bg-gray-50 p-3 rounded\">{booking.special_requirements}</div>
                      </div>
                    )}

                    {booking.status === 'pending' && (
                      <button
                        onClick={() => handleConfirmBooking(booking.id)}
                        className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 font-semibold\"
                      >
                        Confirm Booking
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Create Service Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4\">
          <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6\">
            <div className="flex items-center justify-between mb-6\">
              <h2 className="text-2xl font-bold\">Create Security Service</h2>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-gray-500 hover:text-gray-700\"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateService} className="space-y-4\">
              <div>
                <label className="block text-sm font-medium mb-2\">Title *</label>
                <input
                  type=\"text\"
                  required
                  className="w-full px-4 py-2 border rounded-lg\"
                  value={serviceForm.title}
                  onChange={(e) => setServiceForm({ ...serviceForm, title: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2\">Description *</label>
                <textarea
                  required
                  rows={4}
                  className="w-full px-4 py-2 border rounded-lg\"
                  value={serviceForm.description}
                  onChange={(e) => setServiceForm({ ...serviceForm, description: e.target.value })}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4\">
                <div>
                  <label className="block text-sm font-medium mb-2\">Service Type *</label>
                  <select
                    required
                    className="w-full px-4 py-2 border rounded-lg\"
                    value={serviceForm.service_type}
                    onChange={(e) => setServiceForm({ ...serviceForm, service_type: e.target.value })}
                  >
                    <option>Security Guards</option>
                    <option>CCTV Installation</option>
                    <option>Remote Monitoring</option>
                    <option>Patrol Units</option>
                    <option>K9 Units</option>
                    <option>Emergency Response</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2\">Price Range *</label>
                  <input
                    type=\"text\"
                    required
                    placeholder=\"e.g., 100,000 - 300,000 XAF/month\"
                    className="w-full px-4 py-2 border rounded-lg\"
                    value={serviceForm.price_range}
                    onChange={(e) => setServiceForm({ ...serviceForm, price_range: e.target.value })}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4\">
                <div>
                  <label className="block text-sm font-medium mb-2\">Location *</label>
                  <input
                    type=\"text\"
                    required
                    placeholder=\"City or region\"
                    className="w-full px-4 py-2 border rounded-lg\"
                    value={serviceForm.location}
                    onChange={(e) => setServiceForm({ ...serviceForm, location: e.target.value })}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2\">Response Time</label>
                  <input
                    type=\"text\"
                    placeholder=\"e.g., 15 minutes\"
                    className="w-full px-4 py-2 border rounded-lg\"
                    value={serviceForm.response_time}
                    onChange={(e) => setServiceForm({ ...serviceForm, response_time: e.target.value })}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2\">Features (comma separated)</label>
                <input
                  type=\"text\"
                  placeholder=\"24/7 Service, Armed Guards, Rapid Response\"
                  className="w-full px-4 py-2 border rounded-lg\"
                  value={serviceForm.features}
                  onChange={(e) => setServiceForm({ ...serviceForm, features: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2\">Certifications (comma separated)</label>
                <input
                  type=\"text\"
                  placeholder=\"Armed Security License, First Aid Certified\"
                  className="w-full px-4 py-2 border rounded-lg\"
                  value={serviceForm.certifications}
                  onChange={(e) => setServiceForm({ ...serviceForm, certifications: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2\">Availability</label>
                <select
                  className="w-full px-4 py-2 border rounded-lg\"
                  value={serviceForm.availability}
                  onChange={(e) => setServiceForm({ ...serviceForm, availability: e.target.value })}
                >
                  <option>Available</option>
                  <option>Limited</option>
                  <option>Unavailable</option>
                </select>
              </div>

              <div className="flex gap-4\">
                <button
                  type=\"submit\"
                  className="flex-1 bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700\"
                >
                  Create Service
                </button>
                <button
                  type=\"button\"
                  onClick={() => setShowCreateModal(false)}
                  className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50\"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProviderDashboard;
