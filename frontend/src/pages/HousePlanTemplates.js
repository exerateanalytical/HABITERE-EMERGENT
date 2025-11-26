import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import {
  Home, Building, Layers, Users, ArrowRight, CheckCircle,
  FileText, TrendingUp, Star, Zap
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const HousePlanTemplates = () => {
  const navigate = useNavigate();
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/house-plans/templates`);
      setTemplates(response.data.templates);
    } catch (error) {
      console.error('Error fetching templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUseTemplate = (templateId) => {
    navigate(`/house-plans/builder?template=${templateId}`);
  };

  const getTypeColor = (type) => {
    const colors = {
      'bungalow': 'bg-green-100 text-green-800',
      'duplex': 'bg-blue-100 text-blue-800',
      'apartment': 'bg-purple-100 text-purple-800',
      'multi_story': 'bg-orange-100 text-orange-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-600 to-blue-600 rounded-xl shadow-lg p-8 mb-8 text-white">
          <h1 className="text-4xl font-black mb-3 flex items-center">
            <Building className="w-10 h-10 mr-3" />
            House Plan Templates
          </h1>
          <p className="text-lg text-green-50 mb-6">
            Choose from our professionally designed templates and customize to your needs
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white/10 backdrop-blur rounded-lg p-4">
              <CheckCircle className="w-8 h-8 mb-2" />
              <div className="font-bold text-lg">{templates.length} Templates</div>
              <div className="text-sm text-green-100">Ready to use</div>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-lg p-4">
              <Zap className="w-8 h-8 mb-2" />
              <div className="font-bold text-lg">Instant Results</div>
              <div className="text-sm text-green-100">Get BOQ immediately</div>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-lg p-4">
              <FileText className="w-8 h-8 mb-2" />
              <div className="font-bold text-lg">Fully Customizable</div>
              <div className="text-sm text-green-100">Modify any room</div>
            </div>
          </div>
        </div>

        {/* Templates Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading templates...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {templates.map((template) => (
              <div
                key={template.id}
                className="bg-white rounded-xl shadow-lg overflow-hidden border-2 border-gray-100 hover:border-green-300 transition-all hover:shadow-xl"
              >
                {/* Template Header */}
                <div className="bg-gradient-to-br from-green-500 to-blue-500 p-6 text-white">
                  <div className="flex items-start justify-between mb-3">
                    <Home className="w-12 h-12" />
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${getTypeColor(template.house_type)}`}>
                      {template.house_type.toUpperCase()}
                    </span>
                  </div>
                  <h3 className="text-xl font-bold mb-2">{template.name}</h3>
                  <p className="text-sm text-green-50">{template.description}</p>
                </div>

                {/* Template Stats */}
                <div className="p-6">
                  <div className="grid grid-cols-3 gap-3 mb-6">
                    <div className="bg-gray-50 rounded-lg p-3 text-center">
                      <Layers className="w-6 h-6 text-green-600 mx-auto mb-1" />
                      <div className="text-lg font-bold text-gray-900">{template.floors_count}</div>
                      <div className="text-xs text-gray-600">Floors</div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3 text-center">
                      <Building className="w-6 h-6 text-blue-600 mx-auto mb-1" />
                      <div className="text-lg font-bold text-gray-900">{template.total_rooms}</div>
                      <div className="text-xs text-gray-600">Rooms</div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3 text-center">
                      <TrendingUp className="w-6 h-6 text-purple-600 mx-auto mb-1" />
                      <div className="text-lg font-bold text-gray-900">{template.total_area}m²</div>
                      <div className="text-xs text-gray-600">Area</div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleUseTemplate(template.id)}
                      className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-3 rounded-lg font-bold flex items-center justify-center"
                    >
                      Use Template
                      <ArrowRight className="w-5 h-5 ml-2" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Custom Plan CTA */}
        <div className="mt-12 bg-white rounded-xl shadow-lg p-8 border-2 border-green-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                Need a Custom Design?
              </h3>
              <p className="text-gray-600">
                Create your own floor plan from scratch with our easy-to-use builder
              </p>
            </div>
            <Link
              to="/house-plans/builder"
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg font-bold flex items-center whitespace-nowrap"
            >
              <FileText className="w-5 h-5 mr-2" />
              Custom Builder
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HousePlanTemplates;
