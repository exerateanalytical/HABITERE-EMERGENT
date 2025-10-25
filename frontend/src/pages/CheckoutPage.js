import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { CheckCircle, CreditCard, Smartphone, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const CheckoutPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('mtn_momo');
  const [phoneNumber, setPhoneNumber] = useState('');

  const planId = location.state?.planId;

  useEffect(() => {
    if (!user) {
      navigate('/auth/login', { state: { from: '/checkout' } });
      return;
    }

    if (!planId) {
      navigate('/pricing');
      return;
    }

    fetchPlan();
  }, [planId, user]);

  const fetchPlan = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/subscriptions/plans`);
      const selectedPlan = response.data.plans.find(p => p.id === planId);
      if (selectedPlan) {
        setPlan(selectedPlan);
      } else {
        setError('Plan not found');
      }
    } catch (error) {
      console.error('Error fetching plan:', error);
      setError('Failed to load plan details');
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (e) => {
    e.preventDefault();
    setProcessing(true);
    setError('');

    try {
      const response = await axios.post(
        `${BACKEND_URL}/api/subscriptions/subscribe`,
        {
          plan_id: planId,
          payment_method: paymentMethod,
          phone_number: phoneNumber || undefined
        },
        { withCredentials: true }
      );

      setSuccess(true);
      setTimeout(() => {
        navigate('/dashboard');
      }, 3000);
    } catch (error) {
      console.error('Subscription error:', error);
      setError(error.response?.data?.detail || 'Failed to process subscription. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-600"></div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-12 h-12 text-green-600" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Subscription Activated!
          </h2>
          <p className="text-gray-600 mb-6">
            Your subscription has been successfully activated. Redirecting to dashboard...
          </p>
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-black text-gray-900 mb-2">Complete Your Subscription</h1>
          <p className="text-gray-600">Secure payment powered by Habitere</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-lg p-6 sticky top-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Order Summary</h3>
              
              {plan && (
                <>
                  <div className="mb-4">
                    <p className="text-gray-600 mb-2">Plan</p>
                    <p className="text-lg font-bold text-gray-900">{plan.name}</p>
                  </div>

                  <div className="border-t border-gray-200 pt-4 mb-4">
                    <div className="flex justify-between mb-2">
                      <span className="text-gray-600">Subtotal</span>
                      <span className="font-semibold">{plan.price.toLocaleString()} FCFA</span>
                    </div>
                    <div className="flex justify-between mb-2">
                      <span className="text-gray-600">Tax</span>
                      <span className="font-semibold">0 FCFA</span>
                    </div>
                  </div>

                  <div className="border-t-2 border-gray-300 pt-4">
                    <div className="flex justify-between">
                      <span className="text-lg font-bold text-gray-900">Total</span>
                      <span className="text-2xl font-black text-green-600">
                        {plan.price.toLocaleString()} FCFA
                      </span>
                    </div>
                    {plan.billing_cycle === 'yearly' && (
                      <p className="text-sm text-gray-500 mt-2">Billed annually</p>
                    )}
                  </div>

                  <div className="mt-6 bg-green-50 border border-green-200 rounded-xl p-4">
                    <ul className="space-y-2">
                      {plan.features.slice(0, 3).map((feature, idx) => (
                        <li key={idx} className="flex items-center text-sm text-gray-700">
                          <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Payment Form */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Payment Method</h3>

              {error && (
                <div className="mb-6 bg-red-50 border border-red-200 rounded-xl p-4 flex items-start">
                  <AlertCircle className="w-5 h-5 text-red-600 mr-3 mt-0.5 flex-shrink-0" />
                  <p className="text-red-700">{error}</p>
                </div>
              )}

              <form onSubmit={handleSubscribe}>
                {/* Payment Method Selection */}
                <div className="mb-6">
                  <label className="block text-sm font-bold text-gray-700 mb-4">
                    Select Payment Method
                  </label>
                  
                  <div className="space-y-3">
                    <button
                      type="button"
                      onClick={() => setPaymentMethod('mtn_momo')}
                      className={`w-full p-4 rounded-xl border-2 transition-all ${
                        paymentMethod === 'mtn_momo'
                          ? 'border-green-600 bg-green-50'
                          : 'border-gray-200 hover:border-green-300'
                      }`}
                    >
                      <div className="flex items-center">
                        <Smartphone className="w-6 h-6 text-yellow-500 mr-3" />
                        <div className="text-left">
                          <p className="font-bold text-gray-900">MTN Mobile Money</p>
                          <p className="text-sm text-gray-600">Pay with MTN MoMo</p>
                        </div>
                      </div>
                    </button>

                    <button
                      type="button"
                      onClick={() => setPaymentMethod('orange_money')}
                      className={`w-full p-4 rounded-xl border-2 transition-all ${
                        paymentMethod === 'orange_money'
                          ? 'border-green-600 bg-green-50'
                          : 'border-gray-200 hover:border-green-300'
                      }`}
                    >
                      <div className="flex items-center">
                        <Smartphone className="w-6 h-6 text-orange-500 mr-3" />
                        <div className="text-left">
                          <p className="font-bold text-gray-900">Orange Money</p>
                          <p className="text-sm text-gray-600">Pay with Orange Money</p>
                        </div>
                      </div>
                    </button>

                    <button
                      type="button"
                      onClick={() => setPaymentMethod('bank_transfer')}
                      className={`w-full p-4 rounded-xl border-2 transition-all ${
                        paymentMethod === 'bank_transfer'
                          ? 'border-green-600 bg-green-50'
                          : 'border-gray-200 hover:border-green-300'
                      }`}
                    >
                      <div className="flex items-center">
                        <CreditCard className="w-6 h-6 text-blue-500 mr-3" />
                        <div className="text-left">
                          <p className="font-bold text-gray-900">Bank Transfer</p>
                          <p className="text-sm text-gray-600">Pay via bank transfer</p>
                        </div>
                      </div>
                    </button>
                  </div>
                </div>

                {/* Phone Number (for mobile money) */}
                {(paymentMethod === 'mtn_momo' || paymentMethod === 'orange_money') && (
                  <div className="mb-6">
                    <label htmlFor="phone" className="block text-sm font-bold text-gray-700 mb-2">
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      id="phone"
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value)}
                      placeholder="+237 6XX XXX XXX"
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    />
                  </div>
                )}

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={processing}
                  className="w-full bg-green-600 hover:bg-green-700 text-white py-4 px-6 rounded-xl font-bold text-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {processing ? (
                    <span className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                      Processing...
                    </span>
                  ) : (
                    'Complete Subscription'
                  )}
                </button>

                <p className="text-sm text-gray-500 text-center mt-4">
                  By subscribing, you agree to our Terms of Service and Privacy Policy
                </p>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CheckoutPage;
