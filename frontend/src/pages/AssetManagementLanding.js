import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Package, Wrench, DollarSign, TrendingUp, CheckCircle, Clock, Shield, 
  BarChart3, Bell, FileText, Calendar, Users, ArrowRight, Building2,
  Smartphone, Zap, Award, HeadphonesIcon, Settings, Target,
  LineChart, ClipboardCheck, MapPin, Star, PhoneCall
} from 'lucide-react';

const AssetManagementLanding = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const handleGetStarted = (type) => {
    if (type === 'diy') {
      if (user) {
        navigate('/assets/dashboard');
      } else {
        navigate('/auth/register');
      }
    } else {
      navigate('/contact', { state: { service: 'Managed Asset Management' } });
    }
  };

  return (
    <div className="min-h-screen bg-white">
      
      {/* Hero Section - Industry Standard */}
      <div className="relative bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
          }}></div>
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-32">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div>
              <div className="inline-flex items-center px-4 py-2 bg-green-600/20 border border-green-600/30 rounded-full mb-6">
                <Award className="w-5 h-5 text-green-400 mr-2" />
                <span className="text-sm font-bold text-green-400">Trusted by 500+ Property Owners</span>
              </div>

              <h1 className="text-4xl md:text-5xl lg:text-6xl font-black mb-6 leading-tight">
                Professional Asset Management
                <span className="block text-green-500 mt-2">for Real Estate</span>
              </h1>

              <p className="text-xl text-gray-300 mb-8 leading-relaxed">
                Maximize your property value with comprehensive asset management. 
                Choose <span className="text-white font-semibold">DIY tools</span> or let our 
                <span className="text-green-400 font-semibold"> expert team manage everything</span> for you.
              </p>

              {/* Key Stats */}
              <div className="grid grid-cols-3 gap-6 mb-10">
                <div className="text-center">
                  <div className="text-3xl font-black text-green-400 mb-1">30%</div>
                  <div className="text-sm text-gray-400">Cost Savings</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-black text-green-400 mb-1">24/7</div>
                  <div className="text-sm text-gray-400">Monitoring</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-black text-green-400 mb-1">500+</div>
                  <div className="text-sm text-gray-400">Properties</div>
                </div>
              </div>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4">
                <button
                  onClick={() => handleGetStarted('diy')}
                  className="group bg-green-600 hover:bg-green-700 text-white px-8 py-4 rounded-xl font-bold text-lg shadow-2xl hover:shadow-green-600/50 transition-all flex items-center justify-center"
                >
                  Start DIY Management
                  <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
                <button
                  onClick={() => handleGetStarted('managed')}
                  className="bg-gray-800 hover:bg-gray-700 text-white border-2 border-gray-600 hover:border-green-600 px-8 py-4 rounded-xl font-bold text-lg transition-all"
                >
                  Get Managed Service
                </button>
              </div>
            </div>

            {/* Right Image/Visual */}
            <div className="hidden lg:block">
              <div className="relative">
                <img
                  src="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&q=90"
                  alt="Modern building asset management"
                  className="rounded-2xl shadow-2xl border-4 border-gray-700"
                />
                {/* Floating Stats Card */}
                <div className="absolute -bottom-6 -left-6 bg-white rounded-2xl shadow-2xl p-6 max-w-xs">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                      <TrendingUp className="w-6 h-6 text-green-600" />
                    </div>
                    <div>
                      <div className="text-2xl font-black text-gray-900">98.5%</div>
                      <div className="text-sm text-gray-600">Asset Uptime</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Service Options Toggle */}
      <div className="bg-gray-50 py-16 border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-black text-gray-900 mb-4">
              Choose Your Management Style
            </h2>
            <p className="text-xl text-gray-600">
              Whether you prefer hands-on control or professional management, we've got you covered
            </p>
          </div>

          {/* Tab Switcher */}
          <div className="flex justify-center mb-12">
            <div className="inline-flex bg-white rounded-2xl shadow-lg p-2 border-2 border-gray-200">
              <button
                onClick={() => setActiveTab('diy')}
                className={`px-8 py-4 rounded-xl font-bold text-lg transition-all ${
                  activeTab === 'diy'
                    ? 'bg-green-600 text-white shadow-lg'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Settings className="w-5 h-5 inline mr-2" />
                DIY Management
              </button>
              <button
                onClick={() => setActiveTab('managed')}
                className={`px-8 py-4 rounded-xl font-bold text-lg transition-all ${
                  activeTab === 'managed'
                    ? 'bg-green-600 text-white shadow-lg'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Users className="w-5 h-5 inline mr-2" />
                Managed Service
              </button>
            </div>
          </div>

          {/* DIY Management Content */}
          {activeTab === 'diy' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition-all">
                <div className="w-16 h-16 bg-green-100 rounded-2xl flex items-center justify-center mb-6">
                  <Package className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">Asset Tracking</h3>
                <p className="text-gray-600 mb-6">
                  Complete inventory management with QR codes, photos, documents, and warranty tracking. Know exactly what you own and where it is.
                </p>
                <ul className="space-y-3">
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5" />
                    <span className="text-gray-700">Unlimited asset records</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5" />
                    <span className="text-gray-700">Custom categories & tags</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5" />
                    <span className="text-gray-700">Document storage</span>
                  </li>
                </ul>
              </div>

              <div className="bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition-all">
                <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mb-6">
                  <Wrench className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">Maintenance Scheduling</h3>
                <p className="text-gray-600 mb-6">
                  Automated maintenance schedules with priority management, technician assignments, and progress tracking.
                </p>
                <ul className="space-y-3">
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-blue-600 mr-2 mt-0.5" />
                    <span className="text-gray-700">Recurring schedules</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-blue-600 mr-2 mt-0.5" />
                    <span className="text-gray-700">Priority management</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-blue-600 mr-2 mt-0.5" />
                    <span className="text-gray-700">Automated reminders</span>
                  </li>
                </ul>
              </div>

              <div className="bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition-all">
                <div className="w-16 h-16 bg-purple-100 rounded-2xl flex items-center justify-center mb-6">
                  <BarChart3 className="w-8 h-8 text-purple-600" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">Analytics & Reports</h3>
                <p className="text-gray-600 mb-6">
                  Comprehensive dashboards with expense tracking, asset performance, and cost optimization insights.
                </p>
                <ul className="space-y-3">
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-purple-600 mr-2 mt-0.5" />
                    <span className="text-gray-700">Real-time analytics</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-purple-600 mr-2 mt-0.5" />
                    <span className="text-gray-700">Expense tracking</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-purple-600 mr-2 mt-0.5" />
                    <span className="text-gray-700">Custom reports</span>
                  </li>
                </ul>
              </div>
            </div>
          )}

          {/* Managed Service Content */}
          {activeTab === 'managed' && (
            <div>
              <div className="bg-gradient-to-br from-green-600 to-green-700 rounded-3xl shadow-2xl p-12 text-white mb-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
                  <div>
                    <h3 className="text-3xl font-black mb-4">
                      Full-Service Asset Management
                    </h3>
                    <p className="text-green-50 text-lg mb-6">
                      Let our expert team handle everything - from tracking to maintenance coordination, expense management to compliance.
                    </p>
                    <div className="flex items-center gap-3 mb-6">
                      <div className="flex -space-x-2">
                        <div className="w-10 h-10 bg-white rounded-full border-2 border-green-600"></div>
                        <div className="w-10 h-10 bg-white rounded-full border-2 border-green-600"></div>
                        <div className="w-10 h-10 bg-white rounded-full border-2 border-green-600"></div>
                      </div>
                      <span className="text-sm font-semibold">Dedicated Team of 15+ Professionals</span>
                    </div>
                    <button
                      onClick={() => handleGetStarted('managed')}
                      className="bg-white text-green-600 hover:bg-green-50 px-8 py-4 rounded-xl font-bold text-lg transition-all"
                    >
                      Request Consultation
                    </button>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                      <HeadphonesIcon className="w-8 h-8 mb-3" />
                      <div className="text-2xl font-black mb-1">24/7</div>
                      <div className="text-sm text-green-100">Support Available</div>
                    </div>
                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                      <Target className="w-8 h-8 mb-3" />
                      <div className="text-2xl font-black mb-1">99.5%</div>
                      <div className="text-sm text-green-100">Task Completion</div>
                    </div>
                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                      <Clock className="w-8 h-8 mb-3" />
                      <div className="text-2xl font-black mb-1">2hrs</div>
                      <div className="text-sm text-green-100">Avg Response Time</div>
                    </div>
                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                      <Star className="w-8 h-8 mb-3" />
                      <div className="text-2xl font-black mb-1">4.9/5</div>
                      <div className="text-sm text-green-100">Client Rating</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* What's Included */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {[
                  { icon: ClipboardCheck, title: 'Asset Registration', desc: 'We handle complete inventory setup' },
                  { icon: Calendar, title: 'Maintenance Coordination', desc: 'Schedule and manage all tasks' },
                  { icon: DollarSign, title: 'Expense Management', desc: 'Track and optimize all costs' },
                  { icon: FileText, title: 'Compliance Reports', desc: 'Monthly detailed reporting' },
                  { icon: PhoneCall, title: 'Vendor Management', desc: 'Coordinate with contractors' },
                  { icon: Bell, title: 'Proactive Alerts', desc: 'We notify you of critical issues' },
                  { icon: LineChart, title: 'Performance Analysis', desc: 'Quarterly strategy reviews' },
                  { icon: Shield, title: 'Insurance Liaison', desc: 'Handle claims and documentation' }
                ].map((service, idx) => {
                  const Icon = service.icon;
                  return (
                    <div key={idx} className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-all">
                      <Icon className="w-8 h-8 text-green-600 mb-3" />
                      <h4 className="font-bold text-gray-900 mb-2">{service.title}</h4>
                      <p className="text-sm text-gray-600">{service.desc}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Testimonials */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-black text-gray-900 mb-4">
              Trusted by Leading Property Owners
            </h2>
            <p className="text-xl text-gray-600">See what our clients say about our services</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { name: 'Jean Mbarga', role: 'Property Owner', property: '12 Commercial Buildings', rating: 5, text: 'Habitere reduced our maintenance costs by 35% in the first year. The DIY platform is incredibly intuitive.' },
              { name: 'Marie Ndongo', role: 'Real Estate Company', property: '50+ Properties', rating: 5, text: 'The managed service team is exceptional. They handle everything professionally, saving us countless hours.' },
              { name: 'Paul Essomba', role: 'Hotel Owner', property: 'Luxury Hotel Chain', rating: 5, text: 'Asset tracking and preventive maintenance have significantly improved our operational efficiency.' }
            ].map((testimonial, idx) => (
              <div key={idx} className="bg-gray-50 rounded-2xl p-8 border border-gray-200 hover:shadow-lg transition-all">
                <div className="flex items-center mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-gray-700 mb-6 italic">"{testimonial.text}"</p>
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center text-white font-bold text-lg mr-4">
                    {testimonial.name[0]}
                  </div>
                  <div>
                    <div className="font-bold text-gray-900">{testimonial.name}</div>
                    <div className="text-sm text-gray-600">{testimonial.role}</div>
                    <div className="text-xs text-gray-500">{testimonial.property}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Final CTA */}
      <div className="bg-gradient-to-r from-gray-900 to-gray-800 text-white py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl md:text-5xl font-black mb-6">
            Ready to Transform Your Asset Management?
          </h2>
          <p className="text-xl text-gray-300 mb-10">
            Join 500+ property owners who trust Habitere with their assets
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => handleGetStarted('diy')}
              className="bg-green-600 hover:bg-green-700 text-white px-10 py-5 rounded-xl font-bold text-xl transition-all shadow-2xl"
            >
              Start Free Trial
            </button>
            <button
              onClick={() => handleGetStarted('managed')}
              className="bg-white text-gray-900 hover:bg-gray-100 px-10 py-5 rounded-xl font-bold text-xl transition-all"
            >
              Schedule Demo
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssetManagementLanding;
