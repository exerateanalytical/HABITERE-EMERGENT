import React from 'react';
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

const LandingPage = () => {
  const { login } = useAuth();
  
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

  const handleGetStarted = () => {
    const redirectUrl = `${window.location.origin}/auth/callback`;
    login(redirectUrl);
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
            
            {/* CTA Buttons - Native mobile feel */}
            <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto px-4">
              <button
                onClick={handleGetStarted}
                className="group relative bg-gradient-to-r from-blue-600 to-purple-600 active:from-blue-700 active:to-purple-700 text-white font-bold px-8 py-5 rounded-2xl shadow-lg active:shadow-md transform active:scale-95 transition-all duration-100 text-lg touch-manipulation w-full sm:flex-1"
                data-testid="get-started-btn"
                aria-label="Get started for free"
              >
                <span className="flex items-center justify-center gap-2">
                  Get Started Free
                  <ArrowRight className="w-5 h-5" />
                </span>
              </button>
              
              <a 
                href="/properties" 
                className="group bg-white active:bg-gray-100 border-2 border-gray-300 text-gray-800 font-bold px-8 py-5 rounded-2xl shadow-md active:shadow-sm transform active:scale-95 transition-all duration-100 text-lg touch-manipulation flex items-center justify-center gap-2 w-full sm:flex-1"
                data-testid="browse-properties-btn"
                aria-label="Browse available properties"
              >
                <span>Browse Properties</span>
                <Home className="w-5 h-5" />
              </a>
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
                    <Star className="w-4 h-4 text-yellow-400 fill-current" />
                    <Star className="w-4 h-4 text-yellow-400 fill-current" />
                    <Star className="w-4 h-4 text-yellow-400 fill-current" />
                    <Star className="w-4 h-4 text-yellow-400 fill-current" />
                    <Star className="w-4 h-4 text-yellow-400 fill-current" />
                  </div>
                  <span className="text-sm font-semibold text-gray-900">4.9 Rating</span>
                </div>
              </div>
              
              {/* Mobile money badge */}
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-xl shadow-2xl border-2 border-white/20 zoom-in">
                <div className="flex items-center space-x-2">
                  <div className="w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center">
                    <span className="text-xs font-bold text-gray-900">M</span>
                  </div>
                  <span className="text-sm font-semibold">MTN MoMo</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Premium Search Section */}
      <section className="py-8 md:py-12 bg-white relative -mt-8 md:-mt-12">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-gradient-to-br from-white via-blue-50/30 to-purple-50/30 rounded-3xl shadow-2xl border border-white/20 backdrop-blur-sm p-6 md:p-8 hover:shadow-3xl transition-all duration-500">
            <div className="text-center mb-6">
              <h2 className="text-xl md:text-2xl font-bold text-gray-900 mb-2">
                Find Your Dream Property
              </h2>
              <p className="text-sm md:text-base text-gray-600">Search from over 1,000 verified properties across Cameroon</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Property Type</label>
                <select className="w-full px-4 py-3 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-2xl shadow-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 text-base appearance-none cursor-pointer hover:shadow-xl" data-testid="search-type">
                  <option>All Types</option>
                  <option>🏠 House</option>
                  <option>🏢 Apartment</option>
                  <option>🏞️ Land</option>
                  <option>🏪 Commercial</option>
                  <option>🏨 Hotel</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Location</label>
                <select className="w-full px-4 py-3 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-2xl shadow-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 text-base appearance-none cursor-pointer hover:shadow-xl" data-testid="search-location">
                  <option>All Locations</option>
                  <option>📍 Douala</option>
                  <option>📍 Yaoundé</option>
                  <option>📍 Bafoussam</option>
                  <option>📍 Bamenda</option>
                  <option>📍 Garoua</option>
                  <option>📍 Maroua</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Price Range</label>
                <select className="w-full px-4 py-3 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-2xl shadow-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 text-base appearance-none cursor-pointer hover:shadow-xl" data-testid="search-price">
                  <option>Any Price</option>
                  <option>💰 Under 100K XAF</option>
                  <option>💰 100K - 500K XAF</option>
                  <option>💰 500K - 1M XAF</option>
                  <option>💰 1M - 5M XAF</option>
                  <option>💰 Over 5M XAF</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Search</label>
                <button 
                  className="group w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 active:from-blue-800 active:to-purple-800 text-white font-bold px-6 py-4 rounded-xl shadow-lg hover:shadow-2xl active:shadow-lg transform hover:-translate-y-1 active:translate-y-0 transition-all duration-200 text-base sm:text-lg touch-manipulation min-h-[56px]" 
                  data-testid="search-btn"
                  aria-label="Search properties"
                >
                  <div className="flex items-center justify-center gap-2">
                    <Search className="w-5 h-5 sm:w-6 sm:h-6 group-hover:scale-110 transition-transform duration-200" />
                    <span>Search Properties</span>
                  </div>
                </button>
              </div>
            </div>
            
            {/* Quick filters - Mobile optimized */}
            <div className="mt-6 flex flex-wrap gap-2 sm:gap-3 justify-center items-center">
              <span className="text-sm font-medium text-gray-600">Popular:</span>
              <button className="px-5 py-3 bg-white hover:bg-blue-50 active:bg-blue-100 border-2 border-gray-200 hover:border-blue-300 active:border-blue-400 rounded-full text-sm sm:text-base font-semibold text-gray-700 hover:text-blue-700 active:text-blue-800 transition-all duration-200 touch-manipulation min-h-[44px] shadow-sm hover:shadow-md">Houses in Douala</button>
              <button className="px-5 py-3 bg-white hover:bg-blue-50 active:bg-blue-100 border-2 border-gray-200 hover:border-blue-300 active:border-blue-400 rounded-full text-sm sm:text-base font-semibold text-gray-700 hover:text-blue-700 active:text-blue-800 transition-all duration-200 touch-manipulation min-h-[44px] shadow-sm hover:shadow-md">Apartments</button>
              <button className="px-5 py-3 bg-white hover:bg-blue-50 active:bg-blue-100 border-2 border-gray-200 hover:border-blue-300 active:border-blue-400 rounded-full text-sm sm:text-base font-semibold text-gray-700 hover:text-blue-700 active:text-blue-800 transition-all duration-200 touch-manipulation min-h-[44px] shadow-sm hover:shadow-md">Land for Sale</button>
            </div>
          </div>
        </div>
      </section>

      {/* Premium Features Section */}
      <section className="py-16 md:py-24 bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 md:mb-20 fade-in">
            <div className="inline-block px-4 py-2 bg-gradient-to-r from-blue-100 to-purple-100 rounded-full mb-6">
              <span className="text-sm font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Why Choose Habitere?</span>
            </div>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-gray-900 mb-6 leading-tight">
              The Most Trusted Platform
              <span className="block bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                in Cameroon
              </span>
            </h2>
            <p className="text-lg md:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              We're committed to making real estate and home services accessible, 
              secure, and convenient for everyone across all regions of Cameroon.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              const colors = [
                'from-blue-500 to-blue-600',
                'from-purple-500 to-purple-600', 
                'from-green-500 to-green-600',
                'from-orange-500 to-orange-600'
              ];
              const bgColors = [
                'from-blue-50 to-blue-100',
                'from-purple-50 to-purple-100',
                'from-green-50 to-green-100', 
                'from-orange-50 to-orange-100'
              ];
              
              return (
                <div key={index} className={`group relative bg-gradient-to-br ${bgColors[index % 4]} rounded-3xl p-6 md:p-8 shadow-xl hover:shadow-2xl transform hover:-translate-y-2 transition-all duration-500 border border-white/20 hover:border-white/40`} data-testid={`feature-${index}`}>
                  <div className="relative z-10">
                    <div className={`w-16 md:w-20 h-16 md:h-20 bg-gradient-to-br ${colors[index % 4]} rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg group-hover:shadow-xl group-hover:scale-110 transition-all duration-300`}>
                      <Icon className="w-8 md:w-10 h-8 md:h-10 text-white" />
                    </div>
                    <h3 className="text-xl md:text-2xl font-bold text-gray-900 mb-4 group-hover:text-gray-800 transition-colors duration-300">
                      {feature.title}
                    </h3>
                    <p className="text-base md:text-lg text-gray-700 leading-relaxed group-hover:text-gray-600 transition-colors duration-300">
                      {feature.description}
                    </p>
                  </div>
                  
                  {/* Decorative elements */}
                  <div className="absolute top-4 right-4 w-8 h-8 bg-white/20 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <div className="absolute bottom-4 left-4 w-6 h-6 bg-white/10 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300 delay-100"></div>
                </div>
              );
            })}
          </div>
          
          {/* Trust indicators */}
          <div className="mt-16 text-center">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
              <div className="flex flex-col items-center space-y-2">
                <div className="w-12 h-12 bg-green-100 rounded-2xl flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                </div>
                <span className="text-sm font-semibold text-gray-700">Verified Properties</span>
              </div>
              <div className="flex flex-col items-center space-y-2">
                <div className="w-12 h-12 bg-blue-100 rounded-2xl flex items-center justify-center">
                  <Shield className="w-6 h-6 text-blue-600" />
                </div>
                <span className="text-sm font-semibold text-gray-700">Secure Payments</span>
              </div>
              <div className="flex flex-col items-center space-y-2">
                <div className="w-12 h-12 bg-purple-100 rounded-2xl flex items-center justify-center">
                  <Users className="w-6 h-6 text-purple-600" />
                </div>
                <span className="text-sm font-semibold text-gray-700">Trusted Professionals</span>
              </div>
              <div className="flex flex-col items-center space-y-2">
                <div className="w-12 h-12 bg-orange-100 rounded-2xl flex items-center justify-center">
                  <Clock className="w-6 h-6 text-orange-600" />
                </div>
                <span className="text-sm font-semibold text-gray-700">24/7 Support</span>
              </div>
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
              
              <a href="/services" className="btn-primary">
                Explore Services
                <ArrowRight className="ml-2 w-5 h-5" />
              </a>
            </div>

            <div className="relative">
              <img 
                src="https://images.unsplash.com/photo-1505798577917-a65157d3320a"
                alt="Professional contractor"
                className="rounded-2xl shadow-lg object-cover w-full h-96"
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
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <FeaturedProperties 
            title="Featured Properties" 
            limit={8}
            showAll={true}
          />
        </div>
      </section>

      {/* Professional Services Carousel */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <ServicesCarousel 
            title="Connect with Trusted Professionals" 
            limit={12}
            showAll={true}
          />
        </div>
      </section>

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

          {/* Mobile: Horizontal scroll, Desktop: Grid */}
          <div className="md:hidden">
            <div className="flex overflow-x-auto scrollbar-hide gap-4 pb-4 snap-x snap-mandatory touch-action-pan-x">
              {testimonials.map((testimonial, index) => (
                <div key={index} className="flex-none w-80 card hover-lift snap-start" data-testid={`testimonial-${index}`}>
                  <div className="card-body p-4">
                    <div className="flex items-center mb-3">
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <Star key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                      ))}
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-4 italic leading-relaxed">
                      "{testimonial.content}"
                    </p>
                    
                    <div className="flex items-center">
                      <img 
                        src={testimonial.image}
                        alt={testimonial.name}
                        className="w-10 h-10 rounded-full object-cover mr-3"
                      />
                      <div>
                        <h4 className="font-medium text-gray-900 text-sm">{testimonial.name}</h4>
                        <p className="text-xs text-gray-600">{testimonial.role}, {testimonial.location}</p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="flex justify-center mt-4">
              <div className="swipe-indicator" />
            </div>
          </div>

          {/* Desktop Grid */}
          <div className="hidden md:grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="card hover-lift" data-testid={`testimonial-${index}`}>
                <div className="card-body">
                  <div className="flex items-center mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  
                  <p className="text-gray-600 mb-6 italic">
                    "{testimonial.content}"
                  </p>
                  
                  <div className="flex items-center">
                    <img 
                      src={testimonial.image}
                      alt={testimonial.name}
                      className="w-12 h-12 rounded-full object-cover mr-4"
                    />
                    <div>
                      <h4 className="font-semibold text-gray-900">{testimonial.name}</h4>
                      <p className="text-sm text-gray-600">{testimonial.role}, {testimonial.location}</p>
                    </div>
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