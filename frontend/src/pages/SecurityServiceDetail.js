import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Shield, MapPin, Star, Phone, Mail, CheckCircle, Clock, Award, ArrowLeft, Calendar } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const SecurityServiceDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [service, setService] = useState(null);
  const [provider, setProvider] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [bookingData, setBookingData] = useState({
    booking_type: 'scheduled',
    start_date: '',
    end_date: '',
    duration: '1 month',
    location: '',
    num_guards: 1,
    special_requirements: ''
  });

  useEffect(() => {
    fetchServiceDetails();
  }, [id]);

  const fetchServiceDetails = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/security/services/${id}`);
      setService(response.data.service);
      setProvider(response.data.provider);
    } catch (error) {
      console.error('Error fetching service details:', error);
      alert('Service not found');
      navigate('/security/services');
    } finally {
      setLoading(false);
    }
  };

  const handleBookNow = () => {
    if (!user) {
      alert('Please login to book this service');
      navigate('/auth/login');
      return;
    }
    setShowBookingModal(true);
  };

  const handleBookingSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(
        `${BACKEND_URL}/api/security/bookings`,
        {
          service_id: service.id,
          ...bookingData
        },
        { withCredentials: true }
      );
      
      alert('Booking request submitted successfully! The provider will contact you soon.');
      setShowBookingModal(false);
      navigate('/dashboard');
    } catch (error) {
      console.error('Error creating booking:', error);
      alert(error.response?.data?.detail || 'Failed to create booking');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  if (!service) return null;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Back Button */}
        <button
          onClick={() => navigate('/security/services')}
          className="flex items-center text-gray-600 hover:text-green-600 mb-6"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Services
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Hero Image */}
            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl h-64 md:h-96 flex items-center justify-center mb-6">
              <Shield className="w-32 h-32 text-white" />
            </div>

            {/* Service Info */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h1 className="text-3xl font-bold mb-2">{service.title}</h1>
                  <div className="flex items-center text-gray-600 mb-2">
                    <MapPin className="w-5 h-5 mr-2" />
                    <span>{service.location}</span>
                  </div>
                  <span className="inline-block bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                    {service.service_type}
                  </span>
                </div>
                {service.verified && (
                  <div className="flex items-center bg-green-100 text-green-800 px-3 py-2 rounded-lg">
                    <CheckCircle className="w-5 h-5 mr-2" />
                    <span className="font-semibold">Verified</span>
                  </div>
                )}
              </div>

              <div className="border-t pt-4 mt-4">
                <h2 className="text-xl font-bold mb-3">Description</h2>
                <p className="text-gray-700 leading-relaxed">{service.description}</p>
              </div>

              {/* Features */}
              {service.features && service.features.length > 0 && (
                <div className="border-t pt-4 mt-4">
                  <h2 className="text-xl font-bold mb-3">Features</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {service.features.map((feature, index) => (
                      <div key={index} className="flex items-center">
                        <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Certifications */}
              {service.certifications && service.certifications.length > 0 && (
                <div className="border-t pt-4 mt-4">
                  <h2 className="text-xl font-bold mb-3">Certifications</h2>
                  <div className="flex flex-wrap gap-2">
                    {service.certifications.map((cert, index) => (
                      <span key={index} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm flex items-center">
                        <Award className="w-4 h-4 mr-1" />
                        {cert}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Response Time */}
              {service.response_time && (
                <div className="border-t pt-4 mt-4">
                  <div className="flex items-center">
                    <Clock className="w-5 h-5 text-green-600 mr-2" />
                    <span className="font-semibold">Response Time:</span>
                    <span className="ml-2">{service.response_time}</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            {/* Booking Card */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-6 sticky top-24">
              <div className="mb-6">
                <div className="text-sm text-gray-600 mb-1">Price Range</div>
                <div className="text-2xl font-bold text-green-600">{service.price_range}</div>
              </div>

              <div className="space-y-3 mb-6">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Availability</span>
                  <span className={`font-semibold ${service.availability === 'Available' ? 'text-green-600' : 'text-orange-600'}`}>
                    {service.availability}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Bookings</span>
                  <span className="font-semibold">{service.booking_count || 0}</span>
                </div>
                {service.average_rating > 0 && (
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Rating</span>
                    <div className="flex items-center">
                      <Star className="w-5 h-5 text-yellow-500 fill-current" />
                      <span className="ml-1 font-semibold">{service.average_rating.toFixed(1)}</span>
                      <span className="text-gray-500 ml-1">({service.review_count})</span>
                    </div>
                  </div>
                )}
              </div>

              <button
                onClick={handleBookNow}
                disabled={service.availability !== 'Available'}
                className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed mb-3"
              >
                {service.availability === 'Available' ? 'Book Now' : 'Currently Unavailable'}
              </button>

              <button
                onClick={() => navigate(`/messages?userId=${service.provider_id}`)}
                className="w-full bg-white border-2 border-green-600 text-green-600 py-3 rounded-lg font-semibold hover:bg-green-50"
              >
                Contact Provider
              </button>
            </div>

            {/* Provider Info */}
            {provider && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-bold mb-4">Service Provider</h3>
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mr-3">
                    <Shield className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <div className="font-semibold">{provider.name}</div>
                    <div className="text-sm text-gray-600">{provider.role?.replace('_', ' ')}</div>
                  </div>
                </div>
                {provider.email && (
                  <div className="flex items-center text-sm text-gray-600 mb-2">
                    <Mail className="w-4 h-4 mr-2" />
                    <span>{provider.email}</span>
                  </div>
                )}
                {provider.phone && (
                  <div className="flex items-center text-sm text-gray-600">
                    <Phone className="w-4 h-4 mr-2" />
                    <span>{provider.phone}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Booking Modal */}
      {showBookingModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">Book Security Service</h2>
              <button
                onClick={() => setShowBookingModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleBookingSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Booking Type</label>
                <select
                  className="w-full px-4 py-2 border rounded-lg"
                  value={bookingData.booking_type}
                  onChange={(e) => setBookingData({ ...bookingData, booking_type: e.target.value })}
                >
                  <option value="instant">Instant (Available Now)</option>
                  <option value="scheduled">Scheduled</option>
                  <option value="emergency">Emergency</option>
                </select>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Start Date *</label>
                  <input
                    type="date"
                    required
                    className="w-full px-4 py-2 border rounded-lg"
                    value={bookingData.start_date}
                    onChange={(e) => setBookingData({ ...bookingData, start_date: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">End Date</label>
                  <input
                    type="date"
                    className="w-full px-4 py-2 border rounded-lg"
                    value={bookingData.end_date}
                    onChange={(e) => setBookingData({ ...bookingData, end_date: e.target.value })}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Duration</label>
                <input
                  type="text"
                  placeholder="e.g., 1 month, 24 hours, ongoing"
                  className="w-full px-4 py-2 border rounded-lg"
                  value={bookingData.duration}
                  onChange={(e) => setBookingData({ ...bookingData, duration: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Location *</label>
                <input
                  type="text"
                  required
                  placeholder="Service location address"
                  className="w-full px-4 py-2 border rounded-lg"
                  value={bookingData.location}
                  onChange={(e) => setBookingData({ ...bookingData, location: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Number of Guards</label>
                <input
                  type="number"
                  min="1"
                  className="w-full px-4 py-2 border rounded-lg"
                  value={bookingData.num_guards}
                  onChange={(e) => setBookingData({ ...bookingData, num_guards: parseInt(e.target.value) })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Special Requirements</label>
                <textarea
                  rows={4}
                  placeholder="Any special requirements or instructions..."
                  className="w-full px-4 py-2 border rounded-lg"
                  value={bookingData.special_requirements}
                  onChange={(e) => setBookingData({ ...bookingData, special_requirements: e.target.value })}
                />
              </div>

              <div className="flex gap-4">
                <button
                  type="submit"
                  className="flex-1 bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700"
                >
                  Submit Booking Request
                </button>
                <button
                  type="button"
                  onClick={() => setShowBookingModal(false)}
                  className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
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

export default SecurityServiceDetail;
