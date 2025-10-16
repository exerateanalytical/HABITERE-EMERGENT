import React, { useState } from 'react';
import { ChevronDown, Search, HelpCircle } from 'lucide-react';
import SEOHead from '../components/SEOHead';

const FAQ = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [openIndex, setOpenIndex] = useState(null);

  const faqs = [
    {
      category: 'Getting Started',
      questions: [
        {
          q: 'How do I create an account on Habitere?',
          a: 'Click on "Get Started" or "Sign Up" and choose to register with your email or Google account. You\'ll need to verify your email and select your role (Property Seeker, Owner, Agent, or Service Provider).'
        },
        {
          q: 'Is Habitere free to use?',
          a: 'Yes! Creating an account and browsing properties is completely free. Property owners and service providers can list their offerings for free. We may introduce premium features in the future.'
        },
        {
          q: 'What areas does Habitere cover?',
          a: 'Habitere currently covers major cities in Cameroon including Yaoundé, Douala, Bamenda, Bafoussam, Garoua, and is expanding to more regions.'
        }
      ]
    },
    {
      category: 'For Property Seekers',
      questions: [
        {
          q: 'How do I search for properties?',
          a: 'Use our search filters to narrow down properties by location, price range, property type, number of bedrooms, and more. You can also save your favorite properties for later viewing.'
        },
        {
          q: 'How do I contact a property owner?',
          a: 'On each property listing, you\'ll find options to message the owner directly through our platform, call them, or contact via WhatsApp. You can also book a viewing appointment.'
        },
        {
          q: 'Are the properties verified?',
          a: 'Yes! Properties with a "Verified" badge have been reviewed by our team. We verify ownership documents and property details to ensure authenticity.'
        },
        {
          q: 'Can I save properties to view later?',
          a: 'Yes! Click the heart icon on any property to save it to your favorites. You can access all your saved properties from your dashboard.'
        }
      ]
    },
    {
      category: 'For Property Owners & Agents',
      questions: [
        {
          q: 'How do I list a property?',
          a: 'After creating an account as a Property Owner or Agent, go to your dashboard and click "Add Property". Fill in the details, upload high-quality photos, and publish. Your listing will go live immediately.'
        },
        {
          q: 'How many photos can I upload?',
          a: 'You can upload up to 10 photos per property listing. We recommend uploading clear, well-lit photos from different angles to attract more interest.'
        },
        {
          q: 'Can I edit my property listing after publishing?',
          a: 'Yes! You can edit, pause, or delete your listings anytime from your dashboard. Simply go to "My Properties" and select the property you want to modify.'
        },
        {
          q: 'How do I get verified?',
          a: 'Upload your identification documents and property ownership documents through your profile settings. Our team will review and verify your account within 24-48 hours.'
        },
        {
          q: 'Do I pay to list properties?',
          a: 'No, listing properties is completely free. There are no hidden charges or commissions on transactions.'
        }
      ]
    },
    {
      category: 'For Service Providers',
      questions: [
        {
          q: 'What services can I offer on Habitere?',
          a: 'We welcome plumbers, electricians, carpenters, painters, bricklayers, and other home service professionals. Create your profile and showcase your services to thousands of property owners.'
        },
        {
          q: 'How do clients contact me?',
          a: 'Clients can reach you through our messaging system, phone, or WhatsApp. You\'ll receive notifications for all inquiries.'
        },
        {
          q: 'Can I showcase my previous work?',
          a: 'Yes! Add photos of your completed projects to your service listing. This helps build trust and attracts more clients.'
        },
        {
          q: 'Is there a fee to list my services?',
          a: 'No, creating a service profile and receiving client inquiries is completely free.'
        }
      ]
    },
    {
      category: 'Payments & Security',
      questions: [
        {
          q: 'How do I make payments?',
          a: 'Habitere facilitates connections but doesn\'t handle property transactions directly. All payments and agreements are made directly between buyers/tenants and sellers/landlords. Always meet in person and verify properties before making any payments.'
        },
        {
          q: 'Is my personal information safe?',
          a: 'Yes! We use industry-standard encryption to protect your data. We never share your personal information with third parties without your consent. Read our Privacy Policy for more details.'
        },
        {
          q: 'How do I report suspicious listings?',
          a: 'If you encounter any suspicious listings or users, click the "Report" button on the listing or contact our support team immediately at support@habitere.com.'
        },
        {
          q: 'What should I do if I\'m scammed?',
          a: 'If you suspect fraud, contact us immediately and report to local authorities. We recommend always meeting in person, verifying documents, and never sending money without seeing the property first.'
        }
      ]
    },
    {
      category: 'Technical Support',
      questions: [
        {
          q: 'I forgot my password. What should I do?',
          a: 'Click "Forgot Password" on the login page. Enter your email address and we\'ll send you a reset link. Follow the instructions to create a new password.'
        },
        {
          q: 'Why can\'t I upload photos?',
          a: 'Ensure your photos are in JPG, PNG, or JPEG format and under 5MB each. Try using a different browser or clearing your cache. If the problem persists, contact support.'
        },
        {
          q: 'The website is not loading properly. What should I do?',
          a: 'Try clearing your browser cache, using an updated browser, or checking your internet connection. If issues persist, contact us at support@habitere.com with details about the problem.'
        },
        {
          q: 'How do I delete my account?',
          a: 'Go to Settings > Account > Delete Account. Note that this action is irreversible and will remove all your listings and data. Alternatively, contact support for assistance.'
        }
      ]
    }
  ];

  const filteredFaqs = faqs.map(category => ({
    ...category,
    questions: category.questions.filter(faq =>
      faq.q.toLowerCase().includes(searchQuery.toLowerCase()) ||
      faq.a.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })).filter(category => category.questions.length > 0);

  const toggleQuestion = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <SEOHead 
        title="FAQ - Frequently Asked Questions | Habitere"
        description="Find answers to common questions about using Habitere. Learn how to list properties, search for homes, and connect with service providers in Cameroon."
      />

      {/* Hero Section */}
      <div className="bg-gradient-to-br from-blue-600 to-purple-600 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 md:py-20">
          <div className="text-center">
            <HelpCircle className="w-12 h-12 sm:w-16 sm:h-16 mx-auto mb-4 sm:mb-6" />
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-3 sm:mb-4">
              Frequently Asked Questions
            </h1>
            <p className="text-base sm:text-lg md:text-xl text-blue-100 mb-6 sm:mb-8">
              Find answers to common questions about Habitere
            </p>

            {/* Search */}
            <div className="max-w-2xl mx-auto">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search for answers..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 sm:py-4 rounded-full text-gray-900 focus:ring-2 focus:ring-white focus:outline-none text-sm sm:text-base"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* FAQ Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
        {filteredFaqs.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600 text-base sm:text-lg">No results found. Try a different search term.</p>
          </div>
        ) : (
          <div className="space-y-8 sm:space-y-12">
            {filteredFaqs.map((category, catIndex) => (
              <div key={catIndex}>
                <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4 sm:mb-6">{category.category}</h2>
                <div className="space-y-3 sm:space-y-4">
                  {category.questions.map((faq, qIndex) => {
                    const globalIndex = `${catIndex}-${qIndex}`;
                    const isOpen = openIndex === globalIndex;
                    
                    return (
                      <div key={qIndex} className="bg-white rounded-xl shadow-md overflow-hidden">
                        <button
                          onClick={() => toggleQuestion(globalIndex)}
                          className="w-full px-4 sm:px-6 py-4 sm:py-5 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
                        >
                          <span className="font-semibold text-gray-900 pr-4 text-sm sm:text-base">{faq.q}</span>
                          <ChevronDown className={`w-5 h-5 text-gray-500 flex-shrink-0 transition-transform ${
                            isOpen ? 'transform rotate-180' : ''
                          }`} />
                        </button>
                        {isOpen && (
                          <div className="px-4 sm:px-6 pb-4 sm:pb-5">
                            <p className="text-sm sm:text-base text-gray-600 leading-relaxed">{faq.a}</p>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Still Have Questions */}
        <div className="mt-12 sm:mt-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl p-6 sm:p-8 text-center text-white">
          <h3 className="text-xl sm:text-2xl font-bold mb-3 sm:mb-4">Still have questions?</h3>
          <p className="text-blue-100 mb-6 sm:mb-8 text-sm sm:text-base">
            Can't find what you're looking for? Our support team is here to help.
          </p>
          <a
            href="/contact"
            className="inline-block bg-white text-blue-600 px-6 sm:px-8 py-3 sm:py-4 rounded-full font-semibold hover:bg-gray-100 transition-colors text-sm sm:text-base"
          >
            Contact Support
          </a>
        </div>
      </div>
    </div>
  );
};

export default FAQ;