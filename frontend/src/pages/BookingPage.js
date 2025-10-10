import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { 
  Calendar, 
  Clock, 
  MapPin, 
  User, 
  CreditCard,
  ArrowLeft,
  Building,
  Wrench,
  AlertCircle,
  CheckCircle
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const BookingPage = () => {
  const { type, id } = useParams(); // type is 'property' or 'service'
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [step, setStep] = useState(1); // 1: Details, 2: Payment, 3: Confirmation
  
  // Booking form data
  const [bookingData, setBookingData] = useState({
    scheduled_date: '',
    notes: '',
    payment_method: 'mtn_momo',
    phone_number: user?.phone || ''
  });
  
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [bookingId, setBookingId] = useState(null);
  const [paymentId, setPaymentId] = useState(null);

  useEffect(() => {
    if (id && type) {
      fetchItem();
    }
  }, [id, type]);

  const fetchItem = async () => {
    try {
      setLoading(true);
      const endpoint = type === 'property' ? 'properties' : 'services';
      const response = await axios.get(`${API}/${endpoint}/${id}`);
      setItem(response.data);
    } catch (err) {
      console.error('Error fetching item:', err);
      setError(`${type} not found`);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setBookingData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleBookingSubmit = async (e) => {
    e.preventDefault();
    
    if (!bookingData.scheduled_date) {
      setError('Please select a date and time');
      return;
    }

    try {
      setPaymentLoading(true);
      setError('');

      // Create booking
      const bookingPayload = {
        scheduled_date: bookingData.scheduled_date,
        notes: bookingData.notes
      };

      if (type === 'property') {
        bookingPayload.property_id = id;
      } else {
        bookingPayload.service_id = id;
      }

      const bookingResponse = await axios.post(`${API}/bookings`, bookingPayload);
      setBookingId(bookingResponse.data.id);

      // Calculate booking amount (this would be more complex in real app)
      const amount = type === 'property' ? 25000 : 50000; // Booking fee in XAF

      // Create payment
      const paymentPayload = {
        booking_id: bookingResponse.data.id,
        amount: amount,
        method: bookingData.payment_method,
        phone_number: bookingData.phone_number
      };

      const paymentResponse = await axios.post(`${API}/payments/mtn-momo`, paymentPayload);
      setPaymentId(paymentResponse.data.payment_id);
      
      setStep(3); // Move to confirmation
      
    } catch (err) {
      console.error('Booking error:', err);
      setError(err.response?.data?.detail || 'Failed to create booking');
    } finally {
      setPaymentLoading(false);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('fr-CM', {
      style: 'currency',
      currency: 'XAF',
      minimumFractionDigits: 0
    }).format(price);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-300 rounded mb-6"></div>
            <div className="card">
              <div className="card-body">
                <div className="space-y-4">
                  <div className="h-6 bg-gray-300 rounded w-3/4"></div>
                  <div className="h-4 bg-gray-300 rounded w-1/2"></div>
                  <div className="h-32 bg-gray-300 rounded"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error && !item) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Not Found</h2>
          <p className="text-gray-600 mb-8">{error}</p>
          <button
            onClick={() => navigate(-1)}
            className="btn-primary"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="booking-page">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors mb-4"
            data-testid="back-btn"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back
          </button>
          
          <h1 className="text-3xl font-bold text-gray-900">
            Book {type === 'property' ? 'Property Viewing' : 'Service'}
          </h1>
          
          {/* Progress indicator */}
          <div className="flex items-center space-x-4 mt-6">
            <div className={`flex items-center ${step >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
              }`}>
                1
              </div>
              <span className="ml-2 text-sm font-medium">Details</span>
            </div>
            
            <div className="flex-1 h-px bg-gray-200"></div>
            
            <div className={`flex items-center ${step >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
              }`}>
                2
              </div>
              <span className="ml-2 text-sm font-medium">Payment</span>
            </div>
            
            <div className="flex-1 h-px bg-gray-200"></div>
            
            <div className={`flex items-center ${step >= 3 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                step >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
              }`}>
                3
              </div>
              <span className="ml-2 text-sm font-medium">Confirmation</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Booking Form */}
          <div className="lg:col-span-2">
            {step === 1 && (
              <form onSubmit={(e) => { e.preventDefault(); setStep(2); }} className="card">
                <div className="card-body">
                  <h2 className="text-xl font-semibold text-gray-900 mb-6">
                    Booking Details
                  </h2>

                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        <Calendar className="w-4 h-4 inline mr-2" />
                        Select Date & Time
                      </label>
                      <input
                        type="datetime-local"
                        value={bookingData.scheduled_date}
                        onChange={(e) => handleInputChange('scheduled_date', e.target.value)}
                        min={new Date().toISOString().slice(0, 16)}
                        className="form-input"
                        required
                        data-testid="scheduled-date"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Additional Notes (Optional)
                      </label>
                      <textarea
                        value={bookingData.notes}
                        onChange={(e) => handleInputChange('notes', e.target.value)}
                        placeholder={`Any specific requirements for the ${type} ${type === 'property' ? 'viewing' : 'service'}...`}
                        rows={4}
                        className="form-textarea"
                        data-testid="booking-notes"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Your Phone Number
                      </label>
                      <input
                        type="tel"
                        value={bookingData.phone_number}
                        onChange={(e) => handleInputChange('phone_number', e.target.value)}
                        placeholder="+237 6XX XX XX XX"
                        className="form-input"
                        required
                        data-testid="phone-number"
                      />
                      <p className="text-sm text-gray-500 mt-1">
                        We'll use this number to send booking confirmations and payment prompts
                      </p>
                    </div>
                  </div>

                  <div className="flex justify-between mt-8">
                    <button
                      type="button"
                      onClick={() => navigate(-1)}
                      className="btn-secondary"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="btn-primary"
                      data-testid="continue-to-payment-btn"
                    >
                      Continue to Payment
                    </button>
                  </div>
                </div>
              </form>
            )}

            {step === 2 && (
              <form onSubmit={handleBookingSubmit} className="card">
                <div className="card-body">
                  <h2 className="text-xl font-semibold text-gray-900 mb-6">
                    Payment Information
                  </h2>

                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-3">
                        Payment Method
                      </label>
                      <div className="space-y-3">
                        <label className="flex items-center p-4 border-2 border-gray-200 rounded-lg cursor-pointer hover:bg-blue-50 hover:border-blue-300">
                          <input
                            type="radio"
                            name="payment_method"
                            value="mtn_momo"
                            checked={bookingData.payment_method === 'mtn_momo'}
                            onChange={(e) => handleInputChange('payment_method', e.target.value)}
                            className="sr-only"
                          />
                          <div className={`w-4 h-4 rounded-full border-2 mr-3 ${
                            bookingData.payment_method === 'mtn_momo' 
                              ? 'border-blue-600 bg-blue-600' 
                              : 'border-gray-300'
                          }`}>
                            {bookingData.payment_method === 'mtn_momo' && (
                              <div className="w-full h-full rounded-full bg-white scale-50"></div>
                            )}
                          </div>
                          <div className="flex items-center">
                            <CreditCard className="w-6 h-6 mr-3 text-orange-500" />
                            <div>
                              <div className="font-medium">MTN Mobile Money</div>
                              <div className="text-sm text-gray-500">Pay with your MTN MoMo account</div>
                            </div>
                          </div>
                        </label>

                        <label className="flex items-center p-4 border-2 border-gray-200 rounded-lg cursor-pointer opacity-50">
                          <input
                            type="radio"
                            name="payment_method"
                            value="bank_transfer"
                            disabled
                            className="sr-only"
                          />
                          <div className="w-4 h-4 rounded-full border-2 border-gray-300 mr-3"></div>
                          <div className="flex items-center">
                            <CreditCard className="w-6 h-6 mr-3 text-gray-400" />
                            <div>
                              <div className="font-medium text-gray-400">Bank Transfer</div>
                              <div className="text-sm text-gray-400">Coming soon</div>
                            </div>
                          </div>
                        </label>
                      </div>
                    </div>

                    <div className="border-t border-gray-200 pt-6">
                      <div className="flex justify-between text-lg font-semibold">
                        <span>Booking Fee:</span>
                        <span className="text-blue-600">
                          {formatPrice(type === 'property' ? 25000 : 50000)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-500 mt-1">
                        {type === 'property' 
                          ? 'Refundable booking fee for property viewing'
                          : 'Service booking fee (applied to final invoice)'
                        }
                      </p>
                    </div>
                  </div>

                  {error && (
                    <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
                      <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" />
                      <div className="text-red-700">{error}</div>
                    </div>
                  )}

                  <div className="flex justify-between mt-8">
                    <button
                      type="button"
                      onClick={() => setStep(1)}
                      className="btn-secondary"
                      disabled={paymentLoading}
                    >
                      Back
                    </button>
                    <button
                      type="submit"
                      className="btn-primary"
                      disabled={paymentLoading}
                      data-testid="confirm-booking-btn"
                    >
                      {paymentLoading ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Processing...
                        </>
                      ) : (
                        'Confirm Booking'
                      )}
                    </button>
                  </div>
                </div>
              </form>
            )}

            {step === 3 && (
              <div className="card">
                <div className="card-body text-center">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <CheckCircle className="w-8 h-8 text-green-600" />
                  </div>
                  
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">
                    Booking Confirmed!
                  </h2>
                  
                  <p className="text-gray-600 mb-6">
                    Your {type} booking has been confirmed. You should receive an MTN Mobile Money 
                    payment prompt on your phone shortly.
                  </p>

                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                    <h3 className="font-semibold text-blue-900 mb-2">Next Steps:</h3>
                    <ul className="text-left text-blue-800 space-y-1 text-sm">
                      <li>1. Approve the payment on your phone</li>
                      <li>2. You'll receive a confirmation SMS</li>
                      <li>3. The {type === 'property' ? 'owner' : 'service provider'} will contact you</li>
                    </ul>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <button
                      onClick={() => navigate('/dashboard')}
                      className="btn-primary"
                      data-testid="go-to-dashboard-btn"
                    >
                      Go to Dashboard
                    </button>
                    <button
                      onClick={() => navigate('/messages')}
                      className="btn-secondary"
                    >
                      View Messages
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Item Summary */}
          <div className="lg:col-span-1">
            <div className="card sticky top-8">
              <div className="card-body">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  {type === 'property' ? 'Property' : 'Service'} Summary
                </h3>

                {item && (
                  <div className="space-y-4">
                    <div className="flex items-start space-x-3">
                      <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                        type === 'property' ? 'bg-blue-100' : 'bg-green-100'
                      }`}>
                        {type === 'property' ? (
                          <Building className={`w-6 h-6 ${type === 'property' ? 'text-blue-600' : 'text-green-600'}`} />
                        ) : (
                          <Wrench className="w-6 h-6 text-green-600" />
                        )}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900">{item.title}</h4>
                        <div className="flex items-center text-gray-500 text-sm mt-1">
                          <MapPin className="w-4 h-4 mr-1" />
                          {item.location}
                        </div>
                      </div>
                    </div>

                    {item.price && (
                      <div className="border-t border-gray-200 pt-4">
                        <div className="text-sm text-gray-500">
                          {type === 'property' ? 'Property Price' : 'Service Price'}
                        </div>
                        <div className="text-lg font-semibold text-blue-600">
                          {type === 'property' ? formatPrice(item.price) : (item.price_range || 'Contact for quote')}
                        </div>
                      </div>
                    )}

                    <div className="border-t border-gray-200 pt-4">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">Booking Fee</span>
                        <span className="font-semibold">
                          {formatPrice(type === 'property' ? 25000 : 50000)}
                        </span>
                      </div>
                    </div>

                    {step > 1 && bookingData.scheduled_date && (
                      <div className="border-t border-gray-200 pt-4">
                        <div className="text-sm text-gray-500 mb-1">Scheduled Date</div>
                        <div className="flex items-center text-gray-900">
                          <Clock className="w-4 h-4 mr-2" />
                          {new Date(bookingData.scheduled_date).toLocaleDateString('en-US', {
                            weekday: 'long',
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                <div className="border-t border-gray-200 mt-6 pt-6">
                  <div className="flex items-start space-x-3">
                    <User className="w-5 h-5 text-blue-600 mt-0.5" />
                    <div className="text-sm text-gray-600">
                      <p className="font-medium text-gray-900 mb-1">Booking for</p>
                      <p>{user?.name}</p>
                      <p>{bookingData.phone_number || user?.phone}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookingPage;