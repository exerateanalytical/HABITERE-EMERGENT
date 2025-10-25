import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Shield, Users, Camera, Eye, Car, Dog, Phone, CheckCircle, 
  ArrowRight, Lock, Clock, Award, AlertTriangle, Zap, 
  MapPin, Star, BadgeCheck, Target, Headphones, TrendingUp,
  FileCheck, UserCheck, Calendar
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const HomelandSecurity = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/security/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const services = [
    {
      icon: Shield,
      title: 'Armed Security Guards',
      description: '24/7 professional armed and unarmed security personnel with military-grade training',
      color: 'bg-red-600',
      hoverColor: 'hover:bg-red-700',
      href: '/security/services?type=Security Guards'
    },
    {
      icon: Camera,
      title: 'CCTV & Surveillance',
      description: 'High-definition surveillance systems with AI-powered monitoring and analytics',
      color: 'bg-blue-600',
      hoverColor: 'hover:bg-blue-700',
      href: '/security/services?type=CCTV Installation'
    },
    {
      icon: Eye,
      title: 'Control Room Monitoring',
      description: 'Advanced 24/7 control room operations with instant threat detection',
      color: 'bg-purple-600',
      hoverColor: 'hover:bg-purple-700',
      href: '/security/services?type=Remote Monitoring'
    },
    {
      icon: Car,
      title: 'Mobile Patrol Units',
      description: 'Rapid response mobile patrols covering wide security perimeters',
      color: 'bg-orange-600',
      hoverColor: 'hover:bg-orange-700',
      href: '/security/services?type=Patrol Units'
    },
    {
      icon: Dog,
      title: 'K9 Security Teams',
      description: 'Elite K9 units with specialized detection and patrol capabilities',
      color: 'bg-yellow-600',
      hoverColor: 'hover:bg-yellow-700',
      href: '/security/services?type=K9 Units'
    },
    {
      icon: AlertTriangle,
      title: 'Emergency Response',
      description: 'Tactical emergency response teams with sub-10 minute arrival times',
      color: 'bg-red-700',
      hoverColor: 'hover:bg-red-800',
      href: '/security/services?type=Emergency Response'
    }
  ];

  const certifications = [
    { icon: BadgeCheck, title: 'ISO 9001 Certified', desc: 'Quality Management' },
    { icon: Shield, title: 'Licensed & Insured', desc: 'Full Coverage' },
    { icon: Award, title: 'Industry Awards', desc: '5+ Recognition' },
    { icon: Star, title: 'Top Rated', desc: '4.9/5 Stars' }
  ];

  return (
    <div className="min-h-screen bg-gray-900">
      
      {/* Hero Section - Dark, Bold, Professional */}
      <div className="relative bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white overflow-hidden">
        {/* Security Pattern Overlay */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
          }}></div>
        </div>

        {/* Red Accent Lines */}
        <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-red-600 via-red-500 to-red-600"></div>
        
        <div className="container mx-auto px-4 py-16 md:py-24 lg:py-28 relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            
            {/* Left Content */}
            <div className="max-w-2xl">
              {/* Trust Badge */}
              <div className="inline-flex items-center px-4 py-2 bg-red-600/20 border-2 border-red-600 rounded-full mb-6">
                <Shield className="w-5 h-5 text-red-500 mr-2" />
                <span className="text-sm font-bold text-red-500 uppercase tracking-wider">Cameroon's Elite Security Force</span>
              </div>

              <h1 className="text-5xl md:text-6xl lg:text-7xl font-black text-white mb-6 leading-tight">
                HOMELAND
                <span className="block text-red-600">SECURITY</span>
              </h1>
              
              <p className="text-xl md:text-2xl text-gray-300 mb-8 leading-relaxed font-light">
                Professional armed security solutions for <span className="text-white font-semibold">residential, commercial</span> and <span className="text-white font-semibold">industrial</span> properties across Cameroon.
              </p>

              {/* Key Features */}
              <div className="grid grid-cols-2 gap-4 mb-8">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-red-600/20 flex items-center justify-center flex-shrink-0">
                    <Clock className="w-5 h-5 text-red-500" />
                  </div>
                  <span className="text-gray-300 font-medium">24/7 Protection</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-red-600/20 flex items-center justify-center flex-shrink-0">
                    <Zap className="w-5 h-5 text-red-500" />
                  </div>
                  <span className="text-gray-300 font-medium">Rapid Response</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-red-600/20 flex items-center justify-center flex-shrink-0">
                    <BadgeCheck className="w-5 h-5 text-red-500" />
                  </div>
                  <span className="text-gray-300 font-medium">Licensed Guards</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-red-600/20 flex items-center justify-center flex-shrink-0">
                    <Lock className="w-5 h-5 text-red-500" />
                  </div>
                  <span className="text-gray-300 font-medium">Full Insurance</span>
                </div>
              </div>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4">
                <button
                  onClick={() => navigate('/security/services')}
                  className="group bg-red-600 hover:bg-red-700 text-white px-8 py-4 rounded-lg font-bold text-lg transition-all shadow-xl hover:shadow-2xl hover:shadow-red-600/50 flex items-center justify-center"
                >
                  Request Security Quote
                  <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
                <button
                  onClick={() => navigate('/security/apply')}
                  className="bg-gray-800 hover:bg-gray-700 text-white border-2 border-gray-700 hover:border-red-600 px-8 py-4 rounded-lg font-bold text-lg transition-all"
                >
                  Join Our Team
                </button>
              </div>
            </div>

            {/* Right Image */}
            <div className="relative">
              <div className="relative rounded-2xl overflow-hidden shadow-2xl border-4 border-red-600/30">
                <img 
                  src="https://images.unsplash.com/photo-1552622594-9a37efeec618?w=800&q=90"
                  alt="Professional Security Guard"
                  className="w-full h-auto object-cover"
                />
                {/* Overlay Badge */}
                <div className="absolute bottom-6 left-6 right-6 bg-black/80 backdrop-blur-sm border border-red-600/50 rounded-xl p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm text-gray-400 mb-1">Trusted Security</div>
                      <div className="text-2xl font-black text-white">1000+ <span className="text-red-500">Clients Protected</span></div>
                    </div>
                    <Shield className="w-12 h-12 text-red-600" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Bar - Bold Red Theme */}
      {!loading && stats && (
        <div className="bg-gradient-to-r from-red-600 to-red-700 text-white py-8 border-y-4 border-red-800">
          <div className="container mx-auto px-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
              <div className="border-r border-red-800/50 last:border-0">
                <div className="text-4xl md:text-5xl font-black mb-2">{stats.total_services}+</div>
                <div className="text-sm md:text-base font-semibold uppercase tracking-wider opacity-90">Active Services</div>
              </div>
              <div className="border-r border-red-800/50 last:border-0">
                <div className="text-4xl md:text-5xl font-black mb-2">{stats.available_guards}+</div>
                <div className="text-sm md:text-base font-semibold uppercase tracking-wider opacity-90">Elite Guards</div>
              </div>
              <div className="border-r border-red-800/50 last:border-0">
                <div className="text-4xl md:text-5xl font-black mb-2">{stats.total_bookings}+</div>
                <div className="text-sm md:text-base font-semibold uppercase tracking-wider opacity-90">Operations</div>
              </div>
              <div>
                <div className="text-4xl md:text-5xl font-black mb-2">24/7</div>
                <div className="text-sm md:text-base font-semibold uppercase tracking-wider opacity-90">Support</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Services Grid - Dark Professional */}
      <section className="py-20 bg-gray-900">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <div className="inline-block px-4 py-2 bg-red-600/10 border border-red-600/30 rounded-full mb-4">
              <span className="text-sm font-bold text-red-500 uppercase tracking-wider">Our Services</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
              Comprehensive Security Solutions
            </h2>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Military-grade security services tailored for your specific needs
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {services.map((service, index) => {
              const Icon = service.icon;
              return (
                <Link
                  key={index}
                  to={service.href}
                  className="group relative bg-gray-800 rounded-xl shadow-xl hover:shadow-2xl transition-all p-8 border-2 border-gray-700 hover:border-red-600 overflow-hidden"
                >
                  {/* Hover Effect Overlay */}
                  <div className="absolute inset-0 bg-gradient-to-br from-red-600/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  
                  <div className="relative z-10">
                    <div className={`w-16 h-16 rounded-xl ${service.color} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-lg`}>
                      <Icon className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold mb-3 text-white group-hover:text-red-500 transition-colors">
                      {service.title}
                    </h3>
                    <p className="text-gray-400 leading-relaxed mb-4">{service.description}</p>
                    
                    <div className="flex items-center text-red-500 font-semibold">
                      Learn More
                      <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-2 transition-transform" />
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* Certifications - Trust Badges */}
      <section className="py-16 bg-black border-y border-gray-800">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {certifications.map((cert, index) => {
              const Icon = cert.icon;
              return (
                <div key={index} className="text-center group">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-600/10 border-2 border-red-600/30 mb-4 group-hover:bg-red-600/20 group-hover:scale-110 transition-all">
                    <Icon className="w-8 h-8 text-red-600" />
                  </div>
                  <h3 className="font-bold text-white mb-1">{cert.title}</h3>
                  <p className="text-sm text-gray-500">{cert.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Join Team CTA - Bold Red */}
      <section className="py-20 bg-gradient-to-br from-gray-900 via-red-900/20 to-gray-900">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-red-600/20 border-4 border-red-600 mb-6">
              <Users className="w-10 h-10 text-red-500" />
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-white mb-6">
              Join The Elite Security Force
            </h2>
            <p className="text-xl text-gray-300 mb-8 leading-relaxed">
              Are you a trained security professional? Apply now to join Cameroon's most trusted security team. 
              <span className="text-white font-semibold"> Competitive pay, professional training, and career growth.</span>
            </p>
            
            {/* Benefits Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10">
              <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
                <div className="text-2xl font-bold text-red-500 mb-1">₣500K+</div>
                <div className="text-sm text-gray-400">Monthly Salary</div>
              </div>
              <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
                <div className="text-2xl font-bold text-red-500 mb-1">Full</div>
                <div className="text-sm text-gray-400">Health Insurance</div>
              </div>
              <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
                <div className="text-2xl font-bold text-red-500 mb-1">24/7</div>
                <div className="text-sm text-gray-400">Support System</div>
              </div>
            </div>

            <button
              onClick={() => navigate('/security/apply')}
              className="bg-red-600 hover:bg-red-700 text-white px-10 py-5 rounded-xl font-bold text-xl transition-all shadow-2xl hover:shadow-red-600/50 inline-flex items-center"
            >
              Apply Now
              <ArrowRight className="ml-3 w-6 h-6" />
            </button>
          </div>
        </div>
      </section>

      {/* Footer CTA - Dark Professional */}
      <section className="bg-black text-white py-20 border-t-4 border-red-600">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl md:text-5xl font-black mb-6">
            Security You Can Trust.
            <span className="block text-red-600">Anytime. Anywhere.</span>
          </h2>
          <p className="text-xl mb-10 text-gray-300 max-w-2xl mx-auto">
            Protect your property, business, and loved ones with Cameroon's most advanced security platform.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate('/security/services')}
              className="bg-red-600 hover:bg-red-700 px-10 py-5 rounded-xl font-bold text-xl transition-all shadow-xl hover:shadow-2xl hover:shadow-red-600/50"
            >
              Get Protected Today
            </button>
            <button
              onClick={() => navigate('/contact')}
              className="bg-gray-800 hover:bg-gray-700 border-2 border-gray-700 hover:border-red-600 px-10 py-5 rounded-xl font-bold text-xl transition-all"
            >
              Contact Us
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomelandSecurity;
