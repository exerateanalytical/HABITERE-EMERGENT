import React, { useState } from 'react';
import SEOHead from '../components/SEOHead';
import { generateSEOData, generateStructuredData } from '../utils/seoData';
import { useAuth } from '../context/AuthContext';
import ServicesCarousel from '../components/ServicesCarousel';
import FeaturedProperties from '../components/FeaturedProperties';
import { 
  Search, 
  MapPin, 
  Star, 
  Users, 
  Shield, 
  Clock, 
  ArrowRight, 
  Building, 
  Wrench, 
  Home,
  CheckCircle,
  Phone
} from 'lucide-react';
import RippleButton from '../components/RippleButton';
import StickySearchBar from '../components/StickySearchBar';
import { LazyImage, LazySection } from '../components/LazyComponents';

const LandingPage = () => {
  const { login } = useAuth();
  
  // Search form state
  const [searchForm, setSearchForm] = useState({
    propertyType: '',
    location: '',
    priceRange: ''
  });
  const [searchError, setSearchError] = useState('');
  
  // Generate comprehensive SEO data for homepage
  const seoData = generateSEOData('homepage', {
    location: 'Cameroon',
    count: '1000+'
  });
  
  const structuredData = generateStructuredData('RealEstateAgent', {
    name: 'Habitere',
    description: 'Cameroon\'s leading real estate and home services platform',
    location: 'Cameroon',
    region: 'Centre',
    telephone: '+27675668211',
    areaServed: 'Cameroon'
  });

  // Duplicate declarations removed - using the first ones above

  const navigate = (path) => {
    window.location.href = path;
  };

  const handleGetStarted = () => {
    navigate('/auth/register');
  };

  const handleBrowseProperties = () => {
    navigate('/properties');
  };

  const handleExploreServices = () => {
    navigate('/services');
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    
    // Clear any previous errors
    setSearchError('');
    
    // Build query params
    const params = new URLSearchParams();
    if (searchForm.propertyType) params.append('type', searchForm.propertyType);
    if (searchForm.location) params.append('location', searchForm.location);
    if (searchForm.priceRange) params.append('price', searchForm.priceRange);
    
    // Navigate to properties page with filters
    const queryString = params.toString();
    navigate(`/properties${queryString ? '?' + queryString : ''}`);
  };

  const handleInputChange = (field, value) => {
    setSearchForm(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (searchError) setSearchError('');
  };

  const features = [
    {
      icon: Building,
      title: 'Property Listings',
      description: 'Browse thousands of properties for rent and sale across Cameroon'
    },
    {
      icon: Wrench,
      title: 'Professional Services',
      description: 'Connect with verified contractors, architects, and home service professionals'
    },
    {
      icon: Shield,
      title: 'Secure Payments',
      description: 'Pay safely with MTN Mobile Money and bank transfers'
    },
    {
      icon: Clock,
      title: '24/7 Support',
      description: 'Get help whenever you need it with our dedicated support team'
    }
  ];

  const services = [
    'Construction Companies',
    'Architects',
    'Interior Designers',
    'Plumbers',
    'Electricians',
    'Painters',
    'Carpenters',
    'Cleaning Services',
    'Building Material Suppliers',
    'Property Evaluators'
  ];

  const testimonials = [
    {
      name: 'Marie Ngozi',
      role: 'Property Owner',
      location: 'Douala',
      content: 'Habitere made it so easy to find reliable tenants for my apartment. The platform is user-friendly and the support team is excellent.',
      rating: 5,
      image: 'https://via.placeholder.com/60'
    },
    {
      name: 'Jean Baptiste',
      role: 'Construction Company',
      location: 'Yaoundé',
      content: 'As a construction company, Habitere has connected us with numerous clients. The payment system with MTN Mobile Money is very convenient.',
      rating: 5,
      image: 'https://via.placeholder.com/60'
    },
    {
      name: 'Sarah Mballa',
      role: 'Property Seeker',
      location: 'Bafoussam',
      content: 'I found my dream home through Habitere. The search filters and detailed property information made the process seamless.',
      rating: 5,
      image: 'https://via.placeholder.com/60'
    }
  ];

  return (
    <div className="min-h-screen bg-white" data-testid="landing-page">
      <SEOHead
        title={seoData.title}
        description={seoData.description}
        keywords={seoData.keywords}
        focusKeyword={seoData.focusKeyword}
        structuredData={structuredData}
        ogImage="https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=1200&q=80"
        location="Cameroon"
      />
      <SEOHead 
        seoData={seoData} 
        structuredData={structuredData} 
      />
      
      {/* Sticky Search Bar */}
      <StickySearchBar />
      
      {/* Hero Section - Green Theme with Property Image */}
      <section className="relative overflow-hidden bg-gradient-to-br from-green-600 to-green-800 pt-16 pb-12 sm:pt-20 sm:pb-16 md:pt-16 md:pb-12 lg:pt-20 lg:pb-16 safe-area-top">
        {/* Property Image Background */}
        <div className="absolute inset-0">
          <img 
            src="https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=1920&q=80" 
            alt="Modern property in Cameroon"
            className="w-full h-full object-cover opacity-20"
          />
          <div className="absolute inset-0 bg-gradient-to-br from-green-600/95 to-green-800/95"></div>
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDE0YzMuMzE0IDAgNiAyLjY4NiA2IDZzLTIuNjg2IDYtNiA2LTYtMi42ODYtNi02IDIuNjg2LTYgNi02em0wIDRjLTEuMTA1IDAtMiAuODk1LTIgMnMuODk1IDIgMiAyIDItLjg5NSAyLTItLjg5NS0yLTItMnoiLz48L2c+PC9nPjwvc3ZnPg==')] opacity-20"></div>
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
            {/* Left Content */}
            <div className="max-w-2xl">
              {/* Trust badge - Green theme */}
              <div className="inline-flex items-center px-5 py-3 bg-white/95 backdrop-blur-sm rounded-full shadow-2xl border-2 border-white/20 hover:scale-105 transition-transform duration-300 mb-6">
                <div className="w-2.5 h-2.5 bg-green-500 rounded-full mr-3 animate-pulse shadow-lg shadow-green-500/50"></div>
                <span className="text-sm font-bold text-gray-800 tracking-wide">#1 Platform in Cameroon</span>
                <Star className="w-4 h-4 text-yellow-500 fill-current ml-2" />
              </div>
              
              {/* Heading - Green accent */}
              <div className="space-y-4 mb-8">
                <h1 className="text-4xl sm:text-5xl md:text-5xl lg:text-6xl font-black text-white leading-tight tracking-tight">
                  Find Your Perfect
                  <span className="block mt-2 text-yellow-300">
                    Home & Services
                  </span>
                  <span className="block mt-2 text-2xl sm:text-3xl md:text-3xl lg:text-4xl font-bold text-green-100">
                    in Cameroon
                  </span>
                </h1>
                
                <p className="text-base sm:text-lg md:text-xl text-green-50 leading-relaxed">
                  Cameroon's most trusted real estate platform. Browse <span className="font-semibold text-white">verified properties</span> and connect with <span className="font-semibold text-white">top professionals</span>.
                </p>
              </div>
              
              {/* CTA Buttons - Green theme */}
              <div className="flex flex-col sm:flex-row gap-4 mb-8">
                <RippleButton
                  onClick={handleGetStarted}
                  variant="primary"
                  className="w-full sm:flex-1 bg-white text-green-600 hover:bg-green-50 shadow-2xl hover:shadow-3xl transform hover:scale-105 transition-all duration-300 py-4 px-6 text-base font-bold rounded-xl"
                  ariaLabel="Get started for free"
                  data-testid="get-started-btn"
                >
                  Get Started Free
                  <ArrowRight className="w-5 h-5 ml-2" />
                </RippleButton>
                
                <RippleButton
                  onClick={handleBrowseProperties}
                  variant="secondary"
                  className="w-full sm:flex-1 bg-transparent text-white border-2 border-white/30 hover:bg-white/10 backdrop-blur-sm shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300 py-4 px-6 text-base font-bold rounded-xl"
                  ariaLabel="Browse available properties"
                  data-testid="browse-properties-btn"
                >
                  Browse Properties
                  <Home className="w-5 h-5 ml-2" />
                </RippleButton>
              </div>

              {/* Stats - Green theme */}
              <div className="grid grid-cols-3 gap-3 md:gap-6">
                <div className="bg-white/10 backdrop-blur-md rounded-2xl p-4 md:p-6 text-center shadow-2xl border border-white/20 hover:bg-white/20 transform hover:scale-105 transition-all duration-300">
                  <div className="text-2xl sm:text-3xl md:text-4xl font-black text-white mb-1">1000+</div>
                  <div className="text-xs sm:text-sm md:text-base text-green-100 font-semibold">Properties</div>
                </div>
                <div className="bg-white/10 backdrop-blur-md rounded-2xl p-4 md:p-6 text-center shadow-2xl border border-white/20 hover:bg-white/20 transform hover:scale-105 transition-all duration-300">
                  <div className="text-2xl sm:text-3xl md:text-4xl font-black text-white mb-1">500+</div>
                  <div className="text-xs sm:text-sm md:text-base text-green-100 font-semibold">Professionals</div>
                </div>
                <div className="bg-white/10 backdrop-blur-md rounded-2xl p-4 md:p-6 text-center shadow-2xl border border-white/20 hover:bg-white/20 transform hover:scale-105 transition-all duration-300">
                  <div className="text-2xl sm:text-3xl md:text-4xl font-black text-white mb-1">10K+</div>
                  <div className="text-xs sm:text-sm md:text-base text-green-100 font-semibold">Users</div>
                </div>
              </div>
            </div>

            {/* Right - Featured Property Image with Overlay */}
            <div className="relative hidden lg:block">
              <div className="relative rounded-3xl overflow-hidden shadow-2xl border-4 border-white/20">
                <img 
                  src="https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&q=90"
                  alt="Featured luxury property"
                  className="w-full h-[500px] object-cover"
                />
                {/* Property Info Overlay */}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/70 to-transparent p-8">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="px-3 py-1 bg-green-500 text-white text-xs font-bold rounded-full">FOR SALE</span>
                    <span className="px-3 py-1 bg-green-600 text-white text-xs font-bold rounded-full">VERIFIED</span>
                  </div>
                  <h3 className="text-2xl font-black text-white mb-2">Modern Villa in Douala</h3>
                  <div className="flex items-center gap-4 text-white/90 text-sm mb-3">
                    <div className="flex items-center gap-1">
                      <Home className="w-4 h-4" />
                      <span>4 Beds</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Building className="w-4 h-4" />
                      <span>3 Baths</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <MapPin className="w-4 h-4" />
                      <span>Bonanjo</span>
                    </div>
                  </div>
                  <div className="text-3xl font-black text-yellow-400">
                    ₣150M XAF
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Search Section - Enhanced Desktop Design */}
      <section className="py-12 sm:py-16 md:py-20 bg-gradient-to-b from-white to-gray-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-3xl shadow-2xl border-2 border-gray-100 p-6 sm:p-8 md:p-10 lg:p-12 hover:shadow-3xl transition-shadow duration-500">
            {/* Header */}
            <div className="text-center mb-8 md:mb-10">
              <div className="inline-block px-4 py-2 bg-green-50 rounded-full mb-4">
                <span className="text-sm font-bold text-green-600">Start Your Search</span>
              </div>
              <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-gray-900 mb-3 tracking-tight">
                Find Your Dream Property
              </h2>
              <p className="text-base md:text-lg text-gray-600 font-medium">
                <span className="text-green-600 font-bold">1,000+</span> verified properties waiting for you
              </p>
            </div>
            
            {/* Search Form - Enhanced Desktop Grid Layout */}
            <form onSubmit={handleSearchSubmit} className="space-y-6 md:space-y-0 md:grid md:grid-cols-3 md:gap-4 lg:gap-6" role="search" aria-label="Property search form">
              {/* Property Type */}
              <div className="space-y-2">
                <label htmlFor="property-type" className="block text-sm font-bold text-gray-800">
                  Property Type
                  <span className="text-gray-400 text-xs ml-2 font-normal">(Optional)</span>
                </label>
                <select 
                  id="property-type"
                  name="propertyType"
                  value={searchForm.propertyType}
                  onChange={(e) => handleInputChange('propertyType', e.target.value)}
                  className="w-full px-4 py-4 bg-gray-50 border-2 border-gray-200 rounded-xl shadow-sm hover:border-blue-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:bg-white active:border-blue-400 transition-all duration-200 text-base appearance-none cursor-pointer touch-manipulation min-h-[56px] h-14 font-medium" 
                  data-testid="search-type"
                  aria-describedby="property-type-hint"
                >
                  <option value="">All Types</option>
                  <option value="house">🏠 House</option>
                  <option value="apartment">🏢 Apartment</option>
                  <option value="land">🏞️ Land</option>
                  <option value="commercial">🏪 Commercial</option>
                </select>
                <span id="property-type-hint" className="sr-only">Select the type of property you're looking for</span>
              </div>
              
              {/* Location */}
              <div className="space-y-2">
                <label htmlFor="location" className="block text-sm font-bold text-gray-800">
                  Location
                  <span className="text-gray-400 text-xs ml-2 font-normal">(Optional)</span>
                </label>
                <select 
                  id="location"
                  name="location"
                  value={searchForm.location}
                  onChange={(e) => handleInputChange('location', e.target.value)}
                  autoComplete="address-level2"
                  className="w-full px-4 py-4 bg-gray-50 border-2 border-gray-200 rounded-xl shadow-sm hover:border-blue-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:bg-white active:border-blue-400 transition-all duration-200 text-base appearance-none cursor-pointer touch-manipulation min-h-[56px] h-14 font-medium" 
                  data-testid="search-location"
                  aria-describedby="location-hint"
                >
                  <option value="">All Locations</option>
                  <option value="douala">📍 Douala</option>
                  <option value="yaounde">📍 Yaoundé</option>
                  <option value="bafoussam">📍 Bafoussam</option>
                  <option value="bamenda">📍 Bamenda</option>
                  <option value="garoua">📍 Garoua</option>
                  <option value="maroua">📍 Maroua</option>
                </select>
                <span id="location-hint" className="sr-only">Choose your preferred location</span>
              </div>
              
              {/* Price Range */}
              <div className="space-y-2">
                <label htmlFor="price-range" className="block text-sm font-bold text-gray-800">
                  Price Range
                  <span className="text-gray-400 text-xs ml-2 font-normal">(Optional)</span>
                </label>
                <select 
                  id="price-range"
                  name="priceRange"
                  value={searchForm.priceRange}
                  onChange={(e) => handleInputChange('priceRange', e.target.value)}
                  className="w-full px-4 py-4 bg-gray-50 border-2 border-gray-200 rounded-xl shadow-sm hover:border-blue-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:bg-white active:border-blue-400 transition-all duration-200 text-base appearance-none cursor-pointer touch-manipulation min-h-[56px] h-14 font-medium" 
                  data-testid="search-price"
                  aria-describedby="price-hint"
                >
                  <option value="">Any Price</option>
                  <option value="0-100000">💰 Under 100K XAF</option>
                  <option value="100000-500000">💰 100K - 500K XAF</option>
                  <option value="500000-1000000">💰 500K - 1M XAF</option>
                  <option value="1000000+">💰 Over 1M XAF</option>
                </select>
                <span id="price-hint" className="sr-only">Select your budget range</span>
              </div>
              
              {/* Error Message - Full width on desktop */}
              {searchError && (
                <div className="md:col-span-3 flex items-center gap-2 p-4 bg-red-50 border-2 border-red-200 rounded-xl" role="alert">
                  <svg className="w-5 h-5 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-sm font-medium text-red-700">{searchError}</span>
                </div>
              )}
              
              {/* Search Button - Full width on desktop */}
              <div className="md:col-span-3 mt-6">
                <RippleButton
                  type="submit"
                  variant="primary"
                  className="w-full md:w-auto md:px-16 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300 py-5 text-lg font-bold rounded-xl"
                  ariaLabel="Search properties"
                  data-testid="search-btn"
                >
                  <Search className="w-6 h-6 mr-2" />
                  Search Properties Now
                </RippleButton>
              </div>
            </form>
            
            {/* Quick Filters - Enhanced Desktop Pills */}
            <div className="mt-8 md:mt-10 flex flex-wrap gap-3 justify-center items-center">
              <span className="text-sm font-bold text-gray-500 py-2">🔥 Popular Searches:</span>
              <RippleButton variant="pill" className="text-gray-700 hover:text-blue-700 hover:bg-blue-50 border-2 border-gray-200 hover:border-blue-300 font-semibold px-5 py-2.5 transition-all duration-300">
                Houses in Douala
              </RippleButton>
              <RippleButton variant="pill" className="text-gray-700 hover:text-blue-700 hover:bg-blue-50 border-2 border-gray-200 hover:border-blue-300 font-semibold px-5 py-2.5 transition-all duration-300">
                Luxury Apartments
              </RippleButton>
              <RippleButton variant="pill" className="text-gray-700 hover:text-blue-700 hover:bg-blue-50 border-2 border-gray-200 hover:border-blue-300 font-semibold px-5 py-2.5 transition-all duration-300">
                Land for Sale
              </RippleButton>
            </div>
          </div>
        </div>
      </section>


      {/* Features Section - Enhanced Desktop Design */}
      <section className="py-16 sm:py-20 md:py-24 lg:py-28 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="text-center mb-12 md:mb-16">
            <div className="inline-block px-6 py-3 bg-blue-50 rounded-full mb-6 shadow-lg">
              <span className="text-sm md:text-base font-black text-blue-600">Why Choose Habitere?</span>
            </div>
            <h2 className="text-4xl sm:text-5xl md:text-6xl font-black text-gray-900 mb-6 tracking-tight">
              The Most Trusted Platform
              <span className="block mt-2 text-blue-600">in Cameroon</span>
            </h2>
            <p className="text-lg md:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Making real estate <span className="font-bold text-gray-900">accessible, secure</span> and <span className="font-bold text-gray-900">transparent</span> for everyone
            </p>
          </div>

          {/* Feature Cards - Enhanced Desktop Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              const colors = [
                { bg: 'bg-blue-500', light: 'bg-blue-50', text: 'text-blue-600', border: 'border-blue-200', hover: 'hover:border-blue-400' },
                { bg: 'bg-purple-500', light: 'bg-purple-50', text: 'text-purple-600', border: 'border-purple-200', hover: 'hover:border-purple-400' },
                { bg: 'bg-green-500', light: 'bg-green-50', text: 'text-green-600', border: 'border-green-200', hover: 'hover:border-green-400' },
                { bg: 'bg-orange-500', light: 'bg-orange-50', text: 'text-orange-600', border: 'border-orange-200', hover: 'hover:border-orange-400' }
              ];
              const colorScheme = colors[index % 4];
              
              return (
                <div 
                  key={index} 
                  className={`group bg-white rounded-3xl p-8 shadow-lg border-2 ${colorScheme.border} ${colorScheme.hover} hover:shadow-2xl transform hover:scale-105 hover:-translate-y-2 transition-all duration-300 cursor-pointer`}
                  data-testid={`feature-${index}`}
                >
                  {/* Icon with gradient background */}
                  <div className={`relative w-20 h-20 ${colorScheme.light} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-md`}>
                    <div className={`absolute inset-0 ${colorScheme.bg} opacity-0 group-hover:opacity-10 rounded-2xl transition-opacity duration-300`}></div>
                    <Icon className={`w-10 h-10 ${colorScheme.text} relative z-10`} />
                  </div>
                  
                  {/* Content */}
                  <h3 className="text-xl md:text-2xl font-black text-gray-900 mb-3 group-hover:text-blue-600 transition-all duration-300">
                    {feature.title}
                  </h3>
                  <p className="text-base text-gray-600 leading-relaxed font-medium">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
          
          {/* Trust Badges - Enhanced Desktop Grid */}
          <div className="mt-16 md:mt-20 grid grid-cols-2 sm:grid-cols-4 gap-6 md:gap-8">
            <div className="flex flex-col items-center p-6 bg-gradient-to-br from-green-50 to-emerald-50 rounded-3xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 border-2 border-green-100">
              <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-500 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
                <CheckCircle className="w-8 h-8 text-white" />
              </div>
              <span className="text-base md:text-lg font-black text-gray-800 text-center">100% Verified</span>
              <span className="text-sm text-gray-600 mt-1">Properties Checked</span>
            </div>
            
            <div className="flex flex-col items-center p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-3xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 border-2 border-blue-100">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <span className="text-base md:text-lg font-black text-gray-800 text-center">Secure Payments</span>
              <span className="text-sm text-gray-600 mt-1">Protected Transactions</span>
            </div>
            
            <div className="flex flex-col items-center p-6 bg-gradient-to-br from-purple-50 to-pink-50 rounded-3xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 border-2 border-purple-100">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
                <Users className="w-8 h-8 text-white" />
              </div>
              <span className="text-base md:text-lg font-black text-gray-800 text-center">Trusted by 10K+</span>
              <span className="text-sm text-gray-600 mt-1">Happy Customers</span>
            </div>
            
            <div className="flex flex-col items-center p-6 bg-gradient-to-br from-orange-50 to-red-50 rounded-3xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 border-2 border-orange-100">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-500 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
                <Clock className="w-8 h-8 text-white" />
              </div>
              <span className="text-base md:text-lg font-black text-gray-800 text-center">24/7 Support</span>
              <span className="text-sm text-gray-600 mt-1">Always Available</span>
            </div>
          </div>
        </div>
      </section>

      {/* Services Section - Enhanced Desktop Styling */}
      <section className="py-20 md:py-28 bg-gradient-to-br from-white via-blue-50/30 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            <div className="order-2 lg:order-1">
              <div className="inline-block px-4 py-2 bg-blue-100 rounded-full mb-6">
                <span className="text-sm font-bold text-blue-600">Professional Services</span>
              </div>
              
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-black text-gray-900 mb-6 leading-tight">
                Professional Home Services 
                <span className="block text-blue-600">at Your Fingertips</span>
              </h2>
              
              <p className="text-lg md:text-xl text-gray-600 mb-8 leading-relaxed">
                Connect with <span className="font-bold text-gray-900">verified professionals</span> for all your home improvement and maintenance needs. 
                From construction to interior design, find trusted experts in your area.
              </p>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-10">
                {services.map((service, index) => (
                  <div key={index} className="flex items-center space-x-3 bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow border border-gray-100">
                    <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    </div>
                    <span className="text-gray-800 font-semibold">{service}</span>
                  </div>
                ))}
              </div>
              
              <RippleButton
                variant="primary"
                onClick={handleExploreServices}
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-xl font-bold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all"
                ariaLabel="Explore services"
              >
                Explore Services
                <ArrowRight className="w-5 h-5 ml-2" />
              </RippleButton>
            </div>

            <div className="relative order-1 lg:order-2">
              <div className="relative rounded-3xl overflow-hidden shadow-2xl border-4 border-blue-100">
                <LazyImage
                  src="https://images.unsplash.com/photo-1505798577917-a65157d3320a?w=800&q=90"
                  alt="Professional contractor"
                  width={600}
                  height={384}
                  className="w-full h-auto"
                />
                {/* Floating Badge */}
                <div className="absolute top-6 right-6 bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl p-5 border border-blue-100">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center">
                      <Users className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <div className="text-lg font-black text-gray-900">500+</div>
                      <div className="text-sm text-gray-600 font-medium">Professionals</div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Decorative Elements */}
              <div className="absolute -bottom-6 -left-6 w-32 h-32 bg-blue-200 rounded-full blur-3xl opacity-50 -z-10"></div>
              <div className="absolute -top-6 -right-6 w-40 h-40 bg-purple-200 rounded-full blur-3xl opacity-50 -z-10"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Properties Carousel */}
      <LazySection threshold={0.1}>
        <section className="py-20 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <FeaturedProperties 
              title="Featured Properties" 
              limit={8}
              showAll={true}
            />
          </div>
        </section>
      </LazySection>

      {/* Professional Services Carousel */}
      <LazySection threshold={0.1}>
        <section className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <ServicesCarousel 
              title="Connect with Trusted Professionals" 
              limit={12}
              showAll={true}
            />
          </div>
        </section>
      </LazySection>

      {/* Testimonials Section - Enhanced Desktop Design */}
      <section className="py-16 md:py-24 bg-gradient-to-br from-blue-50 via-blue-100/50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 md:mb-16">
            <div className="inline-block px-4 py-2 bg-blue-600 rounded-full mb-6">
              <span className="text-sm font-bold text-white uppercase tracking-wider">Testimonials</span>
            </div>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-gray-900 mb-4">
              What Our Users Say
            </h2>
            <p className="text-lg md:text-xl text-gray-600 max-w-2xl mx-auto">
              Join <span className="font-bold text-blue-600">10,000+ satisfied users</span> across Cameroon
            </p>
          </div>

          {/* Testimonial Cards - Mobile Swipe */}
          <div className="md:hidden">
            <div className="flex overflow-x-auto gap-4 pb-4 snap-x snap-mandatory -mx-4 px-4 scrollbar-hide">
              {testimonials.map((testimonial, index) => (
                <div 
                  key={index} 
                  className="flex-none w-[85%] sm:w-80 bg-white rounded-3xl p-8 shadow-xl snap-center touch-manipulation transform hover:scale-105 transition-transform duration-200 border-2 border-blue-100"
                  data-testid={`testimonial-${index}`}
                >
                  <div className="flex items-center mb-6">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <p className="text-gray-700 mb-6 text-base leading-relaxed font-medium italic">"{testimonial.text}"</p>
                  <div className="flex items-center">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold text-lg mr-3">
                      {testimonial.name[0]}
                    </div>
                    <div>
                      <div className="font-bold text-gray-900">{testimonial.name}</div>
                      <div className="text-sm text-gray-600">{testimonial.role}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Testimonial Grid - Desktop */}
          <div className="hidden md:grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div 
                key={index} 
                className="group bg-white rounded-3xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 border-2 border-blue-100 hover:border-blue-300 transform hover:-translate-y-2"
                data-testid={`testimonial-${index}`}
              >
                <div className="flex items-center mb-6">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-gray-700 mb-8 text-base md:text-lg leading-relaxed font-medium italic">"{testimonial.text}"</p>
                <div className="flex items-center">
                  <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold text-xl mr-4 group-hover:scale-110 transition-transform">
                    {testimonial.name[0]}
                  </div>
                  <div>
                    <div className="font-bold text-gray-900 text-lg">{testimonial.name}</div>
                    <div className="text-sm text-gray-600">{testimonial.role}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;