import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { 
  Shield, Users, Camera, Eye, Car, Dog, Phone, CheckCircle, 
  ArrowRight, Lock, Clock, Award, AlertTriangle, Zap, 
  MapPin, Star, BadgeCheck, Target, TrendingUp, UserCheck,
  FileText, Briefcase, PhoneCall
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const SecurityPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
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
      features: ['Licensed Officers', 'Background Verified', 'Fully Insured', '24/7 Availability'],
      color: 'from-red-600 to-red-700',
      href: '/security/services?type=Security Guards'
    },
    {
      icon: Camera,
      title: 'CCTV & Surveillance',
      description: 'High-definition surveillance systems with AI-powered monitoring and analytics',
      features: ['4K Resolution', 'Night Vision', 'Cloud Storage', 'Mobile Access'],
      color: 'from-blue-600 to-blue-700',
      href: '/security/services?type=CCTV Installation'
    },
    {
      icon: Eye,
      title: 'Control Room Monitoring',
      description: 'Advanced 24/7 control room operations with instant threat detection',
      features: ['Live Monitoring', 'Instant Alerts', 'Incident Reports', 'Video Verification'],
      color: 'from-purple-600 to-purple-700',
      href: '/security/services?type=Remote Monitoring'
    },
    {
      icon: Car,
      title: 'Mobile Patrol Units',
      description: 'Rapid response mobile patrols covering wide security perimeters',
      features: ['GPS Tracking', 'Random Routes', 'Checkpoint Scanning', 'Quick Response'],
      color: 'from-orange-600 to-orange-700',
      href: '/security/services?type=Patrol Units'
    },
    {
      icon: Dog,
      title: 'K9 Security Teams',
      description: 'Elite K9 units with specialized detection and patrol capabilities',
      features: ['Drug Detection', 'Bomb Detection', 'Patrol Support', 'Handler Certified'],
      color: 'from-yellow-600 to-yellow-700',
      href: '/security/services?type=K9 Units'
    },
    {
      icon: AlertTriangle,
      title: 'Emergency Response',
      description: 'Tactical emergency response teams with sub-10 minute arrival times',
      features: ['Rapid Response', 'Tactical Training', 'Armed Support', 'Crisis Management'],
      color: 'from-red-700 to-red-800',
      href: '/security/services?type=Emergency Response'
    }
  ];

  const whyChooseUs = [
    { icon: Award, title: '15+ Years Experience', desc: 'Industry-leading security expertise' },
    { icon: Users, title: '500+ Security Officers', desc: 'Highly trained professionals' },
    { icon: Target, title: '99.9% Success Rate', desc: 'Proven track record' },
    { icon: Clock, title: '24/7 Support', desc: 'Always available' },
    { icon: Shield, title: 'Licensed & Insured', desc: 'Full protection coverage' },
    { icon: Star, title: '4.9/5 Client Rating', desc: 'Trusted by thousands' }
  ];

  return (
    <div className="min-h-screen bg-white">
      
      {/* Hero Section with Professional Security Officer */}
      <div className="relative bg-gradient-to-br from-gray-900 via-black to-gray-800 text-white overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
          }}></div>
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            
            {/* Left Side - Content */}
            <div className="text-left space-y-6">
              <div className="inline-flex items-center space-x-2 bg-red-600/20 backdrop-blur-sm border border-red-500/30 px-4 py-2 rounded-full">
                <Shield className="w-5 h-5 text-red-400" />
                <span className="text-sm font-semibold text-red-300">Homeland Security Services</span>
              </div>

              <h1 className="text-4xl md:text-5xl lg:text-6xl font-black leading-tight">
                Professional Security
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-400">
                  You Can Trust
                </span>
              </h1>

              <p className="text-xl text-gray-300 leading-relaxed max-w-2xl">
                Cameroon's leading security services provider with military-grade training, 
                24/7 monitoring, and rapid response teams protecting homes, businesses, and events.
              </p>

              {/* Key Stats */}
              <div className="grid grid-cols-3 gap-4 py-6">
                <div className="text-center">
                  <div className="text-3xl font-black text-white">500+</div>
                  <div className="text-sm text-gray-400">Security Officers</div>
                </div>
                <div className="text-center border-l border-r border-gray-700">
                  <div className="text-3xl font-black text-white">15+</div>
                  <div className="text-sm text-gray-400">Years Experience</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-black text-white">99.9%</div>
                  <div className="text-sm text-gray-400">Success Rate</div>
                </div>
              </div>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 pt-4">
                <button
                  onClick={() => navigate('/security/services')}
                  className="group bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white px-8 py-4 rounded-xl font-bold text-lg transition-all shadow-2xl hover:shadow-red-500/50 flex items-center justify-center"
                >
                  Book Security Service
                  <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
                
                <button
                  onClick={() => navigate('/security/apply')}
                  className="group bg-white/10 backdrop-blur-sm border-2 border-white/30 hover:bg-white/20 text-white px-8 py-4 rounded-xl font-bold text-lg transition-all flex items-center justify-center"
                >
                  <UserCheck className="mr-2 w-5 h-5" />
                  Apply as Security Guard
                </button>
              </div>

              {/* Trust Badges */}
              <div className="flex items-center space-x-6 pt-6">
                <div className="flex items-center space-x-2">
                  <BadgeCheck className="w-5 h-5 text-green-400" />
                  <span className="text-sm text-gray-400">Licensed & Insured</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Award className="w-5 h-5 text-yellow-400" />
                  <span className="text-sm text-gray-400">ISO 9001 Certified</span>
                </div>
              </div>
            </div>

            {/* Right Side - Professional Security Officer Image */}
            <div className="relative">
              <div className="relative rounded-2xl overflow-hidden shadow-2xl">
                <img
                  src="https://images.unsplash.com/photo-1618371690240-e0d46eead4b8?w=800&q=90"
                  alt="Professional Homeland Security Officer"
                  className="w-full h-[600px] object-cover"
                />
                {/* Overlay Badge */}
                <div className="absolute bottom-6 left-6 right-6 bg-black/80 backdrop-blur-md rounded-xl p-6 border border-white/10">
                  <div className="flex items-center space-x-4">
                    <div className="w-16 h-16 bg-gradient-to-br from-red-600 to-red-700 rounded-xl flex items-center justify-center">
                      <Shield className="w-8 h-8 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="text-white font-bold text-lg">Homeland Security</div>
                      <div className="text-gray-400 text-sm">Professional Security Services</div>
                    </div>
                    <div className="text-right">
                      <div className="text-yellow-400 flex items-center text-sm">
                        <Star className="w-4 h-4 fill-current mr-1" />
                        4.9/5
                      </div>
                      <div className="text-gray-400 text-xs">2,500+ Reviews</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Floating Stats Cards */}
              <div className="absolute -top-6 -right-6 bg-green-600 text-white px-6 py-4 rounded-xl shadow-2xl">
                <div className="text-2xl font-black">24/7</div>
                <div className="text-sm">Available</div>
              </div>
              
              <div className="absolute -bottom-6 -left-6 bg-blue-600 text-white px-6 py-4 rounded-xl shadow-2xl">
                <div className="text-2xl font-black">&lt;10min</div>
                <div className="text-sm">Response Time</div>
              </div>
            </div>

          </div>
        </div>
      </div>

      {/* Services Grid */}
      <div className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-black text-gray-900 mb-4">
              Our Security Services
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Comprehensive security solutions tailored to protect what matters most to you
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {services.map((service, index) => {
              const Icon = service.icon;
              return (
                <div
                  key={index}
                  className="group bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden cursor-pointer border border-gray-100"
                  onClick={() => navigate(service.href)}
                >
                  <div className={`bg-gradient-to-r ${service.color} p-6`}>
                    <Icon className="w-12 h-12 text-white mb-3" />
                    <h3 className="text-2xl font-bold text-white">{service.title}</h3>
                  </div>
                  
                  <div className="p-6">
                    <p className="text-gray-600 mb-4">{service.description}</p>
                    
                    <ul className="space-y-2 mb-4">
                      {service.features.map((feature, idx) => (
                        <li key={idx} className="flex items-center text-sm text-gray-700">
                          <CheckCircle className="w-4 h-4 text-green-600 mr-2 flex-shrink-0" />
                          {feature}
                        </li>
                      ))}
                    </ul>

                    <button className="w-full bg-gray-900 hover:bg-black text-white py-3 rounded-xl font-semibold transition-all flex items-center justify-center group-hover:shadow-lg">
                      Book Service
                      <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Why Choose Us */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-black text-gray-900 mb-4">
              Why Choose Homeland Security?
            </h2>
            <p className="text-xl text-gray-600">
              Industry-leading expertise and commitment to your safety
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {whyChooseUs.map((item, index) => {
              const Icon = item.icon;
              return (
                <div key={index} className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-8 hover:shadow-xl transition-all">
                  <div className="w-16 h-16 bg-gradient-to-br from-red-600 to-red-700 rounded-xl flex items-center justify-center mb-4">
                    <Icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{item.title}</h3>
                  <p className="text-gray-600">{item.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-gray-900 to-black text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            
            {/* Book Security Service */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20">
              <Briefcase className="w-12 h-12 text-red-400 mb-4" />
              <h3 className="text-3xl font-black mb-4">Need Security Services?</h3>
              <p className="text-gray-300 mb-6">
                Get instant quotes for armed guards, CCTV installation, mobile patrols, and more. 
                Protect your property with Cameroon's most trusted security provider.
              </p>
              <button
                onClick={() => navigate('/security/services')}
                className="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white px-8 py-4 rounded-xl font-bold text-lg transition-all shadow-xl flex items-center"
              >
                Browse Security Services
                <ArrowRight className="ml-2 w-5 h-5" />
              </button>
            </div>

            {/* Apply as Security Guard */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20">
              <UserCheck className="w-12 h-12 text-green-400 mb-4" />
              <h3 className="text-3xl font-black mb-4">Join Our Team</h3>
              <p className="text-gray-300 mb-6">
                Looking for a career in security? Join Homeland Security's elite team. 
                We offer competitive pay, comprehensive training, and career advancement opportunities.
              </p>
              <button
                onClick={() => navigate('/security/apply')}
                className="bg-white text-gray-900 hover:bg-gray-100 px-8 py-4 rounded-xl font-bold text-lg transition-all shadow-xl flex items-center"
              >
                Apply Now
                <ArrowRight className="ml-2 w-5 h-5" />
              </button>
            </div>

          </div>
        </div>
      </div>

      {/* Contact Section */}
      <div className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-black text-gray-900 mb-4">
            24/7 Emergency Hotline
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Our security team is always ready to respond
          </p>
          <a
            href="tel:+237675668211"
            className="inline-flex items-center bg-gradient-to-r from-red-600 to-red-700 text-white px-10 py-5 rounded-xl font-bold text-2xl hover:shadow-2xl transition-all"
          >
            <Phone className="mr-3 w-8 h-8" />
            +237 675 668 211
          </a>
        </div>
      </div>

    </div>
  );
};

export default SecurityPage;
