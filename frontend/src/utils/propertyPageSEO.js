// Dynamic SEO generator for individual property and service pages
import { generateSEOData, generateStructuredData, cameroonNeighborhoods } from './seoData';

// Generate comprehensive keywords for a property
export const generatePropertyKeywords = (property) => {
  const keywords = [];
  
  // Base property keywords
  const propertyTypeKeywords = {
    'house': ['maison', 'house', 'villa', 'résidence'],
    'apartment': ['appartement', 'apartment', 'studio', 'duplex'], 
    'land': ['terrain', 'land', 'lot', 'parcelle'],
    'commercial': ['bureau', 'office', 'magasin', 'commercial']
  };
  
  const transactionKeywords = {
    'rent': ['à louer', 'for rent', 'location', 'rental'],
    'sale': ['à vendre', 'for sale', 'vente', 'achat']
  };
  
  // Add property type keywords
  if (propertyTypeKeywords[property.property_type]) {
    keywords.push(...propertyTypeKeywords[property.property_type]);
  }
  
  // Add transaction type keywords  
  if (transactionKeywords[property.listing_type]) {
    keywords.push(...transactionKeywords[property.listing_type]);
  }
  
  // Add location-specific keywords
  if (property.location) {
    const location = property.location.toLowerCase();
    keywords.push(
      `${property.property_type} ${property.listing_type} ${location}`,
      `${property.property_type === 'house' ? 'maison' : 'appartement'} ${property.listing_type === 'rent' ? 'à louer' : 'à vendre'} ${location}`,
      `immobilier ${location}`,
      `real estate ${location}`
    );
    
    // Add neighborhood keywords if available
    Object.entries(cameroonNeighborhoods).forEach(([city, neighborhoods]) => {
      if (location.includes(city.toLowerCase())) {
        neighborhoods.forEach(neighborhood => {
          keywords.push(
            `${property.property_type} ${neighborhood.toLowerCase()} ${location}`,
            `${property.property_type === 'house' ? 'maison' : 'appartement'} ${neighborhood.toLowerCase()}`
          );
        });
      }
    });
  }
  
  // Add bedroom/bathroom specific keywords
  if (property.bedrooms) {
    keywords.push(
      `${property.bedrooms} chambres ${property.location}`,
      `${property.bedrooms} bedroom ${property.location}`,
      `${property.property_type} ${property.bedrooms} chambres`
    );
  }
  
  // Add price range keywords
  if (property.price) {
    const price = parseInt(property.price);
    if (price < 100000) {
      keywords.push('pas cher', 'affordable', 'budget');
    } else if (price > 1000000) {
      keywords.push('luxe', 'luxury', 'haut de gamme', 'premium');
    }
    
    keywords.push(
      `${property.price} XAF ${property.location}`,
      `prix ${property.property_type} ${property.location}`
    );
  }
  
  // Add amenity keywords
  if (property.amenities) {
    property.amenities.forEach(amenity => {
      keywords.push(`${property.property_type} avec ${amenity.toLowerCase()}`);
    });
  }
  
  return keywords.join(', ');
};

// Generate SEO-optimized property title
export const generatePropertyTitle = (property) => {
  const location = property.location || 'Cameroon';
  const propertyType = property.property_type === 'house' ? 'Maison' : 
                      property.property_type === 'apartment' ? 'Appartement' :
                      property.property_type === 'land' ? 'Terrain' : 'Propriété';
  
  const transaction = property.listing_type === 'rent' ? 'à Louer' : 'à Vendre';
  const bedrooms = property.bedrooms ? ` ${property.bedrooms} Chambres` : '';
  const area = property.area_sqm ? ` ${property.area_sqm}m²` : '';
  const price = property.price ? ` ${property.price} XAF` : '';
  
  return `${propertyType}${bedrooms}${area} ${transaction} ${location}${price} | Habitere`;
};

// Generate SEO-optimized property description
export const generatePropertyDescription = (property) => {
  const location = property.location || 'Cameroon';
  const propertyType = property.property_type === 'house' ? 'maison' : 
                      property.property_type === 'apartment' ? 'appartement' :
                      property.property_type === 'land' ? 'terrain' : 'propriété';
  
  const transaction = property.listing_type === 'rent' ? 'à louer' : 'à vendre';
  const bedrooms = property.bedrooms ? ` ${property.bedrooms} chambres,` : '';
  const bathrooms = property.bathrooms ? ` ${property.bathrooms} salles de bain,` : '';
  const area = property.area_sqm ? ` ${property.area_sqm}m²,` : '';
  const verified = property.verified ? ' Propriété vérifiée.' : '';
  
  let description = `${propertyType.charAt(0).toUpperCase() + propertyType.slice(1)} ${transaction} à ${location}.${bedrooms}${bathrooms}${area}${verified}`;
  
  if (property.amenities && property.amenities.length > 0) {
    description += ` Équipements: ${property.amenities.slice(0, 3).join(', ')}.`;
  }
  
  description += ` Prix: ${property.price} XAF. Réservation sécurisée avec MTN Mobile Money. Visitez Habitere pour plus de détails.`;
  
  return description;
};

// Generate service-specific SEO data
export const generateServiceSEO = (service) => {
  const location = service.location || 'Cameroon';
  const category = service.category || 'service';
  
  const keywords = [
    `${category} ${location.toLowerCase()}`,
    `professionnel ${category} cameroun`,
    `service ${category} ${location.toLowerCase()}`,
    `expert ${category}`,
    `${category} vérifié`,
    `${category} licensed`,
    `construction ${location.toLowerCase()}`,
    `rénovation ${location.toLowerCase()}`,
    `home services cameroon`
  ];
  
  const title = `${service.title || `Professionnel ${category}`} à ${location} | Services Vérifiés - Habitere`;
  
  const description = `${service.title || `Service ${category} professionnel`} à ${location}. ${service.rating ? `${service.rating}★ évalué, ` : ''}Expert vérifié, assuré. ${service.experience || '5+ ans'} d'expérience. Réservation sécurisée MTN MoMo.`;
  
  return {
    title,
    description,
    keywords: keywords.join(', '),
    focusKeyword: `${category} ${location.toLowerCase()}`
  };
};

// Generate breadcrumb structured data
export const generateBreadcrumbData = (property) => {
  const breadcrumbs = [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Accueil",
      "item": window.location.origin
    },
    {
      "@type": "ListItem", 
      "position": 2,
      "name": "Propriétés",
      "item": `${window.location.origin}/properties`
    }
  ];
  
  if (property.location && property.location !== 'Cameroon') {
    breadcrumbs.push({
      "@type": "ListItem",
      "position": 3,
      "name": property.location,
      "item": `${window.location.origin}/properties?location=${encodeURIComponent(property.location.toLowerCase())}`
    });
  }
  
  breadcrumbs.push({
    "@type": "ListItem",
    "position": breadcrumbs.length + 1,
    "name": property.title,
    "item": window.location.href
  });
  
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": breadcrumbs
  };
};

export default {
  generatePropertyKeywords,
  generatePropertyTitle,
  generatePropertyDescription,
  generateServiceSEO,
  generateBreadcrumbData
};