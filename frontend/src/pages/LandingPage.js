import React from 'react';
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
  CheckCircle
} from 'lucide-react';

const LandingPage = () => {
  const { login } = useAuth();

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
      {/* Hero Section - Premium Mobile-First Design */}
      <section className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-8 sm:py-12 md:py-20 lg:py-24 safe-area-top">
        {/* Background decorative elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-blue-200/30 to-purple-200/30 rounded-full blur-3xl"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-tr from-indigo-200/30 to-blue-200/30 rounded-full blur-3xl"></div>
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-16 items-center">
            <div className="space-y-6 md:space-y-8 text-center lg:text-left fade-in">
              {/* Trust badge */}
              <div className="inline-flex items-center px-4 py-2 bg-white/80 backdrop-blur-sm rounded-full shadow-lg border border-white/20">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                <span className="text-sm font-medium text-gray-700">#1 Platform in Cameroon</span>
              </div>
              
              <div className="space-y-4 md:space-y-6">
                <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl font-extrabold text-gray-900 leading-[1.1] tracking-tight">
                  Find Your Perfect
                  <span className="block mt-2">
                    <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-700 bg-clip-text text-transparent"> Home</span> and
                    <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-700 bg-clip-text text-transparent"> Services</span>
                  </span>
                  <span className="block mt-2 text-xl sm:text-2xl md:text-3xl lg:text-4xl xl:text-5xl font-semibold text-gray-700">
                    in Cameroon
                  </span>
                </h1>
                <p className="text-base sm:text-lg md:text-xl text-gray-600 leading-relaxed max-w-2xl mx-auto lg:mx-0 font-medium">
                  Cameroon's most trusted platform for real estate and home services. 
                  Discover verified properties, connect with certified professionals, and make secure payments with MTN MoMo.
                </p>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-3 md:gap-4 max-w-lg mx-auto lg:mx-0">
                <button
                  onClick={handleGetStarted}
                  className="group relative overflow-hidden bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold px-8 py-4 rounded-2xl shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all duration-300 text-base md:text-lg touch-action-manipulation"
                  data-testid="get-started-btn"
                >
                  <span className="relative z-10 flex items-center justify-center">
                    Get Started Free
                    <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
                  </span>
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-blue-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </button>
                <a 
                  href="/properties" 
                  className="group bg-white/90 backdrop-blur-sm hover:bg-white border-2 border-gray-200 hover:border-blue-300 text-gray-700 hover:text-blue-700 font-semibold px-8 py-4 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 text-base md:text-lg touch-action-manipulation flex items-center justify-center"
                  data-testid="browse-properties-btn"
                >
                  Browse Properties
                  <Home className="ml-2 w-5 h-5 group-hover:scale-110 transition-transform duration-300" />
                </a>
              </div>

              {/* Enhanced mobile-optimized stats */}
              <div className="grid grid-cols-3 gap-4 sm:gap-6 md:gap-8 pt-6 max-w-md mx-auto lg:mx-0">
                <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-4 text-center shadow-lg border border-white/20 hover:shadow-xl transition-all duration-300">
                  <div className="text-xl sm:text-2xl md:text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">1000+</div>
                  <div className="text-xs sm:text-sm text-gray-600 font-medium mt-1">Properties</div>
                </div>
                <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-4 text-center shadow-lg border border-white/20 hover:shadow-xl transition-all duration-300">
                  <div className="text-xl sm:text-2xl md:text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">500+</div>
                  <div className="text-xs sm:text-sm text-gray-600 font-medium mt-1">Professionals</div>
                </div>
                <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-4 text-center shadow-lg border border-white/20 hover:shadow-xl transition-all duration-300">
                  <div className="text-xl sm:text-2xl md:text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">10K+</div>
                  <div className="text-xs sm:text-sm text-gray-600 font-medium mt-1">Happy Users</div>
                </div>
              </div>
            </div>

            <div className="relative slide-up">
              <div className="grid grid-cols-2 gap-4 md:gap-6">
                <div className="space-y-4">
                  <div className="relative group overflow-hidden rounded-3xl shadow-2xl">
                    <img 
                      src="https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800&q=80"
                      alt="Modern house with keys"
                      className="object-cover h-48 sm:h-56 md:h-64 w-full transform group-hover:scale-105 transition-transform duration-700"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
                  </div>
                  <div className="relative group overflow-hidden rounded-2xl shadow-xl">
                    <img 
                      src="https://images.unsplash.com/photo-1605146769289-440113cc3d00?w=600&q=80"
                      alt="Residential houses"
                      className="object-cover h-32 sm:h-36 w-full transform group-hover:scale-105 transition-transform duration-700"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
                  </div>
                </div>
                <div className="space-y-4 pt-8">
                  <div className="relative group overflow-hidden rounded-2xl shadow-xl">
                    <img 
                      src="https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=600&q=80"
                      alt="Luxury house with pool"
                      className="object-cover h-32 sm:h-36 w-full transform group-hover:scale-105 transition-transform duration-700"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
                  </div>
                  <div className="relative group overflow-hidden rounded-3xl shadow-2xl">
                    <img 
                      src="https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&q=80"
                      alt="Modern apartment building"
                      className="object-cover h-48 sm:h-56 md:h-64 w-full transform group-hover:scale-105 transition-transform duration-700"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
                  </div>
                </div>
              </div>
              
              {/* Enhanced floating cards */}
              <div className="absolute top-4 left-4 bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl p-3 border border-white/20 hover:shadow-3xl transition-all duration-300 zoom-in">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm font-semibold text-gray-900">Available Now</span>
                </div>
              </div>
              
              <div className="absolute bottom-4 right-4 bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl p-3 border border-white/20 hover:shadow-3xl transition-all duration-300 zoom-in">
                <div className="flex items-center space-x-2">
                  <div className="flex items-center">
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

      {/* Search Section - Mobile Optimized */}
      <section className="py-8 md:py-12 bg-white relative -mt-6 md:-mt-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-xl md:rounded-2xl shadow-lg md:shadow-xl border border-gray-100 p-4 md:p-6">
            <h2 className="text-lg md:text-xl font-semibold text-gray-900 mb-3 md:mb-4">
              Quick Search
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3 md:gap-4">
              <div>
                <select className="form-select text-base" data-testid="search-type">
                  <option>Property Type</option>
                  <option>House</option>
                  <option>Apartment</option>
                  <option>Land</option>
                  <option>Commercial</option>
                </select>
              </div>
              <div>
                <select className="form-select text-base" data-testid="search-location">
                  <option>Location</option>
                  <option>Douala</option>
                  <option>Yaoundé</option>
                  <option>Bafoussam</option>
                  <option>Bamenda</option>
                </select>
              </div>
              <div>
                <select className="form-select text-base" data-testid="search-price">
                  <option>Price Range</option>
                  <option>Under 100,000 XAF</option>
                  <option>100,000 - 500,000 XAF</option>
                  <option>500,000 - 1,000,000 XAF</option>
                  <option>Over 1,000,000 XAF</option>
                </select>
              </div>
              <button className="btn-primary btn-mobile-full md:btn-primary flex items-center justify-center text-base touch-action-manipulation" data-testid="search-btn">
                <Search className="w-4 md:w-5 h-4 md:h-5 mr-2" />
                Search
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section - Mobile Optimized */}
      <section className="py-12 md:py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8 md:mb-16">
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 mb-3 md:mb-4">
              Why Choose Habitere?
            </h2>
            <p className="text-base md:text-lg text-gray-600 max-w-2xl mx-auto px-4">
              We're committed to making real estate and home services accessible, 
              secure, and convenient for everyone in Cameroon.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="card hover-lift text-center card-mobile-elevated" data-testid={`feature-${index}`}>
                  <div className="card-body p-4 md:p-6">
                    <div className="w-10 md:w-12 h-10 md:h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3 md:mb-4">
                      <Icon className="w-5 md:w-6 h-5 md:h-6 text-blue-600" />
                    </div>
                    <h3 className="text-lg md:text-xl font-semibold text-gray-900 mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-sm md:text-base text-gray-600 leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </div>
              );
            })}
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

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-indigo-700">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Find Your Perfect Home or Service?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Join Habitere today and discover the easiest way to buy, rent, or sell properties, 
            and connect with trusted professionals across Cameroon.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={handleGetStarted}
              className="inline-flex items-center px-8 py-4 border border-transparent text-lg font-medium rounded-full text-blue-700 bg-white hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 shadow-lg hover:shadow-xl"
              data-testid="cta-get-started-btn"
            >
              Get Started for Free
              <ArrowRight className="ml-2 w-5 h-5" />
            </button>
            <a
              href="/properties"
              className="inline-flex items-center px-8 py-4 border-2 border-white text-lg font-medium rounded-full text-white bg-transparent hover:bg-white hover:text-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-white transition-all duration-200"
              data-testid="cta-browse-properties-btn"
            >
              Browse Properties
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="md:col-span-2">
              <div className="flex items-center mb-4">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <Building className="w-5 h-5 text-white" />
                </div>
                <span className="ml-2 text-xl font-bold">Habitere</span>
              </div>
              <p className="text-gray-400 mb-4 max-w-md">
                Cameroon's leading platform for real estate and home services. 
                Making property transactions and professional services accessible to everyone.
              </p>
              <div className="flex items-center space-x-2 text-gray-400">
                <MapPin className="w-4 h-4" />
                <span>Douala, Cameroon</span>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Quick Links</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="/properties" className="hover:text-white transition-colors">Properties</a></li>
                <li><a href="/services" className="hover:text-white transition-colors">Services</a></li>
                <li><a href="#" className="hover:text-white transition-colors">About Us</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
                <li><a href="#" className="hover:text-white transition-colors">FAQ</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-12 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Habitere. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;