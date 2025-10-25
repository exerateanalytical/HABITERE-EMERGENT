import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  CreditCard, Calendar, CheckCircle, AlertCircle, 
  Clock, RefreshCw, TrendingUp, FileText 
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const SubscriptionDashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [subscription, setSubscription] = useState(null);
  const [plan, setPlan] = useState(null);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user) {
      fetchSubscriptionData();
    }
  }, [user]);

  const fetchSubscriptionData = async () => {
    try {
      // Fetch subscription
      const subResponse = await axios.get(
        `${BACKEND_URL}/api/subscriptions/my-subscription`,
        { withCredentials: true }
      );

      if (subResponse.data.has_subscription) {
        setSubscription(subResponse.data.subscription);
        setPlan(subResponse.data.plan);
      }

      // Fetch payment history
      const paymentResponse = await axios.get(
        `${BACKEND_URL}/api/subscriptions/payment-history`,
        { withCredentials: true }
      );
      setPayments(paymentResponse.data.payments);

    } catch (error) {
      console.error('Error fetching subscription data:', error);
      setError('Failed to load subscription details');
    } finally {
      setLoading(false);
    }
  };

  const handleRenew = () => {
    navigate('/checkout', { state: { planId: plan?.id, isRenewal: true } });
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getDaysRemaining = (endDate) => {
    const end = new Date(endDate);
    const now = new Date();
    const diffTime = end - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-600"></div>
      </div>
    );
  }

  if (!subscription) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
            <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <CreditCard className="w-10 h-10 text-gray-400" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              No Active Subscription
            </h2>
            <p className="text-gray-600 mb-8">
              Subscribe to a plan to unlock all features and start growing your business.
            </p>
            <button
              onClick={() => navigate('/pricing')}
              className="bg-green-600 hover:bg-green-700 text-white px-8 py-4 rounded-xl font-bold text-lg transition-all"
            >
              View Plans
            </button>
          </div>
        </div>
      </div>
    );
  }

  const daysRemaining = subscription.end_date ? getDaysRemaining(subscription.end_date) : null;
  const isExpired = subscription.status === 'expired';
  const isExpiringSoon = daysRemaining !== null && daysRemaining <= 30;

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-black text-gray-900">Subscription</h1>
          <p className="text-gray-600 mt-2">Manage your subscription and billing</p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-xl p-4 flex items-start">
            <AlertCircle className="w-5 h-5 text-red-600 mr-3 mt-0.5" />
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Expiry Warning */}
        {isExpired && (
          <div className="mb-6 bg-red-50 border-2 border-red-200 rounded-xl p-6">
            <div className="flex items-start">
              <AlertCircle className="w-6 h-6 text-red-600 mr-3 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-lg font-bold text-red-900 mb-2">Subscription Expired</h3>
                <p className="text-red-700 mb-4">
                  Your subscription has expired. Renew now to continue accessing premium features.
                </p>
                <button
                  onClick={handleRenew}
                  className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-bold"
                >
                  Renew Subscription
                </button>
              </div>
            </div>
          </div>
        )}

        {isExpiringSoon && !isExpired && (
          <div className="mb-6 bg-yellow-50 border-2 border-yellow-200 rounded-xl p-6">
            <div className="flex items-start">
              <Clock className="w-6 h-6 text-yellow-600 mr-3 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-lg font-bold text-yellow-900 mb-2">Subscription Expiring Soon</h3>
                <p className="text-yellow-700">
                  Your subscription expires in {daysRemaining} days. Renew now to avoid interruption.
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Current Plan */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">{plan?.name}</h2>
                  <div className="flex items-center gap-2">
                    {subscription.status === 'active' ? (
                      <>
                        <CheckCircle className="w-5 h-5 text-green-600" />
                        <span className="text-green-600 font-semibold">Active</span>
                      </>
                    ) : (
                      <>
                        <AlertCircle className="w-5 h-5 text-red-600" />
                        <span className="text-red-600 font-semibold">Expired</span>
                      </>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-black text-green-600">
                    {plan?.price.toLocaleString()} FCFA
                  </p>
                  <p className="text-sm text-gray-500">per year</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-gray-50 rounded-xl p-4">
                  <div className="flex items-center text-gray-600 mb-2">
                    <Calendar className="w-4 h-4 mr-2" />
                    <span className="text-sm">Start Date</span>
                  </div>
                  <p className="font-bold text-gray-900">{formatDate(subscription.start_date)}</p>
                </div>
                <div className="bg-gray-50 rounded-xl p-4">
                  <div className="flex items-center text-gray-600 mb-2">
                    <Calendar className="w-4 h-4 mr-2" />
                    <span className="text-sm">Expires</span>
                  </div>
                  <p className="font-bold text-gray-900">
                    {subscription.end_date ? formatDate(subscription.end_date) : 'N/A'}
                  </p>
                </div>
              </div>

              <div className="border-t border-gray-200 pt-6">
                <h3 className="font-bold text-gray-900 mb-4">Features Included</h3>
                <ul className="space-y-3">
                  {plan?.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start">
                      <CheckCircle className="w-5 h-5 text-green-600 mr-3 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="mt-6">
                <button
                  onClick={handleRenew}
                  className="w-full bg-green-600 hover:bg-green-700 text-white py-3 px-6 rounded-xl font-bold flex items-center justify-center"
                >
                  <RefreshCw className="w-5 h-5 mr-2" />
                  Renew Subscription
                </button>
              </div>
            </div>

            {/* Payment History */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Payment History</h2>
                <FileText className="w-6 h-6 text-gray-400" />
              </div>

              {payments.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No payment history</p>
              ) : (
                <div className="space-y-4">
                  {payments.map((payment) => (
                    <div
                      key={payment.id}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-xl"
                    >
                      <div>
                        <p className="font-bold text-gray-900">
                          {payment.amount.toLocaleString()} {payment.currency}
                        </p>
                        <p className="text-sm text-gray-600">
                          {payment.payment_date ? formatDate(payment.payment_date) : 'Pending'}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {payment.transaction_id || 'N/A'}
                        </p>
                      </div>
                      <div>
                        <span
                          className={`px-3 py-1 rounded-full text-sm font-bold ${
                            payment.payment_status === 'completed'
                              ? 'bg-green-100 text-green-700'
                              : payment.payment_status === 'pending'
                              ? 'bg-yellow-100 text-yellow-700'
                              : 'bg-red-100 text-red-700'
                          }`}
                        >
                          {payment.payment_status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-green-600 to-green-700 text-white rounded-2xl shadow-lg p-8">
              <TrendingUp className="w-12 h-12 mb-4" />
              <h3 className="text-2xl font-bold mb-2">Need More Features?</h3>
              <p className="text-green-100 mb-6">
                Upgrade to a higher plan for more capabilities
              </p>
              <button
                onClick={() => navigate('/pricing')}
                className="w-full bg-white text-green-600 py-3 px-6 rounded-xl font-bold hover:bg-green-50 transition-all"
              >
                View All Plans
              </button>
            </div>

            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h3 className="font-bold text-gray-900 mb-4">Need Help?</h3>
              <p className="text-gray-600 mb-6">
                Contact our support team for assistance with your subscription.
              </p>
              <button
                onClick={() => navigate('/contact')}
                className="w-full bg-gray-100 hover:bg-gray-200 text-gray-900 py-3 px-6 rounded-xl font-bold transition-all"
              >
                Contact Support
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SubscriptionDashboard;
