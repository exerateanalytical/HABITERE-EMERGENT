import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Check, Building, Wrench, Home, Hammer, ShoppingCart, 
  Sofa, Hotel, ArrowRight, Shield, Star, Zap
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const PricingPage = () => {
  const navigate = useNavigate();
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/subscriptions/plans`);
      setPlans(response.data.plans);
    } catch (error) {
      console.error('Error fetching plans:', error);
      setError('Failed to load subscription plans');
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = (planId) => {
    navigate('/checkout', { state: { planId } });
  };

  const getPlanIcon = (userRole) => {
    const icons = {
      'real_estate_agent': Building,
      'service_professional': Wrench,
      'real_estate_company': Home,
      'construction_company': Hammer,
      'building_material_supplier': ShoppingCart,
      'furnishing_shop': Sofa,
      'hotel': Hotel
    };
    return icons[userRole] || Building;
  };

  const getPlanColor = (index) => {
    const colors = [
      { bg: 'bg-blue-600', light: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-600' },
      { bg: 'bg-green-600', light: 'bg-green-50', border: 'border-green-200', text: 'text-green-600' },
      { bg: 'bg-purple-600', light: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-600' },
      { bg: 'bg-orange-600', light: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-600' },
      { bg: 'bg-pink-600', light: 'bg-pink-50', border: 'border-pink-200', text: 'text-pink-600' },
      { bg: 'bg-indigo-600', light: 'bg-indigo-50', border: 'border-indigo-200', text: 'text-indigo-600' },
      { bg: 'bg-red-600', light: 'bg-red-50', border: 'border-red-200', text: 'text-red-600' }
    ];
    return colors[index % colors.length];
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-green-600 to-green-700 text-white py-16 md:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center px-4 py-2 bg-white/20 rounded-full mb-6">
            <Star className="w-5 h-5 mr-2" />
            <span className="text-sm font-bold">Simple, Transparent Pricing</span>
          </div>
          
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-black mb-6">
            Choose Your Plan
          </h1>
          <p className="text-xl md:text-2xl text-green-50 max-w-3xl mx-auto">
            Start growing your business with Habitere. No hidden fees, cancel anytime.
          </p>

          {/* Trust Indicators */}
          <div className="flex flex-wrap justify-center gap-6 mt-10">
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              <span>Secure Payment</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5" />
              <span>Instant Activation</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-5 h-5" />
              <span>Cancel Anytime</span>
            </div>
          </div>
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {error && (
          <div className="mb-8 bg-red-50 border border-red-200 rounded-xl p-4">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
          {plans.map((plan, index) => {
            const Icon = getPlanIcon(plan.user_role);
            const colors = getPlanColor(index);
            const isCommission = plan.billing_cycle === 'per_booking';

            return (
              <div
                key={plan.id}
                className={`bg-white rounded-3xl shadow-xl hover:shadow-2xl transition-all duration-300 overflow-hidden border-2 ${colors.border} hover:scale-105`}
              >
                {/* Card Header */}
                <div className={`${colors.light} p-8 text-center border-b-2 ${colors.border}`}>
                  <div className={`inline-flex items-center justify-center w-16 h-16 ${colors.bg} rounded-2xl mb-4`}>
                    <Icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-2xl font-black text-gray-900 mb-2">{plan.name}</h3>
                  <div className="mt-4">
                    {isCommission ? (
                      <div>
                        <span className={`text-5xl font-black ${colors.text}`}>
                          {plan.commission_rate}%
                        </span>
                        <span className="text-gray-600 text-lg ml-2">per booking</span>
                      </div>
                    ) : (
                      <div>
                        <span className={`text-5xl font-black ${colors.text}`}>
                          {plan.price.toLocaleString()}
                        </span>
                        <span className="text-gray-600 text-lg ml-2">FCFA/year</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Card Body */}
                <div className="p-8">
                  <ul className="space-y-4 mb-8">
                    {plan.features.map((feature, idx) => (
                      <li key={idx} className="flex items-start">
                        <Check className={`w-5 h-5 ${colors.text} mr-3 mt-0.5 flex-shrink-0`} />
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <button
                    onClick={() => handleSubscribe(plan.id)}
                    className={`w-full ${colors.bg} hover:opacity-90 text-white py-4 px-6 rounded-xl font-bold text-lg transition-all duration-300 flex items-center justify-center group`}
                  >
                    Get Started
                    <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* FAQ Section */}
        <div className="mt-20 text-center">
          <h2 className="text-3xl font-black text-gray-900 mb-4">
            Have Questions?
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Contact our support team for help choosing the right plan
          </p>
          <button
            onClick={() => navigate('/contact')}
            className="bg-green-600 hover:bg-green-700 text-white px-8 py-4 rounded-xl font-bold text-lg transition-all"
          >
            Contact Support
          </button>
        </div>
      </div>
    </div>
  );
};

export default PricingPage;
