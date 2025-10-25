import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import ServicesCarousel from '../components/ServicesCarousel';
import Reviews from '../components/Reviews';
import StarRating from '../components/StarRating';
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
    // Navigate to messages with userId query parameter
    navigate(`/messages?userId=${property.owner_id}`);
  };

  const handleCall = () => {
    if (!owner?.phone) {
      alert("Phone number not available");
      return;
    }
    window.location.href = `tel:${owner.phone}`;
  };

  const handleWhatsApp = () => {
    if (!owner?.phone) {
      alert("Phone number not available");
      return;
    }
    const message = encodeURIComponent(`Hi, I am interested in your property: ${property?.title}`);
    const phoneNumber = owner.phone.replace(/[^0-9]/g, ""); // Remove non-numeric characters
    window.open(`https://wa.me/${phoneNumber}?text=${message}`, "_blank");
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this property? This action cannot be undone.')) {
      return;
    }

    try {
      await axios.delete(`${API}/properties/${id}`);
      alert('Property deleted successfully');
      navigate('/profile');
    } catch (err) {
      console.error('Error deleting property:', err);
      alert('Failed to delete property. Please try again.');
    }
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
      <div className="min-h-screen bg-gray-50 py-4 sm:py-6 md:py-8">
        <div className="max-w-6xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8">
          <div className="animate-pulse">
            <div className="h-64 sm:h-80 md:h-96 bg-gray-300 rounded-xl sm:rounded-2xl mb-4 sm:mb-6 md:mb-8"></div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 md:gap-8">
              <div className="space-y-3 sm:space-y-4">
                <div className="h-6 sm:h-8 bg-gray-300 rounded w-3/4"></div>
                <div className="h-4 bg-gray-300 rounded w-1/2"></div>
                <div className="space-y-2">
                  <div className="h-4 bg-gray-300 rounded"></div>
                  <div className="h-4 bg-gray-300 rounded"></div>
                  <div className="h-4 bg-gray-300 rounded w-5/6"></div>
                </div>
              </div>
              <div className="h-48 sm:h-64 bg-gray-300 rounded-xl"></div>
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
        <div className="max-w-6xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8 py-3 sm:py-4">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors text-sm sm:text-base"
            data-testid="back-btn"
          >
            <ArrowLeft className="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" />
            Back
          </button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8 py-4 sm:py-6 md:py-8">
        {/* Image Gallery */}
        <div className="relative mb-4 sm:mb-6 md:mb-8">
          <div className="h-64 sm:h-80 md:h-96 lg:h-[500px] rounded-xl sm:rounded-2xl overflow-hidden bg-gray-200">
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
                  className="absolute left-2 sm:left-4 top-1/2 transform -translate-y-1/2 bg-white bg-opacity-80 hover:bg-opacity-100 rounded-full p-2 sm:p-3 shadow-lg transition-all"
                  data-testid="prev-image-btn"
                >
                  <ChevronLeft className="w-4 h-4 sm:w-5 sm:h-5" />
                </button>
                <button
                  onClick={nextImage}
                  className="absolute right-2 sm:right-4 top-1/2 transform -translate-y-1/2 bg-white bg-opacity-80 hover:bg-opacity-100 rounded-full p-2 sm:p-3 shadow-lg transition-all"
                  data-testid="next-image-btn"
                >
                  <ChevronRight className="w-4 h-4 sm:w-5 sm:h-5" />
                </button>

                {/* Image indicators */}
                <div className="absolute bottom-3 sm:bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-1.5 sm:space-x-2">
                  {images.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => setCurrentImageIndex(index)}
                      className={`w-2 h-2 sm:w-3 sm:h-3 rounded-full transition-colors ${
                        index === currentImageIndex ? 'bg-white' : 'bg-white bg-opacity-50'
                      }`}
                    />
                  ))}
                </div>
              </>
            )}

            {/* Action buttons overlay */}
            <div className="absolute top-2 sm:top-4 right-2 sm:right-4 flex space-x-1.5 sm:space-x-2">
              <button
                onClick={toggleFavorite}
                className={`p-2 sm:p-3 rounded-full transition-colors shadow-lg ${
                  isFavorite ? 'bg-red-500 text-white' : 'bg-white text-gray-600 hover:text-red-500'
                }`}
                data-testid="favorite-btn"
              >
                <Heart className={`w-4 h-4 sm:w-5 sm:h-5 ${isFavorite ? 'fill-current' : ''}`} />
              </button>
              <button
                className="p-2 sm:p-3 bg-white text-gray-600 hover:text-blue-600 rounded-full transition-colors shadow-lg"
                data-testid="share-btn"
              >
                <Share2 className="w-4 h-4 sm:w-5 sm:h-5" />
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6 md:gap-8">
          {/* Property Details */}
          <div className="lg:col-span-2 space-y-4 sm:space-y-6 md:space-y-8">
            {/* Header */}
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-3 sm:mb-4">
                <span className={`badge text-xs sm:text-sm ${
                  property.listing_type === 'rent' ? 'badge-success' : 
                  property.listing_type === 'sale' ? 'badge-primary' : 'badge-warning'
                }`}>
                  {property.listing_type === 'rent' ? 'For Rent' : 
                   property.listing_type === 'sale' ? 'For Sale' : 'For Lease'}
                </span>
                {property.verified && (
                  <span className="badge badge-success flex items-center text-xs sm:text-sm">
                    <Shield className="w-2.5 h-2.5 sm:w-3 sm:h-3 mr-0.5 sm:mr-1" />
                    Verified
                  </span>
                )}
                <span className="badge badge-secondary capitalize text-xs sm:text-sm">
                  {property.property_type}
                </span>
              </div>

              <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 mb-2 sm:mb-3">
                {property.title}
              </h1>

              <div className="flex items-center text-gray-600 mb-3 sm:mb-4 text-sm sm:text-base">
                <MapPin className="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2 flex-shrink-0" />
                <span className="truncate">{property.location}</span>
              </div>

              {/* Rating Display */}
              {property.average_rating > 0 && (
                <div className="flex items-center mb-3 sm:mb-4">
                  <StarRating rating={property.average_rating} size="md" />
                  <span className="ml-2 text-gray-600 text-sm">
                    {property.average_rating} ({property.review_count} {property.review_count === 1 ? 'review' : 'reviews'})
                  </span>
                </div>
              )}

              <div className="text-2xl sm:text-3xl md:text-4xl font-bold text-blue-600 mb-3 sm:mb-4">
                {formatPrice(property.price)}
                {property.listing_type === 'rent' && 
                  <span className="text-sm sm:text-base md:text-lg text-gray-500 font-normal">/month</span>
                }
              </div>

              {/* Property stats */}
              <div className="flex flex-wrap items-center gap-3 sm:gap-4 md:gap-6 text-gray-600 text-sm sm:text-base">
                {property.bedrooms > 0 && (
                  <div className="flex items-center">
                    <BedDouble className="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" />
                    <span className="font-medium">{property.bedrooms}</span>
                    <span className="ml-1 hidden sm:inline">bedrooms</span>
                    <span className="ml-1 sm:hidden">beds</span>
                  </div>
                )}
                {property.bathrooms > 0 && (
                  <div className="flex items-center">
                    <Bath className="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" />
                    <span className="font-medium">{property.bathrooms}</span>
                    <span className="ml-1 hidden sm:inline">bathrooms</span>
                    <span className="ml-1 sm:hidden">baths</span>
                  </div>
                )}
                {property.area_sqm && (
                  <div className="flex items-center">
                    <Square className="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" />
                    <span className="font-medium">{property.area_sqm}</span>
                    <span className="ml-1">m²</span>
                  </div>
                )}
              </div>
            </div>

            {/* Description */}
            <div className="card">
              <div className="card-body">
                <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-3 sm:mb-4">Description</h3>
                <p className="text-sm sm:text-base text-gray-600 leading-relaxed whitespace-pre-wrap">
                  {property.description}
                </p>
              </div>
            </div>

            {/* Amenities */}
            {property.amenities && property.amenities.length > 0 && (
              <div className="card">
                <div className="card-body">
                  <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-3 sm:mb-4">Amenities</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 sm:gap-3">
                    {property.amenities.map((amenity, index) => (
                      <div key={index} className="flex items-center text-gray-600 text-sm sm:text-base">
                        <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-green-500 rounded-full mr-2 sm:mr-3 flex-shrink-0"></div>
                        <span className="truncate">{amenity}</span>
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
                  <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-3 sm:mb-4">
                    More Photos ({images.length})
                  </h3>
                  <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-4 gap-2 sm:gap-3 md:gap-4">
                    {images.map((image, index) => (
                      <button
                        key={index}
                        onClick={() => setCurrentImageIndex(index)}
                        className={`relative h-20 sm:h-24 rounded-lg overflow-hidden border-2 transition-colors ${
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
                            <Eye className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600" />
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
            <div className="card lg:sticky lg:top-8">
              <div className="card-body">
                <div className="text-center mb-4 sm:mb-6">
                  <div className="text-xl sm:text-2xl font-bold text-blue-600 mb-1">
                    {formatPrice(property.price)}
                  </div>
                  {property.listing_type === 'rent' && (
                    <div className="text-sm sm:text-base text-gray-500">per month</div>
                  )}
                </div>

                {user ? (
                  <div className="space-y-2 sm:space-y-3">
                    {/* Show Edit and Delete buttons if user is the owner */}
                    {user.id === property.owner_id ? (
                      <>
                        <button
                          onClick={() => navigate(`/properties/edit/${property.id}`)}
                          className="btn-primary w-full justify-center bg-green-600 hover:bg-green-700 text-sm sm:text-base"
                        >
                          <Edit className="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" />
                          Edit Property
                        </button>
                        <button
                          onClick={handleDelete}
                          className="btn-secondary w-full justify-center bg-red-600 hover:bg-red-700 text-white border-red-600 text-sm sm:text-base"
                        >
                          <Trash2 className="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" />
                          Delete Property
                        </button>
                      </>
                    ) : (
                      <>
                        <button
                          onClick={handleBooking}
                          className="btn-primary w-full justify-center text-sm sm:text-base"
                          data-testid="book-viewing-btn"
                        >
                          <Calendar className="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" />
                          Book Viewing
                        </button>

                        <button
                          onClick={handleMessage}
                          className="btn-secondary w-full justify-center text-sm sm:text-base"
                          data-testid="message-owner-btn"
                        >
                          <MessageSquare className="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" />
                          Message Owner
                        </button>
                      </>
                    )}

                    <div className="grid grid-cols-2 gap-2 sm:gap-3">
                      <button 
                        onClick={handleCall}
                        className="btn-outline w-full justify-center text-sm sm:text-base"
                      >
                        <Phone className="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" />
                        Call
                      </button>
                      
                      <button 
                        onClick={handleWhatsApp}
                        className="w-full inline-flex items-center justify-center px-3 py-2.5 sm:px-4 sm:py-3 border-2 border-green-600 text-sm sm:text-base font-medium rounded-full text-green-600 bg-white hover:bg-green-600 hover:text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all duration-200 touch-manipulation"
                        style={{ minHeight: '44px' }}
                      >
                        <svg className="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.890-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                        </svg>
                        WhatsApp
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3 mt-3 sm:mt-4">
                      <Link
                        to={`/booking/property/${property.id}`}
                        className="btn-primary w-full justify-center text-sm sm:text-base"
                      >
                        <Calendar className="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" />
                        Book Viewing
                      </Link>
                      
                      <Link
                        to={`/messages?userId=${property.owner_id}`}
                        className="btn-outline w-full justify-center text-sm sm:text-base"
                      >
                        <MessageSquare className="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" />
                        Message Owner
                      </Link>
                      
                      <Link
                        to="/security/services"
                        className="bg-green-600 hover:bg-green-700 text-white px-4 py-2.5 rounded-lg font-medium transition-colors flex items-center w-full justify-center text-sm sm:text-base"
                      >
                        <Shield className="w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" />
                        Hire Security
                      </Link>
                    </div>
                  </div>
                ) : (
                  <div className="text-center">
                    <p className="text-sm sm:text-base text-gray-600 mb-3 sm:mb-4">
                      Sign in to book or contact
                    </p>
                    <Link to="/auth/callback" className="btn-primary w-full justify-center text-sm sm:text-base">
                      Sign In
                    </Link>
                  </div>
                )}

                {/* Owner info */}
                <div className="border-t border-gray-200 mt-4 sm:mt-6 pt-4 sm:pt-6">
                  <div className="flex items-center space-x-3 sm:space-x-4">
                    {owner?.picture ? (
                      <img 
                        src={owner.picture} 
                        alt={owner.name}
                        className="w-12 h-12 sm:w-14 sm:h-14 rounded-full object-cover border-2 border-gray-200 flex-shrink-0"
                      />
                    ) : (
                      <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white text-lg sm:text-xl font-bold flex-shrink-0">
                        {owner?.name?.charAt(0)?.toUpperCase() || <User className="w-6 h-6 sm:w-7 sm:h-7" />}
                      </div>
                    )}
                    <div className="min-w-0">
                      <p className="text-xs sm:text-sm text-gray-600">Listed by</p>
                      <h4 className="font-semibold text-sm sm:text-base text-gray-900 truncate">{owner?.name || 'Property Owner'}</h4>
                      <p className="text-xs text-gray-500 truncate">{owner?.role?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Verified Seller'}</p>
                    </div>
                  </div>
                </div>

                {/* Safety note */}
                <div className="border-t border-gray-200 mt-4 sm:mt-6 pt-4 sm:pt-6">
                  <div className="flex items-start space-x-2 sm:space-x-3">
                    <Shield className="w-4 h-4 sm:w-5 sm:h-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <div className="text-xs sm:text-sm text-gray-600">
                      <p className="font-medium text-gray-900 mb-1">Your safety matters</p>
                      <p>Always meet in person and verify before payment.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Professional Services Carousel */}
        <div className="mt-8 sm:mt-10 md:mt-12">
          <ServicesCarousel 
            title="Professional Services for Your Property" 
            limit={8}
            showAll={true}
          />
        </div>

        {/* Reviews Section */}
        <Reviews propertyId={id} type="property" />

        {/* Similar Properties */}
        <div className="mt-8 sm:mt-10 md:mt-12">
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4 sm:mb-6">Similar Properties</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 md:gap-6">
            {/* Placeholder for similar properties */}
            {[1, 2, 3].map((index) => (
              <div key={index} className="card group">
                <div className="relative overflow-hidden">
                  <img
                    src={`https://images.unsplash.com/photo-156044820${index}-e02f11c3d0e2`}
                    alt={`Similar property ${index}`}
                    className="w-full h-40 sm:h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute top-2 sm:top-3 left-2 sm:left-3">
                    <span className="badge badge-primary text-xs">For Rent</span>
                  </div>
                </div>
                <div className="card-body">
                  <h3 className="font-semibold text-sm sm:text-base text-gray-900 mb-1 sm:mb-2 truncate">
                    Similar Property {index}
                  </h3>
                  <div className="flex items-center text-gray-500 text-xs sm:text-sm mb-2 sm:mb-3">
                    <MapPin className="w-3 h-3 sm:w-4 sm:h-4 mr-1 flex-shrink-0" />
                    <span className="truncate">Douala, Cameroon</span>
                  </div>
                  <div className="text-base sm:text-lg font-bold text-blue-600">
                    {formatPrice(property.price * (0.8 + index * 0.2))}
                    <span className="text-xs sm:text-sm text-gray-500 font-normal">/month</span>
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