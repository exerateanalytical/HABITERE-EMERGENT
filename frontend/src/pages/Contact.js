import React, { useState } from 'react';
import { Mail, Phone, MapPin, Send, MessageSquare, Clock, AlertCircle, CheckCircle } from 'lucide-react';
import SEOHead from '../components/SEOHead';

const Contact = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [status, setStatus] = useState({ type: '', message: '' });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus({ type: '', message: '' });

    // Simulate form submission (replace with actual API call)
    setTimeout(() => {
      setStatus({
        type: 'success',
        message: 'Thank you for contacting us! We\'ll get back to you within 24 hours.'
      });
      setFormData({ name: '', email: '', subject: '', message: '' });
      setLoading(false);
    }, 1500);
  };

  const contactInfo = [
    {
      icon: Mail,
      title: 'Email Us',
      details: 'support@habitere.com',
      link: 'mailto:support@habitere.com',
      description: 'Send us an email anytime'
    },
    {
      icon: Phone,
      title: 'Call Us',
      details: '+237 6XX XXX XXX',
      link: 'tel:+237600000000',
      description: 'Mon-Fri from 8am to 6pm'
    },
    {
      icon: MapPin,
      title: 'Visit Us',
      details: 'Yaoundé, Cameroon',
      link: null,
      description: 'Come say hello at our office'
    },
    {
      icon: Clock,
      title: 'Working Hours',
      details: 'Mon - Fri: 8am - 6pm',
      link: null,
      description: 'Saturday: 9am - 3pm'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <SEOHead 
        title="Contact Habitere - Real Estate Support in Cameroon | Get Help Now"
        description="Need help finding a property in Cameroon? Contact Habitere's expert support team in Douala & Yaoundé. Email, phone, and live chat support available Mon-Sat."
        keywords="contact habitere, habitere support, real estate help cameroon, property support douala, yaoundé real estate contact, cameroon housing help"
        focusKeyword="contact habitere cameroon"
        canonicalUrl="https://habitere.com/contact"
        structuredData={{
          "@context": "https://schema.org",
          "@type": "ContactPage",
          "name": "Contact Habitere",
          "description": "Get in touch with Habitere for real estate inquiries",
          "url": "https://habitere.com/contact",
          "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+237-6XX-XXX-XXX",
            "contactType": "customer service",
            "email": "support@habitere.com",
            "areaServed": "CM",
            "availableLanguage": ["en", "fr"]
          }
        }}
      />

      {/* Hero Section */}
      <div className="bg-gradient-to-br from-blue-600 to-purple-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 md:py-20">
          <div className="text-center">
            <MessageSquare className="w-12 h-12 sm:w-16 sm:h-16 mx-auto mb-4 sm:mb-6" />
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-3 sm:mb-4">
              Get In Touch
            </h1>
            <p className="text-base sm:text-lg md:text-xl text-blue-100 max-w-2xl mx-auto">
              Have questions? We'd love to hear from you. Send us a message and we'll respond as soon as possible.
            </p>
          </div>
        </div>
      </div>

      {/* Contact Info Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-10">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {contactInfo.map((info, index) => {
            const Icon = info.icon;
            return (
              <div key={index} className="bg-white rounded-2xl shadow-xl p-4 sm:p-6 text-center">
                <Icon className="w-8 h-8 sm:w-10 sm:h-10 text-blue-600 mx-auto mb-3 sm:mb-4" />
                <h3 className="font-bold text-gray-900 mb-1 sm:mb-2 text-sm sm:text-base">{info.title}</h3>
                {info.link ? (
                  <a href={info.link} className="text-blue-600 hover:text-blue-700 font-medium text-xs sm:text-sm">
                    {info.details}
                  </a>
                ) : (
                  <p className="text-gray-900 font-medium text-xs sm:text-sm">{info.details}</p>
                )}
                <p className="text-gray-500 text-xs mt-1 sm:mt-2">{info.description}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Contact Form & Map */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 md:py-20">
        <div className="grid lg:grid-cols-2 gap-8 lg:gap-12">
          {/* Contact Form */}
          <div className="bg-white rounded-2xl shadow-xl p-6 sm:p-8">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4 sm:mb-6">Send Us a Message</h2>
            
            {status.message && (
              <div className={`mb-6 p-4 rounded-lg flex items-start ${
                status.type === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
              }`}>
                {status.type === 'success' ? (
                  <CheckCircle className="w-5 h-5 text-green-600 mr-2 flex-shrink-0 mt-0.5" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
                )}
                <p className={`text-sm ${
                  status.type === 'success' ? 'text-green-800' : 'text-red-800'
                }`}>{status.message}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="w-full px-4 py-2.5 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm sm:text-base"
                  placeholder="Your name"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full px-4 py-2.5 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm sm:text-base"
                  placeholder="your@email.com"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Subject</label>
                <input
                  type="text"
                  name="subject"
                  value={formData.subject}
                  onChange={handleChange}
                  className="w-full px-4 py-2.5 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm sm:text-base"
                  placeholder="How can we help?"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Message</label>
                <textarea
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  rows="5"
                  className="w-full px-4 py-2.5 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm sm:text-base"
                  placeholder="Tell us more about your inquiry..."
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 sm:py-4 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center text-sm sm:text-base"
              >
                {loading ? (
                  'Sending...'
                ) : (
                  <>
                    <Send className="w-4 h-4 sm:w-5 sm:h-5 mr-2" />
                    Send Message
                  </>
                )}
              </button>
            </form>
          </div>

          {/* FAQ Preview */}
          <div>
            <div className="bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl p-6 sm:p-8 text-white mb-6 sm:mb-8">
              <h3 className="text-xl sm:text-2xl font-bold mb-3 sm:mb-4">Quick Support</h3>
              <p className="text-blue-100 mb-4 sm:mb-6 text-sm sm:text-base">
                Need immediate help? Check out our FAQ section or browse these common topics:
              </p>
              <div className="space-y-2 sm:space-y-3">
                <a href="/faq" className="block bg-white/10 hover:bg-white/20 rounded-lg p-3 sm:p-4 transition-colors">
                  <p className="font-semibold text-sm sm:text-base">How do I list a property?</p>
                </a>
                <a href="/faq" className="block bg-white/10 hover:bg-white/20 rounded-lg p-3 sm:p-4 transition-colors">
                  <p className="font-semibold text-sm sm:text-base">How do I verify my account?</p>
                </a>
                <a href="/faq" className="block bg-white/10 hover:bg-white/20 rounded-lg p-3 sm:p-4 transition-colors">
                  <p className="font-semibold text-sm sm:text-base">What are the payment options?</p>
                </a>
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-xl p-6 sm:p-8">
              <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-3 sm:mb-4">Response Time</h3>
              <p className="text-gray-600 mb-4 sm:mb-6 text-sm sm:text-base">
                We typically respond to all inquiries within:
              </p>
              <div className="space-y-3 sm:space-y-4">
                <div className="flex items-center">
                  <div className="w-8 h-8 sm:w-10 sm:h-10 bg-green-100 rounded-full flex items-center justify-center mr-3 sm:mr-4 flex-shrink-0">
                    <CheckCircle className="w-4 h-4 sm:w-5 sm:h-5 text-green-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 text-sm sm:text-base">Email: 24 hours</p>
                    <p className="text-xs sm:text-sm text-gray-500">Usually much faster!</p>
                  </div>
                </div>
                <div className="flex items-center">
                  <div className="w-8 h-8 sm:w-10 sm:h-10 bg-blue-100 rounded-full flex items-center justify-center mr-3 sm:mr-4 flex-shrink-0">
                    <Phone className="w-4 h-4 sm:w-5 sm:h-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 text-sm sm:text-base">Phone: Immediate</p>
                    <p className="text-xs sm:text-sm text-gray-500">During business hours</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Contact;