import React from 'react';
import { FileText, AlertTriangle, CheckCircle, Scale } from 'lucide-react';
import SEOHead from '../components/SEOHead';

const Terms = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <SEOHead 
        title="Terms & Conditions | Habitere"
        description="Read Habitere's terms and conditions. Understand your rights and responsibilities when using our platform."
      />

      <div className="bg-gradient-to-br from-blue-600 to-purple-600 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
          <FileText className="w-12 h-12 sm:w-16 sm:h-16 mx-auto mb-4" />
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-4 text-center">Terms & Conditions</h1>
          <p className="text-blue-100 text-center">Last updated: January 2025</p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
        <div className="bg-white rounded-2xl shadow-xl p-6 sm:p-8 md:p-10 space-y-8">
          
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">1. Acceptance of Terms</h2>
            <p className="text-gray-600">
              By accessing and using Habitere ("the Platform"), you accept and agree to be bound by these Terms and Conditions. If you do not agree to these terms, please do not use our services.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">2. User Accounts</h2>
            <div className="space-y-3 text-gray-600">
              <p><strong>2.1 Registration:</strong> You must provide accurate, current, and complete information during registration.</p>
              <p><strong>2.2 Account Security:</strong> You are responsible for maintaining the confidentiality of your account credentials.</p>
              <p><strong>2.3 Account Types:</strong> Users can register as Property Seekers, Property Owners, Real Estate Agents, or Service Providers.</p>
              <p><strong>2.4 Age Requirement:</strong> You must be at least 18 years old to create an account.</p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">3. Property Listings</h2>
            <div className="space-y-3 text-gray-600">
              <p><strong>3.1 Accuracy:</strong> Property owners and agents must provide accurate, truthful information about properties.</p>
              <p><strong>3.2 Ownership:</strong> You must have legal authority to list any property on the Platform.</p>
              <p><strong>3.3 Photos:</strong> All photos must be genuine representations of the property. Stock photos are prohibited.</p>
              <p><strong>3.4 Pricing:</strong> Listed prices must be accurate and current.</p>
              <p><strong>3.5 Removal Rights:</strong> Habitere reserves the right to remove any listing that violates these terms.</p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">4. User Conduct</h2>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
              <div className="flex items-start">
                <AlertTriangle className="w-5 h-5 text-yellow-600 mr-2 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-yellow-800">Users agree NOT to engage in prohibited activities</p>
              </div>
            </div>
            <ul className="list-disc pl-6 space-y-2 text-gray-600">
              <li>Post false, misleading, or fraudulent information</li>
              <li>Impersonate another person or entity</li>
              <li>Harass, abuse, or harm other users</li>
              <li>Upload malicious software or viruses</li>
              <li>Scrape or copy content without permission</li>
              <li>Attempt to circumvent security measures</li>
              <li>Use the Platform for illegal purposes</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">5. Transactions</h2>
            <div className="space-y-3 text-gray-600">
              <p><strong>5.1 Platform Role:</strong> Habitere is a marketplace platform that connects users. We do not participate in actual property transactions.</p>
              <p><strong>5.2 User Responsibility:</strong> All agreements, payments, and contracts are between buyers/tenants and sellers/landlords.</p>
              <p><strong>5.3 Verification:</strong> Users must verify property details, ownership documents, and meet in person before transactions.</p>
              <p><strong>5.4 No Liability:</strong> Habitere is not liable for disputes, losses, or damages arising from transactions.</p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Service Provider Terms</h2>
            <div className="space-y-3 text-gray-600">
              <p><strong>6.1 Professional Services:</strong> Service providers must be qualified and licensed where required by law.</p>
              <p><strong>6.2 Quality Standards:</strong> Services must be performed professionally and meet agreed specifications.</p>
              <p><strong>6.3 Direct Contracts:</strong> Agreements for services are directly between clients and service providers.</p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Intellectual Property</h2>
            <div className="space-y-3 text-gray-600">
              <p><strong>7.1 Platform Content:</strong> All content on Habitere (logo, design, text) is owned by Habitere or licensed to us.</p>
              <p><strong>7.2 User Content:</strong> You retain ownership of content you post but grant us a license to use it on the Platform.</p>
              <p><strong>7.3 Restrictions:</strong> You may not reproduce, distribute, or create derivative works without permission.</p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">8. Disclaimers</h2>
            <div className="bg-gray-100 border border-gray-300 rounded-lg p-4">
              <p className="text-gray-700 text-sm">
                THE PLATFORM IS PROVIDED "AS IS" WITHOUT WARRANTIES OF ANY KIND. HABITERE DOES NOT GUARANTEE ACCURACY, COMPLETENESS, OR RELIABILITY OF USER-GENERATED CONTENT. USE AT YOUR OWN RISK.
              </p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">9. Limitation of Liability</h2>
            <p className="text-gray-600">
              To the maximum extent permitted by law, Habitere shall not be liable for any indirect, incidental, special, or consequential damages arising from your use of the Platform.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">10. Termination</h2>
            <div className="space-y-3 text-gray-600">
              <p><strong>10.1 By You:</strong> You may terminate your account at any time through account settings.</p>
              <p><strong>10.2 By Us:</strong> We may suspend or terminate accounts that violate these terms without notice.</p>
              <p><strong>10.3 Effect:</strong> Upon termination, your right to use the Platform ceases immediately.</p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">11. Governing Law</h2>
            <p className="text-gray-600">
              These Terms are governed by the laws of the Republic of Cameroon. Any disputes shall be resolved in the courts of Cameroon.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">12. Changes to Terms</h2>
            <p className="text-gray-600">
              We reserve the right to modify these Terms at any time. Changes will be effective immediately upon posting. Your continued use constitutes acceptance of the modified terms.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">13. Contact</h2>
            <p className="text-gray-600">
              For questions about these Terms, contact us at:
            </p>
            <p className="text-blue-600 font-semibold mt-2">legal@habitere.com</p>
          </section>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-8">
            <div className="flex items-start">
              <CheckCircle className="w-6 h-6 text-blue-600 mr-3 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-blue-900 mb-2">Agreement</p>
                <p className="text-sm text-blue-800">
                  By using Habitere, you acknowledge that you have read, understood, and agree to be bound by these Terms and Conditions.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Terms;
