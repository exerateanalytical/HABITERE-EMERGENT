import React from 'react';
import { Shield, Lock, Eye, UserCheck, Database, Globe } from 'lucide-react';
import SEOHead from '../components/SEOHead';

const Privacy = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <SEOHead 
        title="Privacy Policy - How Habitere Protects Your Data | Cameroon Real Estate Privacy"
        description="Habitere's comprehensive privacy policy for users in Cameroon. Learn how we collect, use, and protect your personal data on Africa's leading real estate platform. GDPR compliant."
        keywords="habitere privacy policy, data protection cameroon, real estate privacy, gdpr cameroon, personal data security, privacy policy douala"
        focusKeyword="habitere privacy policy"
        canonicalUrl="https://habitere.com/privacy"
      />

      <div className="bg-gradient-to-br from-blue-600 to-purple-600 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
          <Shield className="w-12 h-12 sm:w-16 sm:h-16 mx-auto mb-4" />
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-4 text-center">Privacy Policy</h1>
          <p className="text-blue-100 text-center">Last updated: January 2025</p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
        <div className="bg-white rounded-2xl shadow-xl p-6 sm:p-8 md:p-10 space-y-8">
          <section>
            <div className="flex items-center mb-4">
              <Lock className="w-6 h-6 text-blue-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">Information We Collect</h2>
            </div>
            <p className="text-gray-600 mb-4">
              We collect information you provide directly to us when you create an account, list properties, or use our services:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-gray-600">
              <li><strong>Account Information:</strong> Name, email address, phone number, profile picture</li>
              <li><strong>Property Listings:</strong> Property details, photos, location, pricing information</li>
              <li><strong>Communications:</strong> Messages sent through our platform, support inquiries</li>
              <li><strong>Usage Data:</strong> Pages visited, features used, search queries, device information</li>
            </ul>
          </section>

          <section>
            <div className="flex items-center mb-4">
              <Database className="w-6 h-6 text-blue-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">How We Use Your Information</h2>
            </div>
            <p className="text-gray-600 mb-4">We use your information to:</p>
            <ul className="list-disc pl-6 space-y-2 text-gray-600">
              <li>Provide, maintain, and improve our services</li>
              <li>Process and complete transactions</li>
              <li>Send you technical notices, updates, and support messages</li>
              <li>Respond to your comments and questions</li>
              <li>Prevent fraud and enhance security</li>
              <li>Analyze usage patterns to improve user experience</li>
            </ul>
          </section>

          <section>
            <div className="flex items-center mb-4">
              <UserCheck className="w-6 h-6 text-blue-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">Information Sharing</h2>
            </div>
            <p className="text-gray-600 mb-4">
              We do not sell your personal information. We may share your information only in the following circumstances:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-gray-600">
              <li><strong>With Your Consent:</strong> When you authorize us to share specific information</li>
              <li><strong>Public Listings:</strong> Property and service listings you create are visible to all users</li>
              <li><strong>Legal Requirements:</strong> When required by law or to protect our legal rights</li>
              <li><strong>Service Providers:</strong> Third-party services that help us operate (email, hosting, analytics)</li>
            </ul>
          </section>

          <section>
            <div className="flex items-center mb-4">
              <Eye className="w-6 h-6 text-blue-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">Your Rights and Choices</h2>
            </div>
            <p className="text-gray-600 mb-4">You have the right to:</p>
            <ul className="list-disc pl-6 space-y-2 text-gray-600">
              <li><strong>Access:</strong> Request a copy of your personal data</li>
              <li><strong>Correction:</strong> Update or correct inaccurate information</li>
              <li><strong>Deletion:</strong> Request deletion of your account and data</li>
              <li><strong>Opt-Out:</strong> Unsubscribe from marketing emails</li>
              <li><strong>Data Portability:</strong> Request your data in a portable format</li>
            </ul>
          </section>

          <section>
            <div className="flex items-center mb-4">
              <Shield className="w-6 h-6 text-blue-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">Data Security</h2>
            </div>
            <p className="text-gray-600">
              We implement appropriate technical and organizational measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction. However, no internet transmission is completely secure, and we cannot guarantee absolute security.
            </p>
          </section>

          <section>
            <div className="flex items-center mb-4">
              <Globe className="w-6 h-6 text-blue-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">Cookies and Tracking</h2>
            </div>
            <p className="text-gray-600">
              We use cookies and similar tracking technologies to collect usage data and improve your experience. You can control cookie preferences through your browser settings.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Contact Us</h2>
            <p className="text-gray-600">
              If you have questions about this Privacy Policy or how we handle your data, please contact us at:
            </p>
            <p className="text-blue-600 font-semibold mt-2">privacy@habitere.com</p>
          </section>
        </div>
      </div>
    </div>
  );
};

export default Privacy;
