import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { 
  Calendar, 
  Clock, 
  MapPin, 
  User,
  ArrowLeft,
  Building,
  Wrench,
  AlertCircle,
  CheckCircle,
  Send
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const BookingPage = () => {
  const { type, id } = useParams(); // type is 'property' or 'service'
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  
  // Available time slots
  const [availableSlots, setAvailableSlots] = useState([]);
  const [loadingSlots, setLoadingSlots] = useState(false);
  
  // Booking form data
  const [bookingData, setBookingData] = useState({
    scheduled_date: '',
    scheduled_time: '',
    duration_hours: 1,
    notes: ''
  });
  
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/auth/login');
      return;
    }
    
    if (id && type) {
      fetchItem();
    }
  }, [id, type, user]);

  useEffect(() => {
    if (bookingData.scheduled_date && type === 'property' && id) {
      fetchAvailableSlots();
    }
  }, [bookingData.scheduled_date]);

  const fetchItem = async () => {
    try {
      setLoading(true);
      const endpoint = type === 'property' 
        ? `/api/properties/${id}` 
        : `/api/services/${id}`;
      
      const response = await axios.get(`${BACKEND_URL}${endpoint}`);
      setItem(response.data);
    } catch (err) {
      console.error('Error fetching item:', err);
      setError('Failed to load booking details');
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailableSlots = async () => {
    try {
      setLoadingSlots(true);
      const response = await axios.get(
        `${BACKEND_URL}/api/bookings/property/${id}/slots?date=${bookingData.scheduled_date}`
      );
      setAvailableSlots(response.data.slots || []);
    } catch (err) {
      console.error('Error fetching slots:', err);
    } finally {
      setLoadingSlots(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setBookingData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!bookingData.scheduled_date) {
      alert('Please select a date');
      return;
    }
    
    if (type === 'property' && !bookingData.scheduled_time) {
      alert('Please select a time slot');
      return;
    }

    try {
      setSubmitting(true);
      
      const booking = {
        booking_type: type === 'property' ? 'property_viewing' : 'service_booking',
        ...(type === 'property' ? { property_id: id } : { service_id: id }),
        scheduled_date: new Date(bookingData.scheduled_date).toISOString(),
        scheduled_time: bookingData.scheduled_time,
        duration_hours: parseInt(bookingData.duration_hours),
        notes: bookingData.notes
      };
      
      const response = await axios.post(
        `${BACKEND_URL}/api/bookings`,
        booking,
        { withCredentials: true }
      );
      
      setSuccess(true);
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
      
    } catch (err) {
      console.error('Error creating booking:', err);
      alert(err.response?.data?.detail || 'Failed to create booking');
    } finally {
      setSubmitting(false);
    }
  };

  // Get minimum date (today)
  const getMinDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !item) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600 mb-4">{error || 'Item not found'}</p>
          <button
            onClick={() => navigate(-1)}
            className="btn-primary"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Booking Successful!</h2>
          <p className="text-gray-600 mb-4">
            Your booking request has been submitted. You'll receive a confirmation once approved.
          </p>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn-primary"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <button
          onClick={() => navigate(-1)}
          className="flex items-center text-blue-600 hover:text-blue-700 mb-6"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back
        </button>

        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {/* Item Info */}
          <div className="p-6 bg-gradient-to-r from-blue-50 to-purple-50 border-b">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                {type === 'property' ? (
                  <Building className="w-12 h-12 text-blue-600" />
                ) : (
                  <Wrench className="w-12 h-12 text-purple-600" />
                )}
              </div>
              <div className="ml-4 flex-1">
                <h1 className="text-2xl font-bold text-gray-900 mb-2">{item.title}</h1>
                {type === 'property' && (
                  <div className="flex items-center text-gray-600 mb-2">
                    <MapPin className="w-4 h-4 mr-1" />
                    {item.location}
                  </div>
                )}
                {type === 'property' && (
                  <p className="text-2xl font-bold text-blue-600">
                    {item.price?.toLocaleString()} {item.currency}
                    {item.listing_type === 'rent' && '/month'}
                  </p>
                )}
                {type === 'service' && (
                  <p className="text-lg text-gray-700">{item.category}</p>
                )}
              </div>
            </div>
          </div>

          {/* Booking Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              {type === 'property' ? 'Schedule Property Viewing' : 'Book Service'}
            </h2>

            {/* Date Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="w-4 h-4 inline mr-1" />
                Select Date
              </label>
              <input
                type="date"
                name="scheduled_date"
                value={bookingData.scheduled_date}
                onChange={handleInputChange}
                min={getMinDate()}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Time Slot Selection (for property viewings) */}
            {type === 'property' && bookingData.scheduled_date && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Clock className="w-4 h-4 inline mr-1" />
                  Select Time Slot
                </label>
                {loadingSlots ? (
                  <p className="text-gray-500">Loading available slots...</p>
                ) : (
                  <div className="grid grid-cols-3 md:grid-cols-4 gap-2">
                    {availableSlots.map((slot) => (
                      <button
                        key={slot.time}
                        type="button"
                        onClick={() => handleInputChange({ target: { name: 'scheduled_time', value: slot.time } })}
                        disabled={!slot.available}
                        className={`px-4 py-2 rounded-lg border text-sm font-medium transition-colors ${
                          bookingData.scheduled_time === slot.time
                            ? 'bg-blue-600 text-white border-blue-600'
                            : slot.available
                            ? 'border-gray-300 hover:border-blue-500 hover:bg-blue-50'
                            : 'border-gray-200 bg-gray-100 text-gray-400 cursor-not-allowed'
                        }`}
                      >
                        {slot.time}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Duration */}
            {type === 'service' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Duration (hours)
                </label>
                <select
                  name="duration_hours"
                  value={bookingData.duration_hours}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="1">1 hour</option>
                  <option value="2">2 hours</option>
                  <option value="3">3 hours</option>
                  <option value="4">4 hours</option>
                  <option value="8">Full day (8 hours)</option>
                </select>
              </div>
            )}

            {/* Notes */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Additional Notes (Optional)
              </label>
              <textarea
                name="notes"
                value={bookingData.notes}
                onChange={handleInputChange}
                rows="4"
                placeholder="Any specific requirements or questions..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Submit Button */}
            <div className="flex items-center justify-between pt-4 border-t">
              <button
                type="button"
                onClick={() => navigate(-1)}
                className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="btn-primary flex items-center disabled:opacity-50"
              >
                <Send className="w-4 h-4 mr-2" />
                {submitting ? 'Submitting...' : 'Submit Booking Request'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default BookingPage;
