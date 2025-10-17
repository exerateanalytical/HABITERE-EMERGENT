import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Building, Mail, Phone, MapPin, Facebook, Twitter, Instagram, Linkedin, ChevronDown, ChevronUp } from 'lucide-react';

const FooterMobile = () => {
  const currentYear = new Date().getFullYear();
  const [openSection, setOpenSection] = useState(null);

  const toggleSection = (section) => {
    setOpenSection(openSection === section ? null : section);
  };

  const footerSections = [
    {
      id: 'company',
      title: 'Company',
      links: [
        { name: 'About Us', path: '/about' },
        { name: 'Contact', path: '/contact' },
        { name: 'Help Center', path: '/help-center' }
      ]
    },
    {
      id: 'resources',
      title: 'Resources',
      links: [
        { name: 'Properties', path: '/properties' },
        { name: 'Services', path: '/services' },
        { name: 'FAQ', path: '/faq' }
      ]
    },
    {
      id: 'legal',
      title: 'Legal',
      links: [
        { name: 'Privacy Policy', path: '/privacy' },
        { name: 'Terms & Conditions', path: '/terms' }
      ]
    }
  ];

  const socialLinks = [
    { name: 'Facebook', icon: Facebook, url: '#' },
    { name: 'Twitter', icon: Twitter, url: '#' },
    { name: 'Instagram', icon: Instagram, url: '#' },
    { name: 'LinkedIn', icon: Linkedin, url: '#' }
  ];

  return (
    <footer className="bg-gray-900 text-gray-300 safe-area-bottom">
      <div className="max-w-7xl mx-auto px-4 py-8 sm:py-12">
        {/* Brand Section */}
        <div className="mb-8">
          <Link to="/" className="flex items-center mb-4">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Building className="w-6 h-6 text-white" />
            </div>
            <span className="ml-3 text-2xl font-bold text-white">Habitere</span>
          </Link>
          <p className="text-gray-400 text-sm leading-relaxed">
            Cameroon's leading platform for real estate and home services.
          </p>
        </div>

        {/* Accordion Sections - Mobile Only */}
        <div className="md:hidden space-y-2 mb-8">
          {footerSections.map((section) => (
            <div key={section.id} className="border-b border-gray-800">
              <button
                onClick={() => toggleSection(section.id)}
                className="w-full flex items-center justify-between py-4 text-left text-white font-semibold touch-manipulation min-h-[48px]"
                aria-expanded={openSection === section.id}
                aria-controls={`footer-${section.id}`}
              >
                <span>{section.title}</span>
                {openSection === section.id ? (
                  <ChevronUp className="w-5 h-5" />
                ) : (
                  <ChevronDown className="w-5 h-5" />
                )}
              </button>
              
              <div
                id={`footer-${section.id}`}
                className={`overflow-hidden transition-all duration-300 ${
                  openSection === section.id ? 'max-h-96 pb-4' : 'max-h-0'
                }`}
              >
                <ul className="space-y-3">
                  {section.links.map((link) => (
                    <li key={link.path}>
                      <Link
                        to={link.path}
                        className="block text-gray-400 hover:text-white active:text-blue-400 transition-colors py-2 min-h-[48px] flex items-center touch-manipulation"
                      >
                        {link.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>

        {/* Desktop Grid - Hidden on Mobile */}
        <div className="hidden md:grid md:grid-cols-3 gap-8 mb-8">
          {footerSections.map((section) => (
            <div key={section.id}>
              <h3 className="text-white font-bold mb-4">{section.title}</h3>
              <ul className="space-y-3">
                {section.links.map((link) => (
                  <li key={link.path}>
                    <Link
                      to={link.path}
                      className="text-gray-400 hover:text-white transition-colors"
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Contact Info */}
        <div className="mb-8 space-y-3">
          <div className="flex items-center text-sm">
            <Mail className="w-4 h-4 mr-3 text-blue-500" />
            <span>support@habitere.com</span>
          </div>
          <div className="flex items-center text-sm">
            <Phone className="w-4 h-4 mr-3 text-blue-500" />
            <span>+237 6XX XXX XXX</span>
          </div>
          <div className="flex items-center text-sm">
            <MapPin className="w-4 h-4 mr-3 text-blue-500" />
            <span>Douala, Cameroon</span>
          </div>
        </div>

        {/* Social Links */}
        <div className="flex gap-3 mb-8">
          {socialLinks.map((social) => {
            const Icon = social.icon;
            return (
              <a
                key={social.name}
                href={social.url}
                className="w-10 h-10 bg-gray-800 hover:bg-blue-600 active:bg-blue-700 rounded-full flex items-center justify-center transition-all duration-200 touch-manipulation transform active:scale-95"
                aria-label={social.name}
              >
                <Icon className="w-5 h-5" />
              </a>
            );
          })}
        </div>

        {/* Copyright */}
        <div className="pt-8 border-t border-gray-800 text-center text-sm text-gray-500">
          <p>&copy; {currentYear} Habitere. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default FooterMobile;
