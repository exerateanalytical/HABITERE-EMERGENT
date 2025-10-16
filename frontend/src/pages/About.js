import React from 'react';
import { Link } from 'react-router-dom';
import { Home, Users, Shield, TrendingUp, Heart, Award } from 'lucide-react';
import SEOHead from '../components/SEOHead';

const About = () => {
  const stats = [
    { label: 'Properties Listed', value: '1,000+', icon: Home },
    { label: 'Happy Users', value: '5,000+', icon: Users },
    { label: 'Verified Agents', value: '200+', icon: Shield },
    { label: 'Success Stories', value: '850+', icon: Heart }
  ];

  const values = [
    {
      icon: Shield,
      title: 'Trust & Transparency',
      description: 'We verify all property listings and professionals to ensure your safety and peace of mind.'
    },
    {
      icon: Heart,
      title: 'Customer First',
      description: 'Your satisfaction is our priority. We provide exceptional support throughout your journey.'
    },
    {
      icon: TrendingUp,
      title: 'Innovation',
      description: 'We leverage technology to make property transactions seamless and efficient.'
    },
    {
      icon: Award,
      title: 'Excellence',
      description: 'We maintain the highest standards in service quality and professionalism.'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <SEOHead 
        title="About Habitere - Leading Real Estate Platform in Cameroon"
        description="Learn about Habitere's mission to revolutionize real estate in Cameroon. Discover how we connect property seekers with their dream homes."
      />

      {/* Hero Section */}
      <div className="bg-gradient-to-br from-blue-600 to-purple-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20 md:py-24">
          <div className="text-center">
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-4 sm:mb-6">
              Transforming Real Estate in Cameroon
            </h1>
            <p className="text-lg sm:text-xl md:text-2xl text-blue-100 max-w-3xl mx-auto">
              Connecting people with their perfect homes and trusted professionals across Cameroon
            </p>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-10">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div key={index} className="bg-white rounded-2xl shadow-xl p-4 sm:p-6 text-center">
                <Icon className="w-8 h-8 sm:w-10 sm:h-10 text-blue-600 mx-auto mb-2 sm:mb-3" />
                <div className="text-2xl sm:text-3xl font-bold text-gray-900 mb-1">{stat.value}</div>
                <div className="text-xs sm:text-sm text-gray-600">{stat.label}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Our Story */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 md:py-20">
        <div className="grid md:grid-cols-2 gap-8 md:gap-12 items-center">
          <div>
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 mb-4 sm:mb-6">
              Our Story
            </h2>
            <div className="space-y-4 text-gray-600 text-sm sm:text-base">
              <p>
                Founded in 2024, Habitere emerged from a simple observation: finding quality housing and reliable property services in Cameroon was unnecessarily difficult. We knew there had to be a better way.
              </p>
              <p>
                Today, Habitere is Cameroon's fastest-growing property platform, serving thousands of users across Yaoundé, Douala, and beyond. We've simplified the entire process—from searching for properties to connecting with trusted professionals.
              </p>
              <p>
                Our platform brings together property seekers, owners, agents, and service professionals in one trusted ecosystem. Whether you're looking for your dream home, listing a property, or offering professional services, Habitere is your partner in success.
              </p>
            </div>
          </div>
          <div className="bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl p-1">
            <img
              src="https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800"
              alt="Modern Cameroon real estate"
              className="w-full h-64 sm:h-80 md:h-96 object-cover rounded-xl"
            />
          </div>
        </div>
      </div>

      {/* Our Values */}
      <div className="bg-white py-12 sm:py-16 md:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8 sm:mb-12">
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 mb-3 sm:mb-4">
              Our Core Values
            </h2>
            <p className="text-base sm:text-lg text-gray-600 max-w-2xl mx-auto">
              These principles guide everything we do at Habitere
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-8">
            {values.map((value, index) => {
              const Icon = value.icon;
              return (
                <div key={index} className="text-center">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Icon className="w-8 h-8 text-blue-600" />
                  </div>
                  <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-2">{value.title}</h3>
                  <p className="text-sm sm:text-base text-gray-600">{value.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Team Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 md:py-20">
        <div className="text-center mb-8 sm:mb-12">
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 mb-3 sm:mb-4">
            Why Choose Habitere?
          </h2>
          <p className="text-base sm:text-lg text-gray-600 max-w-2xl mx-auto">
            We're more than just a platform—we're your trusted partner in property matters
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 sm:gap-8">
          <div className="bg-white p-6 sm:p-8 rounded-2xl shadow-lg">
            <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-3">Verified Listings</h3>
            <p className="text-sm sm:text-base text-gray-600">
              Every property is verified by our team to ensure authenticity and quality. No fake listings, no surprises.
            </p>
          </div>

          <div className="bg-white p-6 sm:p-8 rounded-2xl shadow-lg">
            <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-3">Professional Network</h3>
            <p className="text-sm sm:text-base text-gray-600">
              Access verified plumbers, electricians, agents, and more. Quality service providers at your fingertips.
            </p>
          </div>

          <div className="bg-white p-6 sm:p-8 rounded-2xl shadow-lg">
            <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-3">Local Expertise</h3>
            <p className="text-sm sm:text-base text-gray-600">
              Built for Cameroon, by Cameroonians. We understand the local market and your unique needs.
            </p>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-br from-blue-600 to-purple-600 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 text-center">
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-4 sm:mb-6">
            Join Thousands of Happy Users
          </h2>
          <p className="text-base sm:text-lg md:text-xl text-blue-100 mb-6 sm:mb-8">
            Start your property journey with Habitere today
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/auth/register"
              className="bg-white text-blue-600 px-6 sm:px-8 py-3 sm:py-4 rounded-full font-semibold hover:bg-gray-100 transition-colors text-sm sm:text-base"
            >
              Get Started Free
            </Link>
            <Link
              to="/properties"
              className="border-2 border-white text-white px-6 sm:px-8 py-3 sm:py-4 rounded-full font-semibold hover:bg-white hover:text-blue-600 transition-colors text-sm sm:text-base"
            >
              Browse Properties
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;