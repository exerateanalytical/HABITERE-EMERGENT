import React from 'react';
import { Link } from 'react-router-dom';
import { HelpCircle, Home, Users, Wrench, Shield, CreditCard, MessageSquare, BookOpen, Video, FileText } from 'lucide-react';
import SEOHead from '../components/SEOHead';

const HelpCenter = () => {
  const categories = [
    {
      icon: Home,
      title: 'Property Listings',
      description: 'Learn how to list, edit, and manage properties',
      color: 'blue',
      articles: ['How to list a property', 'Upload property photos', 'Edit property details', 'Delete a listing']
    },
    {
      icon: Users,
      title: 'Account & Profile',
      description: 'Manage your account settings and profile',
      color: 'purple',
      articles: ['Create an account', 'Reset password', 'Update profile', 'Verify account']
    },
    {
      icon: Wrench,
      title: 'Service Providers',
      description: 'Guide for plumbers, electricians, and professionals',
      color: 'green',
      articles: ['Create service listing', 'Receive client inquiries', 'Portfolio showcase', 'Pricing guidelines']
    },
    {
      icon: Shield,
      title: 'Safety & Security',
      description: 'Stay safe while using Habitere',
      color: 'red',
      articles: ['Verify property ownership', 'Avoid scams', 'Report suspicious users', 'Safe payment practices']
    },
    {
      icon: CreditCard,
      title: 'Payments',
      description: 'Understanding transactions and fees',
      color: 'yellow',
      articles: ['How payments work', 'Platform fees', 'Refund policy', 'Payment security']
    },
    {
      icon: MessageSquare,
      title: 'Communication',
      description: 'Contact property owners and service providers',
      color: 'indigo',
      articles: ['Send messages', 'Call property owner', 'WhatsApp contact', 'Book viewings']
    }
  ];

  const quickLinks = [
    { icon: BookOpen, title: 'Browse FAQ', link: '/faq', description: 'Find quick answers' },
    { icon: MessageSquare, title: 'Contact Support', link: '/contact', description: 'Get personalized help' },
    { icon: FileText, title: 'Terms & Privacy', link: '/terms', description: 'Legal information' },
    { icon: Video, title: 'Video Tutorials', link: '#', description: 'Watch how-to guides' }
  ];

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-100 text-blue-600',
      purple: 'bg-purple-100 text-purple-600',
      green: 'bg-green-100 text-green-600',
      red: 'bg-red-100 text-red-600',
      yellow: 'bg-yellow-100 text-yellow-600',
      indigo: 'bg-indigo-100 text-indigo-600'
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <SEOHead 
        title="Help Center - Guides & Support | Habitere Cameroon Real Estate Help"
        description="Comprehensive help center for Habitere users in Cameroon. Find step-by-step guides for listing properties, finding homes, hiring professionals, payments, and account management."
        keywords="habitere help center, real estate help cameroon, property listing guide, user support habitere, how to use habitere, real estate platform help"
        focusKeyword="habitere help center"
        canonicalUrl="https://habitere.com/help-center"
      />

      {/* Hero Section */}
      <div className="bg-gradient-to-br from-blue-600 to-purple-600 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 md:py-20">
          <div className="text-center">
            <HelpCircle className="w-12 h-12 sm:w-16 sm:h-16 mx-auto mb-4 sm:mb-6" />
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-3 sm:mb-4">
              How Can We Help You?
            </h1>
            <p className="text-base sm:text-lg md:text-xl text-blue-100 mb-6 sm:mb-8">
              Browse our comprehensive guides and resources
            </p>

            {/* Search Bar */}
            <div className="max-w-2xl mx-auto">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search for help..."
                  className="w-full px-4 sm:px-6 py-3 sm:py-4 rounded-full text-gray-900 focus:ring-2 focus:ring-white focus:outline-none text-sm sm:text-base"
                />
                <button className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-blue-600 text-white px-4 sm:px-6 py-2 sm:py-2.5 rounded-full hover:bg-blue-700 transition-colors text-sm sm:text-base">
                  Search
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Help Categories */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
        <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-6 sm:mb-8 text-center">Browse by Category</h2>
        
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-12 sm:mb-16">
          {categories.map((category, index) => {
            const Icon = category.icon;
            return (
              <div key={index} className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-shadow p-6 sm:p-8">
                <div className={`w-12 h-12 sm:w-14 sm:h-14 ${getColorClasses(category.color)} rounded-xl flex items-center justify-center mb-4`}>
                  <Icon className="w-6 h-6 sm:w-7 sm:h-7" />
                </div>
                <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-2">{category.title}</h3>
                <p className="text-sm sm:text-base text-gray-600 mb-4">{category.description}</p>
                <ul className="space-y-2">
                  {category.articles.map((article, idx) => (
                    <li key={idx}>
                      <a href="#" className="text-sm text-blue-600 hover:text-blue-700 hover:underline">
                        → {article}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>

        {/* Quick Links */}
        <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-6 sm:mb-8 text-center">Quick Links</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {quickLinks.map((link, index) => {
            const Icon = link.icon;
            return (
              <Link
                key={index}
                to={link.link}
                className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow p-4 sm:p-6 text-center"
              >
                <Icon className="w-8 h-8 sm:w-10 sm:h-10 text-blue-600 mx-auto mb-3" />
                <h3 className="font-bold text-gray-900 mb-1 text-sm sm:text-base">{link.title}</h3>
                <p className="text-xs sm:text-sm text-gray-600">{link.description}</p>
              </Link>
            );
          })}
        </div>

        {/* Popular Articles */}
        <div className="mt-12 sm:mt-16 bg-white rounded-2xl shadow-xl p-6 sm:p-8">
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-6">Popular Articles</h2>
          <div className="grid md:grid-cols-2 gap-4 sm:gap-6">
            <div className="space-y-4">
              <a href="/faq" className="block p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <h3 className="font-semibold text-gray-900 mb-1 text-sm sm:text-base">How do I create an account?</h3>
                <p className="text-xs sm:text-sm text-gray-600">Step-by-step registration guide</p>
              </a>
              <a href="/faq" className="block p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <h3 className="font-semibold text-gray-900 mb-1 text-sm sm:text-base">How to list my property?</h3>
                <p className="text-xs sm:text-sm text-gray-600">Complete property listing tutorial</p>
              </a>
              <a href="/faq" className="block p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <h3 className="font-semibold text-gray-900 mb-1 text-sm sm:text-base">How to contact property owners?</h3>
                <p className="text-xs sm:text-sm text-gray-600">Learn communication options</p>
              </a>
            </div>
            <div className="space-y-4">
              <a href="/faq" className="block p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <h3 className="font-semibold text-gray-900 mb-1 text-sm sm:text-base">Is my information safe?</h3>
                <p className="text-xs sm:text-sm text-gray-600">Privacy and security explained</p>
              </a>
              <a href="/faq" className="block p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <h3 className="font-semibold text-gray-900 mb-1 text-sm sm:text-base">How do payments work?</h3>
                <p className="text-xs sm:text-sm text-gray-600">Understanding transactions</p>
              </a>
              <a href="/faq" className="block p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <h3 className="font-semibold text-gray-900 mb-1 text-sm sm:text-base">How to verify my account?</h3>
                <p className="text-xs sm:text-sm text-gray-600">Account verification process</p>
              </a>
            </div>
          </div>
        </div>

        {/* Contact Support CTA */}
        <div className="mt-12 sm:mt-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl p-6 sm:p-8 text-center text-white">
          <MessageSquare className="w-12 h-12 sm:w-16 sm:h-16 mx-auto mb-4" />
          <h3 className="text-xl sm:text-2xl font-bold mb-3 sm:mb-4">Still Need Help?</h3>
          <p className="text-blue-100 mb-6 sm:mb-8 text-sm sm:text-base">
            Our support team is available 24/7 to assist you
          </p>
          <Link
            to="/contact"
            className="inline-block bg-white text-blue-600 px-6 sm:px-8 py-3 sm:py-4 rounded-full font-semibold hover:bg-gray-100 transition-colors text-sm sm:text-base"
          >
            Contact Support Team
          </Link>
        </div>
      </div>
    </div>
  );
};

export default HelpCenter;
