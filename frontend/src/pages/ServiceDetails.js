import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { 
  MapPin, 
  Star, 
  Users, 
  MessageSquare, 
  Calendar,
  ChevronLeft,
  ChevronRight,
  Shield,
  Eye,
  ArrowLeft,
  Phone,
  Award,
  CheckCircle,
  Clock
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ServiceDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [service, setService] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  useEffect(() => {
    if (id) {
      fetchService();
    }
  }, [id]);

  const fetchService = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/services/${id}`);
      setService(response.data);
    } catch (err) {
      console.error('Error fetching service:', err);
      setError('Service not found');
    } finally {
      setLoading(false);
    }
  };

  const handleBooking = () => {
    if (!user) {
      navigate('/auth/callback');
      return;
    }
    navigate(`/booking/service/${id}`);
  };

  const handleMessage = () => {
    if (!user) {
      navigate('/auth/callback');
      return;
    }
    navigate('/messages', { state: { recipientId: service.provider_id } });
  };

  const images = service?.images?.length > 0 
    ? service.images 
    : ['https://images.unsplash.com/photo-1505798577917-a65157d3320a'];

  const nextImage = () => {
    setCurrentImageIndex((prev) => (prev + 1) % images.length);
  };

  const prevImage = () => {
    setCurrentImageIndex((prev) => (prev - 1 + images.length) % images.length);
  };

  // Mock reviews data
  const reviews = [
    {
      id: 1,
      reviewer: 'Marie Ngozi',
      rating: 5,
      comment: 'Excellent work! Very professional and completed the project on time.',
      date: '2024-01-15',
      avatar: 'https://via.placeholder.com/40'
    },
    {
      id: 2,
      reviewer: 'Jean Baptiste',
      rating: 5,
      comment: 'Highly recommend! Great quality work and fair pricing.',
      date: '2024-01-10',
      avatar: 'https://via.placeholder.com/40'
    },
    {
      id: 3,
      reviewer: 'Sarah Mballa',
      rating: 4,
      comment: 'Good service, would hire again.',
      date: '2024-01-05',
      avatar: 'https://via.placeholder.com/40'
    }
  ];

  const stats = {
    totalProjects: 15,
    rating: 4.8,
    reviewCount: 24,
    responseTime: '< 2 hours'
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-pulse">
            <div className="h-96 bg-gray-300 rounded-xl mb-8"></div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="space-y-4">
                <div className="h-8 bg-gray-300 rounded w-3/4"></div>
                <div className="h-4 bg-gray-300 rounded w-1/2"></div>
                <div className="space-y-2">
                  <div className="h-4 bg-gray-300 rounded"></div>
                  <div className="h-4 bg-gray-300 rounded"></div>
                  <div className="h-4 bg-gray-300 rounded w-5/6"></div>
                </div>
              </div>
              <div className="h-64 bg-gray-300 rounded-xl"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !service) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Service Not Found</h2>
          <p className="text-gray-600 mb-8">The service you're looking for doesn't exist or has been removed.</p>
          <Link to="/services" className="btn-primary">
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Services
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="service-details">
      {/* Back button */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
            data-testid="back-btn"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Services
          </button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Image Gallery */}
        <div className="relative mb-8">
          <div className="h-96 md:h-[500px] rounded-xl overflow-hidden bg-gray-200">
            <img
              src={images[currentImageIndex]}
              alt={service.title}
              className="w-full h-full object-cover"
              data-testid="service-image"
            />
            
            {/* Image navigation */}
            {images.length > 1 && (
              <>
                <button
                  onClick={prevImage}
                  className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-white bg-opacity-80 hover:bg-opacity-100 rounded-full p-3 shadow-lg transition-all"
                  data-testid="prev-image-btn"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <button
                  onClick={nextImage}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-white bg-opacity-80 hover:bg-opacity-100 rounded-full p-3 shadow-lg transition-all"
                  data-testid="next-image-btn"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>

                {/* Image indicators */}
                <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
                  {images.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => setCurrentImageIndex(index)}
                      className={`w-3 h-3 rounded-full transition-colors ${
                        index === currentImageIndex ? 'bg-white' : 'bg-white bg-opacity-50'
                      }`}
                    />
                  ))}
                </div>
              </>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Service Details */}
          <div className="lg:col-span-2 space-y-8">
            {/* Header */}
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <span className="badge badge-primary capitalize">
                  {service.category.replace('_', ' ')}
                </span>
                {service.verified && (
                  <span className="badge badge-success flex items-center">
                    <Shield className="w-3 h-3 mr-1" />
                    Verified
                  </span>
                )}
                {service.available && (
                  <span className="badge badge-success flex items-center">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Available
                  </span>
                )}
              </div>

              <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
                {service.title}
              </h1>

              <div className="flex items-center text-gray-600 mb-4">
                <MapPin className="w-5 h-5 mr-2" />
                {service.location}
              </div>

              {service.price_range && (
                <div className="text-2xl font-bold text-blue-600 mb-4">
                  {service.price_range}
                </div>
              )}

              {/* Stats */}
              <div className="flex items-center space-x-6 text-sm">
                <div className="flex items-center">
                  <Star className="w-5 h-5 text-yellow-400 fill-current mr-1" />
                  <span className="font-semibold">{stats.rating}</span>
                  <span className="text-gray-500 ml-1">({stats.reviewCount} reviews)</span>
                </div>
                <div className="flex items-center text-gray-600">
                  <Users className="w-5 h-5 mr-1" />
                  <span>{stats.totalProjects} projects completed</span>
                </div>
                <div className="flex items-center text-gray-600">
                  <Clock className="w-5 h-5 mr-1" />
                  <span>Responds in {stats.responseTime}</span>
                </div>
              </div>
            </div>

            {/* Description */}
            <div className="card">
              <div className="card-body">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">About This Service</h3>
                <p className="text-gray-600 leading-relaxed whitespace-pre-wrap">
                  {service.description}
                </p>
              </div>
            </div>

            {/* Portfolio */}
            {images.length > 1 && (
              <div className="card">
                <div className="card-body">
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">
                    Portfolio ({images.length} photos)
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {images.map((image, index) => (
                      <button
                        key={index}
                        onClick={() => setCurrentImageIndex(index)}
                        className={`relative h-32 rounded-lg overflow-hidden border-2 transition-colors ${
                          index === currentImageIndex ? 'border-blue-500' : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <img
                          src={image}
                          alt={`Portfolio ${index + 1}`}
                          className="w-full h-full object-cover"
                        />
                        {index === currentImageIndex && (
                          <div className="absolute inset-0 bg-blue-500 bg-opacity-20 flex items-center justify-center">
                            <Eye className="w-6 h-6 text-blue-600" />
                          </div>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Reviews */}
            <div className="card">
              <div className="card-body">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-semibold text-gray-900">
                    Reviews ({reviews.length})
                  </h3>
                  <div className="flex items-center">
                    <Star className="w-5 h-5 text-yellow-400 fill-current mr-1" />
                    <span className="font-semibold">{stats.rating}</span>
                    <span className="text-gray-500 ml-1">average</span>
                  </div>
                </div>

                <div className="space-y-6">
                  {reviews.map((review) => (
                    <div key={review.id} className="border-b border-gray-100 last:border-b-0 pb-6 last:pb-0">
                      <div className="flex items-start space-x-4">
                        <img
                          src={review.avatar}
                          alt={review.reviewer}
                          className="w-12 h-12 rounded-full object-cover"
                        />
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <h4 className="font-semibold text-gray-900">{review.reviewer}</h4>
                            <div className="flex items-center">
                              {[...Array(5)].map((_, i) => (
                                <Star 
                                  key={i} 
                                  className={`w-4 h-4 ${
                                    i < review.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
                                  }`} 
                                />
                              ))}
                            </div>
                            <span className="text-sm text-gray-500">
                              {new Date(review.date).toLocaleDateString()}
                            </span>
                          </div>
                          <p className="text-gray-600">{review.comment}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Contact Card */}
          <div className="lg:col-span-1">
            <div className="card sticky top-8">
              <div className="card-body">
                {/* Provider info */}
                <div className="text-center mb-6">
                  <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl font-bold text-blue-600">
                      {service.title?.[0]?.toUpperCase()}
                    </span>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">Service Provider</h3>
                  <div className="flex items-center justify-center text-sm text-gray-500 mt-1">
                    <Star className="w-4 h-4 text-yellow-400 fill-current mr-1" />
                    {stats.rating} ({stats.reviewCount} reviews)
                  </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900">{stats.totalProjects}</div>
                    <div className="text-xs text-gray-500">Projects</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900">{stats.responseTime}</div>
                    <div className="text-xs text-gray-500">Response</div>
                  </div>
                </div>

                {user ? (
                  <div className="space-y-3">
                    <button
                      onClick={handleBooking}
                      className="btn-primary w-full justify-center"
                      data-testid="book-service-btn"
                    >
                      <Calendar className="w-5 h-5 mr-2" />
                      Book Service
                    </button>

                    <button
                      onClick={handleMessage}
                      className="btn-secondary w-full justify-center"
                      data-testid="message-provider-btn"
                    >
                      <MessageSquare className="w-5 h-5 mr-2" />
                      Send Message
                    </button>

                    <button className="btn-outline w-full justify-center">
                      <Phone className="w-5 h-5 mr-2" />
                      Call Provider
                    </button>
                  </div>
                ) : (
                  <div className="text-center">
                    <p className="text-gray-600 mb-4">
                      Sign in to book this service or contact the provider
                    </p>
                    <Link to="/auth/callback" className="btn-primary w-full justify-center">
                      Sign In to Contact
                    </Link>
                  </div>
                )}

                {/* Badges */}
                <div className="border-t border-gray-200 mt-6 pt-6">
                  <div className="space-y-3">
                    <div className="flex items-center text-sm text-gray-600">
                      <Shield className="w-4 h-4 text-green-500 mr-2" />
                      Identity Verified
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <Award className="w-4 h-4 text-blue-500 mr-2" />
                      Top Rated Professional
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                      Available for New Projects
                    </div>
                  </div>
                </div>

                {/* Safety note */}
                <div className="border-t border-gray-200 mt-6 pt-6">
                  <div className="flex items-start space-x-3">
                    <Shield className="w-5 h-5 text-green-500 mt-0.5" />
                    <div className="text-sm text-gray-600">
                      <p className="font-medium text-gray-900 mb-1">Safe hiring practices</p>
                      <p>Always discuss project details and pricing before starting work.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Similar Services */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Similar Services</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((index) => (
              <div key={index} className="card group">
                <div className="relative overflow-hidden">
                  <img
                    src={`https://images.unsplash.com/photo-150579857${index}-a65157d3320a`}
                    alt={`Similar service ${index}`}
                    className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute top-3 left-3">
                    <span className="badge badge-primary">{service.category}</span>
                  </div>
                </div>
                <div className="card-body">
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Similar {service.category} Service {index}
                  </h3>
                  <div className="flex items-center text-gray-500 text-sm mb-3">
                    <MapPin className="w-4 h-4 mr-1" />
                    {service.location}
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center text-sm">
                      <Star className="w-4 h-4 text-yellow-400 fill-current mr-1" />
                      <span>4.{8 + index}</span>
                    </div>
                    {service.price_range && (
                      <div className="text-sm font-semibold text-blue-600">
                        {service.price_range}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ServiceDetails;