import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Shield, Users, Camera, Eye, Car, Dog, Phone, CheckCircle, ArrowRight } from 'lucide-react';

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
      title: 'Security Guards',
      description: '24/7 professional armed and unarmed security personnel',
      color: 'from-green-500 to-green-600',
      href: '/security/services?type=Security Guards'
    },
    {
      icon: Camera,
      title: 'CCTV Installation',
      description: 'High-quality surveillance camera installation and monitoring',
      color: 'from-blue-500 to-blue-600',
      href: '/security/services?type=CCTV Installation'
    },
    {
      icon: Eye,
      title: 'Remote Monitoring',
      description: 'Advanced remote monitoring solutions with real-time alerts',
      color: 'from-purple-500 to-purple-600',
      href: '/security/services?type=Remote Monitoring'
    },
    {
      icon: Car,
      title: 'Patrol Units',
      description: 'Mobile patrol services for comprehensive area coverage',
      color: 'from-orange-500 to-orange-600',
      href: '/security/services?type=Patrol Units'
    },
    {
      icon: Dog,
      title: 'K9 Units',
      description: 'Trained security dogs for enhanced protection',
      color: 'from-yellow-500 to-yellow-600',
      href: '/security/services?type=K9 Units'
    },
    {
      icon: Phone,
      title: 'Emergency Response',
      description: 'Rapid emergency response teams available 24/7',
      color: 'from-red-500 to-red-600',
      href: '/security/services?type=Emergency Response'
    }
  ];

  const howItWorks = [
    { step: 1, title: 'Browse Services', description: 'Explore our range of security solutions' },
    { step: 2, title: 'Book Instantly', description: 'Schedule or hire security services immediately' },
    { step: 3, title: 'Stay Protected', description: 'Enjoy peace of mind with professional security' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div 
        className="relative bg-black text-white py-20 md:py-32"
        style={{
          backgroundImage: 'linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url(https://images.unsplash.com/photo-1552622594-9a37efeec618?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODB8MHwxfHNlYXJjaHwzfHxwcm9mZXNzaW9uYWwlMjB1bmlmb3JtJTIwc2VjdXJpdHl8ZW58MHx8fHwxNzYwNzQzMjY0fDA&ixlib=rb-4.1.0&q=85)',
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      >
        <div className="container mx-auto px-4 text-center">
          <div className="max-w-4xl mx-auto">
            <div className="inline-flex items-center bg-green-600 text-white px-4 py-2 rounded-full mb-6">
              <Shield className="w-5 h-5 mr-2" />
              <span className="font-semibold">Homeland Security by Habitere</span>
            </div>
            
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Protect What Matters Most
            </h1>
            
            <p className="text-xl md:text-2xl mb-8 text-gray-200">
              Hire trusted guards and advanced security services for your home, estate, or business.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => navigate('/security/services')}
                className="bg-green-600 hover:bg-green-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-colors flex items-center justify-center"
              >
                Book Security Now
                <ArrowRight className="ml-2 w-5 h-5" />
              </button>
              
              <button
                onClick={() => navigate('/security/apply')}
                className="bg-white hover:bg-gray-100 text-black px-8 py-4 rounded-lg font-semibold text-lg transition-colors flex items-center justify-center"
              >
                Apply to Become a Guard
                <Users className="ml-2 w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      {!loading && stats && (
        <div className="bg-green-600 text-white py-8">
          <div className="container mx-auto px-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-3xl md:text-4xl font-bold">{stats.total_services}+</div>
                <div className="text-sm md:text-base opacity-90">Security Services</div>
              </div>
              <div>
                <div className="text-3xl md:text-4xl font-bold">{stats.available_guards}+</div>
                <div className="text-sm md:text-base opacity-90">Verified Guards</div>
              </div>
              <div>
                <div className="text-3xl md:text-4xl font-bold">{stats.total_bookings}+</div>
                <div className="text-sm md:text-base opacity-90">Bookings Completed</div>
              </div>
              <div>
                <div className="text-3xl md:text-4xl font-bold">24/7</div>
                <div className="text-sm md:text-base opacity-90">Support Available</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Action Tiles */}
      <section className="py-16 container mx-auto px-4">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">Our Security Services</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((service, index) => {
            const Icon = service.icon;
            return (
              <Link
                key={index}
                to={service.href}
                className="group bg-white rounded-xl shadow-lg hover:shadow-2xl transition-all p-6 border border-gray-200 hover:border-green-500"
              >
                <div className={`w-16 h-16 rounded-lg bg-gradient-to-br ${service.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <Icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-2 group-hover:text-green-600 transition-colors">
                  {service.title}
                </h3>
                <p className="text-gray-600">{service.description}</p>
              </Link>
            );
          })}
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">How It Works</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {howItWorks.map((item, index) => (
              <div key={index} className="text-center">
                <div className="w-16 h-16 rounded-full bg-green-600 text-white flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                  {item.step}
                </div>
                <h3 className="text-xl font-bold mb-2">{item.title}</h3>
                <p className="text-gray-600">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Apply as a Guard Section */}
      <section className="py-16 bg-gradient-to-br from-green-600 to-green-700 text-white">
        <div className="container mx-auto px-4 text-center">
          <div className="max-w-3xl mx-auto">
            <Users className="w-16 h-16 mx-auto mb-6" />
            <h2 className="text-3xl md:text-4xl font-bold mb-6">Join Our Security Team</h2>
            <p className="text-xl mb-8 opacity-90">
              Are you a trained security professional? Apply now to become a certified guard with Homeland Security.
            </p>
            <button
              onClick={() => navigate('/security/apply')}
              className="bg-white text-green-600 hover:bg-gray-100 px-8 py-4 rounded-lg font-semibold text-lg transition-colors inline-flex items-center"
            >
              Apply Now
              <ArrowRight className="ml-2 w-5 h-5" />
            </button>
          </div>
        </div>
      </section>

      {/* Why Choose Us */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
            Why Choose Homeland Security by Habitere
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            {[
              { icon: CheckCircle, title: 'Verified Professionals', description: 'All guards undergo thorough background checks' },
              { icon: Shield, title: 'Trusted Platform', description: 'Integrated with Cameroon\'s leading real estate platform' },
              { icon: Phone, title: '24/7 Support', description: 'Round-the-clock customer support and emergency response' },
              { icon: Camera, title: 'Advanced Tech', description: 'Latest security technology and monitoring systems' }
            ].map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="bg-white p-6 rounded-xl shadow-lg text-center">
                  <Icon className="w-12 h-12 text-green-600 mx-auto mb-4" />
                  <h3 className="font-bold text-lg mb-2">{feature.title}</h3>
                  <p className="text-gray-600 text-sm">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Footer CTA */}
      <section className="bg-black text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Security You Can Trust. Anytime. Anywhere.
          </h2>
          <p className="text-xl mb-8 text-gray-300">
            Protect your property and loved ones with Cameroon's most trusted security platform.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate('/security/services')}
              className="bg-green-600 hover:bg-green-700 px-8 py-4 rounded-lg font-semibold text-lg transition-colors"
            >
              Hire a Guard Today
            </button>
            <button
              onClick={() => navigate('/security/apply')}
              className="bg-white hover:bg-gray-100 text-black px-8 py-4 rounded-lg font-semibold text-lg transition-colors"
            >
              Join as a Guard
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomelandSecurity;
