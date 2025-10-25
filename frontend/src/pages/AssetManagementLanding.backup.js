import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Package, Wrench, DollarSign, TrendingUp, CheckCircle, Clock, Shield, BarChart3, Bell, FileText, Calendar, Users } from 'lucide-react';

const AssetManagementLanding = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const handleGetStarted = () => {
    if (user) {
      navigate('/assets/dashboard');
    } else {
      navigate('/auth/register');
    }
  };

  const handleLogin = () => {
    navigate('/auth/login');
  };

  const features = [
    {
      icon: Package,
      title: 'Asset Inventory Management',
      description: 'Track all your property assets from equipment to infrastructure with detailed records and documentation.',
      color: 'bg-green-100 text-green-600'
    },
    {
      icon: Wrench,
      title: 'Maintenance Scheduling',
      description: 'Schedule and track maintenance tasks with priority levels, assignments, and automated reminders.',
      color: 'bg-blue-100 text-blue-600'
    },
    {
      icon: DollarSign,
      title: 'Expense Tracking',
      description: 'Monitor all asset-related expenses with approval workflows and budget management tools.',
      color: 'bg-purple-100 text-purple-600'
    },
    {
      icon: Bell,
      title: 'Automated Alerts',
      description: 'Receive timely notifications for upcoming maintenance, overdue tasks, and pending approvals.',
      color: 'bg-orange-100 text-orange-600'
    },
    {
      icon: BarChart3,
      title: 'Analytics Dashboard',
      description: 'Get insights into asset performance, maintenance costs, and operational efficiency.',
      color: 'bg-indigo-100 text-indigo-600'
    },
    {
      icon: FileText,
      title: 'Document Management',
      description: 'Store and access all asset documentation, warranties, and compliance certificates in one place.',
      color: 'bg-teal-100 text-teal-600'
    }
  ];

  const benefits = [
    'Reduce maintenance costs by up to 30%',
    'Prevent equipment failures with proactive scheduling',
    'Improve asset lifecycle management',
    'Streamline approval workflows',
    'Real-time visibility across all properties',
    'Automated compliance tracking'
  ];

  const assetCategories = [
    { name: 'Real Estate', icon: Package, count: '100+' },
    { name: 'Building Equipment', icon: Wrench, count: '500+' },
    { name: 'Infrastructure', icon: TrendingUp, count: '200+' },
    { name: 'Furniture & Fixtures', icon: Package, count: '300+' },
    { name: 'Vehicles', icon: Package, count: '50+' },
    { name: 'Tools & Machinery', icon: Wrench, count: '150+' }
  ];

  const howItWorks = [
    {
      step: '1',
      title: 'Register Your Assets',
      description: 'Create a comprehensive inventory of all your property assets with detailed specifications and documents.',
      icon: Package
    },
    {
      step: '2',
      title: 'Schedule Maintenance',
      description: 'Set up maintenance schedules, assign tasks to technicians, and track progress in real-time.',
      icon: Calendar
    },
    {
      step: '3',
      title: 'Monitor & Optimize',
      description: 'Track expenses, analyze performance metrics, and optimize your asset management strategy.',
      icon: BarChart3
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-br from-green-600 via-green-700 to-green-800 text-white">
        <div className="absolute inset-0 bg-black opacity-10"></div>
        <div className="relative container mx-auto px-4 py-20 md:py-32">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full mb-6">
              <Package className="w-5 h-5 mr-2" />
              <span className="text-sm font-semibold">Professional Asset Management</span>
            </div>
            
            <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
              Manage Your Property Assets
              <span className="block text-green-200">Like a Pro</span>
            </h1>
            
            <p className="text-xl md:text-2xl text-green-100 mb-8 leading-relaxed">
              Complete asset lifecycle management, maintenance scheduling, and expense tracking for property owners and estate managers
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={handleGetStarted}
                className="bg-white text-green-700 px-8 py-4 rounded-lg font-bold text-lg hover:bg-green-50 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
              >
                Get Started Free
              </button>
              {!user && (
                <button
                  onClick={handleLogin}
                  className="bg-green-500 text-white px-8 py-4 rounded-lg font-bold text-lg hover:bg-green-400 transition-all border-2 border-white/30"
                >
                  Sign In
                </button>
              )}
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-16">
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                <div className="text-3xl font-bold mb-1">1000+</div>
                <div className="text-green-200 text-sm">Assets Managed</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                <div className="text-3xl font-bold mb-1">500+</div>
                <div className="text-green-200 text-sm">Properties</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                <div className="text-3xl font-bold mb-1">30%</div>
                <div className="text-green-200 text-sm">Cost Reduction</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                <div className="text-3xl font-bold mb-1">24/7</div>
                <div className="text-green-200 text-sm">Support</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Complete Asset Management Solution
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Everything you need to manage, maintain, and optimize your property assets in one powerful platform
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-gray-50 rounded-xl p-8 hover:shadow-lg transition-shadow">
                <div className={`w-16 h-16 ${feature.color} rounded-lg flex items-center justify-center mb-6`}>
                  <feature.icon className="w-8 h-8" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-600">
              Get started with asset management in three simple steps
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {howItWorks.map((step, index) => (
              <div key={index} className="relative">
                <div className="bg-white rounded-xl p-8 shadow-md hover:shadow-xl transition-shadow h-full">
                  <div className="w-16 h-16 bg-green-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mb-6 mx-auto">
                    {step.step}
                  </div>
                  <step.icon className="w-12 h-12 text-green-600 mx-auto mb-4" />
                  <h3 className="text-xl font-bold text-gray-900 mb-3 text-center">{step.title}</h3>
                  <p className="text-gray-600 text-center">{step.description}</p>
                </div>
                {index < howItWorks.length - 1 && (
                  <div className="hidden md:block absolute top-1/2 right-0 transform translate-x-1/2 -translate-y-1/2">
                    <div className="w-8 h-0.5 bg-green-300"></div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Asset Categories */}
      <div className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Manage All Asset Types
            </h2>
            <p className="text-xl text-gray-600">
              From real estate to equipment, track every asset across your properties
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
            {assetCategories.map((category, index) => (
              <div key={index} className="bg-gray-50 rounded-lg p-6 text-center hover:bg-green-50 transition-colors cursor-pointer">
                <category.icon className="w-12 h-12 text-green-600 mx-auto mb-3" />
                <div className="text-2xl font-bold text-gray-900 mb-1">{category.count}</div>
                <div className="text-sm text-gray-600">{category.name}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Benefits Section */}
      <div className="py-20 bg-gradient-to-br from-green-600 to-green-700 text-white">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Why Choose Habitere Asset Management?
              </h2>
              <p className="text-xl text-green-100">
                Join hundreds of property owners and managers who trust us with their assets
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {benefits.map((benefit, index) => (
                <div key={index} className="flex items-start bg-white/10 backdrop-blur-sm rounded-lg p-6">
                  <CheckCircle className="w-6 h-6 text-green-300 mr-4 flex-shrink-0 mt-1" />
                  <span className="text-lg">{benefit}</span>
                </div>
              ))}
            </div>

            <div className="text-center mt-12">
              <button
                onClick={handleGetStarted}
                className="bg-white text-green-700 px-10 py-4 rounded-lg font-bold text-lg hover:bg-green-50 transition-all shadow-xl"
              >
                Start Managing Your Assets Today
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-20 bg-gray-900 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Transform Your Asset Management?
          </h2>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Get started today and experience the power of professional asset management
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={handleGetStarted}
              className="bg-green-600 text-white px-8 py-4 rounded-lg font-bold text-lg hover:bg-green-700 transition-all"
            >
              Get Started Free
            </button>
            <button
              onClick={() => navigate('/contact')}
              className="bg-gray-800 text-white px-8 py-4 rounded-lg font-bold text-lg hover:bg-gray-700 transition-all border border-gray-700"
            >
              Contact Sales
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssetManagementLanding;
