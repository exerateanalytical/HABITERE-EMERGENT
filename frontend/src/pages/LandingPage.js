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
      
      {/* Hero Section - Native Mobile-First Design */}
      <section className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-white to-purple-50 pt-20 pb-12 sm:pt-24 sm:pb-16 md:pt-28 md:pb-20 safe-area-top">
        {/* Optimized background - Single subtle gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-100/20 via-transparent to-purple-100/20"></div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto text-center space-y-8">
            {/* Trust badge - Optimized for mobile */}
            <div className="inline-flex items-center px-4 py-2.5 bg-white rounded-full shadow-md border border-gray-200">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
              <span className="text-sm font-semibold text-gray-800">#1 Platform in Cameroon</span>
            </div>
            
            {/* Heading - Mobile optimized hierarchy */}
            <div className="space-y-4">
              <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-extrabold text-gray-900 leading-tight">
                Find Your Perfect
                <span className="block mt-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Home & Services
                </span>
                <span className="block mt-2 text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-gray-700">
                  in Cameroon
                </span>
              </h1>
              
              <p className="text-lg sm:text-xl md:text-2xl text-gray-600 leading-relaxed max-w-3xl mx-auto px-4">
                Cameroon's most trusted real estate platform. Browse verified properties and connect with professionals.
              </p>
            </div>
            
            {/* CTA Buttons - Native mobile feel with ripple effects */}
            <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto px-4">
              <RippleButton
                onClick={handleGetStarted}
                variant="primary"
                className="w-full sm:flex-1"
                ariaLabel="Get started for free"
                data-testid="get-started-btn"
              >
                <span className="font-bold">Get Started Free</span>
                <ArrowRight className="w-5 h-5" />
              </RippleButton>
              
              <RippleButton
                onClick={handleBrowseProperties}
                variant="secondary"
                className="w-full sm:flex-1"
                ariaLabel="Browse available properties"
                data-testid="browse-properties-btn"
              >
                <span className="font-bold">Browse Properties</span>
                <Home className="w-5 h-5" />
              </RippleButton>
            </div>

            {/* Stats - Optimized for mobile screens */}
            <div className="grid grid-cols-3 gap-3 sm:gap-4 max-w-xl mx-auto pt-8 px-4">
              <div className="bg-white rounded-2xl p-4 sm:p-5 text-center shadow-md border border-gray-100">
                <div className="text-2xl sm:text-3xl font-extrabold text-blue-600">1000+</div>
                <div className="text-xs sm:text-sm text-gray-600 font-medium mt-1">Properties</div>
              </div>
              <div className="bg-white rounded-2xl p-4 sm:p-5 text-center shadow-md border border-gray-100">
                <div className="text-2xl sm:text-3xl font-extrabold text-purple-600">500+</div>
                <div className="text-xs sm:text-sm text-gray-600 font-medium mt-1">Professionals</div>
              </div>
              <div className="bg-white rounded-2xl p-4 sm:p-5 text-center shadow-md border border-gray-100">
                <div className="text-2xl sm:text-3xl font-extrabold text-green-600">10K+</div>
                <div className="text-xs sm:text-sm text-gray-600 font-medium mt-1">Users</div>
              </div>
            </div>
            
            {/* Trust indicators - Mobile optimized */}
            <div className="flex flex-wrap items-center justify-center gap-4 pt-4 px-4">
              <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-full shadow-sm">
                <Shield className="w-4 h-4 text-green-600" />
                <span className="text-sm font-medium text-gray-700">Verified</span>
              </div>
              <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-full shadow-sm">
                <Star className="w-4 h-4 text-yellow-500 fill-current" />
                <span className="text-sm font-medium text-gray-700">4.9 Rating</span>
              </div>
              <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-full shadow-sm">
                <Users className="w-4 h-4 text-blue-600" />
                <span className="text-sm font-medium text-gray-700">10K+ Users</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Search Section - Mobile Native Design */}
      <section className="py-8 sm:py-12 bg-white">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-5 sm:p-6 md:p-8">
            {/* Header */}
            <div className="text-center mb-6">
              <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
                Find Your Dream Property
              </h2>
              <p className="text-base text-gray-600">1,000+ verified properties</p>
            </div>
            
            {/* Search Form - Mobile Optimized Stack */}
            <form onSubmit={handleSearchSubmit} className="space-y-4" role="search" aria-label="Property search form">
              {/* Property Type */}
              <div className="space-y-2">
                <label htmlFor="property-type" className="block text-sm font-semibold text-gray-700">
                  Property Type
                  <span className="text-gray-400 text-xs ml-1">(Optional)</span>
                </label>
                <select 
                  id="property-type"
                  name="propertyType"
                  value={searchForm.propertyType}
                  onChange={(e) => handleInputChange('propertyType', e.target.value)}
                  className="w-full px-4 py-4 bg-white border-2 border-gray-200 rounded-2xl shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 active:border-blue-400 transition-all duration-100 text-base appearance-none cursor-pointer touch-manipulation min-h-[56px] h-14" 
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
                <label htmlFor="location" className="block text-sm font-semibold text-gray-700">
                  Location
                  <span className="text-gray-400 text-xs ml-1">(Optional)</span>
                </label>
                <select 
                  id="location"
                  name="location"
                  value={searchForm.location}
                  onChange={(e) => handleInputChange('location', e.target.value)}
                  autoComplete="address-level2"
                  className="w-full px-4 py-4 bg-white border-2 border-gray-200 rounded-2xl shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 active:border-blue-400 transition-all duration-100 text-base appearance-none cursor-pointer touch-manipulation min-h-[56px] h-14" 
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
                <label htmlFor="price-range" className="block text-sm font-semibold text-gray-700">
                  Price Range
                  <span className="text-gray-400 text-xs ml-1">(Optional)</span>
                </label>
                <select 
                  id="price-range"
                  name="priceRange"
                  value={searchForm.priceRange}
                  onChange={(e) => handleInputChange('priceRange', e.target.value)}
                  className="w-full px-4 py-4 bg-white border-2 border-gray-200 rounded-2xl shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 active:border-blue-400 transition-all duration-100 text-base appearance-none cursor-pointer touch-manipulation min-h-[56px] h-14" 
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
              
              {/* Error Message */}
              {searchError && (
                <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-xl" role="alert">
                  <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-sm text-red-700">{searchError}</span>
                </div>
              )}
              
              {/* Search Button */}
              <RippleButton
                type="submit"
                variant="primary"
                className="w-full"
                ariaLabel="Search properties"
                data-testid="search-btn"
              >
                <span className="font-bold">Search Properties</span>
                <Search className="w-5 h-5" />
              </RippleButton>
            </form>
            
            {/* Quick Filters - Native Mobile Pills */}
            <div className="mt-6 flex flex-wrap gap-2 justify-center">
              <span className="text-sm font-medium text-gray-500 py-2">Popular:</span>
              <RippleButton variant="pill" className="text-gray-700 active:text-blue-700">
                Houses in Douala
              </RippleButton>
              <RippleButton variant="pill" className="text-gray-700 active:text-blue-700">
                Apartments
              </RippleButton>
              <RippleButton variant="pill" className="text-gray-700 active:text-blue-700">
                Land for Sale
              </RippleButton>
            </div>
          </div>
        </div>
      </section>


      {/* Features Section - Mobile Native Cards */}
      <section className="py-12 sm:py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          {/* Header */}
          <div className="text-center mb-10 sm:mb-12">
            <div className="inline-block px-4 py-2 bg-blue-50 rounded-full mb-4">
              <span className="text-sm font-bold text-blue-600">Why Habitere?</span>
            </div>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              The Most Trusted Platform
              <span className="block text-blue-600">in Cameroon</span>
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Making real estate accessible and secure for everyone
            </p>
          </div>

          {/* Feature Cards - Mobile Optimized */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              const colors = ['blue', 'purple', 'green', 'orange'];
              const color = colors[index % 4];
              
              return (
                <div 
                  key={index} 
                  className={`bg-white rounded-3xl p-6 sm:p-8 shadow-md border-2 border-gray-100 active:border-${color}-200 transform active:scale-95 transition-all duration-100 touch-manipulation`}
                  data-testid={`feature-${index}`}
                >
                  {/* Icon */}
                  <div className={`w-16 h-16 bg-${color}-100 rounded-2xl flex items-center justify-center mb-5`}>
                    <Icon className={`w-8 h-8 text-${color}-600`} />
                  </div>
                  
                  {/* Content */}
                  <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-base text-gray-600 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
          
          {/* Trust Badges - Mobile Grid */}
          <div className="mt-12 grid grid-cols-2 sm:grid-cols-4 gap-4 sm:gap-6">
            <div className="flex flex-col items-center p-4 bg-white rounded-2xl shadow-sm">
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mb-2">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <span className="text-sm font-semibold text-gray-700 text-center">Verified</span>
            </div>
            
            <div className="flex flex-col items-center p-4 bg-white rounded-2xl shadow-sm">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-2">
                <Shield className="w-6 h-6 text-blue-600" />
              </div>
              <span className="text-sm font-semibold text-gray-700 text-center">Secure</span>
            </div>
            
            <div className="flex flex-col items-center p-4 bg-white rounded-2xl shadow-sm">
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-2">
                <Users className="w-6 h-6 text-purple-600" />
              </div>
              <span className="text-sm font-semibold text-gray-700 text-center">Trusted</span>
            </div>
            
            <div className="flex flex-col items-center p-4 bg-white rounded-2xl shadow-sm">
              <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center mb-2">
                <Clock className="w-6 h-6 text-orange-600" />
              </div>
              <span className="text-sm font-semibold text-gray-700 text-center">24/7</span>
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
                Professional Home Services at Your Fingertips
              </h2>
              <p className="text-lg text-gray-600 mb-8">
                Connect with verified professionals for all your home improvement and maintenance needs. 
                From construction to interior design, find trusted experts in your area.
              </p>
              
              <div className="grid grid-cols-2 gap-3 mb-8">
                {services.map((service, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <span className="text-gray-700">{service}</span>
                  </div>
                ))}
              </div>
              
              <RippleButton
                variant="primary"
                onClick={handleExploreServices}
                className="mt-4"
                ariaLabel="Explore services"
              >
                <span className="font-bold">Explore Services</span>
                <ArrowRight className="w-5 h-5" />
              </RippleButton>
            </div>

            <div className="relative">
              <LazyImage
                src="https://images.unsplash.com/photo-1505798577917-a65157d3320a"
                alt="Professional contractor"
                width={600}
                height={384}
                className="rounded-2xl shadow-lg"
              />
              <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg p-3">
                <div className="flex items-center space-x-2">
                  <Users className="w-5 h-5 text-blue-600" />
                  <div>
                    <div className="text-sm font-semibold text-gray-900">500+ Professionals</div>
                    <div className="text-xs text-gray-600">Verified & Trusted</div>
                  </div>
                </div>
              </div>
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

      {/* Testimonials Section - Mobile Optimized */}
      <section className="py-12 md:py-20 bg-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8 md:mb-16">
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 mb-3 md:mb-4">
              What Our Users Say
            </h2>
            <p className="text-base md:text-lg text-gray-600">
              Join thousands of satisfied users across Cameroon
            </p>
          </div>


          {/* Testimonial Cards - Native Swipe on Mobile */}
          <div className="md:hidden">
            <div className="flex overflow-x-auto gap-4 pb-4 snap-x snap-mandatory -mx-4 px-4 scrollbar-hide">
              {testimonials.map((testimonial, index) => (
                <div 
                  key={index} 
                  className="flex-none w-[85%] sm:w-80 bg-white rounded-3xl p-6 shadow-lg snap-center touch-manipulation transform hover:scale-105 transition-transform duration-200"
                  data-testid={`testimonial-${index}`}
                >
                  {/* Rating */}
                  <div className="flex items-center gap-1 mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  
                  {/* Content */}
                  <p className="text-base text-gray-700 mb-6 leading-relaxed line-clamp-4">
                    "{testimonial.content}"
                  </p>
                  
                  {/* Author */}
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-lg">
                      {testimonial.name.charAt(0)}
                    </div>
                    <div>
                      <h4 className="font-bold text-gray-900">{testimonial.name}</h4>
                      <p className="text-sm text-gray-600">{testimonial.role}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            {/* Swipe Indicator - Enhanced with active state */}
            <div className="flex justify-center gap-2 mt-4">
              {testimonials.map((_, index) => (
                <div 
                  key={index} 
                  className={`h-2 rounded-full transition-all duration-300 ${
                    index === 0 ? 'w-6 bg-blue-600' : 'w-2 bg-gray-300'
                  }`}
                ></div>
              ))}
            </div>
            
            {/* Swipe hint */}
            <div className="text-center mt-3 text-sm text-gray-500 animate-pulse">
              Swipe to see more →
            </div>
          </div>

          {/* Desktop Grid */}
          <div className="hidden md:grid grid-cols-1 md:grid-cols-3 gap-6">
            {testimonials.map((testimonial, index) => (
              <div 
                key={index} 
                className="bg-white rounded-3xl p-8 shadow-md border border-gray-100 hover:shadow-xl hover:border-blue-200 transition-all duration-300 transform hover:scale-105"
                data-testid={`testimonial-${index}`}
              >
                {/* Rating */}
                <div className="flex items-center gap-1 mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                
                {/* Content */}
                <p className="text-gray-700 mb-6 leading-relaxed line-clamp-4">
                  "{testimonial.content}"
                </p>
                
                {/* Author */}
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-xl">
                    {testimonial.name.charAt(0)}
                  </div>
                  <div>
                    <h4 className="font-bold text-gray-900">{testimonial.name}</h4>
                    <p className="text-sm text-gray-600">{testimonial.role}</p>
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