import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import ServicesCarousel from '../components/ServicesCarousel';
import { 
  MapPin, 
  BedDouble, 
  Bath, 
  Square, 
  Heart, 
  Share2, 
  Phone, 
  MessageSquare, 
  Calendar,
  ChevronLeft,
  ChevronRight,
  Star,
  Shield,
  Eye,
  ArrowLeft,
  User,
  Edit,
  Trash2
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PropertyDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [property, setProperty] = useState(null);
  const [owner, setOwner] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isFavorite, setIsFavorite] = useState(false);

  useEffect(() => {
    if (id) {
      fetchProperty();
    }
  }, [id]);

  const fetchProperty = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/properties/${id}`);
      setProperty(response.data);
      
      // Fetch owner data
      if (response.data.owner_id) {
        try {
          const ownerResponse = await axios.get(`${API}/users/${response.data.owner_id}`);
          setOwner(ownerResponse.data);
        } catch (ownerErr) {
          console.log('Could not fetch owner data:', ownerErr);
          // Don't fail the whole page if owner fetch fails
        }
      }
    } catch (err) {
      console.error('Error fetching property:', err);
      setError('Property not found');
    } finally {
      setLoading(false);
    }
  };

  const handleBooking = () => {
    if (!user) {
      navigate('/auth/callback');
      return;
    }
    navigate(`/booking/property/${id}`);
  };

  const handleMessage = () => {
    if (!user) {
      navigate('/auth/callback');
      return;
    }
    // Navigate to messages with pre-filled recipient
    navigate('/messages', { state: { recipientId: property.owner_id } });
  };

  const toggleFavorite = () => {
    setIsFavorite(!isFavorite);
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('fr-CM', {
      style: 'currency',
      currency: 'XAF',
      minimumFractionDigits: 0
    }).format(price);
  };

  const images = property?.images?.length > 0 
    ? property.images.map(img => 
        img.startsWith('/uploads/') ? `${BACKEND_URL}${img}` : img
      )
    : ['https://images.unsplash.com/photo-1560448204-e02f11c3d0e2'];

  const nextImage = () => {
    setCurrentImageIndex((prev) => (prev + 1) % images.length);
  };

  const prevImage = () => {
    setCurrentImageIndex((prev) => (prev - 1 + images.length) % images.length);
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

  if (error || !property) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Property Not Found</h2>
          <p className="text-gray-600 mb-8">The property you're looking for doesn't exist or has been removed.</p>
          <Link to="/properties" className="btn-primary">
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Properties
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="property-details">
      {/* Back button */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
            data-testid="back-btn"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Properties
          </button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Image Gallery */}
        <div className="relative mb-8">
          <div className="h-96 md:h-[500px] rounded-xl overflow-hidden bg-gray-200">
            <img
              src={images[currentImageIndex]}
              alt={property.title}
              className="w-full h-full object-cover"
              data-testid="property-image"
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

            {/* Action buttons overlay */}
            <div className="absolute top-4 right-4 flex space-x-2">
              <button
                onClick={toggleFavorite}
                className={`p-3 rounded-full transition-colors ${
                  isFavorite ? 'bg-red-500 text-white' : 'bg-white text-gray-600 hover:text-red-500'
                }`}
                data-testid="favorite-btn"
              >
                <Heart className={`w-5 h-5 ${isFavorite ? 'fill-current' : ''}`} />
              </button>
              <button
                className="p-3 bg-white text-gray-600 hover:text-blue-600 rounded-full transition-colors"
                data-testid="share-btn"
              >
                <Share2 className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Property Details */}
          <div className="lg:col-span-2 space-y-8">
            {/* Header */}
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <span className={`badge ${
                  property.listing_type === 'rent' ? 'badge-success' : 
                  property.listing_type === 'sale' ? 'badge-primary' : 'badge-warning'
                }`}>
                  {property.listing_type === 'rent' ? 'For Rent' : 
                   property.listing_type === 'sale' ? 'For Sale' : 'For Lease'}
                </span>
                {property.verified && (
                  <span className="badge badge-success flex items-center">
                    <Shield className="w-3 h-3 mr-1" />
                    Verified
                  </span>
                )}
                <span className="badge badge-secondary capitalize">
                  {property.property_type}
                </span>
              </div>

              <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
                {property.title}
              </h1>

              <div className="flex items-center text-gray-600 mb-4">
                <MapPin className="w-5 h-5 mr-2" />
                {property.location}
              </div>

              <div className="text-3xl md:text-4xl font-bold text-blue-600 mb-4">
                {formatPrice(property.price)}
                {property.listing_type === 'rent' && 
                  <span className="text-lg text-gray-500 font-normal">/month</span>
                }
              </div>

              {/* Property stats */}
              <div className="flex items-center space-x-6 text-gray-600">
                {property.bedrooms > 0 && (
                  <div className="flex items-center">
                    <BedDouble className="w-5 h-5 mr-2" />
                    <span className="font-medium">{property.bedrooms}</span>
                    <span className="ml-1">bedrooms</span>
                  </div>
                )}
                {property.bathrooms > 0 && (
                  <div className="flex items-center">
                    <Bath className="w-5 h-5 mr-2" />
                    <span className="font-medium">{property.bathrooms}</span>
                    <span className="ml-1">bathrooms</span>
                  </div>
                )}
                {property.area_sqm && (
                  <div className="flex items-center">
                    <Square className="w-5 h-5 mr-2" />
                    <span className="font-medium">{property.area_sqm}</span>
                    <span className="ml-1">m²</span>
                  </div>
                )}
              </div>
            </div>

            {/* Description */}
            <div className="card">
              <div className="card-body">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">Description</h3>
                <p className="text-gray-600 leading-relaxed whitespace-pre-wrap">
                  {property.description}
                </p>
              </div>
            </div>

            {/* Amenities */}
            {property.amenities && property.amenities.length > 0 && (
              <div className="card">
                <div className="card-body">
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">Amenities</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {property.amenities.map((amenity, index) => (
                      <div key={index} className="flex items-center text-gray-600">
                        <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                        {amenity}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Additional Images */}
            {images.length > 1 && (
              <div className="card">
                <div className="card-body">
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">
                    More Photos ({images.length})
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {images.map((image, index) => (
                      <button
                        key={index}
                        onClick={() => setCurrentImageIndex(index)}
                        className={`relative h-24 rounded-lg overflow-hidden border-2 transition-colors ${
                          index === currentImageIndex ? 'border-blue-500' : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <img
                          src={image}
                          alt={`Property photo ${index + 1}`}
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
          </div>

          {/* Booking Card */}
          <div className="lg:col-span-1">
            <div className="card sticky top-8">
              <div className="card-body">
                <div className="text-center mb-6">
                  <div className="text-2xl font-bold text-blue-600 mb-1">
                    {formatPrice(property.price)}
                  </div>
                  {property.listing_type === 'rent' && (
                    <div className="text-gray-500">per month</div>
                  )}
                </div>

                {user ? (
                  <div className="space-y-3">
                    {/* Show Edit and Delete buttons if user is the owner */}
                    {user.id === property.owner_id ? (
                      <>
                        <button
                          onClick={() => navigate(`/properties/edit/${property.id}`)}
                          className="btn-primary w-full justify-center bg-green-600 hover:bg-green-700"
                        >
                          <Edit className="w-5 h-5 mr-2" />
                          Edit Property
                        </button>
                        <button
                          onClick={handleDelete}
                          className="btn-secondary w-full justify-center bg-red-600 hover:bg-red-700 text-white border-red-600"
                        >
                          <Trash2 className="w-5 h-5 mr-2" />
                          Delete Property
                        </button>
                      </>
                    ) : (
                      <>
                        <button
                          onClick={handleBooking}
                          className="btn-primary w-full justify-center"
                          data-testid="book-viewing-btn"
                        >
                          <Calendar className="w-5 h-5 mr-2" />
                          Book Viewing
                        </button>

                        <button
                          onClick={handleMessage}
                          className="btn-secondary w-full justify-center"
                          data-testid="message-owner-btn"
                        >
                          <MessageSquare className="w-5 h-5 mr-2" />
                          Message Owner
                        </button>
                      </>
                    )}

                    <button className="btn-outline w-full justify-center">
                      <Phone className="w-5 h-5 mr-2" />
                      Call Owner
                    </button>
                  </div>
                ) : (
                  <div className="text-center">
                    <p className="text-gray-600 mb-4">
                      Sign in to book a viewing or contact the owner
                    </p>
                    <Link to="/auth/callback" className="btn-primary w-full justify-center">
                      Sign In to Contact
                    </Link>
                  </div>
                )}

                {/* Owner info */}
                <div className="border-t border-gray-200 mt-6 pt-6">
                  <div className="flex items-center space-x-4">
                    {owner?.picture ? (
                      <img 
                        src={owner.picture} 
                        alt={owner.name}
                        className="w-14 h-14 rounded-full object-cover border-2 border-gray-200"
                      />
                    ) : (
                      <div className="w-14 h-14 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white text-xl font-bold">
                        {owner?.name?.charAt(0)?.toUpperCase() || <User className="w-7 h-7" />}
                      </div>
                    )}
                    <div>
                      <p className="text-sm text-gray-600">Listed by</p>
                      <h4 className="font-semibold text-gray-900">{owner?.name || 'Property Owner'}</h4>
                      <p className="text-xs text-gray-500">{owner?.role?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Verified Seller'}</p>
                    </div>
                  </div>
                </div>

                {/* Safety note */}
                <div className="border-t border-gray-200 mt-6 pt-6">
                  <div className="flex items-start space-x-3">
                    <Shield className="w-5 h-5 text-green-500 mt-0.5" />
                    <div className="text-sm text-gray-600">
                      <p className="font-medium text-gray-900 mb-1">Your safety matters</p>
                      <p>Always meet in person and verify the property before making any payments.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Professional Services Carousel */}
        <div className="mt-12">
          <ServicesCarousel 
            title="Professional Services for Your Property" 
            limit={8}
            showAll={true}
          />
        </div>

        {/* Similar Properties */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Similar Properties</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Placeholder for similar properties */}
            {[1, 2, 3].map((index) => (
              <div key={index} className="card group">
                <div className="relative overflow-hidden">
                  <img
                    src={`https://images.unsplash.com/photo-156044820${index}-e02f11c3d0e2`}
                    alt={`Similar property ${index}`}
                    className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute top-3 left-3">
                    <span className="badge badge-primary">For Rent</span>
                  </div>
                </div>
                <div className="card-body">
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Similar Property {index}
                  </h3>
                  <div className="flex items-center text-gray-500 text-sm mb-3">
                    <MapPin className="w-4 h-4 mr-1" />
                    Douala, Cameroon
                  </div>
                  <div className="text-lg font-bold text-blue-600">
                    {formatPrice(property.price * (0.8 + index * 0.2))}
                    <span className="text-sm text-gray-500 font-normal">/month</span>
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

export default PropertyDetails;